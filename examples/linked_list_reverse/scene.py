"""链表反转 —— 链表递归示例。

演示**链表递归**：先一路递归到链尾，回溯时逐个把 ``next`` 指向前一个
节点。所以画面上的箭头方向是**会变**的，这是这一期最该看清的地方。

上半屏放链表本身（节点 + next 箭头 + head 指针），下半屏放调用树。

运行：
    manimgl examples/linked_list_reverse/scene.py ListReverse -w
"""
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = _HERE
while not os.path.isdir(os.path.join(_ROOT, "engine")):
    _parent = os.path.dirname(_ROOT)
    if _parent == _ROOT:
        break
    _ROOT = _parent
sys.path.insert(0, _ROOT)

from manimlib import *                                    # noqa: E402

from engine import (AlgoScene, Region, TreeSpec, complexity_row,  # noqa: E402
                    curtain, theme)

VALUES = (1, 2, 3, 4)

# 由 tools/trace.py 从 reverse.py 导出：单支递归，每个调用只有一个子调用
NODES = (
    (1, "1→2→3→4", 0, None),
    (2, "2→3→4", 1, 1),
    (3, "3→4", 2, 2),
    (4, "4", 3, 3),
)
CHILDREN = {1: (2,), 2: (3,), 3: (4,)}
LEAF_ORDER = (4,)


class ListReverse(AlgoScene):
    TITLE_TEXT = "链表反转"
    TITLE_TAG = "n = 4"

    CODE_SOURCE = (
        "Node* reverse(Node* head) {",
        "    if (!head || !head->next) return head;",
        "    Node* rest = reverse(head->next);",
        "    head->next->next = head;",
        "    head->next = NULL;",
        "    return rest;",
        "}",
    )

    CODE_CENTER = (-4.95, 1.30)
    STATUS_CENTER = (-4.95, -0.95)

    def setup(self):
        self.spec = TreeSpec(NODES, CHILDREN, LEAF_ORDER)

    def build(self):
        list_region, tree_region = self._regions()
        # 链表不显示下标：节点值本身就是标识，而下方的 head 指针箭头
        # 正好压在第一个下标上，两个标签会叠在一起
        self.chain = self.add_linked_list(VALUES, region=list_region,
                                          show_index=False)
        self.tree = self.add_tree(self.spec, region=tree_region)
        self.scene_intro()
        self.scene_walk()
        self.scene_wrapup()

    @staticmethod
    def _regions():
        """上半屏链表、下半屏调用树。单支树很窄，下面这块够用。"""
        return Region(-2.30, 6.46, -3.28, 3.02).split_top(0.30)

    # ------------------------------------------------------------ 场景
    def scene_intro(self):
        self.add_title(run_time=0.30)
        self.add_code(run_time=0.50)
        self.code.bind(sig=0, base=1, rec=2, flip=3, cut=4, back=5)
        self.code.focus_now("base")
        self.chain.appear(run_time=0.70)
        self.add_status()
        self.add_hint()
        self.head_ptr = self.chain.pointer(0, "head")
        self.tree.root(run_time=0.32)
        self.status.set("reverse(head)", run_time=0.20)
        self.wait(0.30)

    def scene_walk(self):
        self.hint.set("先一路递归到链尾", run_time=0.26)

        # 1 → 2 → 3 一路往下（节点 4 是链尾，作为边界）
        for nid, index in ((2, 1), (3, 2)):
            self.code.focus(self, "rec", run_time=0.14)
            self.chain.highlight(index, theme.BLUE, 3.2)
            self.tree.enter(nid, run_time=0.26)
            self.status.set(f"reverse({index + 1}→…)",
                            run_time=0.16)
        self.chain.highlight(3, theme.BLUE, 3.2)
        self.tree.enter(4, run_time=0.24)
        self.status.set("只剩一个节点，直接返回", run_time=0.18)
        self.wait(0.30)

        # 边界返回：链尾就是新链的头
        self.hint.set("从链尾往回返，边返边改指针", run_time=0.26)
        self.tree.return_value(4, "=4", hold=0.55)
        self.chain.mark(3, theme.GREEN, 2.6)

        # 开始回溯：每返回一层，反转一根箭头
        for nid, link in ((3, 2), (2, 1), (1, 0)):
            self.code.focus(self, "flip", run_time=0.16)
            self.status.set(f"{link + 1}.next->next = {link + 1}",
                            run_time=0.18)
            self.chain.highlight(link, theme.BLUE, 3.2)
            self.chain.reverse_link(link, run_time=0.42)
            self.code.focus(self, "cut", run_time=0.14)
            self.chain.mark(link, theme.GREEN, 2.6)
            if nid == 1:
                # 根调用返回的是新链头
                self.tree.return_value(nid, f"={link + 1}", hold=0.40)
            else:
                self.tree.send_up(nid)
                self.tree.finish(nid)

        self.code.focus(self, "back", run_time=0.16)
        self.hint.set("新链的头是原来的尾", run_time=0.26)
        self.chain.mark(3, theme.GREEN, 3.0)
        self.chain.mark(2, theme.GREEN, 2.6)
        self.chain.mark(1, theme.GREEN, 2.6)
        self.chain.mark(0, theme.GREEN, 2.6)
        self.wait(0.55)

    def scene_wrapup(self):
        self.code.hide(self, run_time=0.28)
        self.status.clear(run_time=0.18)
        self.hint.clear(run_time=0.18)
        self.play(FadeOut(self.head_ptr), run_time=0.20)
        curtain(self, run_time=0.30)

        result = Text("4 → 3 → 2 → 1", font=theme.mono_font(),
                      font_size=theme.SIZE_RESULT, color=theme.GREEN)
        result.move_to(np.array([0.0, 0.55, 0.0]))
        rows = VGroup(
            complexity_row("时间  ", "", "n", theme.GREEN),
            complexity_row("栈空间  ", "", "n", theme.GREEN),
        ).arrange(RIGHT, buff=0.90)
        rows.move_to(np.array([0.0, -0.60, 0.0]))

        self.play(FadeIn(result, shift=UP * 0.10), run_time=0.42)
        self.play(FadeIn(rows, shift=UP * 0.08), run_time=0.36)
        self.wait(1.70)


class ListReverseLite(ListReverse):
    """简易版：去掉铺垫，只留"下降到链尾 → 回溯改指针"。

    代码压到 7 行，链表仍是 4 个节点。完整版会讲清局面（指针含义、
    每一步的局部变量），这一版假设观众已经知道链表反转在干什么，
    直接看时序。

    运行：
        manimgl examples/linked_list_reverse/scene.py ListReverseLite -w
    """

    CODE_SOURCE = (
        "Node* reverse(Node* h) {",
        "    if (!h || !h->next) return h;",
        "    Node* r = reverse(h->next);",
        "    h->next->next = h;",
        "    h->next = NULL;",
        "    return r;",
        "}",
    )

    CODE_CENTER = (-4.95, 1.20)

    def build(self):
        list_region, tree_region = self._regions()
        self.chain = self.add_linked_list(VALUES, region=list_region,
                                          show_index=False)
        self.tree = self.add_tree(self.spec, region=tree_region)

        # ---- 布置：直接进正题，不做独立片头 ----
        self.add_title(run_time=0.26)
        self.add_code(run_time=0.44)
        self.code.bind(base=1, rec=2, flip=3, cut=4, back=5)
        self.code.focus_now("base")
        self.chain.appear(run_time=0.50)
        self.add_status()
        self.add_hint()
        self.tree.root(run_time=0.28)
        self.status.set("reverse(head)", run_time=0.18)

        # ---- 下降到链尾 ----
        self.hint.set("一路递归到链尾", run_time=0.22)
        for nid, index in ((2, 1), (3, 2)):
            self.code.focus(self, "rec", run_time=0.12)
            self.chain.highlight(index, theme.BLUE, 3.2)
            self.tree.enter(nid, run_time=0.22)
        self.chain.highlight(3, theme.BLUE, 3.2)
        self.tree.enter(4, run_time=0.20)
        self.status.set("只剩一个节点，返回", run_time=0.16)
        self.wait(0.22)

        # ---- 回溯：每返回一层，翻一根箭头 ----
        self.hint.set("边往回返，边改指针方向", run_time=0.22)
        self.tree.return_value(4, "=4", hold=0.38)
        self.chain.mark(3, theme.GREEN, 2.6)

        for nid, link in ((3, 2), (2, 1), (1, 0)):
            self.code.focus(self, "flip", run_time=0.14)
            self.chain.highlight(link, theme.BLUE, 3.0)
            self.chain.reverse_link(link, run_time=0.36)
            self.code.focus(self, "cut", run_time=0.12)
            self.chain.mark(link, theme.GREEN, 2.6)
            self.status.set(f"{link + 1}.next->next = {link + 1}",
                            run_time=0.16)
            if nid == 1:
                self.tree.return_value(nid, "=4", hold=0.34)
            else:
                self.tree.send_up(nid)
                self.tree.finish(nid)

        # ---- 结论 ----
        self.hint.set("新链的头是原来的尾", run_time=0.22)
        self.code.hide(self, run_time=0.26)
        self.status.clear(run_time=0.16)
        self.hint.clear(run_time=0.16)
        curtain(self, run_time=0.26)

        result = Text("4 → 3 → 2 → 1", font=theme.mono_font(),
                      font_size=theme.SIZE_RESULT, color=theme.GREEN)
        result.move_to(np.array([0.0, 0.35, 0.0]))
        rows = VGroup(
            complexity_row("时间  ", "", "n", theme.GREEN),
            complexity_row("栈空间  ", "", "n", theme.GREEN),
        ).arrange(RIGHT, buff=0.90)
        rows.move_to(np.array([0.0, -0.70, 0.0]))

        self.play(FadeIn(result, shift=UP * 0.10), run_time=0.38)
        self.play(FadeIn(rows, shift=UP * 0.08), run_time=0.32)
        self.wait(1.50)
