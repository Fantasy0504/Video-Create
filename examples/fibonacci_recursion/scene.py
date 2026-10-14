"""斐波那契数列 · 非记忆化递归。

对应 PRD 第二部分：演示 ``fib(5)`` 的调用、返回与重复计算。
采用真实的深度优先顺序 —— 先完整算完左子树，再进入右子树，
调用与返回交替进行，不按层统一返回（PRD 9.1）。

运行：
    manimgl examples/fibonacci_recursion/scene.py FibonacciNaive -w
"""
import os
import sys

# 允许直接 manimgl 运行，不必先安装本包：向上找到含 engine/ 的目录
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = _HERE
while not os.path.isdir(os.path.join(_ROOT, "engine")):
    _parent = os.path.dirname(_ROOT)
    if _parent == _ROOT:
        break
    _ROOT = _parent
sys.path.insert(0, _ROOT)

from manimlib import *                                    # noqa: E402

from engine import AlgoScene, TreeSpec, complexity_row, curtain, theme  # noqa: E402


class FibonacciNaive(AlgoScene):
    TITLE_TEXT = "非记忆化递归"
    TITLE_TAG = "fib(5)"

    CODE_SOURCE = (
        "int fib(int n) {",
        "    if (n <= 1) return n;",
        "    int left = fib(n - 1);",
        "    int right = fib(n - 2);",
        "    return left + right;",
        "}",
    )

    # (id, 显示名, 深度, 父节点)。id 就是真实的进入顺序：
    # 同参数的多次调用必须是不同 id，不得合并成共享节点（PRD 第 8 节）。
    NODES = (
        (1, "fib(5)", 0, None),
        (2, "fib(4)", 1, 1),
        (3, "fib(3)", 2, 2),
        (4, "fib(2)", 3, 3),
        (5, "fib(1)", 4, 4),
        (6, "fib(0)", 4, 4),
        (7, "fib(1)", 3, 3),
        (8, "fib(2)", 3, 2),
        (9, "fib(1)", 4, 8),
        (10, "fib(0)", 4, 8),
        (11, "fib(3)", 1, 1),
        (12, "fib(2)", 2, 11),
        (13, "fib(1)", 3, 12),
        (14, "fib(0)", 3, 12),
        (15, "fib(1)", 2, 11),
    )
    CHILDREN = {
        1: (2, 11), 2: (3, 8), 3: (4, 7), 4: (5, 6),
        8: (9, 10), 11: (12, 15), 12: (13, 14),
    }
    LEAF_ORDER = (5, 6, 7, 9, 10, 13, 14, 15)

    # ---------------------------------------------------------------- 准备
    def setup(self):
        self.spec = TreeSpec(self.NODES, self.CHILDREN, self.LEAF_ORDER)
        self.calls = {}          # 各调用已填好的 left / right

    def build(self):
        self.tree = self.add_tree(self.spec)
        self.scene_intro()
        self.scene_rules()
        self.scene_first_descent()
        self.scene_finish_tree()
        self.scene_duplicates()
        self.scene_conclusion()

    # ------------------------------------------------------- 单步小助手
    def name_of(self, nid):
        return self.spec.label[nid]

    def fill(self, nid, side, value, run_time=0.24):
        """把子调用的返回值填入父调用自己的局部变量（PRD 9.2）。"""
        self.calls.setdefault(nid, {})[side] = value
        self.status.set_call(self.name_of(nid), **self.calls[nid],
                             run_time=run_time)

    def sum_node(self, nid, hold=0.35):
        """两个值齐备后展示一次可读的求和，再把结果沿真实父子边回传。"""
        self.code.focus(self, "total", run_time=0.16)
        done = self.calls[nid]
        total = done["left"] + done["right"]
        self.status.set_expr(self.name_of(nid),
                             f"{done['left']} + {done['right']} = {total}",
                             run_time=0.24)
        self.wait(hold)
        self.tree.send_up(nid)
        self.tree.finish(nid)

    # -------------------------------------------------------- 场景一：任务
    def scene_intro(self):
        title = Text("斐波那契 · 非记忆化递归", font=theme.chinese_font(),
                     font_size=theme.SIZE_TITLE, color=theme.WHITE)
        tag = Text("fib(5)", font=theme.mono_font(),
                   font_size=34, color=theme.BLUE)
        sub = Text("看清调用与返回", font=theme.chinese_font(),
                   font_size=24, color=theme.WHITE)
        group = VGroup(title, VGroup(tag, sub).arrange(RIGHT, buff=0.45))
        group.arrange(DOWN, buff=0.40)

        self.play(Write(title), run_time=0.50)
        self.play(FadeIn(tag, shift=UP * 0.10),
                  FadeIn(sub, shift=UP * 0.10), run_time=0.36)
        self.wait(0.70)
        self.play(FadeOut(group), run_time=0.34)

    # ------------------------------------------------------ 场景二：规则
    def scene_rules(self):
        self.add_title()
        self.add_code()
        self.code.bind(sig=0, base=1, left=2, right=3, total=4, end=5)
        self.code.focus_now("base")
        self.wait(0.24)

        note = VGroup(
            Text("fib(0) = 0", font=theme.mono_font(),
                 font_size=20, color=theme.GREEN),
            Text("fib(1) = 1", font=theme.mono_font(),
                 font_size=20, color=theme.GREEN),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        note.next_to(self.code.lines[1], DOWN, buff=0.20)
        note.align_to(self.code.lines[1], LEFT)
        self.play(FadeIn(note, shift=UP * 0.07), run_time=0.34)
        self.wait(0.45)

        for target, hold in (("left", 0.26), ("right", 0.26), ("total", 0.30)):
            self.code.focus(self, target, run_time=0.28)
            self.wait(hold)
        self.play(FadeOut(note), run_time=0.24)

        self.tree.root(run_time=0.38)
        self.add_status()
        self.status.set("fib(5)", run_time=0.26)
        self.wait(0.24)

    # -------------------------------------------- 场景三：第一次递归到底
    def scene_first_descent(self):
        self.add_hint()
        self.hint.set("先算左边", run_time=0.26)

        # 5 → 4 → 3 → 2 一路向下调用
        for nid in (2, 3, 4):
            self.code.focus(self, "left", run_time=0.18)
            self.tree.enter(nid, run_time=0.32)
            self.status.set_call(self.name_of(nid), run_time=0.20)

        # fib(2) 的左子 fib(1) 命中边界
        self.code.focus(self, "left", run_time=0.16)
        self.tree.enter(5, run_time=0.28)
        self.hint.set("到达边界，返回", run_time=0.24)
        self.tree.return_value(5, "=1", hold=0.80)
        self.fill(4, "left", 1)

        # 同一次 fib(2) 再调用 fib(0)
        self.code.focus(self, "right", run_time=0.18)
        self.tree.enter(6, run_time=0.28)
        self.tree.return_value(6, "=0", hold=0.68)
        self.fill(4, "right", 0)

        # fib(2) = 1 + 0 —— 全片最详细的一次求和，留足停顿
        self.hint.set("得到两个值，再求和", run_time=0.24)
        self.sum_node(4, hold=1.10)
        self.fill(3, "left", 1)

        # 回到 fib(3)，再算它右侧独立的 fib(1)
        self.code.focus(self, "left", run_time=0.16)
        self.tree.enter(7, run_time=0.28)
        self.tree.return_value(7, "=1", hold=0.36)
        self.fill(3, "right", 1)

    # ------------------------------------------ 场景四：按真实顺序完成
    def scene_finish_tree(self):
        self.sum_node(3, hold=0.42)
        self.fill(2, "left", 2)

        # fib(4) 右侧是一次全新的 fib(2)，两个基础调用都要重跑
        self.code.focus(self, "right", run_time=0.18)
        self.tree.enter(8, run_time=0.30)
        self.status.set_call(self.name_of(8), run_time=0.18)
        self.tree.enter(9, run_time=0.24)
        self.tree.return_value(9, "=1", hold=0.26)
        self.fill(8, "left", 1)
        self.tree.enter(10, run_time=0.24)
        self.tree.return_value(10, "=0", hold=0.26)
        self.fill(8, "right", 0)
        self.sum_node(8, hold=0.30)
        self.fill(2, "right", 1)

        self.sum_node(2, hold=0.45)
        self.fill(1, "left", 3)
        self.hint.set("左子树算完，再进右边", run_time=0.26)

        # 根节点右侧是又一次全新的 fib(3)
        self.code.focus(self, "right", run_time=0.18)
        self.tree.enter(11, run_time=0.32)
        self.status.set_call(self.name_of(11), run_time=0.18)
        self.tree.enter(12, run_time=0.26)
        self.status.set_call(self.name_of(12), run_time=0.16)
        self.tree.enter(13, run_time=0.22)
        self.tree.return_value(13, "=1", hold=0.24)
        self.fill(12, "left", 1)
        self.tree.enter(14, run_time=0.22)
        self.tree.return_value(14, "=0", hold=0.24)
        self.fill(12, "right", 0)
        self.sum_node(12, hold=0.28)
        self.fill(11, "left", 1)

        self.tree.enter(15, run_time=0.22)
        self.tree.return_value(15, "=1", hold=0.26)
        self.fill(11, "right", 1)
        self.sum_node(11, hold=0.34)
        self.fill(1, "right", 2)

        # 根调用拿到 3 与 2
        self.hint.set("两个子树都回来了", run_time=0.24)
        self.sum_node(1, hold=0.62)
        self.hint.set("fib(5) 得到结果", run_time=0.26)
        self.play(self.tree.boxes[1].animate.set_stroke(theme.GREEN, width=2.8),
                  run_time=0.34)
        self.wait(0.60)

    # --------------------------------------------------- 场景五：重复计算
    def scene_duplicates(self):
        self.code.hide(self)
        self.status.clear()
        self.hint.clear()

        # 三个独立的 fib(2) 与五个独立的 fib(1)
        f2 = self.tree.ids_with_label("fib(2)")
        f1 = self.tree.ids_with_label("fib(1)")
        context = VGroup(self.tree.all_edges,
                         *[self.tree.nodes[k] for k in self.tree.others(f2 + f1)])

        note = Text("fib(2) 被计算 3 次", font=theme.chinese_font(),
                    font_size=26, color=theme.RED)
        note.move_to(np.array([-4.30, 1.10, 0.0]))
        self.play(
            context.animate.set_opacity(0.25),
            *[self.tree.cost_animation(k) for k in f2],
            run_time=0.52,
        )
        self.play(FadeIn(note, shift=RIGHT * 0.10), run_time=0.34)
        self.wait(1.10)

        note2 = Text("fib(1) 被调用 5 次", font=theme.chinese_font(),
                     font_size=26, color=theme.RED)
        note2.move_to(np.array([-4.30, 0.10, 0.0]))
        self.play(
            FadeOut(note),
            *[self.tree.cost_animation(k) for k in f1],
            run_time=0.48,
        )
        self.play(FadeIn(note2, shift=RIGHT * 0.10), run_time=0.34)
        self.wait(1.20)
        self.play(FadeOut(note2), run_time=0.30)

    # ------------------------------------------------------ 场景六：结论
    def scene_conclusion(self):
        curtain(self)

        result = Text("fib(5) = 5", font=theme.mono_font(),
                      font_size=theme.SIZE_RESULT, color=theme.GREEN)
        result.move_to(np.array([0.0, 1.40, 0.0]))
        sentence = Text("相同子问题，会重复计算", font=theme.chinese_font(),
                        font_size=28, color=theme.WHITE)
        sentence.move_to(np.array([0.0, 0.42, 0.0]))

        rows = VGroup(
            complexity_row("时间上界  ", "2", "n", theme.RED),
            complexity_row("栈空间    ", "", "n", theme.GREEN),
        ).arrange(DOWN, buff=0.28)
        rows.move_to(np.array([0.0, -1.00, 0.0]))

        self.play(FadeIn(result, shift=UP * 0.12), run_time=0.48)
        self.play(FadeIn(sentence, shift=UP * 0.10), run_time=0.40)
        self.play(FadeIn(rows, shift=UP * 0.10), run_time=0.44)
        self.wait(2.10)
        self.play(FadeOut(VGroup(result, sentence, rows)), run_time=0.40)


class FibonacciNaiveLite(FibonacciNaive):
    """简洁版：去掉片头动画与重复计算回顾，全程用颜色显示递归与回溯。

    颜色用法（PRD 2.2）：

    * **蓝** —— 当前递归栈，从根一路连到正在执行的那个调用。
      蓝色链条随"往下钻"变长，观众一眼看出现在钻到第几层。
    * **绿** —— 已经算完并返回的调用，连接边一起转绿。
      绿色随"往回退"逐段蔓延，回溯的路径看得见。
    * 白 —— 还没访问到的节点。

    运行：
        manimgl examples/fibonacci_recursion/scene.py FibonacciNaiveLite -w
    """

    def build(self):
        self.tree = self.add_tree(self.spec)
        self.scene_setup()
        self.walk_tree()
        self.scene_wrapup()

    # ------------------------------------------------------------ 布置
    def scene_setup(self):
        self.add_title(run_time=0.30)
        self.add_code(run_time=0.50)
        self.code.bind(sig=0, base=1, left=2, right=3, total=4, end=5)
        self.code.focus_now("base")
        self.add_status()
        self.add_hint()
        self.tree.root(run_time=0.34)
        self.status.set("fib(5)", run_time=0.22)
        self.hint.set("蓝色是当前调用链", run_time=0.26)
        self.wait(0.35)

    # ------------------------------------------------- 整棵树：下行再回退
    def walk_tree(self):
        self.hint.set("一路往下钻，蓝色链条变长", run_time=0.26)

        # 5 → 4 → 3 → 2
        for nid in (2, 3, 4):
            self.code.focus(self, "left", run_time=0.12)
            self.tree.enter(nid, run_time=0.26)
            self.status.set_call(self.name_of(nid), run_time=0.14)
        self.wait(0.20)

        # fib(2) 的左子 fib(1) 命中边界
        self.code.focus(self, "left", run_time=0.12)
        self.tree.enter(5, run_time=0.24)
        self.hint.set("到底了，开始返回", run_time=0.24)
        self.tree.return_value(5, "=1", hold=0.62)
        self.fill(4, "left", 1)

        # 同一次 fib(2) 再调用 fib(0)
        self.code.focus(self, "right", run_time=0.14)
        self.tree.enter(6, run_time=0.24)
        self.tree.return_value(6, "=0", hold=0.52)
        self.fill(4, "right", 0)

        self.hint.set("绿色是已经算完并交回的", run_time=0.24)
        self.sum_node(4, hold=0.85)
        self.fill(3, "left", 1)

        # 回到 fib(3)，再算它右侧独立的 fib(1)
        self.code.focus(self, "left", run_time=0.12)
        self.tree.enter(7, run_time=0.24)
        self.tree.return_value(7, "=1", hold=0.34)
        self.fill(3, "right", 1)

        self.sum_node(3, hold=0.38)
        self.fill(2, "left", 2)

        # fib(4) 右侧是一次全新的 fib(2)，两个基础调用都要重跑
        self.code.focus(self, "right", run_time=0.14)
        self.tree.enter(8, run_time=0.26)
        self.status.set_call(self.name_of(8), run_time=0.14)
        self.tree.enter(9, run_time=0.22)
        self.tree.return_value(9, "=1", hold=0.24)
        self.fill(8, "left", 1)
        self.tree.enter(10, run_time=0.22)
        self.tree.return_value(10, "=0", hold=0.24)
        self.fill(8, "right", 0)
        self.sum_node(8, hold=0.28)
        self.fill(2, "right", 1)

        self.sum_node(2, hold=0.40)
        self.fill(1, "left", 3)
        self.hint.set("左子树整棵绿了，再进右边", run_time=0.26)

        # 根节点右侧是又一次全新的 fib(3)
        self.code.focus(self, "right", run_time=0.14)
        self.tree.enter(11, run_time=0.28)
        self.status.set_call(self.name_of(11), run_time=0.14)
        self.tree.enter(12, run_time=0.24)
        self.status.set_call(self.name_of(12), run_time=0.12)
        self.tree.enter(13, run_time=0.20)
        self.tree.return_value(13, "=1", hold=0.22)
        self.fill(12, "left", 1)
        self.tree.enter(14, run_time=0.20)
        self.tree.return_value(14, "=0", hold=0.22)
        self.fill(12, "right", 0)
        self.sum_node(12, hold=0.26)
        self.fill(11, "left", 1)

        self.tree.enter(15, run_time=0.20)
        self.tree.return_value(15, "=1", hold=0.24)
        self.fill(11, "right", 1)
        self.sum_node(11, hold=0.30)
        self.fill(1, "right", 2)

        self.hint.set("两条链合到根上", run_time=0.24)
        self.sum_node(1, hold=0.55)
        self.wait(0.30)

    # ------------------------------------------------------------ 收尾
    def scene_wrapup(self):
        self.hint.set("每一步都真算了一遍", run_time=0.26)
        self.code.hide(self, run_time=0.28)
        self.status.clear(run_time=0.18)
        self.hint.clear(run_time=0.18)
        curtain(self, run_time=0.30)

        result = Text("fib(5) = 5", font=theme.mono_font(),
                      font_size=theme.SIZE_RESULT, color=theme.GREEN)
        result.move_to(np.array([0.0, 0.55, 0.0]))
        rows = VGroup(
            complexity_row("时间上界  ", "2", "n", theme.RED),
            complexity_row("栈空间    ", "", "n", theme.GREEN),
        ).arrange(RIGHT, buff=0.80)
        rows.move_to(np.array([0.0, -0.60, 0.0]))

        self.play(FadeIn(result, shift=UP * 0.10), run_time=0.40)
        self.play(FadeIn(rows, shift=UP * 0.08), run_time=0.36)
        self.wait(1.70)
