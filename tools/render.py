#!/usr/bin/env python3
"""一键渲染：调用 manimgl，并把成片按项目约定放到 out/。

用法：
    python tools/render.py examples/binary_search/scene.py
    python tools/render.py examples/fibonacci_recursion/scene.py --scene FibonacciNaive
    python tools/render.py examples/binary_search/scene.py -- --low_quality

默认行为：
* 场景类名省略时，自动取文件里第一个 Scene 子类
* 成片复制到 ``out/<示例目录名>.mp4``，manimgl 原始输出仍在 ``videos/``
* ``--`` 之后的参数原样透传给 manimgl（例如 ``-s`` 只渲染末帧、``-l`` 低画质）
"""
from __future__ import annotations

import argparse
import ast
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def find_scene_classes(path: Path) -> list[str]:
    """列出文件里所有继承自 *Scene 的类名，多级继承也算。"""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    bases_of: dict[str, list[str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        bases_of[node.name] = [
            name for name in (
                getattr(b, "id", None) or getattr(b, "attr", None)
                for b in node.bases
            ) if name
        ]

    def is_scene(name: str, seen: frozenset = frozenset()) -> bool:
        if name in seen:
            return False
        if name.endswith("Scene"):          # AlgoScene，或 manimlib 的 Scene
            return True
        return any(is_scene(b, seen | {name}) for b in bases_of.get(name, []))

    return [name for name in bases_of if is_scene(name)]


def find_manimgl() -> str | None:
    found = shutil.which("manimgl")
    if found:
        return found
    # 没在 PATH 里时，看当前解释器旁边的 Scripts（venv 的常见形态）
    suffix = ".exe" if os.name == "nt" else ""
    candidate = Path(sys.executable).parent / f"manimgl{suffix}"
    return str(candidate) if candidate.exists() else None


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="渲染一个算法动画场景")
    parser.add_argument("scene_file", help="场景文件，例如 examples/binary_search/scene.py")
    parser.add_argument("--scene", help="场景类名；省略时取文件里第一个")
    parser.add_argument("--out-dir", default="out", help="成片输出目录（默认 out/）")
    parser.add_argument("--name", help="成片文件名；默认用示例目录名")
    parser.add_argument("extra", nargs="*", help="透传给 manimgl 的额外参数")
    args = parser.parse_args(argv)

    scene_path = Path(args.scene_file)
    if not scene_path.is_absolute():
        scene_path = (Path.cwd() / scene_path).resolve()
    if not scene_path.exists():
        print(f"找不到场景文件：{scene_path}")
        return 2

    classes = find_scene_classes(scene_path)
    if not classes:
        print(f"{scene_path.name} 里没有找到继承自 Scene 的类")
        return 2

    scene_name = args.scene or classes[0]
    if scene_name not in classes:
        print(f"没有名为 {scene_name} 的场景。可选：{', '.join(classes)}")
        return 2

    manimgl = find_manimgl()
    if not manimgl:
        print("找不到 manimgl。先跑 python tools/check_env.py 看缺什么")
        return 1

    cmd = [manimgl, str(scene_path), scene_name, "-w", *args.extra]
    print("渲染中：" + " ".join(cmd))
    print()
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        print(f"\nmanimgl 退出码 {result.returncode}")
        return result.returncode

    produced = ROOT / "videos" / f"{scene_name}.mp4"
    if not produced.exists():
        print(f"\n渲染结束但没有找到 {produced}")
        return 1

    out_dir = ROOT / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{args.name or scene_path.parent.name}.mp4"
    shutil.copy2(produced, target)

    print(f"\n成片：{target}")
    print(f"原始：{produced}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
