#!/usr/bin/env python3
"""引擎自检：不渲染，只检查数据层能不能吃下各类递归形态。

递归动画的调用树形状差别很大，这里把常见的几种都造一遍：

* **二叉**     fib / 归并排序 —— 每个调用两个孩子
* **单支**     链表递归 length(head) —— 每个调用只有一个孩子，
                整条链应当落在同一条竖线上
* **偏斜**     BST 遍历 —— 有的分支深、有的浅
* **多叉**     回溯类 —— 一个调用有若干个孩子
* **不平衡**   数组分治，左右子区间长度不同

跑法：
    python tools/selftest.py
"""
from __future__ import annotations

import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)

from engine.tree import TreeSpec          # noqa: E402

FAILED = []


def check(name, cond, detail=""):
    mark = " OK " if cond else "FAIL"
    print(f"[{mark}] {name}" + (f"  {detail}" if detail else ""))
    if not cond:
        FAILED.append(name)


def layout(spec, box=(2.28, 1.24, -2.48, 6.46)):
    """跑一次布局，顺便检查有没有节点压在一起。"""
    pos = spec.positions(*box)
    xs = [round(float(p[0]), 4) for p in pos.values()]
    ys = [round(float(p[1]), 4) for p in pos.values()]
    points = list(zip(xs, ys))
    return pos, len(set(points)) == len(points)


# --------------------------------------------------------------- 各种形态
def spec_binary():
    """完全二叉：fib(3)"""
    nodes = [
        (1, "f(3)", 0, None),
        (2, "f(2)", 1, 1),
        (3, "f(1)", 1, 1),
        (4, "f(1)", 2, 2),
        (5, "f(0)", 2, 2),
    ]
    children = {1: [2, 3], 2: [4, 5]}
    return TreeSpec(nodes, children, [3, 4, 5])


def spec_chain():
    """单支：链表递归 length(head)，一条链只有 1 个孩子"""
    n = 6
    nodes = [(i + 1, f"len({n - i})", i, None if i == 0 else i)
             for i in range(n + 1)]
    children = {i: [i + 1] for i in range(1, n + 1)}
    return TreeSpec(nodes, children, [n + 1])


def spec_skewed():
    """偏斜：BST 一路往左，中途挂一个右子"""
    nodes = [
        (1, "root", 0, None),
        (2, "L", 1, 1),
        (3, "R", 1, 1),
        (4, "LL", 2, 2),
        (5, "LR", 2, 2),
        (6, "LLL", 3, 4),
    ]
    children = {1: [2, 3], 2: [4, 5], 4: [6]}
    return TreeSpec(nodes, children, [6, 5, 3])


def spec_multiway():
    """多叉：一个调用有三个孩子"""
    nodes = [
        (1, "root", 0, None),
        (2, "a", 1, 1),
        (3, "b", 1, 1),
        (4, "c", 1, 1),
        (5, "a1", 2, 2),
    ]
    children = {1: [2, 3, 4], 2: [5]}
    return TreeSpec(nodes, children, [5, 3, 4])


def spec_uneven():
    """不平衡：归并排序 [0,7) 左右子区间不等长"""
    nodes = [
        (1, "[0,8)", 0, None),
        (2, "[0,4)", 1, 1),
        (3, "[4,8)", 1, 1),
        (4, "[0,2)", 2, 2),
        (5, "[2,4)", 2, 2),
        (6, "[4,6)", 2, 3),
        (7, "[6,7)", 3, 6),
        (8, "[7,8)", 3, 6),
    ]
    children = {1: [2, 3], 2: [4, 5], 3: [6], 6: [7, 8]}
    return TreeSpec(nodes, children, [4, 5, 7, 8])


SHAPES = [
    ("二叉（fib）", spec_binary),
    ("单支（链表）", spec_chain),
    ("偏斜（BST）", spec_skewed),
    ("多叉（回溯）", spec_multiway),
    ("不平衡（归并）", spec_uneven),
]


def main() -> int:
    print("=== 调用树布局 ===")
    for name, make in SHAPES:
        try:
            spec = make()
            pos, distinct = layout(spec)
            check(f"{name} 布局", distinct, "节点无重叠" if distinct else "有节点重叠！")
        except Exception as exc:                      # noqa: BLE001
            check(f"{name} 布局", False, f"{type(exc).__name__}: {exc}")

    print()
    print("=== 单支链应当落在同一条竖线上 ===")
    spec = spec_chain()
    pos = spec.positions(2.28, 1.24, -2.48, 6.46)
    xs = {round(float(p[0]), 4) for p in pos.values()}
    check("链表递归竖直排列", len(xs) == 1, f"x 取值 {sorted(xs)}")

    print()
    print("=== 父节点在子节点中间 ===")
    spec = spec_binary()
    pos = spec.positions(2.28, 1.24, -2.48, 6.46)
    root_x = float(pos[1][0])
    kid_x = [float(pos[2][0]), float(pos[3][0])]
    mid = sum(kid_x) / 2
    check("根节点居中于子节点", abs(root_x - mid) < 1e-9,
          f"根 {root_x:.3f} vs 中点 {mid:.3f}")

    print()
    if FAILED:
        print(f"有 {len(FAILED)} 项没通过：" + "、".join(FAILED))
        return 1
    print("全部通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
