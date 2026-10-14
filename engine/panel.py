"""固定位置的文字组件：标题、代码面板、状态行、底部提示、结论页。

对应 PRD 2.3（文字与代码）与 10.1（画面布局）：
* 代码保留真实语法与缩进，常规内容白色，当前行用蓝色短线定位；
  不给每一行加彩色底板，也不随递归进入而缩放
* 左侧代码区下方显示"当前调用的参数和局部求和值"
* 底部最多一行简短提示，同一阶段只使用一条

两条踩过的经验，写在这里免得重犯：

* **换文本不要用 ``Transform``**。它按点集插值，两段文字结构差得多时会把
  字拉伸扭曲、留下残影。状态行与提示行统一走"淡出旧的 + 淡入新的"。
* **不要写死 ``mono_font()`` 去显示用户给的字符串**。等宽字体通常没有中文
  字形，"第 5 步  B → A" 会只剩数字和字母。凡是要显示文本的地方都用
  ``theme.pick_font(text)``，它按内容挑字体。
"""
from __future__ import annotations

import numpy as np
from manimlib import *

from . import theme


class TitleBar:
    """左上角固定标题，右侧可带一个蓝色输入标记。"""

    def __init__(self, title, tag=None):
        self.title = Text(title, font=theme.chinese_font(),
                          font_size=theme.SIZE_HEADING, color=theme.WHITE)
        self.title.to_corner(UL, buff=0.45)
        self.tag = None
        if tag:
            self.tag = Text(tag, font=theme.mono_font(),
                            font_size=theme.SIZE_HEADING, color=theme.BLUE)
            self.tag.next_to(self.title, RIGHT, buff=0.35)

    @property
    def mob(self):
        return VGroup(self.title, self.tag) if self.tag else self.title

    def show(self, scene, run_time=0.40):
        scene.play(FadeIn(self.mob), run_time=run_time)


class CodePanel:
    """固定位置的代码展示与当前行定位。"""

    def __init__(self, source, *, center=(-5.00, 1.30), size=None,
                 line_buff=0.155, max_width=4.10):
        self._names = {}
        base_size = size or theme.SIZE_CODE
        self.lines = self._render(source, base_size)

        # 代码比安全边距还宽时整体缩小字号，而不是让文字冲出画面。
        # 这是一次性的版面适配，不是"每次进入递归就缩放代码"（PRD 2.3）。
        widest = max((line.get_width() for line in self.lines), default=0.0)
        if widest > max_width:
            base_size = max(13, int(base_size * max_width / widest))
            self.lines = self._render(source, base_size)
        self.size = base_size

        self.mob = VGroup(*self.lines).arrange(DOWN, aligned_edge=LEFT,
                                               buff=line_buff)
        self.mob.move_to(np.array([center[0], center[1], 0.0]))

        self.cursors = []
        for line in self.lines:
            cursor = Line(line.get_left() + LEFT * 0.11 + DOWN * 0.115,
                          line.get_left() + LEFT * 0.11 + UP * 0.115)
            cursor.set_stroke(theme.BLUE, width=3.2)
            cursor.set_stroke(opacity=0.0)
            self.cursors.append(cursor)

    @staticmethod
    def _render(source, font_size):
        # 按行挑字体：等宽字体没有中文字形，代码里带中文注释会渲染成乱码
        # （Consolas 下会退化成一串十六进制方块）。含中文的行改用中文字体，
        # 代价是那一行的拉丁字符不再是等宽，所以注释尽量放行尾、别参与对齐。
        return [Text(text, font=theme.pick_font(text),
                     font_size=font_size, color=theme.WHITE)
                for text in source]

    def bind(self, **names):
        """把有意义的名字绑到行号，例如 ``bind(base=1, left=2, right=3)``。"""
        self._names.update(names)
        return self

    def _index(self, target):
        if isinstance(target, str):
            if target not in self._names:
                raise KeyError(f"未绑定的代码行名：{target}，"
                               f"已绑定 {sorted(self._names)}")
            return self._names[target]
        return target

    def show(self, scene, run_time=0.90):
        scene.play(
            LaggedStart(*[FadeIn(l, shift=RIGHT * 0.12) for l in self.lines],
                        lag_ratio=0.14),
            run_time=run_time,
        )
        scene.add(*self.cursors)

    def focus_now(self, target):
        """不播放动画，直接把蓝色光标定位到某一行。"""
        idx = self._index(target)
        for i, cursor in enumerate(self.cursors):
            cursor.set_stroke(opacity=1.0 if i == idx else 0.0)

    def focus(self, scene, target, run_time=0.24):
        """把蓝色光标移到指定行，其他行隐藏。"""
        idx = self._index(target)
        anims = []
        for i, cursor in enumerate(self.cursors):
            want = 1.0 if i == idx else 0.0
            if abs(cursor.get_stroke_opacity() - want) > 0.01:
                anims.append(cursor.animate.set_stroke(opacity=want))
        if anims:
            scene.play(*anims, run_time=run_time)

    def hide(self, scene, run_time=0.40):
        scene.play(FadeOut(self.mob),
                   *[FadeOut(c) for c in self.cursors],
                   run_time=run_time)


class StatusLine:
    """左侧面板下方的"当前调用的参数和局部求和值"。"""

    def __init__(self, scene, *, center=(-5.00, -0.95), size=None):
        self.scene = scene
        self.pos = np.array([center[0], center[1], 0.0])
        self.size = size or theme.SIZE_NODE
        self.mob = None

    def set(self, text, run_time=0.28):
        new = Text(text, font=theme.pick_font(text),
                   font_size=self.size, color=theme.WHITE)
        new.move_to(self.pos)
        if self.mob is None:
            self.mob = new
            self.scene.play(FadeIn(self.mob, shift=UP * 0.07), run_time=run_time)
            return
        # 不要用 Transform 换文本：它按点集插值，两段文字结构差得多时会把
        # 字拉伸扭曲并留下残影。状态行内容变化大（"目标：A → C" → "第 5 步
        # B → A"），必须整块换掉。斐波那契那期文字结构稳定，所以没暴露。
        old = self.mob
        self.mob = new
        self.scene.play(FadeOut(old, run_time=run_time * 0.6),
                        FadeIn(new, run_time=run_time * 0.6))
        self.scene.remove(old)

    def set_call(self, name, run_time=0.28, **values):
        """``set_call("fib(2)", left=1)`` → ``fib(2)    left = 1``"""
        parts = [name] + [f"{k} = {v}" for k, v in values.items()]
        self.set("    ".join(parts), run_time=run_time)

    def set_expr(self, name, expr, run_time=0.28):
        """``set_expr("fib(2)", "1 + 0 = 1")``"""
        self.set(f"{name}    {expr}", run_time=run_time)

    def clear(self, run_time=0.30):
        if self.mob is not None:
            self.scene.play(FadeOut(self.mob), run_time=run_time)
            self.mob = None


class StaticPanel:
    """跨调用共享的变量（C 里的 ``static``）。

    局部变量每次调用都是新的一份，``static`` 全局只有一份 —— 这个区别
    正是这类题目的教学重点，所以画面上要看得出来：单独占一栏、带
    ``static`` 标签、值被改动时那一行闪绿（PRD 2.2 绿＝已完成的操作）。

    同时把「是哪一次调用改的」写出来，否则观众会以为每次进入函数都重置。
    """

    def __init__(self, scene, *, center=(-5.00, -2.30), size=None,
                 label="static"):
        self.scene = scene
        self.pos = np.array([center[0], center[1], 0.0])
        self.size = size or theme.SIZE_NODE - 2
        self.label = label
        self.mob = None

    def _render(self, values, changed):
        rows = [Text(self.label, font=theme.mono_font(),
                     font_size=self.size, color=theme.WHITE)]
        for name, value in values.items():
            color = theme.GREEN if name == changed else theme.WHITE
            rows.append(Text(f"{name} = {value}", font=theme.pick_font(str(name)),
                             font_size=self.size, color=color))
        block = VGroup(*rows).arrange(DOWN, aligned_edge=LEFT, buff=0.13)

        # 左侧竖线 + static 标签，和上面那栏"当前调用的局部变量"分开
        rule = Line(block.get_top() + LEFT * 0.16,
                    block.get_bottom() + LEFT * 0.16)
        rule.set_stroke(theme.BLUE, width=1.6)
        return VGroup(rule, block).move_to(self.pos)

    def set(self, values, changed=None, run_time=0.26):
        """``set({"count": 3}, changed="count")``

        ``values`` 必须给全量（这一栏是整体重画的），``changed`` 是这次
        被改动的那一项名字，会用绿色标出来。
        """
        new = self._render(dict(values), changed)
        if self.mob is None:
            self.mob = new
            self.scene.play(FadeIn(self.mob, shift=UP * 0.06), run_time=run_time)
            return
        old = self.mob
        self.mob = new
        self.scene.play(FadeOut(old, run_time=run_time * 0.6),
                        FadeIn(new, run_time=run_time * 0.6))
        self.scene.remove(old)

    def clear(self, run_time=0.26):
        if self.mob is not None:
            self.scene.play(FadeOut(self.mob), run_time=run_time)
            self.mob = None


class HintLine:
    """底部最多一行的简短提示。"""

    def __init__(self, scene, *, center=(1.99, -3.52), size=None):
        self.scene = scene
        self.pos = np.array([center[0], center[1], 0.0])
        self.size = size or theme.SIZE_HINT
        self.mob = None

    def set(self, text, run_time=0.30):
        new = Text(text, font=theme.chinese_font(),
                   font_size=self.size, color=theme.WHITE)
        new.move_to(self.pos)
        if self.mob is None:
            self.mob = new
            self.scene.play(FadeIn(self.mob, shift=UP * 0.07), run_time=run_time)
            return
        # 同 StatusLine：整块换掉，避免 Transform 的点集插值留下残影
        old = self.mob
        self.mob = new
        self.scene.play(FadeOut(old, run_time=run_time * 0.6),
                        FadeIn(new, run_time=run_time * 0.6))
        self.scene.remove(old)

    def clear(self, run_time=0.30):
        if self.mob is not None:
            self.scene.play(FadeOut(self.mob), run_time=run_time)
            self.mob = None


def curtain(scene, opacity=0.96, run_time=0.40):
    """压暗已有画面，让结论独占视觉（PRD 2.4：同屏保留一个主要关注点）。"""
    rect = Rectangle(width=FRAME_WIDTH, height=FRAME_HEIGHT)
    rect.set_fill(theme.BG, opacity=opacity)
    rect.set_stroke(width=0)
    scene.play(FadeIn(rect), run_time=run_time)
    return rect


def complexity_row(name, base, exp, color):
    """一行复杂度，例如 ``时间上界  O(2ⁿ)``、``栈空间  O(n)``。

    指数用独立的小字号文本手工上移，因此不依赖 LaTeX，
    也不使用可能缺字的上标字符（PRD 2.3）。
    """
    label = Text(name, font=theme.chinese_font(),
                 font_size=theme.SIZE_HEADING, color=theme.WHITE)
    open_p = Text("O(", font=theme.mono_font(),
                  font_size=theme.SIZE_HEADING, color=color)
    if base:
        main = Text(base, font=theme.mono_font(),
                    font_size=theme.SIZE_HEADING, color=color)
        sup = Text(exp, font=theme.mono_font(),
                   font_size=int(theme.SIZE_HEADING * 0.67), color=color)
        sup.next_to(main, RIGHT, buff=0.015).shift(UP * 0.18)
        core = VGroup(main, sup)
    else:
        core = Text(exp, font=theme.mono_font(),
                    font_size=theme.SIZE_HEADING, color=color)
    close = Text(")", font=theme.mono_font(),
                 font_size=theme.SIZE_HEADING, color=color)
    formula = VGroup(open_p, core, close).arrange(RIGHT, buff=0.03)
    return VGroup(label, formula).arrange(RIGHT, buff=0.30)
