"""链表递归：求链表长度。

演示**单支递归** —— 每次调用只有一个子调用，整条调用链落在同一条竖线上。
入口参数是个对象，所以要用 ``--input-fn`` 生成、用 ``--label-fn`` 起标签。

跑法：
    python tools/trace.py examples/recursion_shapes/linked_list.py:length \\
        --input-fn make_list --args 4 --label-fn node_repr -o traces/linked_list.json
"""


class Node:
    def __init__(self, value, nxt=None):
        self.value = value
        self.next = nxt

    def __repr__(self):
        return f"Node({self.value})"


def make_list(n):
    """造一条 n→…→1 的链表，返回头节点。"""
    head = None
    for value in range(n, 0, -1):
        head = Node(value, head)
    return head


def node_repr(node):
    """把"从当前节点到链尾"显示成一串值 —— 这些就是节点标签。"""
    if node is None:
        return "[]"
    values, cur = [], node
    while cur is not None:
        values.append(cur.value)
        cur = cur.next
    return "[" + ",".join(map(str, values)) + "]"


def length(node):
    """递归求长度：每个调用只有一个子调用。"""
    if node is None:
        return 0
    return 1 + length(node.next)
