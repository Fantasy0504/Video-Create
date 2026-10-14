"""树递归：求二叉树高度。

演示**形状由数据决定的递归** —— 调用树的形状跟着树本身走，
可能有单支的分支（``LLL`` 那种），不像 fib 那样规整。

跑法：
    python tools/trace.py examples/recursion_shapes/binary_tree.py:height \\
        --input-fn make_tree --args 0 --label-fn node_repr -o traces/tree_height.json
"""


class TreeNode:
    def __init__(self, name, left=None, right=None):
        self.name = name
        self.left = left
        self.right = right

    def __repr__(self):
        return f"T({self.name})"


def make_tree(_=0):
    """造一棵故意不平衡的树，`LLL` 那条分支只有单支。

                 root
                /    \\
              L        R
            /   \\
          LL     LR
          /
        LLL
    """
    return TreeNode(
        "root",
        TreeNode("L",
                 TreeNode("LL", TreeNode("LLL")),
                 TreeNode("LR")),
        TreeNode("R"),
    )


def node_repr(node):
    """节点标签就是树节点的名字；空节点显示成 nil。

    用 ASCII 的 ``nil`` 而不是 ``∅``：等宽字体（Consolas）没有 U+2205，
    渲染出来会缺字。``theme.pick_font`` 只认中日韩字符，救不了它。
    """
    return "nil" if node is None else node.name


def height(node):
    """递归求树高：先算左边，再算右边。

    拆成两句是为了保证求值顺序 —— 写成 ``1 + max(height(left),
    height(right))`` 也能跑，但先左后右这件事在代码里看不出来。
    """
    if node is None:
        return 0
    left = height(node.left)
    right = height(node.right)
    return 1 + max(left, right)
