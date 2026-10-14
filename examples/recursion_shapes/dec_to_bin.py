"""十进制转二进制：单支递归 + 字符串拼接。

演示**返回值不是数字**的递归 —— 标签是每一层的商，返回值是逐位拼出来的串。
先递归到底（拿到最高位），再一层层往回拼，所以回溯阶段的颜色变化是重点。

跑法：
    python tools/trace.py examples/recursion_shapes/dec_to_bin.py:dec2bin \\
        --args 13 --label "dec2bin({0})" -o traces/dec_to_bin.json
"""


def dec2bin(n):
    """把非负整数转成二进制字符串。"""
    if n < 2:
        return str(n)
    return dec2bin(n // 2) + str(n % 2)


if __name__ == "__main__":
    for value in (0, 1, 6, 13, 40):
        print(value, "->", dec2bin(value))
