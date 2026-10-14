"""分治法求区间最大值 —— 数组递归示例。

演示**数组递归**：参数是下标区间，画面要同时显示两样东西 ——
数组（当前区间高亮）和调用树。两者靠 ``Region.split_top`` 各占一块，
不会叠在一起。

运行：
    manimgl examples/array_recursion/scene.py ArrayMax -w
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

from engine import (AlgoScene, Region, TreeSpec, complexity_row,  # noqa: E402
                    curtain, theme)

DATA = (7, 2, 9, 4, 1, 8, 3, 6)

# 由 tools/trace.py 从 array_max.py 导出，结构和执行顺序与真实运行一致
NODES = (
    (1, "[0,8)", 0, None),
    (2, "[0,4)", 1, 1),
    (3, "[0,2)", 2, 2),
    (4, "[0,1)", 3, 3),
    (5, "[1,2)", 3, 3),
    (6, "[2,4)", 2, 2),
    (7, "[2,3)", 3, 6),
    (8, "[3,4)", 3, 6),
    (9, "[4,8)", 1, 1),
    (10, "[4,6)", 2, 9),
    (11, "[4,5)", 3, 10),
    (12, "[5,6)", 3, 10),
    (13, "[6,8)", 2, 9),
    (14, "[6,7)", 3, 13),
    (15, "[7,8)", 3, 13),
)
CHILDREN = {
    1: (2, 9), 2: (3, 6), 3: (4, 5), 6: (7, 8),
    9: (10, 13), 10: (11, 12), 13: (14, 15),
}
LEAF_ORDER = (4, 5, 7, 8, 11, 12, 14, 15)

# 每个调用负责的区间，用来高亮数组
SPAN = {nid: (lo, hi) for nid, (lo, hi) in zip(
    [n[0] for n in NODES],
    [(0, 8), (0, 4), (0, 2), (0, 1), (1, 2), (2, 4), (2, 3), (3, 4),
     (4, 8), (4, 6), (4, 5), (5, 6), (6, 8), (6, 7), (7, 8)])}


class ArrayMax(AlgoScene):
    TITLE_TEXT = "分治求最大值"
    TITLE_TAG = "a[0..8)"

    CODE_SOURCE = (
        "int maxOf(int a[], int lo, int hi) {",
        "    if (hi - lo == 1) return a[lo];",
        "    int mid = (lo + hi) / 2;",
        "    int left = maxOf(a, lo, mid);",
        "    int right = maxOf(a, mid, hi);",
        "    return left > right ? left : right;",
        "}",
    )

    # 左侧代码面板窄一点，右侧留给"数组 + 调用树"两块
    CODE_CENTER = (-4.95, 1.30)
    STATUS_CENTER = (-4.95, -0.90)

    def setup(self):
        self.spec = TreeSpec(NODES, CHILDREN, LEAF_ORDER)
        self.calls = {}

    def build(self):
        array_region, tree_region = self._regions()
        self.arr = self.add_array(DATA, region=array_region, show_index=True)
        self.tree = self.add_tree(self.spec, region=tree_region)
        self.scene_intro()
        self.scene_walk()
        self.scene_wrapup()

    @staticmethod
    def _regions():
        """上半屏数组、下半屏调用树 —— PRD 2.4：根据结构安排布局。"""
        return Region(-2.30, 6.46, -3.28, 3.02).split_top(0.26)

    # ------------------------------------------------------------ 区间高亮
    def focus_span(self, lo, hi, run_time=0.26):
        """把数组里 [lo, hi) 这段描出来，其余保持普通色。"""
        anims = [self.arr.accent(i, theme.WHITE, 1.6)
                 for i in range(len(DATA)) if not lo <= i < hi]
        anims += [self.arr.accent(i, theme.BLUE, 2.8) for i in range(lo, hi)]
        self.play(*anims, run_time=run_time)

    def name_of(self, nid):
        return self.spec.label[nid]

    # ------------------------------------------------------------ 场景
    def scene_intro(self):
        self.add_title(run_time=0.30)
        self.add_code(run_time=0.50)
        self.code.bind(sig=0, base=1, mid=2, left=3, right=4, best=5)
        self.code.focus_now("base")
        self.arr.appear(run_time=0.70)
        self.add_status()
        self.add_hint()
        # 根节点 [0,8) 要先出现：后面的 enter 都是它的后代，
        # 漏了这一步会出现"只有一条边、没有节点"的悬空连线。
        self.tree.root(run_time=0.34)
        self.status.set("maxOf(a, 0, 8)", run_time=0.20)
        self.wait(0.30)

    def scene_walk(self):
        """真实深度优先：整棵左子树算完再进右边。顺序由 trace 导出。"""
        self.hint.set("先一路对半拆下去", run_time=0.26)

        # 5 → 4 → 3 → 2（对应 [0,8) → [0,4) → [0,2) → [0,1)）
        for nid in (2, 3, 4):
            lo, hi = SPAN[nid]
            self.code.focus(self, "left", run_time=0.12)
            self.focus_span(lo, hi)
            self.tree.enter(nid, run_time=0.26)
            self.status.set(f"{self.name_of(nid)}    len = {hi - lo}",
                            run_time=0.16)
        self.wait(0.20)

        self.tree.return_value(4, f"={DATA[0]}", hold=0.55)
        self.fill(3, 1, DATA[0])
        lo, hi = SPAN[5]
        self.code.focus(self, "right", run_time=0.12)
        self.focus_span(lo, hi)
        self.tree.enter(5, run_time=0.24)
        self.tree.return_value(5, f"={DATA[1]}", hold=0.45)
        self.fill(3, 2, DATA[1])

        self.hint.set("比出较大的那个", run_time=0.24)
        self.sum_node(3, hold=0.55)
        self.fill(2, 1, max(DATA[0:2]))

        lo, hi = SPAN[6]
        self.code.focus(self, "right", run_time=0.14)
        self.focus_span(lo, hi)
        self.tree.enter(6, run_time=0.26)
        self.focus_span(*SPAN[7])
        self.tree.enter(7, run_time=0.22)
        self.tree.return_value(7, f"={DATA[2]}", hold=0.34)
        self.fill(6, 1, DATA[2])
        self.focus_span(*SPAN[8])
        self.tree.enter(8, run_time=0.22)
        self.tree.return_value(8, f"={DATA[3]}", hold=0.34)
        self.fill(6, 2, DATA[3])
        self.sum_node(6, hold=0.34)
        self.fill(2, 2, max(DATA[2:4]))

        self.sum_node(2, hold=0.45)
        self.fill(1, 1, max(DATA[0:4]))
        self.hint.set("左半边算完，再进右半边", run_time=0.26)

        # 右半边 [4,8)
        lo, hi = SPAN[9]
        self.code.focus(self, "right", run_time=0.14)
        self.focus_span(lo, hi)
        self.tree.enter(9, run_time=0.28)
        self.focus_span(*SPAN[10])
        self.tree.enter(10, run_time=0.24)
        self.focus_span(*SPAN[11])
        self.tree.enter(11, run_time=0.20)
        self.tree.return_value(11, f"={DATA[4]}", hold=0.30)
        self.fill(10, 1, DATA[4])
        self.focus_span(*SPAN[12])
        self.tree.enter(12, run_time=0.20)
        self.tree.return_value(12, f"={DATA[5]}", hold=0.30)
        self.fill(10, 2, DATA[5])
        self.sum_node(10, hold=0.32)
        self.fill(9, 1, max(DATA[4:6]))

        self.focus_span(*SPAN[13])
        self.tree.enter(13, run_time=0.24)
        self.focus_span(*SPAN[14])
        self.tree.enter(14, run_time=0.20)
        self.tree.return_value(14, f"={DATA[6]}", hold=0.30)
        self.fill(13, 1, DATA[6])
        self.focus_span(*SPAN[15])
        self.tree.enter(15, run_time=0.20)
        self.tree.return_value(15, f"={DATA[7]}", hold=0.30)
        self.fill(13, 2, DATA[7])
        self.sum_node(13, hold=0.32)
        self.fill(9, 2, max(DATA[6:8]))

        self.sum_node(9, hold=0.40)
        self.fill(1, 2, max(DATA[4:8]))

        self.hint.set("两边合到根上", run_time=0.26)
        self.sum_node(1, hold=0.65)
        self.wait(0.30)

    # ------------------------------------------------------------ 助手
    def fill(self, nid, order, value, run_time=0.20):
        key = "left" if order == 1 else "right"
        self.calls.setdefault(nid, {})[key] = value
        self.status.set_call(self.name_of(nid), **self.calls[nid],
                             run_time=run_time)

    def sum_node(self, nid, hold=0.35):
        self.code.focus(self, "best", run_time=0.16)
        done = self.calls[nid]
        best = max(done["left"], done["right"])
        self.status.set_expr(self.name_of(nid),
                             f"max({done['left']}, {done['right']}) = {best}",
                             run_time=0.22)
        self.wait(hold)
        self.tree.send_up(nid)
        self.tree.finish(nid)

    def scene_wrapup(self):
        self.code.hide(self, run_time=0.28)
        self.status.clear(run_time=0.18)
        self.hint.clear(run_time=0.18)
        curtain(self, run_time=0.30)

        result = Text(f"最大值 {max(DATA)}", font=theme.chinese_font(),
                      font_size=theme.SIZE_RESULT, color=theme.GREEN)
        result.move_to(np.array([0.0, 0.55, 0.0]))
        rows = VGroup(
            complexity_row("时间  ", "", "n", theme.GREEN),
            complexity_row("递归深度  ", "", "log n", theme.GREEN),
        ).arrange(RIGHT, buff=0.90)
        rows.move_to(np.array([0.0, -0.60, 0.0]))

        self.play(FadeIn(result, shift=UP * 0.10), run_time=0.40)
        self.play(FadeIn(rows, shift=UP * 0.08), run_time=0.36)
        self.wait(1.70)
