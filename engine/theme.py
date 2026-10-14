"""视觉常量与跨平台字体选择。

取值全部来自 PRD 第一部分：
* 2.1 背景统一为纯黑 `#000000`，整幅画面一致
* 2.2 前景只使用白 / 蓝 / 红 / 绿四种主题色，不使用黄、橙、紫
* 2.3 1080p 成片的目标视觉字高：标题 48~60px，代码 30~36px，
      主要节点与说明 28~34px

本模块只依赖 manimpango（manimgl 自带），不引入其它第三方依赖。
"""
from __future__ import annotations

# ------------------------------------------------------------------ 颜色
BG = "#000000"      # 背景。不使用深蓝底、渐变、纹理、光晕、阴影
WHITE = "#FFFFFF"   # 普通文字、非活动代码、节点标签、常规连接线
BLUE = "#58C4DD"    # 当前执行位置、当前处理的对象、正在进入的路径
RED = "#FC6255"     # 重复计算、冲突或需要特别注意的代价
GREEN = "#83C167"   # 已确定的值、已完成的操作、正确结果、返回的数据

# -------------------------------------------------------------- 目标字高
# manimlib 的 font_size 与成片像素约为 1 : 1.35 倍（1080p、帧高 8 单位）。
SIZE_TITLE = 40     # 约 54px
SIZE_HEADING = 30   # 约 40px
SIZE_CODE = 23      # 约 31px
SIZE_NODE = 21      # 约 28px
SIZE_VALUE = 19     # 约 26px
SIZE_HINT = 22      # 约 30px
SIZE_RESULT = 52    # 约 70px

# ------------------------------------------------------------------ 字体
# 按优先级排列，取第一个系统里装了的。让别人 clone 下来就能跑，
# 不用先装思源黑体或 Consolas。
CHINESE_CANDIDATES = (
    "Source Han Sans CN", "Source Han Sans SC", "思源黑体",
    "Noto Sans CJK SC", "Noto Sans SC",
    "PingFang SC", "Microsoft YaHei", "SimHei",
)
MONO_CANDIDATES = (
    "Consolas", "Menlo", "JetBrains Mono",
    "DejaVu Sans Mono", "Cascadia Mono", "Courier New",
)

_cache: dict = {}


def _installed() -> dict:
    """{小写字体名: 真实字体名}，取自 manimpango 的字体索引。"""
    try:
        from manimpango import list_fonts
    except ImportError:
        return {}
    return {name.lower(): name for name in list_fonts()}


def _pick(candidates, fallback: str) -> str:
    key = tuple(candidates)
    if key in _cache:
        return _cache[key]

    installed = _installed()
    chosen = fallback

    # 先精确匹配
    for want in candidates:
        real = installed.get(want.lower())
        if real:
            chosen = real
            break
    else:
        # 再子串匹配，兼容 "Consolas Bold" 这类带字重后缀的注册名
        for want in candidates:
            want_l = want.lower()
            hit = next((real for low, real in installed.items() if want_l in low), None)
            if hit:
                chosen = hit
                break

    _cache[key] = chosen
    return chosen


def chinese_font() -> str:
    """清晰的无衬线中文字体；系统里一个都没有时回退到通用族名。"""
    return _pick(CHINESE_CANDIDATES, "sans-serif")


def mono_font() -> str:
    """等宽代码字体。"""
    return _pick(MONO_CANDIDATES, "monospace")


def describe_fonts() -> str:
    """给环境自检用的可读报告。"""
    return f"中文 = {chinese_font()}    代码 = {mono_font()}"


def pick_font(text: str) -> str:
    """按内容挑字体：含中文就用中文字体。

    等宽字体（Consolas 等）通常没有中文字形，中英混排时会缺字 ——
    "第 5 步  B → A" 里只有数字和字母能显示出来。凡是显示用户给的字符串
    的地方，都应该走这个函数，而不是直接写死 mono_font()。
    """
    for ch in text:
        if "\u4e00" <= ch <= "\u9fff" or "\u3000" <= ch <= "\u303f":
            return chinese_font()
    return mono_font()
