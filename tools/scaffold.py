#!/usr/bin/env python3
"""从 ``tools/trace.py`` 导出的调用树，生成可运行的 scene.py 骨架。

生成的东西占了写新一期最难机械的那部分：

* ``NODES`` / ``CHILDREN`` / ``LEAF_ORDER`` 三份结构数据
* 按**真实事件顺序**排好的 ``enter`` / ``return_value`` / ``fill`` / ``sum_node``
  调用序列 —— 这一段最容易写错（比如写成按层返回就不真实了）

留给人工的仍然是真正需要判断的部分：C++ 代码、标题、底部提示文案、
以及每一段的节奏。生成结果带 TODO 标记，照着改就行。

用法：
    python tools/scaffold.py traces/fib.json \\
        --out examples/fibonacci_recursion/scene_gen.py \\
        --class FibonacciGen --title "非记忆化递归" --tag "fib(5)"
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HEADER = '''"""{title}

本文件由 ``tools/scaffold.py`` 从 ``{source}`` 生成。

结构和执行顺序是自动出来的（和真实运行完全一致），
下面标了 TODO 的地方需要人工决定：C++ 代码、标题、提示文案、节奏。
"""
import os
import sys

# 允许直接 manimgl 运行，不必先安装本包：向上找到含 engine/ 的目录
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = _HERE
while not os.path.isdir(os.path.join(_ROOT, "engine")):
    _parent = os.path.dirname(_ROOT)
    if _parent == _ROOT:
        break
    _ROOT = _parent
sys.path.insert(0, _ROOT)

from manimlib import *                                       # noqa: E402

from engine import AlgoScene, TreeSpec, curtain, theme       # noqa: E402
'''


def render_nodes(nodes):
    lines = ["NODES = ("]
    for n in nodes:
        parent = "None" if n["parent"] is None else str(n["parent"])
        lines.append(f'    ({n["id"]}, {n["label"]!r}, {n["depth"]}, {parent}),')
    lines.append(")")
    return "\n".join(lines)


def render_children(children):
    lines = ["CHILDREN = {"]
    parts = []
    for parent in sorted(children, key=int):
        kid_list = children[parent]
        kids = ", ".join(str(k) for k in kid_list)
        # 单个元素必须留尾逗号：写成 (2) 的话 Python 当它是整数 2，
        # 不是元组，后面 list(children[nid]) 会直接崩。
        if len(kid_list) == 1:
            kids += ","
        parts.append(f"{parent}: ({kids})")
    # 每行放两项，避免行太长
    for i in range(0, len(parts), 2):
        lines.append("    " + ", ".join(parts[i:i + 2]) + ",")
    lines.append("}")
    return "\n".join(lines)


def render_script(payload):
    """按真实事件顺序生成动画调用序列。"""
    nodes = {n["id"]: n for n in payload["nodes"]}
    children = {int(k): v for k, v in payload["children"].items()}
    lines = []

    for ev in payload["events"]:
        nid = ev["id"]
        if ev["kind"] == "enter":
            lines.append(f"        self.tree.enter({nid})")
            continue

        value = ev.get("value")
        kids = children.get(nid, [])
        if kids:
            lines.append(f"        self.sum_node({nid}, result={value!r})")
        else:
            lines.append(f'        self.tree.return_value({nid}, "={value}")')

        parent = nodes[nid]["parent"]
        if parent is not None:
            order = children[parent].index(nid) + 1
            lines.append(f"        self.fill({parent}, {order}, "
                         f"{ev.get('value')})")

    return "\n".join(lines)


def build_source(payload, class_name, title, tag, code, source_json):
    nodes_block = render_nodes(payload["nodes"])
    children_block = render_children(payload["children"])
    leaf = ", ".join(str(i) for i in payload["leaf_order"])
    script = render_script(payload)
    entry = payload["entry"]
    args_text = ", ".join(map(str, entry["args"]))
    summary = payload.get("summary", {})

    # 占位代码必须凑够 6 行，否则下面 bind() 的行号会越界。
    # CODE_SOURCE 里每一行都会被渲染出来，所以这里只能放真代码，不能放注释。
    code_lines = code if code else [
        '        "int f(int n) {",',
        '        "    if (n <= 1) return n;",',
        '        "    int left = f(n - 1);",',
        '        "    int right = f(n - 2);",',
        '        "    return left + right;",',
        '        "}",',
    ]
    code_block = "\n".join(code_lines)

    return f'''{HEADER.format(title=title, source=source_json)}

# ---------------------------------------------------------------- 结构数据
# 由 tools/trace.py 跑 {entry["func"]}({args_text}) 自动导出，
# 共 {summary.get("call_count", "?")} 次调用、{summary.get("base_count", "?")} 次基础情况、
# 最大深度 {summary.get("max_depth", "?")} 层。
{nodes_block}

{children_block}
LEAF_ORDER = ({leaf},)


class {class_name}(AlgoScene):
    TITLE_TEXT = {title!r}
    TITLE_TAG = {tag!r}

    # TODO: 换成这一期的 C++ 代码（默认给的是能跑通的占位）。
    #       行号要和 build() 里 bind() 对得上：
    #         0 函数签名 / 1 边界条件 / 2 左子调用 / 3 右子调用 / 4 求和 / 5 收尾
    CODE_SOURCE = (
{code_block}
    )

    # ------------------------------------------------------------ 节奏
    # TODO: 上面那段是机器生成的、每步同速。真实成片里"第一次执行要讲细、
    # 后续相同步骤可以简化"，把节奏改成下面这样会好看得多：
    #   首次下钻 / 首次求和 —— 用较长的 run_time 与 hold
    #   重复的同类步骤    —— 用较短的一端
    ENTER_RT = 0.28
    RETURN_HOLD = 0.45
    SUM_HOLD = 0.40

    def setup(self):
        self.spec = TreeSpec(NODES, CHILDREN, LEAF_ORDER)
        self.calls = {{}}

    def name_of(self, nid):
        return self.spec.label[nid]

    def fill(self, nid, order, value, run_time=0.22):
        """把第 order 个子调用的返回值，填进父调用自己的局部变量。"""
        key = "left" if order == 1 else "right"
        self.calls.setdefault(nid, {{}})[key] = value
        self.status.set_call(self.name_of(nid), **self.calls[nid],
                             run_time=run_time)

    def sum_node(self, nid, hold=None, result=None):
        """子调用都回来了，把结果算出来并沿真实父子边回传。

        ``result`` 是 trace 记下的**真实返回值**，不要自己拿子值现算 ——
        单支递归（链表长度那种 ``1 + length(rest)``）根本不是求和，
        硬加会算错。
        """
        self.code.focus(self, "total", run_time=0.16)
        done = self.calls[nid]
        vals = [done[k] for k in ("left", "right") if k in done]
        if len(vals) > 1:
            expr = " + ".join(map(str, vals)) + f" = {{result}}"
        else:
            expr = f"= {{result}}"
        self.status.set_expr(self.name_of(nid), expr, run_time=0.22)
        self.wait(self.SUM_HOLD if hold is None else hold)
        self.tree.send_up(nid)
        self.tree.finish(nid)

    # ---------------------------------------------------------------- 构建
    def build(self):
        self.tree = self.add_tree(self.spec)
        self.scene_setup()
        self.walk()
        self.scene_wrapup()

    def scene_setup(self):
        self.add_title(run_time=0.30)
        self.add_code(run_time=0.50)
        # TODO: 行号要对着你贴的 CODE_SOURCE 数一遍
        self.code.bind(sig=0, base=1, left=2, right=3, total=4, end=5)
        self.code.focus_now("base")
        self.add_status()
        self.add_hint()
        self.tree.root(run_time=0.34)
        self.status.set(self.TITLE_TAG, run_time=0.22)
        self.wait(0.30)

    def walk(self):
        """真实深度优先：先算完左子树，再进右子树。这一段是自动生成的。"""
{script}

    def scene_wrapup(self):
        # TODO: 结论页文案按这一期的算法改
        self.code.hide(self, run_time=0.28)
        self.status.clear(run_time=0.18)
        self.hint.clear(run_time=0.18)
        curtain(self, run_time=0.30)
        result = Text("结果是 …", font=theme.chinese_font(),
                      font_size=theme.SIZE_RESULT, color=theme.GREEN)
        result.move_to(np.array([0.0, 0.40, 0.0]))
        self.play(FadeIn(result, shift=UP * 0.10), run_time=0.40)
        self.wait(1.60)
'''


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="从调用树生成 scene.py 骨架")
    parser.add_argument("trace_json", help="tools/trace.py 的输出")
    parser.add_argument("--out", required=True, help="生成的 scene.py 路径")
    parser.add_argument("--class", dest="class_name", required=True,
                        help="场景类名")
    parser.add_argument("--title", default="算法演示", help="左上角标题")
    parser.add_argument("--tag", default="", help="标题右边的蓝色标记")
    parser.add_argument("--code", default=None,
                        help="C++ 代码文件，逐行读进来做 CODE_SOURCE")
    opts = parser.parse_args(argv)

    src = Path(opts.trace_json)
    if not src.is_absolute():
        src = ROOT / src
    if not src.exists():
        raise SystemExit(f"找不到 {src}")
    payload = json.loads(src.read_text(encoding="utf-8"))

    code_lines = None
    if opts.code:
        code_path = Path(opts.code)
        if not code_path.is_absolute():
            code_path = ROOT / code_path
        code_lines = [f"        {line!r},"
                      for line in code_path.read_text(encoding="utf-8").splitlines()]

    text = build_source(payload, opts.class_name, opts.title, opts.tag,
                        code_lines, src.name)

    out = Path(opts.out)
    if not out.is_absolute():
        out = ROOT / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")

    n_calls = payload.get("summary", {}).get("call_count", "?")
    print(f"已生成 {out}")
    print(f"  结构   {len(payload['nodes'])} 个节点（{n_calls} 次调用）")
    print(f"  分镜   {len(payload['events'])} 个事件已按真实顺序排好")
    print("  待办   CODE_SOURCE、标题、提示文案、节奏")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
