"""链表的可视化：节点方框 + next 箭头 + 指针。

和 ``tree`` / ``array`` / ``hanoi`` 平级。链表递归（打印、反转、求长度）
除了调用过程，观众还需要看到**链表本身**：当前走到哪个节点、
``next`` 指向谁、指针怎么挪。

反转这类操作要改 ``next`` 的指向，所以箭头是**可反转**的
（见 ``reverse_link``），不是画上去就不动了。
"""
from __future__ import annotations

import numpy as np
from manimlib import *

from . import theme


def _safe(text):
    """标签里出现 ASCII 之外、等宽字体又覆盖不到的字符很容易缺字。"""
    return theme.pick_font(str(text))


class LinkedListView:
    """一排链表节点，节点之间用箭头表示 next 指向。"""

    def __init__(self, scene, values, *, region=None,
                 center=(2.35, 0.60), node_w=1.10, node_h=0.68,
                 gap=0.66, show_index=True):
        if region is not None:
            center = region.center
            count = max(len(values), 1)
            room = region.width - 0.20
            step = (room - (count - 1) * 0.0) / count if count else 0
            node_w = min(node_w, max(0.55, step - gap))
            node_h = min(node_h, region.height - 0.10)

        self.scene = scene
        self.values = list(values)
        self.count = len(self.values)
        self.node_w, self.node_h, self.gap = node_w, node_h, gap

        total = self.count * node_w + max(self.count - 1, 0) * gap
        x0 = center[0] - total / 2 + node_w / 2
        self.slots = [np.array([x0 + i * (node_w + gap), center[1], 0.0])
                      for i in range(self.count)]

        self.boxes, self.labels, self.indices = [], [], []
        for i, value in enumerate(self.values):
            box = RoundedRectangle(width=node_w, height=node_h,
                                   corner_radius=0.08)
            box.set_fill(theme.BG, opacity=1.0)
            box.set_stroke(theme.WHITE, width=1.7)
            box.move_to(self.slots[i])
            label = Text(str(value), font=_safe(value),
                         font_size=theme.SIZE_NODE, color=theme.WHITE)
            label.move_to(box)
            self.boxes.append(box)
            self.labels.append(label)
            if show_index:
                index = Text(str(i), font=theme.mono_font(),
                             font_size=int(theme.SIZE_NODE * 0.7),
                             color=theme.WHITE)
                index.next_to(box, DOWN, buff=0.10)
                self.indices.append(index)

        # next 箭头：i → i+1，最后一个指向一个空档
        self.arrows = []
        for i in range(self.count - 1):
            self.arrows.append(self._make_arrow(i, i + 1))

    # ---------------------------------------------------------------- 几何
    def _make_arrow(self, src, dst, color=None, width=2.6):
        """从 src 节点指向 dst 节点的箭头。

        src 可能在 dst 左边（正向 next），也可能在右边（反转后 next 指回去）。
        出发边和到达边必须按方向选 —— 写死"从左往右"的话，反转箭头会
        从右边节点的右边缘射到左边节点的左边缘，横跨两个节点、方向错乱。
        """
        if dst >= self.count:
            # 链尾指向空：只在正向（src 在最右）时有意义
            start = self.slots[src] + RIGHT * (self.node_w / 2)
            end = start + RIGHT * self.gap
        elif src < dst:
            start = self.slots[src] + RIGHT * (self.node_w / 2)
            end = self.slots[dst] - RIGHT * (self.node_w / 2)
        else:
            start = self.slots[src] - RIGHT * (self.node_w / 2)
            end = self.slots[dst] + RIGHT * (self.node_w / 2)
        arrow = Arrow(start, end, buff=0.0, stroke_width=width,
                      max_tip_length_to_length_ratio=0.28)
        arrow.set_color(color or theme.WHITE)
        return arrow

    @property
    def mob(self):
        return VGroup(*self.boxes, *self.labels, *self.arrows, *self.indices)

    # ---------------------------------------------------------------- 出现
    def appear(self, run_time=0.80):
        anims = []
        for i in range(self.count):
            anims.append(FadeIn(self.boxes[i], scale=0.88))
            anims.append(FadeIn(self.labels[i]))
            if self.indices:
                anims.append(FadeIn(self.indices[i]))
            if i < len(self.arrows):
                anims.append(GrowArrow(self.arrows[i]))
        self.scene.play(LaggedStart(*anims, lag_ratio=0.06), run_time=run_time)

    # ---------------------------------------------------------------- 原语
    def stroke(self, index, color=None, width=2.6):
        return self.boxes[index].animate.set_stroke(
            color or theme.BLUE, width=width)

    def highlight(self, index, color=None, width=3.0, run_time=0.26):
        self.scene.play(self.stroke(index, color, width), run_time=run_time)

    def reset(self, *indices, run_time=0.20):
        idxs = list(indices) if indices else range(self.count)
        self.scene.play(*[self.stroke(i, theme.WHITE, 1.7) for i in idxs],
                        run_time=run_time)

    def reset_all_now(self):
        for box in self.boxes:
            box.set_stroke(theme.WHITE, width=1.7)

    def mark(self, index, color=None, width=2.4, run_time=0.24):
        """给节点上色（绿=已处理完，红=代价，按 PRD 2.2）。"""
        self.scene.play(self.stroke(index, color or theme.GREEN, width),
                        run_time=run_time)

    def dim_from(self, index, opacity=0.25, run_time=0.40):
        """把 index 之后的节点压暗，用来表示"还没走到"。"""
        tail = [i for i in range(index, self.count)]
        if not tail:
            return
        group = VGroup(*[self.boxes[i] for i in tail],
                       *[self.labels[i] for i in tail],
                       *[self.arrows[i] for i in tail if i < len(self.arrows)])
        self.scene.play(group.animate.set_opacity(opacity), run_time=run_time)

    # ------------------------------------------------------- 反转 next 指向
    def reverse_link(self, index, color=None, run_time=0.42):
        """把 ``index → index+1`` 的箭头翻成 ``index+1 → index``。

        链表反转的核心动作。箭头不是画上去就不动的，所以这里替换成新箭头
        再做 Transform，而不是去改已有箭头的参数。
        """
        if index >= len(self.arrows):
            return
        old = self.arrows[index]
        new = self._make_arrow(index + 1, index, color=color or theme.GREEN, width=3.0)
        self.arrows[index] = new
        self.scene.play(Transform(old, new), run_time=run_time)

    def restore_link(self, index, run_time=0.30):
        """把箭头恢复成正常方向（撤销一次反转）。"""
        if index >= len(self.arrows):
            return
        old = self.arrows[index]
        new = self._make_arrow(index, index + 1)
        self.arrows[index] = new
        self.scene.play(Transform(old, new), run_time=run_time)

    # ---------------------------------------------------------------- 指针
    def pointer(self, index, text, color=None, buff=0.44, run_time=0.28):
        """在节点下方加一个箭头 + 名字，例如 head / cur / prev。"""
        color = color or theme.BLUE
        label = Text(text, font=theme.pick_font(text),
                     font_size=theme.SIZE_VALUE, color=color)
        base = self.boxes[index]
        if self.indices:
            label.next_to(self.indices[index], DOWN, buff=0.12)
        else:
            label.next_to(base, DOWN, buff=buff)
        arrow = Arrow(label.get_top(), base.get_bottom(),
                      buff=0.02, stroke_width=3)
        arrow.set_color(color)
        mob = VGroup(arrow, label)
        self.scene.play(GrowArrow(arrow), FadeIn(label, shift=UP * 0.06),
                        run_time=run_time)
        return mob
