"""链表反转：单支递归 + 回溯时改指针。

演示**链表递归**里最典型的一类 —— 先递归到链尾，回溯时逐个把
``next`` 指向前一个节点。所以箭头方向会变，画面要能跟着改。

跑法：
    python tools/trace.py examples/linked_list_reverse/reverse.py:reverse \\
        --input-fn make_list --args 4 --label-fn node_repr \\
        -o traces/list_reverse.json
"""


class Node:
    def __init__(self, value, nxt=None):
        self.value = value
        self.next = nxt

    def __repr__(self):
        return f"Node({self.value})"


def make_list(n):
    """造一条 1→2→…→n 的链表。"""
    head = None
    for value in range(n, 0, -1):
        head = Node(value, head)
    return head


def node_repr(node):
    """节点标签：从当前节点到头节点这一串值，反转过程中能看出链的走向。"""
    values, seen, cur = [], set(), node
    while cur is not None and id(cur) not in seen:
        seen.add(id(cur))
        values.append(cur.value)
        cur = cur.next
    return "→".join(map(str, values)) if values else "nil"


def reverse(head):
    """递归反转：先反转后面的，再把自己接到新链尾。"""
    if head is None or head.next is None:
        return head
    rest = reverse(head.next)
    head.next.next = head
    head.next = None
    return rest


if __name__ == "__main__":
    print(node_repr(reverse(make_list(4))))
