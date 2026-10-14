"""带 static 变量的递归：跨调用累加的调用计数器。

演示递归里最容易被误解的一类 —— C 的 ``static`` 局部变量**只有一份**，
不会每次进入函数都重新初始化。所以：

* 左边那栏「当前调用的局部变量」每次都换（每次调用都有自己的 n、left、right）
* 下面那栏「static」**始终只有一行**，值一直累加

这两栏放在一起，对比就是这一期的全部意义。

跑法：
    python tools/trace.py examples/static_variable/fib_static.py:fib \\
        --args 4 --label "fib({0})" -o traces/fib_static.json
"""


def fib(n, _counter=None):
    """为了能被 trace 跑，把 static 计数器做成模块级的一份。

    C 里写的是 ``static int calls = 0; calls++;`` —— Python 没有函数级
    static，用模块级变量等价表达：**所有调用共享同一个**。
    """
    if _counter is None:
        _counter = CALLS
    _counter["calls"] += 1
    if n <= 1:
        return n
    left = fib(n - 1)
    right = fib(n - 2)
    return left + right


CALLS = {"calls": 0}


if __name__ == "__main__":
    print(fib(4), CALLS)
