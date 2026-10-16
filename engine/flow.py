"""递归调用/返回的统一细箭头，供模板及手写分镜共用。"""
from manimlib import Arrow
from . import theme


def recursion_arrow(start, end, *, returning=False, buff=0):
    """调用指向子调用（蓝），返回指向直接调用者（绿）。

    ManimGL Arrow 是实心图形：箭身用 thickness 控制，不能用 stroke_width。
    1080p 下 thickness=1.2 约为 2.4px；尖端单独放大至约 19px 宽、17px 长。
    保留细箭身，但方向尖端必须在正常播放尺寸下清晰可辨。
    使用 GrowArrow 播放本对象，不用静态换色冒充方向动画。
    """
    return Arrow(
        start, end, buff=buff, thickness=1.2, stroke_width=0,
        tip_width_ratio=8.0, max_tip_length_to_length_ratio=0.32,
        max_width_to_length_ratio=0.04,
    ).set_color(theme.GREEN if returning else theme.BLUE)
