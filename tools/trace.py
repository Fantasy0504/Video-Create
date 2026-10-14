#!/usr/bin/env python3
"""跑一遍递归函数，把完整的调用记录导出来。

用途：写新一期递归动画时，不必手工数"调用了多少次、谁调用了谁、
什么时候返回"。把 Python 版的等价递归函数交给它，一次跑完就得到调用树。

用法：
    python tools/trace.py <文件.py>:<函数名> --args 5 --label "fib({0})"

例：
    python tools/trace.py examples/fibonacci_recursion/fib_py.py:fib \\
        --args 5 --label "fib({0})" -o traces/fib.json

参数：
    --args    入口参数，逗号分隔（``--args 5`` 或 ``--args 3,A,B,C``）
    --label   节点显示标签的 format 串，``{0} {1} ...`` 对应第几个参数
    --out     输出的 JSON 路径，默认打印到标准输出

输出结构：
    {
      "entry":  {"func": "fib", "args": [5]},
      "nodes":  [{"id", "label", "depth", "parent", "args", "result"}, ...],
      "events": [{"kind": "enter"|"return", "id", "value"}, ...],
      "children":     {"父 id": [子 id, ...]},
      "leaf_order":   [从左到右的叶子 id],
      "call_count":   15,
      "base_count":   8
    }

``label`` 是可选的 —— 不给就用 ``函数名(参数, ...)``。
"""
from __future__ import annotations

import argparse
import functools
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class Tracer:
    """把递归函数包一层，记录每次进入与返回。

    Python 的递归函数通过模块级名字调用自己，所以只要把模块里的名字换成
    包装后的版本，内部递归也会被记录到 —— 不需要改用户的算法代码。
    """

    def __init__(self, label_fmt=None, label_fn=None):
        self.label_fmt = label_fmt
        self.label_fn = label_fn
        self.nodes: list[dict] = []
        self.events: list[dict] = []
        self.stack: list[int] = []

    def _label(self, func_name, args, kwargs):
        if self.label_fn is not None:
            return str(self.label_fn(*args, **kwargs))
        if self.label_fmt:
            try:
                return self.label_fmt.format(*args, **kwargs)
            except (IndexError, KeyError):
                pass
        shown = list(args) + [f"{k}={v}" for k, v in kwargs.items()]
        return f"{func_name}({', '.join(map(str, shown))})"

    def wrap(self, func):
        func_name = getattr(func, "__name__", "f")

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nid = len(self.nodes) + 1
            label = self._label(func_name, args, kwargs)

            self.nodes.append({
                "id": nid,
                "label": label,
                "depth": len(self.stack),
                "parent": self.stack[-1] if self.stack else None,
                "args": [to_jsonable(a) for a in args],
            })
            self.events.append({"kind": "enter", "id": nid})

            self.stack.append(nid)
            result = func(*args, **kwargs)
            self.stack.pop()

            # 返回值也可能是对象（链表反转返回的是头节点），同样要转成
            # 能进 JSON 的形式，否则导出时报 not JSON serializable
            shown = to_jsonable(result)
            self.nodes[nid - 1]["result"] = shown
            self.events.append({"kind": "return", "id": nid, "value": shown})
            return result

        return wrapper


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"无法加载 {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[path.stem] = module
    spec.loader.exec_module(module)
    return module


def to_jsonable(value):
    """对象类型的参数（链表节点、树节点）没法直接进 JSON，转成字符串。

    标量原样保留 —— 它们后面还要用来算距离、做算术。
    """
    if value is None or isinstance(value, (int, float, str, bool)):
        return value
    return str(value)


def parse_args(text):
    """``"5"`` → ``[5]``；``"3,A,B"`` → ``[3, "A", "B"]``"""
    out = []
    for token in text.split(","):
        token = token.strip()
        try:
            out.append(int(token))
        except ValueError:
            try:
                out.append(float(token))
            except ValueError:
                out.append(token)
    return out


def derive_children(nodes):
    """按进入顺序推出每个节点的子节点列表（左在前）。"""
    children: dict[int, list[int]] = {}
    for node in nodes:
        parent = node["parent"]
        if parent is None:
            continue
        children.setdefault(parent, []).append(node["id"])
    return children


def derive_leaf_order(nodes, children):
    """从左到右排列的叶子 id —— 深度优先顺序下的无子节点。"""
    return [n["id"] for n in nodes if n["id"] not in children]


def summarise(nodes, children, events):
    leaves = [n for n in nodes if n["id"] not in children]
    labels: dict[str, int] = {}
    for node in nodes:
        labels[node["label"]] = labels.get(node["label"], 0) + 1
    return {
        "call_count": len(nodes),
        "base_count": len(leaves),
        "max_depth": max((n["depth"] for n in nodes), default=0) + 1,
        "label_counts": labels,
        "enter_return_alternates": _alternates(events),
    }


def _alternates(events):
    """检查进入与返回是否严格成对交替 —— 递归执行顺序是否真实。"""
    stack = []
    for ev in events:
        if ev["kind"] == "enter":
            stack.append(ev["id"])
        else:
            if not stack or stack[-1] != ev["id"]:
                return False
            stack.pop()
    return not stack


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="跑一遍递归函数，导出完整调用树")
    parser.add_argument("target", help="<文件.py>:<函数名>")
    parser.add_argument("--args", default="", help="入口参数，逗号分隔")
    parser.add_argument("--label", default=None,
                        help='节点标签 format 串，例如 "fib({0})"')
    parser.add_argument("--input-fn", default=None,
                        help="从目标文件里调这个函数来生成入口参数，"
                             "用于链表 / 树这类没法写在命令行的对象，"
                             "比如 --input-fn make_list --args 4")
    parser.add_argument("--label-fn", default=None,
                        help="从目标文件里调这个函数，把参数转成节点标签；"
                             "对象参数必须给，否则标签会变成 <Node object at 0x…>")
    parser.add_argument("-o", "--out", default=None, help="输出 JSON 路径")
    opts = parser.parse_args(argv)

    if ":" not in opts.target:
        parser.error("target 要写成 <文件.py>:<函数名>")
    file_part, func_name = opts.target.rsplit(":", 1)

    path = Path(file_part)
    if not path.is_absolute():
        candidate = (Path.cwd() / path)
        path = candidate if candidate.exists() else (ROOT / path)
    if not path.exists():
        raise SystemExit(f"找不到文件：{path}")

    module = load_module(path)
    if not hasattr(module, func_name):
        raise SystemExit(f"{path.name} 里没有 {func_name}"
                         f"（可用：{', '.join(d for d in dir(module) if not d.startswith('_'))}）")

    label_fn = None
    if opts.label_fn:
        if not hasattr(module, opts.label_fn):
            raise SystemExit(f"{path.name} 里没有 {opts.label_fn}")
        label_fn = getattr(module, opts.label_fn)

    tracer = Tracer(opts.label, label_fn)
    setattr(module, func_name, tracer.wrap(getattr(module, func_name)))

    if opts.input_fn:
        maker = getattr(module, opts.input_fn, None)
        if maker is None:
            raise SystemExit(f"{path.name} 里没有 {opts.input_fn}")
        call_args = maker(*parse_args(opts.args))
        if not isinstance(call_args, tuple):
            call_args = (call_args,)
    else:
        call_args = parse_args(opts.args)

    shown = ", ".join(map(str, call_args))
    print(f"跑 {func_name}({shown}) …", file=sys.stderr)
    result = getattr(module, func_name)(*call_args)
    print(f"返回值 {result!r}，记录 {len(tracer.nodes)} 次调用", file=sys.stderr)

    children = derive_children(tracer.nodes)
    payload = {
        "entry": {"func": func_name,
                  "args": [to_jsonable(a) for a in call_args]},
        "nodes": tracer.nodes,
        "events": tracer.events,
        "children": {str(k): v for k, v in children.items()},
        "leaf_order": derive_leaf_order(tracer.nodes, children),
        "summary": summarise(tracer.nodes, children, tracer.events),
    }

    text = json.dumps(payload, ensure_ascii=False, indent=2)
    if opts.out:
        out_path = Path(opts.out)
        if not out_path.is_absolute():
            out_path = ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(text, encoding="utf-8")
        print(f"已写出 {out_path}", file=sys.stderr)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
