"""树形结构的定义与展示。

对应 PRD 第 9 节（真实执行过程与画面规则）与第 10 节（画面布局）。
只解决"结构由算法决定"这一层：节点位置提前规划，首次出现后保持稳定，
不需要树的算法（数组、图、栈）可以完全不用这个模块。

**颜色怎么用**（PRD 2.2 的语义落到递归上）：

===========  ==========================================
蓝 #58C4DD   当前递归栈 —— 从根到正在执行的那个节点
             的整条链，节点与连接边一起染蓝
绿 #83C167   已经算完并回溯上来的调用，边同样是绿的
白 #FFFFFF   还没访问到的节点与边
红 #FC6255   重复计算等代价，只在回顾阶段出现
===========  ==========================================

"往下钻"表现为蓝色链条变长，"往回退"表现为链条逐个转绿 ——
递归与回溯因此一眼可辨，而不是每个节点闪一下蓝色就变回白色。
"""
from __future__ import annotations

import numpy as np
from manimlib import *

from . import theme


def border_point(center, toward, node_w, node_h, gap=0.025):
    """从矩形中心朝 toward 方向，求它与矩形边框的交点，再沿法向外移 gap。

    连斜线时不能按"直线距离截断"来画：那样只有垂直连线正好落在边上，
    斜线会扎进矩形内部或者根本接不到边。必须按矩形边框求交点。
    """
    delta = np.array([toward[0] - center[0], toward[1] - center[1], 0.0])
    length = float(np.linalg.norm(delta))
    if length < 1e-9:
        return np.array(center, dtype=float)

    half_w, half_h = node_w / 2.0, node_h / 2.0
    tx = half_w / abs(delta[0]) if abs(delta[0]) > 1e-9 else float("inf")
    ty = half_h / abs(delta[1]) if abs(delta[1]) > 1e-9 else float("inf")
    point = np.array(center, dtype=float) + delta * min(tx, ty)
    return point + delta / length * gap


class TreeSpec:
    """一次执行的树形结构。

    nodes       ``[(id, label, depth, parent), ...]``，id 即真实的进入顺序，
                同参数的不同调用必须有不同 id，不得合并成共享节点
    children    ``{id: (左子 id, 右子 id)}``
    leaf_order  从左到右排列的叶子 id，决定整棵树的横向展开
    """

    def __init__(self, nodes, children, leaf_order):
        self.nodes = list(nodes)
        self.children = dict(children)
        self.leaf_order = list(leaf_order)
        self.ids = [i for i, *_ in self.nodes]
        self.label = {i: lbl for i, lbl, d, p in self.nodes}
        self.parent = {i: p for i, lbl, d, p in self.nodes}
        self.depth = {i: d for i, lbl, d, p in self.nodes}

    def positions(self, top_y, row_gap, left, right):
        """叶子等距排开，父节点取它所有子节点的中点，因此边不会交叉。

        子节点个数不固定 —— 二叉递归是两个，链表递归只有一个
        （整条链会落在同一条竖线上，正是它该有的样子），
        多叉递归（图遍历、回溯）是若干个。
        """
        xs = {}
        span = (right - left) / max(len(self.leaf_order) - 1, 1)
        for i, nid in enumerate(self.leaf_order):
            xs[nid] = left + i * span
        for nid in sorted(self.children, key=lambda k: self.depth[k], reverse=True):
            kids = list(self.children[nid])
            xs[nid] = sum(xs[k] for k in kids) / len(kids)

        # 整体居中：窄树（单支链表只有一个"叶子"）否则会贴在图形区最左边
        if xs:
            current = (min(xs.values()) + max(xs.values())) / 2
            shift = (left + right) / 2 - current
            for nid in xs:
                xs[nid] += shift

        return {nid: np.array([xs[nid], top_y - self.depth[nid] * row_gap, 0.0])
                for nid in self.ids}


class TreeView:
    """把 TreeSpec 画成矩形节点与连接线，并按真实顺序播放调用与返回。

    维护三个状态，颜色全部由它们推出来：

    * ``visited`` 已经出现过的节点
    * ``path``    当前递归栈（从根到正在执行的节点）
    * ``done``    已经返回过的调用
    """

    MIN_ROW_GAP = 0.34          # 再挤就真的看不清了，低于此值会给出提示
    MIN_NODE_W = 0.72

    def __init__(self, scene, spec, *, top_y=2.28, row_gap=1.24,
                 left=-2.48, right=6.46, node_w=None, node_h=0.50,
                 bottom_y=-3.05, region=None):
        if region is not None:
            pad = 0.12
            left, right = region.x0 + pad, region.x1 - pad
            top_y, bottom_y = region.y1, region.y0

        self.scene = scene
        self.spec = spec

        # ---- 先按真实深度定行距，保证整棵树在画面内 ----
        # 数据量大时（比如 fib(8) 有 67 个节点、7 层），固定行距会撑出画面。
        depth = max(spec.depth.values()) + 1
        if depth > 1:
            row_gap = min(row_gap, (top_y - bottom_y) / (depth - 1))
        row_gap = max(row_gap, 0.20)
        # 节点高度贴着行距取，只留一点缝 —— 深树时才不至于把字号压得太小。
        # 取 0.46 的话，深度 10 的树字号会掉到 10（约 13px），基本看不清。
        node_h = min(node_h, row_gap * 0.80)
        # 标签字号跟着节点一起缩
        size = max(10, int(theme.SIZE_NODE * min(1.0, node_h / 0.50)))

        self.row_gap = row_gap
        self.node_h = node_h
        self.pos = spec.positions(top_y, row_gap, left, right)

        if row_gap < self.MIN_ROW_GAP:
            print(f"[警告] 调用树有 {depth} 层，行距被压到 {row_gap:.2f}，"
                  f"画面会偏挤；建议减小演示输入规模")

        # ---- 再按横向最挤的位置定节点宽度 ----
        # 同层只有一个节点时（单支链表）没有邻居可挤，宽度上限就是整个图形区，
        # 不能写死成一个小常数 —— 否则长标签会被横向挤压、把字号一路压下去。
        gap = self._min_row_gap()
        cap = ((right - left) - 0.20) if gap == float("inf") else (gap - 0.08)

        labels = self._make_labels(size)
        widest = max((l.get_width() for l in labels.values()), default=0.0)
        while size > 10 and widest + 0.30 > cap:
            size -= 1
            labels = self._make_labels(size)
            widest = max((l.get_width() for l in labels.values()), default=0.0)

        self.node_w = (node_w if node_w is not None
                       else max(self.MIN_NODE_W, min(cap, widest + 0.30)))
        self.label_size = size

        # 只在"确实是被空间挤小的"时候警告。
        # 不能拿 node_w <= MIN_NODE_W 当条件：标签本来就短（比如单字符）时
        # 节点取的就是最小宽度，那是正常的，不是看不清。
        widest_row = max(len(v) for v in self._rows().values())
        cramped = (widest + 0.30 > cap) or size <= 13
        if cramped:
            print(f"[警告] 调用树有 {len(spec.ids)} 个节点、{depth} 层、"
                  f"同层最多 {widest_row} 个，节点已缩到 {self.node_w:.2f}、"
                  f"字号 {size}（PRD 2.3 要求 1080p 下约 28~34 px）。"
                  f"这个规模在固定画幅里看不清，建议减小演示输入")

        self.visited, self.path, self.done = set(), [], set()

        self.boxes, self.nodes, self.edges = {}, {}, {}
        for nid in spec.ids:
            box = RoundedRectangle(width=self.node_w, height=node_h,
                                   corner_radius=0.07)
            box.set_fill(theme.BG, opacity=1.0)
            box.set_stroke(theme.WHITE, width=1.5)
            self.boxes[nid] = box
            self.nodes[nid] = VGroup(box, labels[nid]).move_to(self.pos[nid])
            parent = spec.parent[nid]
            if parent is not None:
                edge = Line(
                    border_point(self.pos[parent], self.pos[nid],
                                 self.node_w, node_h),
                    border_point(self.pos[nid], self.pos[parent],
                                 self.node_w, node_h),
                )
                edge.set_stroke(theme.WHITE, width=1.5)
                self.edges[nid] = edge

        self.all_nodes = VGroup(*self.nodes.values())
        self.all_edges = VGroup(*self.edges.values())

    def _make_labels(self, size):
        return {nid: Text(self.spec.label[nid],
                          font=theme.pick_font(self.spec.label[nid]),
                          font_size=size, color=theme.WHITE)
                for nid in self.spec.ids}

    def _has_child_below(self, nid):
        """有没有子节点正好在正下方（单支递归就是这样）。"""
        return any(abs(float(self.pos[c][0]) - float(self.pos[nid][0])) < 1e-6
                   for c in self.spec.children.get(nid, []))

    def _rows(self):
        """按深度分组，每层的 x 坐标（升序）。"""
        rows: dict[int, list[float]] = {}
        for nid in self.spec.ids:
            rows.setdefault(self.spec.depth[nid], []).append(float(self.pos[nid][0]))
        for row in rows.values():
            row.sort()
        return rows

    def _min_row_gap(self):
        """同一层里相邻两个节点之间的最小水平距离。"""
        gaps = []
        for row in self._rows().values():
            gaps.extend(row[i + 1] - row[i] for i in range(len(row) - 1))
        return min(gaps) if gaps else float("inf")

    # ------------------------------------------------------------ 颜色刷新
    _STYLE = {
        "active": (theme.BLUE, 2.7),
        "done": (theme.GREEN, 2.2),
        "idle": (theme.WHITE, 1.5),
    }

    def _state_of(self, nid):
        if nid in self.path:
            return "active"
        if nid in self.done:
            return "done"
        return "idle"

    def _color_anims(self, skip=()):
        """把已出现的节点与边刷成当前该有的颜色，返回一批 animate。

        刚创建、正要 FadeIn / ShowCreation 的对象要放进 ``skip``，
        否则同一个对象会被两个动画同时操作，manimlib 会报错。
        """
        anims = []
        for nid in self.visited:
            if nid in skip:
                continue
            color, width = self._STYLE[self._state_of(nid)]
            anims.append(self.boxes[nid].animate.set_stroke(color, width=width))
            if nid in self.edges:
                anims.append(self.edges[nid].animate.set_stroke(color, width=width))
        return anims

    def refresh(self, run_time=0.28):
        """手动刷新一次配色（一般不用调，enter / finish 会自动处理）。"""
        anims = self._color_anims()
        if anims:
            self.scene.play(*anims, run_time=run_time)

    # ------------------------------------------------------------ 结构出现
    def root(self, run_time=0.38, hold=0.0):
        """只显示根节点，并把递归路径初始化到它。"""
        root = self.spec.ids[0]
        self.visited.add(root)
        self.path.append(root)
        self.boxes[root].set_stroke(theme.BLUE, width=2.7)
        self.scene.play(FadeIn(self.nodes[root], scale=0.82),
                        run_time=run_time)
        if hold:
            self.scene.wait(hold)

    def enter(self, nid, run_time=0.34, hold=0.0):
        """进入一次调用：节点与连接边出现，整条递归路径保持蓝色。"""
        parent = self.spec.parent[nid]
        self.path.append(nid)
        self.visited.add(nid)

        # 新对象直接设成蓝色，不放进 _color_anims，避免和出现动画抢对象
        self.boxes[nid].set_stroke(theme.BLUE, width=2.7)
        anims = [FadeIn(self.nodes[nid], scale=0.82)]
        if parent is not None:
            self.edges[nid].set_stroke(theme.BLUE, width=2.7)
            anims.append(ShowCreation(self.edges[nid]))
        anims.extend(self._color_anims(skip={nid}))
        self.scene.play(*anims, run_time=run_time)
        if hold:
            self.scene.wait(hold)

    def finish(self, nid, run_time=0.26):
        """这次调用已经返回：从递归路径上撤下，节点与边转绿。

        返回后父调用重新成为路径末端，于是蓝色链条缩短一格、
        绿色区域变大一格 —— 回溯因此看得见。
        """
        if nid in self.path:
            self.path.remove(nid)
        self.done.add(nid)
        anims = self._color_anims()
        if anims:
            self.scene.play(*anims, run_time=run_time)

    def reveal_all(self, run_time=0.90):
        """整棵树一次性出现。不需要逐个生长的结构可用。"""
        for nid in self.spec.ids:
            self.visited.add(nid)
        self.scene.play(LaggedStart(
            *[ShowCreation(e) for e in self.edges.values()],
            *[FadeIn(n, scale=0.85) for n in self.nodes.values()],
            lag_ratio=0.05), run_time=run_time)

    # ------------------------------------------------------------ 数值返回
    def return_value(self, nid, text, hold=0.60, send=True, run_time=0.26,
                     finish=True):
        """命中边界的返回：节点转绿、值显示在下方，沿真实父子边回传。"""
        self.boxes[nid].set_stroke(theme.GREEN, width=2.4)
        value = Text(text, font=theme.mono_font(),
                     font_size=theme.SIZE_VALUE, color=theme.GREEN)
        value.next_to(self.nodes[nid], DOWN, buff=0.045)
        # 有子节点正好在正下方时（单支递归），父子连线也是竖直的，
        # 值标签压在线上会被穿过（PRD 2.4：线条不能穿过文字）。
        # 往右让开一点，避开那条线。
        if self._has_child_below(nid):
            value.shift(RIGHT * (self.node_w / 2 + 0.20))
        self.scene.play(FadeIn(value, shift=UP * 0.05), run_time=run_time)
        self.scene.wait(hold)
        if send:
            self.send_up(nid, value)
        self.scene.play(FadeOut(value), run_time=0.16)
        if finish:
            self.finish(nid)

    def send_up(self, nid, mob=None, run_time=0.24):
        """一个绿色小点沿父子边回到父节点，代表真实的数据回传。"""
        parent = self.spec.parent[nid]
        if parent is None:
            return
        start = mob.get_center() if mob is not None else self.nodes[nid].get_center()
        target = border_point(self.pos[parent], start,
                              self.node_w, self.node_h, gap=0.06)
        path = Line(start, target)
        dot = Dot(path.get_start(), radius=0.05)
        dot.set_fill(theme.GREEN, opacity=1.0)
        dot.set_stroke(width=0)
        self.scene.add(dot)
        self.scene.play(MoveAlongPath(dot, path), run_time=run_time)
        self.scene.remove(dot)

    # ---------------------------------------------------------------- 标记
    def mark_done(self, nid, width=2.2):
        self.done.add(nid)
        self.boxes[nid].set_stroke(theme.GREEN, width=width)

    def cost_animation(self, nid, width=3.4):
        """红色强调：重复计算、冲突或需要特别注意的代价（PRD 2.2）。"""
        return self.boxes[nid].animate.set_stroke(theme.RED, width=width)

    def others(self, keep):
        return [nid for nid in self.spec.ids if nid not in keep]

    def ids_with_label(self, text):
        """按显示标签筛选节点，例如找出所有 fib(2) 节点。"""
        return [nid for nid, lbl in self.spec.label.items() if lbl == text]

    def dim_all_but(self, keep, opacity=0.25, run_time=0.45):
        """把不关心的节点与边压暗，只留 keep 里的。"""
        keep = set(keep)
        rest = [nid for nid in self.spec.ids if nid not in keep]
        group = VGroup(*[self.nodes[k] for k in rest],
                       *[self.edges[k] for k in rest if k in self.edges])
        self.scene.play(group.animate.set_opacity(opacity), run_time=run_time)

    def fade_out(self, run_time=0.40):
        self.scene.play(FadeOut(VGroup(self.all_edges, self.all_nodes)),
                        run_time=run_time)
