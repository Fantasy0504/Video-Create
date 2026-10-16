"""算法动画场景基类。

把 PRD 第一部分的通用规范固化下来，子类只需要实现 ``build()``：
* 2.1  背景统一纯黑
* 2.2  前景只用白 / 蓝 / 红 / 绿四种主题色
* 3    节奏规范（见下面的 BEAT 取值）
* 10.1 标题 / 代码 / 状态 / 提示的固定位置：左侧约 38% 放代码，
       右侧约 62% 放图形

节奏取值是分镜的起点，不是要求每种动作都重复累加等待。
"""
from __future__ import annotations

from manimlib import *

from . import theme
from .array import ArrayView
from .layout import Region
from .linkedlist import LinkedListView
from .panel import (CodePanel, HintLine, StaticPanel, StackPanel, StatusLine, TitleBar)
from .tree import TreeSpec, TreeView


class Beat:
    """一个动作的时长与随后的阅读停留，单位秒。"""

    __slots__ = ("run_time", "hold")

    def __init__(self, run_time: float, hold: float):
        self.run_time = run_time
        self.hold = hold

    def __repr__(self):
        return f"Beat(run_time={self.run_time}, hold={self.hold})"


class AlgoScene(Scene):
    # ------------------------------------------------- PRD 第 3 节的节奏规范
    NORMAL = Beat(0.55, 1.80)        # 普通步骤，动作后留出阅读时间
    FIRST = Beat(1.00, 2.30)         # 首次出现的关键规则、边界或返回
    REPEAT = Beat(0.45, 1.60)        # 重复步骤仍可追踪，不快速闪过
    LOCAL_RESULT = Beat(0.65, 2.30)  # 一个完整的局部结果
    CONCLUSION = Beat(0.70, 3.00)    # 最终结论
    TRANSIT = Beat(1.00, 0.00)       # 大场景转场

    # ------------------------------------------------------------ 画面布局
    # 帧为 14.22 × 8 单位，安全边距约 0.45（PRD 2.4）。
    TITLE_TEXT = "算法演示"
    TITLE_TAG = None                 # 例如 "fib(5)"，蓝色输入标记
    CODE_CENTER = (-5.00, 1.30)      # 左侧 38%，代码块中心
    CODE_SOURCE = ()                 # C++ 代码行，逐行原样显示
    STATUS_CENTER = (-5.00, -0.95)   # 代码下方：当前调用参数与局部求和值
    HINT_CENTER = (0.0, -3.44)      # 底部一行提示
    # PRD 10.1：左侧约 38% 放代码，右侧约 62% 放图形。
    # 图形区底部为最多两行字幕预留空间，节点边框不能伸入字幕带。
    # 需要同时显示两种结构时（数组 + 调用树），用 FigureRegions.split_* 切开。
    FIGURE_REGION = Region(-2.48, 6.46, -2.35, 3.02)

    # 旧写法保留：不传 region 时用这组参数
    TREE_BOX = dict(top_y=3.02, row_gap=1.24, left=-2.48, right=6.46,
                    bottom_y=-2.35)

    # ---------------------------------------------------------------- 入口
    def construct(self):
        self.set_background_color(theme.BG)   # PRD 2.1：整幅画面纯黑
        self.setup()
        self.build()

    # ------------------------------------------------------------ 可覆写钩子
    def setup(self):
        """准备数据结构等，在 build() 之前调用。"""

    def build(self):
        raise NotImplementedError("子类必须实现 build()")

    # ---------------------------------------------------------------- 组件
    def add_title(self, text=None, tag=None, run_time=0.40):
        """左上角标题 + 可选的蓝色输入标记。"""
        self.title = TitleBar(text or self.TITLE_TEXT, tag or self.TITLE_TAG)
        self.title.show(self, run_time=run_time)
        return self.title

    def add_code(self, source=None, *, show=True, run_time=0.90, **kw):
        """固定位置的代码面板。用 ``panel.bind(...)`` 给行起名字。"""
        self.code = CodePanel(source or self.CODE_SOURCE,
                              center=self.CODE_CENTER, **kw)
        if show:
            self.code.show(self, run_time=run_time)
        return self.code

    def add_status(self):
        """左侧代码区下方的状态行。"""
        self.status = StatusLine(self, center=self.STATUS_CENTER)
        return self.status

    def add_stack(self, **kw):
        """当前调用栈顶详情，按代码实际底边放在下方。"""
        if hasattr(self, "code"):
            kw.setdefault("left", max(-6.59, float(self.code.mob.get_left()[0])))
            kw.setdefault("top", min(-1.10, float(self.code.mob.get_bottom()[1]) - 0.35))
        self.stack_panel = StackPanel(self, **kw)
        return self.stack_panel

    def add_hint(self):
        """底部提示行。"""
        self.hint = HintLine(self, center=self.HINT_CENTER)
        return self.hint

    def add_tree(self, spec, **kw):
        """按 TreeSpec 构建调用树。不传 region 时用 PRD 10.1 的默认布局。"""
        if "region" not in kw and "top_y" not in kw:
            opts = dict(self.TREE_BOX)
            opts.update(kw)
            self.tree = TreeView(self, spec, **opts)
        else:
            self.tree = TreeView(self, spec, **kw)
        return self.tree

    def add_array(self, values, **kw):
        """数组结构。要和调用树共存时传 ``region=`` 指定各自占哪一块。"""
        self.array = ArrayView(self, values, **kw)
        return self.array

    def add_linked_list(self, values, **kw):
        """链表结构（节点 + next 箭头 + 指针）。"""
        self.list = LinkedListView(self, values, **kw)
        return self.list

    def add_static(self, **kw):
        """跨调用共享的变量栏（C 的 static）。"""
        self.static = StaticPanel(self, **kw)
        return self.static

    # ------------------------------------------------------------ 节奏助手
    def beat(self, kind: Beat, scale: float = 1.0):
        """播放后自动停留，返回 ``(run_time, hold)`` 供分镜取用。

        ``scale`` 小于 1 时用于"已讲清的重复步骤"整体加速。
        """
        return kind.run_time * scale, kind.hold * scale
