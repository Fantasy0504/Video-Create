"""非记忆化递归

本文件由 ``tools/scaffold.py`` 从 ``fib.json`` 生成。

结构和执行顺序是自动出来的（和真实运行完全一致），
下面标了 TODO 的地方需要人工决定：C++ 代码、标题、提示文案、节奏。
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

from manimlib import *                                       # noqa: E402

from engine import AlgoScene, TreeSpec, curtain, theme       # noqa: E402


# ---------------------------------------------------------------- 结构数据
# 由 tools/trace.py 跑 fib(5) 自动导出，
# 共 15 次调用、8 次基础情况、
# 最大深度 5 层。
NODES = (
    (1, 'fib(5)', 0, None),
    (2, 'fib(4)', 1, 1),
    (3, 'fib(3)', 2, 2),
    (4, 'fib(2)', 3, 3),
    (5, 'fib(1)', 4, 4),
    (6, 'fib(0)', 4, 4),
    (7, 'fib(1)', 3, 3),
    (8, 'fib(2)', 2, 2),
    (9, 'fib(1)', 3, 8),
    (10, 'fib(0)', 3, 8),
    (11, 'fib(3)', 1, 1),
    (12, 'fib(2)', 2, 11),
    (13, 'fib(1)', 3, 12),
    (14, 'fib(0)', 3, 12),
    (15, 'fib(1)', 2, 11),
)

CHILDREN = {
    1: (2, 11), 2: (3, 8),
    3: (4, 7), 4: (5, 6),
    8: (9, 10), 11: (12, 15),
    12: (13, 14),
}
LEAF_ORDER = (5, 6, 7, 9, 10, 13, 14, 15,)


class FibonacciGen(AlgoScene):
    TITLE_TEXT = '非记忆化递归'
    TITLE_TAG = 'fib(5)'

    # TODO: 换成这一期的 C++ 代码（默认给的是能跑通的占位）。
    #       行号要和 build() 里 bind() 对得上：
    #         0 函数签名 / 1 边界条件 / 2 左子调用 / 3 右子调用 / 4 求和 / 5 收尾
    CODE_SOURCE = (
        "int f(int n) {",
        "    if (n <= 1) return n;",
        "    int left = f(n - 1);",
        "    int right = f(n - 2);",
        "    return left + right;",
        "}",
    )

    # ------------------------------------------------------------ 节奏
    # TODO: 上面那段是机器生成的、每步同速。真实成片里"第一次执行要讲细、
    # 后续相同步骤可以简化"，把节奏改成下面这样会好看得多：
    #   首次下钻 / 首次求和 —— 用较长的 run_time 与 hold
    #   重复的同类步骤    —— 用较短的一端
    ENTER_RT = 0.28
    RETURN_HOLD = 0.45
    SUM_HOLD = 0.40

    def setup(self):
        self.spec = TreeSpec(NODES, CHILDREN, LEAF_ORDER)
        self.calls = {}

    def name_of(self, nid):
        return self.spec.label[nid]

    def fill(self, nid, order, value, run_time=0.22):
        """把第 order 个子调用的返回值，填进父调用自己的局部变量。"""
        key = "left" if order == 1 else "right"
        self.calls.setdefault(nid, {})[key] = value
        self.status.set_call(self.name_of(nid), **self.calls[nid],
                             run_time=run_time)

    def sum_node(self, nid, hold=None):
        """两个值齐备后展示求和，再把结果沿真实父子边回传。"""
        self.code.focus(self, "total", run_time=0.16)
        done = self.calls[nid]
        total = done["left"] + done["right"]
        self.status.set_expr(self.name_of(nid),
                             f"{done['left']} + {done['right']} = {total}",
                             run_time=0.22)
        self.wait(self.SUM_HOLD if hold is None else hold)
        self.tree.send_up(nid)
        self.tree.finish(nid)

    # ---------------------------------------------------------------- 构建
    def build(self):
        self.tree = self.add_tree(self.spec)
        self.scene_setup()
        self.walk()
        self.scene_wrapup()

    def scene_setup(self):
        self.add_title(run_time=0.30)
        self.add_code(run_time=0.50)
        # TODO: 行号要对着你贴的 CODE_SOURCE 数一遍
        self.code.bind(sig=0, base=1, left=2, right=3, total=4, end=5)
        self.code.focus_now("base")
        self.add_status()
        self.add_hint()
        self.tree.root(run_time=0.34)
        self.status.set(self.TITLE_TAG, run_time=0.22)
        self.wait(0.30)

    def walk(self):
        """真实深度优先：先算完左子树，再进右子树。这一段是自动生成的。"""
        self.tree.enter(1)
        self.tree.enter(2)
        self.tree.enter(3)
        self.tree.enter(4)
        self.tree.enter(5)
        self.tree.return_value(5, "=1")
        self.fill(4, 1, 1)
        self.tree.enter(6)
        self.tree.return_value(6, "=0")
        self.fill(4, 2, 0)
        self.sum_node(4)
        self.fill(3, 1, 1)
        self.tree.enter(7)
        self.tree.return_value(7, "=1")
        self.fill(3, 2, 1)
        self.sum_node(3)
        self.fill(2, 1, 2)
        self.tree.enter(8)
        self.tree.enter(9)
        self.tree.return_value(9, "=1")
        self.fill(8, 1, 1)
        self.tree.enter(10)
        self.tree.return_value(10, "=0")
        self.fill(8, 2, 0)
        self.sum_node(8)
        self.fill(2, 2, 1)
        self.sum_node(2)
        self.fill(1, 1, 3)
        self.tree.enter(11)
        self.tree.enter(12)
        self.tree.enter(13)
        self.tree.return_value(13, "=1")
        self.fill(12, 1, 1)
        self.tree.enter(14)
        self.tree.return_value(14, "=0")
        self.fill(12, 2, 0)
        self.sum_node(12)
        self.fill(11, 1, 1)
        self.tree.enter(15)
        self.tree.return_value(15, "=1")
        self.fill(11, 2, 1)
        self.sum_node(11)
        self.fill(1, 2, 2)
        self.sum_node(1)

    def scene_wrapup(self):
        # TODO: 结论页文案按这一期的算法改
        self.code.hide(self, run_time=0.28)
        self.status.clear(run_time=0.18)
        self.hint.clear(run_time=0.18)
        curtain(self, run_time=0.30)
        result = Text("结果是 …", font=theme.chinese_font(),
                      font_size=theme.SIZE_RESULT, color=theme.GREEN)
        result.move_to(np.array([0.0, 0.40, 0.0]))
        self.play(FadeIn(result, shift=UP * 0.10), run_time=0.40)
        self.wait(1.60)
