"""算法动画引擎。

把 PRD 第一部分的通用规范（纯黑背景、白蓝红绿四色、节奏、布局）固化成
可复用组件。写一个新算法的动画时，只需要：

1. 用 ``TreeSpec`` 声明这次执行的结构
2. 继承 ``AlgoScene``，在 ``build()`` 里按分镜调用组件的方法

示例见 ``scenes/fibonacci_naive.py``。
"""
from . import theme
from .array import ArrayView
from .flow import recursion_arrow
from .hanoi import HanoiView
from .layout import Region
from .linkedlist import LinkedListView
from .panel import (CodePanel, HintLine, StaticPanel, StackPanel, StatusLine, TitleBar,
                    complexity_row, curtain)
from .scene import AlgoScene, Beat
from .recursion import RecursionScene
from .tree import TreeSpec, TreeView

__all__ = [
    "theme",
    "recursion_arrow",
    "AlgoScene",
    "RecursionScene",
    "Beat",
    "Region",
    "TreeSpec",
    "TreeView",
    "ArrayView",
    "HanoiView",
    "LinkedListView",
    "CodePanel",
    "StatusLine",
    "StackPanel",
    "StaticPanel",
    "HintLine",
    "TitleBar",
    "complexity_row",
    "curtain",
]
