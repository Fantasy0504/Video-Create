"""带 static 变量的递归 —— 调用计数器。

这一期讲的是 ``static`` 局部变量在递归里的行为：**只有一份，跨所有调用
共享**，不会每次进入函数都重新初始化。

画面上靠两栏对照来说明：

* 左侧「状态行」是**当前调用**的局部变量，每进一层就换一组
* 左侧「static 栏」**始终只有一行**，值一路累加

运行：
    manimgl examples/static_variable/scene.py FibStatic -w
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = _HERE
while not os.path.isdir(os.path.join(_ROOT, "engine")):
    _parent = os.path.dirname(_ROOT)
    if _parent == _ROOT:
        break
    _ROOT = _parent
sys.path.insert(0, _ROOT)

from manimlib import *                                    # noqa: E402

from engine import (AlgoScene, TreeSpec, complexity_row,  # noqa: E402
                    curtain, theme)

ENTRY = 4

# 由 tools/trace.py 从 fib_static.py 导出
NODES = (
    (1, "fib(4)", 0, None),
    (2, "fib(3)", 1, 1),
    (3, "fib(2)", 2, 2),
    (4, "fib(1)", 3, 3),
    (5, "fib(0)", 3, 3),
    (6, "fib(1)", 2, 2),
    (7, "fib(2)", 1, 1),
    (8, "fib(1)", 2, 7),
    (9, "fib(0)", 2, 7),
)
CHILDREN = {1: (2, 7), 2: (3, 6), 3: (4, 5), 7: (8, 9)}
LEAF_ORDER = (4, 5, 6, 8, 9)

# 每个调用是第几次进入 —— 对应 static 计数器的值
ORDER = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9}


class FibStatic(AlgoScene):
    TITLE_TEXT = "递归里的 static"
    TITLE_TAG = f"fib({ENTRY})"

    CODE_SOURCE = (
        "int fib(int n) {",
        "    static int calls = 0;     // 只有一份",
        "    calls++;                  // 所有调用共用",
        "    if (n <= 1) return n;",
        "    int left = fib(n - 1);",
        "    int right = fib(n - 2);",
        "    return left + right;",
        "}",
    )

    CODE_CENTER = (-5.05, 1.30)
    STATUS_CENTER = (-5.05, -0.85)

    def setup(self):
        self.spec = TreeSpec(NODES, CHILDREN, LEAF_ORDER)
        self.calls = {}

    def build(self):
        self.tree = self.add_tree(self.spec)
        self.scene_intro()
        self.scene_walk()
        self.scene_wrapup()

    # ------------------------------------------------------------ 场景
    def scene_intro(self):
        self.add_title(run_time=0.30)
        self.add_code(run_time=0.55)
        self.code.bind(defn=0, decl=1, incr=2, base=3, left=4, right=5, ret=6)
        self.code.focus_now("decl")
        self.add_status()
        self.add_hint()
        self.static = self.add_static(center=(-5.05, -2.35))
        self.static.set({"calls": 0}, run_time=0.30)
        self.tree.root(run_time=0.34)
        self.hint.set("static 只有一份，所有调用共用", run_time=0.30)
        self.wait(0.40)

    def bump(self, nid, run_time=0.20):
        """进入一次调用：static 计数器加一并高亮这一行。"""
        self.code.focus(self, "incr", run_time=0.12)
        self.static.set({"calls": ORDER[nid]}, changed="calls",
                        run_time=run_time)

    def scene_walk(self):
        self.bump(1)
        self.status.set("fib(4)    自己的 n = 4", run_time=0.18)

        # 一路往左下钻
        for nid in (2, 3):
            self.code.focus(self, "left", run_time=0.12)
            self.tree.enter(nid, run_time=0.24)
            self.bump(nid)
            self.status.set(f"{self.spec.label[nid]}    n = {5 - nid}",
                            run_time=0.16)

        self.code.focus(self, "left", run_time=0.12)
        self.tree.enter(4, run_time=0.22)
        self.bump(4)
        self.hint.set("每进一层，calls 都往上加", run_time=0.26)
        self.tree.return_value(4, "=1", hold=0.42)
        self.fill(3, 1, 1)

        self.code.focus(self, "right", run_time=0.12)
        self.tree.enter(5, run_time=0.22)
        self.bump(5)
        self.tree.return_value(5, "=0", hold=0.36)
        self.fill(3, 2, 0)
        self.sum_node(3, hold=0.36)
        self.fill(2, 1, 1)

        self.code.focus(self, "right", run_time=0.12)
        self.tree.enter(6, run_time=0.22)
        self.bump(6)
        self.tree.return_value(6, "=1", hold=0.34)
        self.fill(2, 2, 1)
        self.sum_node(2, hold=0.38)
        self.fill(1, 1, 2)

        self.hint.set("右边这棵是另一次新调用", run_time=0.26)
        self.code.focus(self, "right", run_time=0.12)
        self.tree.enter(7, run_time=0.26)
        self.bump(7)
        self.tree.enter(8, run_time=0.22)
        self.bump(8)
        self.tree.return_value(8, "=1", hold=0.28)
        self.fill(7, 1, 1)
        self.tree.enter(9, run_time=0.22)
        self.bump(9)
        self.tree.return_value(9, "=0", hold=0.28)
        self.fill(7, 2, 0)
        self.sum_node(7, hold=0.32)
        self.fill(1, 2, 1)

        self.sum_node(1, hold=0.50)
        self.wait(0.30)

    # ------------------------------------------------------------ 助手
    def fill(self, nid, order, value, run_time=0.20):
        key = "left" if order == 1 else "right"
        self.calls.setdefault(nid, {})[key] = value
        self.status.set_call(self.spec.label[nid], **self.calls[nid],
                             run_time=run_time)

    def sum_node(self, nid, hold=0.35):
        self.code.focus(self, "ret", run_time=0.16)
        done = self.calls[nid]
        total = done["left"] + done["right"]
        self.status.set_expr(self.spec.label[nid],
                             f"{done['left']} + {done['right']} = {total}",
                             run_time=0.20)
        self.wait(hold)
        self.tree.send_up(nid)
        self.tree.finish(nid)

    def scene_wrapup(self):
        self.code.hide(self, run_time=0.28)
        self.status.clear(run_time=0.18)
        self.hint.clear(run_time=0.18)
        curtain(self, run_time=0.30)

        result = Text("fib(4) = 3", font=theme.mono_font(),
                      font_size=theme.SIZE_RESULT, color=theme.GREEN)
        result.move_to(np.array([0.0, 0.80, 0.0]))
        note = Text("9 次调用，calls 一路加到 9 —— 中间没有重置过",
                    font=theme.chinese_font(), font_size=26, color=theme.WHITE)
        note.move_to(np.array([0.0, 0.05, 0.0]))
        rows = VGroup(
            complexity_row("时间上界  ", "2", "n", theme.RED),
            complexity_row("栈空间    ", "", "n", theme.GREEN),
        ).arrange(RIGHT, buff=0.80)
        rows.move_to(np.array([0.0, -0.85, 0.0]))

        self.play(FadeIn(result, shift=UP * 0.10), run_time=0.42)
        self.play(FadeIn(note, shift=UP * 0.08), run_time=0.38)
        self.play(FadeIn(rows, shift=UP * 0.08), run_time=0.36)
        self.wait(1.80)
