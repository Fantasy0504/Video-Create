"""数组 / 序列结构的定义与展示。

对应 PRD 2.4："数组沿索引展开"。适合排序、查找、双指针一类算法。

和 ``tree`` 模块平级 —— 用哪种画面结构由算法决定，不统一套成递归树。
需要别的结构（图、栈、队列）时照这个模块的样子再加一个即可。
"""
from __future__ import annotations

import numpy as np
from manimlib import *

from . import theme


class ArrayView:
    """一排带索引的格子，附比较 / 交换 / 命中 / 指针等常用原语。"""

    def __init__(self, scene, values, *, center=(2.35, 0.60),
                 cell_w=0.92, cell_h=0.78, gap=0.10, show_index=True,
                 region=None):
        if region is not None:
            center = region.center
            count = max(len(values), 1)
            room = region.width - 0.10
            cell_w = min(cell_w, (room - (count - 1) * gap) / count)
            cell_h = min(cell_h, region.height - 0.10)

        self.scene = scene
        self.values = list(values)
        self.cell_w, self.cell_h, self.gap = cell_w, cell_h, gap
        self.center = np.array([center[0], center[1], 0.0])
        self.cells, self.numbers, self.indices = [], [], []
        self._build(show_index)

    # ---------------------------------------------------------------- 构建
    def _slot(self, i):
        n = len(self.values)
        total = n * self.cell_w + (n - 1) * self.gap
        x = (self.center[0] - total / 2 + self.cell_w / 2
             + i * (self.cell_w + self.gap))
        return np.array([x, self.center[1], 0.0])

    def _build(self, show_index):
        for i, v in enumerate(self.values):
            cell = Rectangle(width=self.cell_w, height=self.cell_h)
            cell.set_fill(theme.BG, opacity=1.0)
            cell.set_stroke(theme.WHITE, width=1.6)
            cell.move_to(self._slot(i))
            number = Text(str(v), font=theme.pick_font(str(v)),
                          font_size=theme.SIZE_NODE, color=theme.WHITE)
            number.move_to(cell)
            self.cells.append(cell)
            self.numbers.append(number)
            if show_index:
                index = Text(str(i), font=theme.mono_font(),
                             font_size=int(theme.SIZE_NODE * 0.75),
                             color=theme.WHITE)
                index.next_to(cell, DOWN, buff=0.09)
                self.indices.append(index)

        self.boxes = VGroup(*self.cells)
        self.numbers_group = VGroup(*self.numbers)

    @property
    def mob(self):
        return VGroup(self.boxes, self.numbers_group, *self.indices)

    def __len__(self):
        return len(self.values)

    # ---------------------------------------------------------------- 出现
    def appear(self, run_time=0.90):
        anims = []
        for i in range(len(self.values)):
            anims.append(FadeIn(self.cells[i], scale=0.85))
            anims.append(FadeIn(self.numbers[i]))
            if self.indices:
                anims.append(FadeIn(self.indices[i]))
        self.scene.play(LaggedStart(*anims, lag_ratio=0.07), run_time=run_time)

    # ---------------------------------------------------------------- 原语
    def _stroke(self, i, color, width):
        return self.cells[i].animate.set_stroke(color, width=width)

    def accent(self, i, color=None, width=2.8):
        """返回一个动画对象，方便和别的一起塞进同一个 ``play()``。"""
        return self._stroke(i, color or theme.BLUE, width)

    def reset(self, *indices, run_time=0.20):
        idxs = list(indices) if indices else range(len(self.values))
        self.scene.play(*[self._stroke(i, theme.WHITE, 1.6) for i in idxs],
                        run_time=run_time)

    def reset_all_now(self):
        for i in range(len(self.values)):
            self.cells[i].set_stroke(theme.WHITE, width=1.6)

    def compare(self, i, j, hold=0.55, run_time=0.32):
        """比较两个位置：一起变蓝。

        允许 i == j（自比较），此时只对同一个格子做一次动画 —— 重复传同一
        个 animate 对象会让 manimlib 报错。
        """
        anims = [self.accent(i)] if i == j else [self.accent(i), self.accent(j)]
        self.scene.play(*anims, run_time=run_time)
        self.scene.wait(hold)

    def swap(self, i, j, run_time=0.55, hold=0.45):
        """交换两个位置的内容（值动画移动，格子不动）。"""
        a, b = self._slot(i), self._slot(j)
        self.scene.play(self.numbers[i].animate.move_to(b),
                        self.numbers[j].animate.move_to(a),
                        run_time=run_time)
        self.numbers[i], self.numbers[j] = self.numbers[j], self.numbers[i]
        self.values[i], self.values[j] = self.values[j], self.values[i]
        self.scene.wait(hold)

    def hit(self, i, hold=1.20, run_time=0.32):
        """命中 / 已确定：转绿。"""
        self.scene.play(self._stroke(i, theme.GREEN, 3.0), run_time=run_time)
        self.scene.wait(hold)

    def cost(self, i, run_time=0.28):
        """红色强调：越界、冲突或需要特别注意的代价（PRD 2.2）。"""
        self.scene.play(self._stroke(i, theme.RED, 3.0), run_time=run_time)

    def dim_except(self, keep=(), opacity=0.25, run_time=0.45):
        keep = set(keep)
        others = [i for i in range(len(self.values)) if i not in keep]
        if not others:
            return
        group = VGroup(*[self.cells[i] for i in others],
                       *[self.numbers[i] for i in others])
        self.scene.play(group.animate.set_opacity(opacity), run_time=run_time)

    def pointer(self, i, text, color=None, buff=0.46, run_time=0.30):
        """在格子下方放一个箭头 + 名字，例如 low / high / mid。"""
        color = color or theme.BLUE
        label = Text(text, font=theme.pick_font(text),
                     font_size=theme.SIZE_VALUE, color=color)
        label.next_to(self.cells[i], DOWN, buff=buff)
        arrow = Arrow(label.get_top(), self.cells[i].get_bottom(),
                      buff=0.02, stroke_width=3)
        arrow.set_color(color)
        mob = VGroup(arrow, label)
        self.scene.play(GrowArrow(arrow), FadeIn(label, shift=UP * 0.06),
                        run_time=run_time)
        return mob
