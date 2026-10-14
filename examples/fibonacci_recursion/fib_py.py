"""斐波那契的 Python 等价版本。

只用来喂给 ``tools/trace.py`` 跑出调用树 —— 展示给观众看的仍然是 C++
（``scene.py`` 里的 ``CODE_SOURCE``），这份只是让工具能执行、能记录。

保持与 C++ 版本**逐句对应**：先算左子调用、再算右子调用，
写成一个表达式的写法不能保证左侧先求值。
"""


def fib(n):
    if n <= 1:
        return n
    left = fib(n - 1)
    right = fib(n - 2)
    return left + right


if __name__ == "__main__":
    print(fib(5))
