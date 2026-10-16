"""固定位置的文字组件：标题、代码面板、状态行、底部提示、结论页。

对应 PRD 2.3（文字与代码）与 10.1（画面布局）：
* 代码保留真实语法与缩进，非执行代码白色，当前语句文字和侧边光标蓝色；
  不给每一行加彩色底板，也不随递归进入而缩放
* 递归模板的代码下方使用 StackPanel 显示当前栈帧；StatusLine 保留兼容
* 底部整幅居中字幕，按实际字宽换行，至多两行

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
from .text_layout import wrap_text
from .stack_state import CallStack


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
        self._focused = set()
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
        # 保留画面左侧安全边距，不能因代码块居中而裁掉行首。
        self.mob.shift(RIGHT * max(0.0, -FRAME_WIDTH / 2 + 0.52 - self.mob.get_left()[0]))

        self.cursors = []
        for line in self.lines:
            cursor = Line(line.get_left() + LEFT * 0.11 + DOWN * 0.115,
                          line.get_left() + LEFT * 0.11 + UP * 0.115)
            cursor.set_stroke(theme.BLUE, width=3.2)
            cursor.set_stroke(opacity=0.0)
            self.cursors.append(cursor)

    @staticmethod
    def _render(source, font_size):
        # Text 的可见包围盒不包含前导空格，直接左对齐会丢缩进。
        # 用透明行框保留统一左边界，再将文字按缩进放入行框。
        texts, indents = [], []
        for raw in source:
            text = raw.expandtabs(4)
            body = text.lstrip(" ")
            font = theme.pick_font(text)
            count = len(text) - len(body)
            cell = Text("M M", font=font, font_size=font_size).get_width() - Text(
                "MM", font=font, font_size=font_size).get_width()
            mob = Text(body or " ", font=font, font_size=font_size, color=theme.WHITE)
            texts.append(mob)
            indents.append(count * cell)
        width = max((m.get_width() + x for m, x in zip(texts, indents)), default=0.1)
        height = max((m.get_height() for m in texts), default=0.2)
        rows = []
        for mob, indent in zip(texts, indents):
            anchor = Rectangle(width=max(width, 0.01), height=max(height, 0.01))
            anchor.set_stroke(opacity=0).set_fill(opacity=0)
            mob.move_to(anchor.get_left() + RIGHT * (indent + mob.get_width() / 2))
            rows.append(VGroup(anchor, mob))
        return rows

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

    def _indices(self, target):
        targets = target if isinstance(target, (tuple, list)) else [target]
        indices = {self._index(t) for t in targets}
        if any(i < 0 or i >= len(self.lines) for i in indices):
            raise IndexError("执行行超出代码范围")
        return indices

    def focus_now(self, target):
        """原位改色，不创建代码副本；支持多行逻辑语句。"""
        indices = self._indices(target)
        for i, (line, cursor) in enumerate(zip(self.lines, self.cursors)):
            line.set_color(theme.BLUE if i in indices else theme.WHITE)
            cursor.set_stroke(opacity=1.0 if i in indices else 0.0)
        self._focused = indices

    def focus(self, scene, target, run_time=0.24):
        indices = self._indices(target)
        changed = self._focused ^ indices
        anims = []
        for i in changed:
            active = i in indices
            anims.extend((self.lines[i].animate.set_color(theme.BLUE if active else theme.WHITE),
                          self.cursors[i].animate.set_stroke(opacity=1.0 if active else 0.0)))
        if anims:
            scene.play(*anims, run_time=run_time)
        self._focused = indices

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


def wrapped_rows(text, size, max_width, color=theme.WHITE):
    def make(value):
        return Text(value or " ", font=theme.pick_font(value),
                    font_size=size, color=color)
    measure = lambda value: make(value).get_width() if value else 0.0
    return [make(line) for line in wrap_text(text, max_width, measure)]


def replace_panel(panel, new, run_time):
    # 顺序淡出/淡入，保证不同文字不会在同一位置交叉叠字。
    if panel.mob is not None:
        old = panel.mob
        panel.scene.play(FadeOut(old), run_time=run_time / 2)
        panel.scene.remove(old)
    panel.mob = new
    panel.scene.play(FadeIn(new), run_time=run_time / 2)


class StackPanel:
    """代码下方的当前栈帧详情；保存每一层自己的参数与局部变量。"""
    def __init__(self, scene, *, left=-6.59, top=-1.10, width=4.10,
                 bottom=-2.65, size=None):
        self.scene, self.left, self.top = scene, left, top
        self.width, self.bottom = width, bottom
        self.size = size or theme.SIZE_NODE
        self.stack = CallStack()
        self.mob = None

    def show_current(self, run_time=0.30):
        frame = self.stack.current
        if frame is None:
            self.clear(run_time)
            return
        fields = [(f"当前调用 第{len(self.stack.frames)}层", theme.BLUE),
                  (f"{frame.name}  #{frame.call_id}", theme.WHITE)]
        fields += [(f"{k} = {v}", theme.WHITE) for k, v in frame.params.items()]
        fields += [(f"{k} = {v}", theme.GREEN if k == frame.changed else theme.WHITE)
                   for k, v in frame.locals.items()]
        if frame.received:
            fields.append((frame.received, theme.GREEN))
        fields.append((frame.state, theme.WHITE))
        rows = []
        for text, color in fields:
            rows.extend(wrapped_rows(text, self.size, self.width, color))
        header, rows = rows[0], rows[1:]
        # 高度不够则按字段分页展示；每页保留当前层级，不缩字，不覆盖字幕带。
        available = self.top - self.bottom - header.get_height() - 0.10
        pages, page, height = [], [], 0.0
        for row in rows:
            h = row.get_height() + (0.10 if page else 0.0)
            if row.get_height() > available:
                raise ValueError("栈帧区域高度不足，请调整布局")
            if page and height + h > available:
                pages.append(page)
                page, height = [], 0.0
                h = row.get_height()
            page.append(row)
            height += h
        if page:
            pages.append(page)
        for index, page in enumerate(pages):
            block = VGroup(header.copy(), *page).arrange(DOWN, aligned_edge=LEFT, buff=0.10)
            block.shift(np.array([self.left, self.top, 0.0]) - block.get_corner(UL))
            replace_panel(self, block, run_time)
            if index + 1 < len(pages):
                self.scene.wait(2.0)

    def push(self, call_id, name, params=None, locals=None, run_time=0.30):
        self.stack.push(call_id, name, params, locals)
        self.show_current(run_time)

    def update(self, *, locals=None, state=None, changed="", run_time=0.30):
        self.stack.update(locals=locals, state=state, changed=changed)
        self.show_current(run_time)

    def pop(self, call_id, value=None, *, receiver=None, has_value=True, run_time=0.30):
        self.stack.pop(call_id, value, receiver=receiver, has_value=has_value)
        self.show_current(run_time)

    def clear(self, run_time=0.30):
        if self.mob is not None:
            self.scene.play(FadeOut(self.mob), run_time=run_time)
            self.scene.remove(self.mob)
            self.mob = None


class HintLine:
    """整幅画面底部居中字幕；字形高度按 1080p 的 46px 校准。"""
    def __init__(self, scene, *, center=(0.0, -3.44), size=None,
                 max_width=13.10):
        self.scene = scene
        self.pos = np.array([center[0], center[1], 0.0])
        self.size = size or theme.SIZE_HINT
        self.max_width = max_width
        self.mob = None

    def set(self, text, run_time=0.30):
        sample = Text("递归调用", font=theme.chinese_font(), font_size=self.size)
        factor = theme.SUBTITLE_HEIGHT / max(sample.get_height(), 1e-6)
        rows = wrapped_rows(text, self.size, self.max_width / factor)
        if len(rows) > 2:
            raise ValueError("字幕超过两行，请按语义拆为多条字幕依次显示")
        # 固定实际字形高度，而不是假定 font_size 等于像素。
        target_h = theme.SUBTITLE_HEIGHT
        for row in rows:
            row.scale(factor)
            if row.get_width() > self.max_width:
                raise ValueError("字幕按目标字高排版后过宽，请拆分句子")
        new = VGroup(*rows).arrange(DOWN, buff=0.10)
        # 底边固定，两行字幕向上扩展。
        bottom = self.pos[1] - target_h / 2
        new.move_to(np.array([self.pos[0], bottom + new.get_height() / 2, 0.0]))
        replace_panel(self, new, run_time)

    def clear(self, run_time=0.30):
        if self.mob is not None:
            self.scene.play(FadeOut(self.mob), run_time=run_time)
            self.scene.remove(self.mob)
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
