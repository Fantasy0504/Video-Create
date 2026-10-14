#!/usr/bin/env python3
"""环境自检：确认这台机器跑得动 manimgl，缺什么就告诉你怎么补。

用法：
    python tools/check_env.py
"""
from __future__ import annotations

import os
import platform
import shutil
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OK = "[ OK ]"
WARN = "[WARN]"
FAIL = "[FAIL]"


def check_python() -> bool:
    v = sys.version_info
    good = v >= (3, 9)
    print(f"{OK if good else FAIL} Python {v.major}.{v.minor}.{v.micro}")
    print(f"       {sys.executable}")
    if not good:
        print("       manimgl 需要 Python 3.9 或更高")
    return good


def check_manimgl() -> bool:
    try:
        import manimlib
    except ImportError as exc:
        print(f"{FAIL} manimgl 不可用（{exc}）")
        print("       修复：pip install manimgl")
        return False
    version = getattr(manimlib, "__version__", "unknown")
    print(f"{OK} manimgl {version}")
    print(f"       {os.path.dirname(manimlib.__file__)}")
    return True


def check_ffmpeg() -> bool:
    path = shutil.which("ffmpeg")
    if path:
        print(f"{OK} ffmpeg")
        print(f"       {path}")
        return True
    print(f"{FAIL} 在 PATH 里找不到 ffmpeg，manimgl 无法把帧合成 MP4")
    print("       修复：下载 https://ffmpeg.org/download.html 后，"
          "把它的 bin 目录加进 PATH")
    return False


def check_fonts() -> bool:
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)
    try:
        from engine import theme
    except Exception as exc:                      # noqa: BLE001
        print(f"{FAIL} 无法导入 engine 包（{exc}）")
        return False

    good = True
    cn = theme.chinese_font()
    if cn == "sans-serif":
        print(f"{WARN} 没找到可用的中文字体，已回退到通用族名，中文可能缺字")
        print("       装任意一个即可：" + "、".join(theme.CHINESE_CANDIDATES))
        good = False
    else:
        print(f"{OK} 中文字体  {cn}")

    mono = theme.mono_font()
    if mono == "monospace":
        print(f"{WARN} 没找到等宽字体，已回退到通用族名（不影响正确性）")
    else:
        print(f"{OK} 代码字体  {mono}")
    return good


def check_layout() -> bool:
    """顺手看一眼示例文件在不在，避免 clone 下来少了东西。"""
    examples = os.path.join(ROOT, "examples")
    found = []
    if os.path.isdir(examples):
        for name in sorted(os.listdir(examples)):
            scene = os.path.join(examples, name, "scene.py")
            if os.path.isfile(scene):
                found.append(name)
    if found:
        print(f"{OK} 示例场景  {', '.join(found)}")
        return True
    print(f"{WARN} examples/ 下没找到任何 scene.py")
    return True


def main() -> int:
    print(f"平台：{platform.system()} {platform.release()}")
    print(f"项目根：{ROOT}")
    print()

    results = [
        check_python(),
        check_manimgl(),
        check_ffmpeg(),
        check_fonts(),
        check_layout(),
    ]

    print()
    if all(results):
        print("环境就绪。渲染任意示例：")
        print("    python tools/render.py examples/binary_search/scene.py")
        return 0
    print("有检查项没通过，按上面的提示补一下再跑。")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
