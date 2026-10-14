"""数组递归：分治法求区间最大值。

演示**数组递归** —— 参数是数组下标区间，画面要同时显示数组和调用树。
这是 engine 里 Region 分区的用武之地：上半屏放数组，下半屏放调用树。

跑法：
    python tools/trace.py examples/array_recursion/array_max.py:max_of \\
        --args "3,0,8" --label "[{1},{2})" -o traces/array_max.json
"""

DATA = (7, 2, 9, 4, 1, 8, 3, 6)


def make_args(size=8):
    """给 tools/trace.py 用：数组没法写在命令行上，得由函数生成。"""
    return (list(DATA[:size]), 0, size)


def max_of(a, lo, hi):
    """求 a[lo:hi] 的最大值。区间只剩一个元素就是边界。"""
    if hi - lo == 1:
        return a[lo]
    mid = (lo + hi) // 2
    left = max_of(a, lo, mid)
    right = max_of(a, mid, hi)
    return left if left > right else right


if __name__ == "__main__":
    print(max_of(list(DATA), 0, len(DATA)))
