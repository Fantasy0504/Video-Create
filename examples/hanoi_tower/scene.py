"""汉诺塔（递归版）。

演示结构：**三根柱子 + 圆盘**。和递归树、数组都不同 —— 柱子本质是栈，
盘自下而上叠放（PRD 2.4："栈沿入栈方向变化"）。

演示输入 n = 3，共 7 次移动。简洁版，不做调用树展开。

运行：
    manimgl examples/hanoi_tower/scene.py HanoiTower -w
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

from engine import AlgoScene, HanoiView, curtain, theme   # noqa: E402

PEG = ("A", "B", "C")
DISKS = 3


class HanoiTower(AlgoScene):
    TITLE_TEXT = "汉诺塔"
    TITLE_TAG = f"n = {DISKS}"

    CODE_SOURCE = (
        "void hanoi(int n, char from, char to, char via) {",
        "    if (n == 1) {",
        "        move(from, to);",
        "        return;",
        "    }",
        "    hanoi(n - 1, from, via, to);",
        "    move(from, to);",
        "    hanoi(n - 1, via, to, from);",
        "}",
    )

    # 三根柱子居中偏右，代码面板相应左移一点
    CODE_CENTER = (-4.80, 1.20)
    STATUS_CENTER = (-4.80, -1.00)

    # ---------------------------------------------------------------- 准备
    def setup(self):
        self.moves = 0

    def build(self):
        self.pegs = HanoiView(self, pegs=PEG, disks=DISKS, center_x=2.10)
        self.scene_intro()
        self.scene_setup()
        self.solve(DISKS, 0, 2, 1)
        self.scene_conclusion()

    # ------------------------------------------------------------ 递归驱动
    def solve(self, n, src, dst, via):
        """递归函数直接驱动动画：进入一次调用就播一段。

        颜色对应 PRD 2.2：搬运中的盘是**蓝**（当前处理的对象），
        一次子问题收尾时把搬到 dst 的那一摞标**绿**（已完成的操作）——
        和斐波那契那期的回溯是同一种颜色语义，绿块随递归返回而扩大。
        """
        if n == 1:
            self.code.focus(self, "mv", run_time=0.16)
            self.do_move(src, dst)
            self.code.focus(self, "ret", run_time=0.14)
            return

        self.code.focus(self, "call1", run_time=0.18)
        self.hint.set(f"先把 {n - 1} 个盘从 {PEG[src]} 挪到 {PEG[via]}",
                      run_time=0.26)
        self.solve(n - 1, src, via, dst)

        self.code.focus(self, "mv", run_time=0.16)
        self.hint.set(f"挪这摞里最下面的盘：{PEG[src]} → {PEG[dst]}",
                      run_time=0.24)
        self.do_move(src, dst, hold=0.30)

        self.code.focus(self, "call2", run_time=0.18)
        self.hint.set(f"再把 {n - 1} 个盘从 {PEG[via]} 挪到 {PEG[dst]}",
                      run_time=0.26)
        self.solve(n - 1, via, dst, src)
        self.pegs.mark_settled(dst, n)

    def do_move(self, src, dst, hold=0.24):
        self.moves += 1
        self.status.set(f"第 {self.moves} 步    {PEG[src]} → {PEG[dst]}",
                        run_time=0.20)
        self.pegs.move_disk(src, dst, run_time=0.74, hold=hold)

    # -------------------------------------------------------- 场景一：任务
    def scene_intro(self):
        title = Text("汉诺塔 · 递归", font=theme.chinese_font(),
                     font_size=theme.SIZE_TITLE, color=theme.WHITE)
        sub = Text(f"{DISKS} 个盘，从 {PEG[0]} 挪到 {PEG[2]}",
                   font=theme.chinese_font(), font_size=24, color=theme.WHITE)
        tag = Text("A → C", font=theme.mono_font(),
                   font_size=34, color=theme.BLUE)
        group = VGroup(title, VGroup(tag, sub).arrange(RIGHT, buff=0.45))
        group.arrange(DOWN, buff=0.40)

        self.play(Write(title), run_time=0.48)
        self.play(FadeIn(tag, shift=UP * 0.10),
                  FadeIn(sub, shift=UP * 0.10), run_time=0.34)
        self.wait(0.60)
        self.play(FadeOut(group), run_time=0.30)

    # ------------------------------------------------------ 场景二：布置
    def scene_setup(self):
        self.add_title(run_time=0.32)
        self.add_code(run_time=0.52)
        self.code.bind(base=1, mv=2, ret=3, call1=5, call2=7)
        self.code.focus_now("base")
        self.pegs.appear(run_time=0.80)
        self.add_status()
        self.add_hint()
        self.status.set(f"目标：{PEG[0]} → {PEG[2]}", run_time=0.24)
        self.wait(0.35)

    # ------------------------------------------------------ 场景三：结论
    def scene_conclusion(self):
        self.code.hide(self, run_time=0.28)
        self.status.clear(run_time=0.18)
        self.hint.clear(run_time=0.18)
        self.pegs.mark_done(2, run_time=0.34)
        self.wait(0.30)
        curtain(self, run_time=0.30)

        result = Text(f"{self.moves} 次移动", font=theme.chinese_font(),
                      font_size=theme.SIZE_RESULT, color=theme.GREEN)
        result.move_to(np.array([0.0, 0.60, 0.0]))

        # 2^n − 1：上标手工排，负号用真正的 U+2212，不写成普通连字符
        label = Text("最少移动  ", font=theme.chinese_font(),
                     font_size=theme.SIZE_HEADING, color=theme.WHITE)
        two = Text("2", font=theme.mono_font(),
                   font_size=theme.SIZE_HEADING, color=theme.GREEN)
        sup = Text(str(DISKS), font=theme.mono_font(),
                   font_size=int(theme.SIZE_HEADING * 0.67), color=theme.GREEN)
        sup.next_to(two, RIGHT, buff=0.015).shift(UP * 0.18)
        # 先合成一组再参与 arrange，否则 arrange 会把上标拉回同一基线重排
        power = VGroup(two, sup)
        minus = Text("− 1", font=theme.mono_font(),
                     font_size=theme.SIZE_HEADING, color=theme.GREEN)
        formula = VGroup(label, power, minus).arrange(RIGHT, buff=0.16)
        formula.move_to(np.array([0.0, -0.60, 0.0]))

        self.play(FadeIn(result, shift=UP * 0.10), run_time=0.40)
        self.play(FadeIn(formula, shift=UP * 0.08), run_time=0.36)
        self.wait(1.80)
