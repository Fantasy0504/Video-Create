"""画面分区：把图形区切成几块，给不同结构各占一块。

PRD 2.4 要求"根据结构安排布局"。数组递归（归并排序、快排）得**同时**
显示数组和调用树，两种结构不能叠在一起 —— 那就先分区域，再让每个
结构在自己的区域里自适应尺寸。

坐标是 manim 的画面单位：帧宽 14.22、帧高 8，原点在正中。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Region:
    """一个矩形区域，(x0, y0) 是左下角，(x1, y1) 是右上角。"""

    x0: float
    x1: float
    y0: float
    y1: float

    @property
    def width(self) -> float:
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        return self.y1 - self.y0

    @property
    def center(self) -> tuple[float, float]:
        return ((self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2)

    def inset(self, dx: float = 0.0, dy: float | None = None) -> "Region":
        """往里收一圈，留出安全边距。"""
        dy = dx if dy is None else dy
        return Region(self.x0 + dx, self.x1 - dx, self.y0 + dy, self.y1 - dy)

    def split_top(self, part: float, gap: float = 0.30):
        """从上面切走 ``part`` 比例，返回 ``(上面那块, 下面那块)``。"""
        height = (self.height - gap) * part
        top = Region(self.x0, self.x1, self.y1 - height, self.y1)
        bottom = Region(self.x0, self.x1, self.y0, self.y1 - height - gap)
        return top, bottom

    def split_bottom(self, part: float, gap: float = 0.30):
        """从下面切走 ``part`` 比例。"""
        bottom, top = self.split_top(1.0 - part, gap)
        return top, bottom

    def split_left(self, part: float, gap: float = 0.30):
        """从左面切走 ``part`` 比例，返回 ``(左块, 右块)``。"""
        width = (self.width - gap) * part
        left = Region(self.x0, self.x0 + width, self.y0, self.y1)
        right = Region(self.x0 + width + gap, self.x1, self.y0, self.y1)
        return left, right
