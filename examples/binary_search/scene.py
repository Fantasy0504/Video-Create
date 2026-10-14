"""二分查找 —— 数组 + 双指针结构的示例。

展示在一个有序数组里查找目标值：lo / hi 逐步收窄，每轮只看中间元素，
直到命中或区间为空。用来演示引擎里 ``ArrayView`` 这一路的用法。

运行：
    manimgl examples/binary_search/scene.py BinarySearch -w
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

from manimlib import *                                    # noqa: E402

from engine import AlgoScene, ArrayView, complexity_row, curtain, theme  # noqa: E402

DATA = (3, 7, 11, 18, 25, 33, 41)
TARGET = 25


class BinarySearch(AlgoScene):
    TITLE_TEXT = "二分查找"
    TITLE_TAG = f"target = {TARGET}"

    CODE_SOURCE = (
        "int bsearch(int a[], int n, int x) {",
        "    int lo = 0, hi = n - 1;",
        "    while (lo <= hi) {",
        "        int mid = (lo + hi) / 2;",
        "        if (a[mid] == x) return mid;",
        "        if (a[mid] < x) lo = mid + 1;",
        "        else hi = mid - 1;",
        "    }",
        "    return -1;",
        "}",
    )

    # 二分查找的代码行较长，面板会自动缩小字号，中心相应右移一点
    CODE_CENTER = (-4.60, 1.05)
    STATUS_CENTER = (-4.60, -1.05)

    # ---------------------------------------------------------------- 准备
    def setup(self):
        self.ptrs = {}

    def build(self):
        self.array = ArrayView(self, DATA, center=(2.30, 0.50), show_index=False)
        self.scene_intro()
        self.scene_rules()
        self.scene_search()
        self.scene_conclusion()

    # ------------------------------------------------------------ 指针管理
    def move_pointer(self, name, index, color):
        """重放一个指针：旧的淡出，新的出现在目标格下方。"""
        old = self.ptrs.pop(name, None)
        if old is not None:
            self.play(FadeOut(old), run_time=0.16)
        buff = 0.50 if name != "mid" else 0.98
        self.ptrs[name] = self.array.pointer(index, name, color, buff=buff)

    # -------------------------------------------------------- 场景一：任务
    def scene_intro(self):
        title = Text("二分查找", font=theme.chinese_font(),
                     font_size=theme.SIZE_TITLE, color=theme.WHITE)
        sub = Text(f"在 {len(DATA)} 个有序数里找 {TARGET}",
                   font=theme.chinese_font(), font_size=24, color=theme.WHITE)
        tag = Text(str(TARGET), font=theme.mono_font(),
                   font_size=34, color=theme.BLUE)
        group = VGroup(title, VGroup(tag, sub).arrange(RIGHT, buff=0.45))
        group.arrange(DOWN, buff=0.40)

        self.play(Write(title), run_time=0.50)
        self.play(FadeIn(tag, shift=UP * 0.10),
                  FadeIn(sub, shift=UP * 0.10), run_time=0.36)
        self.wait(0.70)
        self.play(FadeOut(group), run_time=0.34)

    # ------------------------------------------------------ 场景二：规则
    def scene_rules(self):
        self.add_title()
        self.add_code()
        self.code.bind(init=1, loop=2, mid=3, equal=4, less=5, more=6, fail=8)
        self.code.focus_now("init")
        self.array.appear(run_time=0.80)
        self.wait(0.30)

        self.add_status()
        self.status.set("lo = 0    hi = 6", run_time=0.26)
        self.add_hint()
        self.hint.set("数组有序，先看中间", run_time=0.28)
        self.wait(0.40)

    # ------------------------------------------------------ 场景三：查找
    def scene_search(self):
        lo, hi = 0, len(DATA) - 1
        self.move_pointer("lo", lo, theme.BLUE)
        self.move_pointer("hi", hi, theme.BLUE)
        self.wait(0.40)

        for round_no in (1, 2, 3):
            mid = (lo + hi) // 2
            self.code.focus(self, "mid", run_time=0.22)
            self.move_pointer("mid", mid, theme.BLUE)
            self.status.set(f"mid = {mid}    a[{mid}] = {DATA[mid]}",
                            run_time=0.26)
            self.play(self.array.accent(mid), run_time=0.24)
            self.wait(0.55)

            if DATA[mid] == TARGET:
                self.code.focus(self, "equal", run_time=0.22)
                self.hint.set(f"a[{mid}] 就是目标", run_time=0.28)
                self.array.reset_all_now()          # 清掉中途的红色排除标记
                self.array.hit(mid, hold=1.10)
                self.array.dim_except([mid], opacity=0.30)
                break

            if DATA[mid] < TARGET:
                self.code.focus(self, "less", run_time=0.22)
                self.hint.set(f"{DATA[mid]} < {TARGET}，丢掉左半边", run_time=0.28)
                self.array.cost(mid, run_time=0.26)
                lo = mid + 1
                self.move_pointer("lo", lo, theme.BLUE)
            else:
                self.code.focus(self, "more", run_time=0.22)
                self.hint.set(f"{DATA[mid]} > {TARGET}，丢掉右半边", run_time=0.28)
                self.array.cost(mid, run_time=0.26)
                hi = mid - 1
                self.move_pointer("hi", hi, theme.BLUE)

            self.status.set(f"lo = {lo}    hi = {hi}", run_time=0.24)
            self.wait(0.55)

        self.wait(0.40)

    # ------------------------------------------------------ 场景四：结论
    def scene_conclusion(self):
        self.code.hide(self)
        self.status.clear()
        self.hint.clear()
        for mob in self.ptrs.values():
            self.play(FadeOut(mob), run_time=0.12)
        self.ptrs.clear()

        curtain(self)

        result = Text(f"a[4] = {TARGET}", font=theme.mono_font(),
                      font_size=theme.SIZE_RESULT, color=theme.GREEN)
        result.move_to(np.array([0.0, 1.40, 0.0]))
        sentence = Text("每轮排除一半，最多 log n 次比较",
                        font=theme.chinese_font(), font_size=28, color=theme.WHITE)
        sentence.move_to(np.array([0.0, 0.42, 0.0]))

        rows = VGroup(
            complexity_row("查找时间  ", "", "log n", theme.GREEN),
            complexity_row("额外空间  ", "", "1", theme.GREEN),
        ).arrange(DOWN, buff=0.28)
        rows.move_to(np.array([0.0, -1.00, 0.0]))

        self.play(FadeIn(result, shift=UP * 0.12), run_time=0.48)
        self.play(FadeIn(sentence, shift=UP * 0.10), run_time=0.40)
        self.play(FadeIn(rows, shift=UP * 0.10), run_time=0.44)
        self.wait(2.10)
        self.play(FadeOut(VGroup(result, sentence, rows)), run_time=0.40)


class BinarySearchLite(BinarySearch):
    """简洁版：去掉片头铺垫与独立规则段，只留查找过程和一句结论。

    运行：
        manimgl examples/binary_search/scene.py BinarySearchLite -w
    """

    TITLE_TEXT = "二分查找"

    def build(self):
        self.array = ArrayView(self, DATA, center=(2.30, 0.45), show_index=False)

        self.add_title(run_time=0.30)
        self.add_code(run_time=0.50)
        self.code.bind(init=1, loop=2, mid=3, equal=4, less=5, more=6)
        self.code.focus_now("init")
        self.array.appear(run_time=0.50)

        self.add_status()
        self.add_hint()

        lo, hi = 0, len(DATA) - 1
        self.move_pointer("lo", lo, theme.BLUE)
        self.move_pointer("hi", hi, theme.BLUE)
        self.status.set(f"lo = {lo}    hi = {hi}", run_time=0.22)
        self.wait(0.25)

        mid = None
        while lo <= hi:
            mid = (lo + hi) // 2
            self.code.focus(self, "mid", run_time=0.16)
            self.move_pointer("mid", mid, theme.BLUE)
            self.status.set(f"mid = {mid}    a[{mid}] = {DATA[mid]}",
                            run_time=0.20)
            self.wait(0.30)

            if DATA[mid] == TARGET:
                self.code.focus(self, "equal", run_time=0.18)
                self.hint.set(f"命中 a[{mid}]", run_time=0.22)
                self.array.reset_all_now()          # 清掉中途的红色排除标记
                self.array.hit(mid, hold=0.90)
                self.array.dim_except([mid], opacity=0.30)
                break

            self.array.cost(mid, run_time=0.22)
            if DATA[mid] < TARGET:
                self.code.focus(self, "less", run_time=0.18)
                lo = mid + 1
                self.move_pointer("lo", lo, theme.BLUE)
            else:
                self.code.focus(self, "more", run_time=0.18)
                hi = mid - 1
                self.move_pointer("hi", hi, theme.BLUE)
            self.status.set(f"lo = {lo}    hi = {hi}", run_time=0.18)
            self.wait(0.30)

        self.exit_to_conclusion(mid)

    def exit_to_conclusion(self, mid):
        for ptr in self.ptrs.values():
            self.play(FadeOut(ptr), run_time=0.10)
        self.ptrs.clear()
        self.code.hide(self, run_time=0.28)
        self.status.clear(run_time=0.18)
        self.hint.clear(run_time=0.18)
        curtain(self, run_time=0.30)

        result = Text(f"a[{mid}] = {TARGET}", font=theme.mono_font(),
                      font_size=theme.SIZE_RESULT, color=theme.GREEN)
        result.move_to(np.array([0.0, 0.55, 0.0]))
        rows = VGroup(
            complexity_row("时间  ", "", "log n", theme.GREEN),
            complexity_row("空间  ", "", "1", theme.GREEN),
        ).arrange(RIGHT, buff=0.90)
        rows.move_to(np.array([0.0, -0.55, 0.0]))

        self.play(FadeIn(result, shift=UP * 0.10), run_time=0.40)
        self.play(FadeIn(rows, shift=UP * 0.08), run_time=0.36)
        self.wait(1.60)
