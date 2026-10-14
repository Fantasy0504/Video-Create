"""汉诺塔：三根柱子 + 若干圆盘。

对应 PRD 2.4："栈沿入栈方向变化" —— 柱子本质就是栈，盘自下而上叠放。

和 ``tree`` / ``array`` 模块平级，结构由算法决定，不强行套成递归树。
需要别的结构（图、队列、链表）时，照这个模块的样子再写一个即可。
"""
from __future__ import annotations

import numpy as np
from manimlib import *

from . import theme


class HanoiView:
    """三根柱子与若干圆盘，附移动 / 高亮等原语。

    盘用整数编号，**1 是最小的盘**，编号越大盘越宽。
    柱子按列表维护，末尾是柱顶。
    """

    def __init__(self, scene, *, pegs=("A", "B", "C"), disks=3,
                 center_x=2.10, base_y=-1.70, peg_gap=2.60, peg_height=3.10,
                 disk_h=0.40, disk_min=1.05, disk_max=2.30, label_size=None):
        self.scene = scene
        self.peg_names = tuple(pegs)
        self.disk_h = disk_h
        self.base_y = base_y
        self.peg_height = peg_height
        self.disk_min, self.disk_max = disk_min, disk_max

        count = len(self.peg_names)
        span = (count - 1) * peg_gap
        xs = [center_x - span / 2 + i * peg_gap for i in range(count)]
        self.peg_x = xs

        # 初始状态：所有盘都在第一根柱上，大的在下、小的在上
        self.stacks = [list(range(disks, 0, -1))] + [[] for _ in range(count - 1)]

        size = label_size or int(theme.SIZE_NODE * 0.85)
        self.disks = {}
        for d in range(1, disks + 1):
            width = self._disk_width(d, disks)
            body = RoundedRectangle(width=width, height=disk_h * 0.82,
                                    corner_radius=disk_h * 0.24)
            body.set_fill(theme.BG, opacity=1.0)
            body.set_stroke(theme.WHITE, width=1.6)
            tag = Text(str(d), font=theme.mono_font(), font_size=size,
                       color=theme.WHITE)
            tag.move_to(body)
            self.disks[d] = VGroup(body, tag).move_to(
                np.array([xs[0], self._level_y(disks - d), 0.0]))

        self._build_frame()

    # ---------------------------------------------------------------- 几何
    def _disk_width(self, d, total):
        if total == 1:
            return (self.disk_min + self.disk_max) / 2
        t = (d - 1) / (total - 1)
        return self.disk_min + (self.disk_max - self.disk_min) * t

    def _level_y(self, level):
        """第 level 层（0 = 最底下那层）的中心高度。"""
        return self.base_y + self.disk_h / 2 + level * self.disk_h

    def _build_frame(self):
        self.poles, self.labels = [], []
        top = self.base_y + self.peg_height
        for i, x in enumerate(self.peg_x):
            pole = Line(np.array([x, self.base_y, 0.0]),
                        np.array([x, top, 0.0]))
            pole.set_stroke(theme.WHITE, width=2.0)
            self.poles.append(pole)

            label = Text(self.peg_names[i], font=theme.mono_font(),
                         font_size=theme.SIZE_NODE, color=theme.WHITE)
            label.next_to(pole, UP, buff=0.18)
            self.labels.append(label)

        left = self.peg_x[0] - self.disk_max / 2 - 0.35
        right = self.peg_x[-1] + self.disk_max / 2 + 0.35
        self.base = Line(np.array([left, self.base_y, 0.0]),
                         np.array([right, self.base_y, 0.0]))
        self.base.set_stroke(theme.WHITE, width=2.4)

        self.frame = VGroup(self.base, *self.poles, *self.labels)

    @property
    def mob(self):
        return VGroup(self.frame, *self.disks.values())

    # ---------------------------------------------------------------- 出现
    def appear(self, run_time=0.80):
        self.scene.play(
            ShowCreation(self.base),
            LaggedStart(*[ShowCreation(p) for p in self.poles], lag_ratio=0.25),
            LaggedStart(*[FadeIn(l) for l in self.labels], lag_ratio=0.25),
            run_time=run_time * 0.6,
        )
        first = self.stacks[0]
        self.scene.play(
            LaggedStart(*[FadeIn(self.disks[d], shift=UP * 0.12)
                          for d in sorted(first)],
                        lag_ratio=0.22),
            run_time=run_time * 0.5,
        )

    # ---------------------------------------------------------------- 原语
    def top_disk(self, peg):
        return self.stacks[peg][-1] if self.stacks[peg] else None

    def size_of(self, peg):
        return len(self.stacks[peg])

    def highlight(self, peg, color=None, width=3.2, run_time=0.26):
        """把某根柱子描粗变色，用来指出当前操作的对象。"""
        return self.poles[peg].animate.set_stroke(
            color or theme.BLUE, width=width)

    def reset_pole(self, peg, run_time=0.22):
        self.scene.play(self.poles[peg].animate.set_stroke(
            theme.WHITE, width=2.0), run_time=run_time)

    def move_disk(self, src, dst, *, lift=0.55, run_time=0.78, hold=0.22,
                  color=None):
        """把 src 柱顶的盘抬起来、平移到 dst 柱、再放下。

        三段式轨迹（抬起 / 平移 / 落下）比直线更接近真实搬运动作，
        抬升高度取"比两柱所有盘都高"的位置，途中不会穿过别的盘。
        """
        disk = self.stacks[src].pop()
        mob = self.disks[disk]

        # 正在搬运的盘 = 当前处理的对象，按 PRD 2.2 用蓝色；
        # 它原来可能是绿的（上个阶段标过"到位"），这里一并覆盖掉。
        self.paint(disk, theme.BLUE, 2.8)

        top_y = max(self.base_y + self.peg_height,
                    self._level_y(max(self.size_of(src), self.size_of(dst)))) + lift
        start = mob.get_center()
        end = np.array([self.peg_x[dst], self._level_y(self.size_of(dst)), 0.0])
        up = np.array([start[0], top_y, 0.0])
        across = np.array([end[0], top_y, 0.0])

        moving = self.poles[src], self.poles[dst]
        stroke = color or theme.BLUE
        self.scene.play(
            mob.animate.move_to(up),
            self.poles[src].animate.set_stroke(stroke, width=3.2),
            self.poles[dst].animate.set_stroke(stroke, width=3.2),
            run_time=run_time * 0.34,
        )
        self.scene.play(mob.animate.move_to(across), run_time=run_time * 0.34)
        self.scene.play(
            mob.animate.move_to(end),
            run_time=run_time * 0.32,
        )
        self.stacks[dst].append(disk)
        self.paint(disk)                       # 落位后恢复普通色
        self.scene.play(
            self.poles[src].animate.set_stroke(theme.WHITE, width=2.0),
            self.poles[dst].animate.set_stroke(theme.WHITE, width=2.0),
            run_time=0.16,
        )
        self.scene.wait(hold)

    def mark_done(self, peg, run_time=0.30):
        """整根柱子上的盘全部就位时，把柱子转绿。"""
        self.scene.play(self.poles[peg].animate.set_stroke(
            theme.GREEN, width=3.0), run_time=run_time)

    # ------------------------------------------------------------ 配色
    def paint(self, disk, color=None, width=1.8):
        """给单个盘上色（盘体描边与数字一起变），瞬时生效。"""
        body, tag = self.disks[disk]
        body.set_stroke(color or theme.WHITE, width=width)
        tag.set_color(color or theme.WHITE)

    def mark_settled(self, peg, count, color=None, run_time=0.26):
        """把某根柱顶部的 count 个盘标绿：这一摞在这个子问题里已经到位。

        颜色对应 PRD 2.2 —— 绿是"已完成的操作"。盘如果之后还要被搬走，
        ``move_disk`` 会在抬起时把它恢复成白色。
        """
        if count <= 0:
            return
        settled = self.stacks[peg][-count:]
        color = color or theme.GREEN
        self.scene.play(
            *[self.disks[d][0].animate.set_stroke(color, width=2.2)
              for d in settled],
            *[self.disks[d][1].animate.set_color(color) for d in settled],
            run_time=run_time,
        )
