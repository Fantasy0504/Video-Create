"""'非记忆化递归'；从 'fib.json' 自动生成。

模板只复现调用/返回边界；判断、循环、局部变量更新、回溯撤销等语句
请在本期分镜中细化，或在事件上补充 line/entry_line/resume_line/locals。
trace 不记录的局部值不得凭空推断。
"""
import sys
from pathlib import Path

_ROOT = next(p for p in Path(__file__).resolve().parents if (p / "engine").is_dir())
sys.path.insert(0, str(_ROOT))
from engine import RecursionScene


class FibonacciGen(RecursionScene):
    TITLE_TEXT = '非记忆化递归'
    TITLE_TAG = 'fib(5)'
    CODE_SOURCE = ('int fib(int n) {', '    if (n <= 1) return n;', '    int left = fib(n - 1);', '    int right = fib(n - 2);', '    return left + right;', '}')
    CODE_LINES = {'enter': 0, 'call': [2, 3], 'return': 4, 'leaf_return': 1}
    PARAM_NAMES = ('n',)
    RECEIVERS = ('left', 'right')
    SUMMARY_DATA = {'result': 'fib(5) = 5', 'takeaway': '相同子问题，会重复计算', 'time': ['时间上界  ', '2', 'n'], 'space': ['辅助空间（调用栈）  ', '', 'n']}
    TRACE = {'entry': {'func': 'fib', 'args': [5]},
 'nodes': [{'id': 1, 'label': 'fib(5)', 'depth': 0, 'parent': None, 'args': [5], 'result': 5},
           {'id': 2, 'label': 'fib(4)', 'depth': 1, 'parent': 1, 'args': [4], 'result': 3},
           {'id': 3, 'label': 'fib(3)', 'depth': 2, 'parent': 2, 'args': [3], 'result': 2},
           {'id': 4, 'label': 'fib(2)', 'depth': 3, 'parent': 3, 'args': [2], 'result': 1},
           {'id': 5, 'label': 'fib(1)', 'depth': 4, 'parent': 4, 'args': [1], 'result': 1},
           {'id': 6, 'label': 'fib(0)', 'depth': 4, 'parent': 4, 'args': [0], 'result': 0},
           {'id': 7, 'label': 'fib(1)', 'depth': 3, 'parent': 3, 'args': [1], 'result': 1},
           {'id': 8, 'label': 'fib(2)', 'depth': 2, 'parent': 2, 'args': [2], 'result': 1},
           {'id': 9, 'label': 'fib(1)', 'depth': 3, 'parent': 8, 'args': [1], 'result': 1},
           {'id': 10, 'label': 'fib(0)', 'depth': 3, 'parent': 8, 'args': [0], 'result': 0},
           {'id': 11, 'label': 'fib(3)', 'depth': 1, 'parent': 1, 'args': [3], 'result': 2},
           {'id': 12, 'label': 'fib(2)', 'depth': 2, 'parent': 11, 'args': [2], 'result': 1},
           {'id': 13, 'label': 'fib(1)', 'depth': 3, 'parent': 12, 'args': [1], 'result': 1},
           {'id': 14, 'label': 'fib(0)', 'depth': 3, 'parent': 12, 'args': [0], 'result': 0},
           {'id': 15, 'label': 'fib(1)', 'depth': 2, 'parent': 11, 'args': [1], 'result': 1}],
 'events': [{'kind': 'enter', 'id': 1},
            {'kind': 'enter', 'id': 2},
            {'kind': 'enter', 'id': 3},
            {'kind': 'enter', 'id': 4},
            {'kind': 'enter', 'id': 5},
            {'kind': 'return', 'id': 5, 'value': 1},
            {'kind': 'enter', 'id': 6},
            {'kind': 'return', 'id': 6, 'value': 0},
            {'kind': 'return', 'id': 4, 'value': 1},
            {'kind': 'enter', 'id': 7},
            {'kind': 'return', 'id': 7, 'value': 1},
            {'kind': 'return', 'id': 3, 'value': 2},
            {'kind': 'enter', 'id': 8},
            {'kind': 'enter', 'id': 9},
            {'kind': 'return', 'id': 9, 'value': 1},
            {'kind': 'enter', 'id': 10},
            {'kind': 'return', 'id': 10, 'value': 0},
            {'kind': 'return', 'id': 8, 'value': 1},
            {'kind': 'return', 'id': 2, 'value': 3},
            {'kind': 'enter', 'id': 11},
            {'kind': 'enter', 'id': 12},
            {'kind': 'enter', 'id': 13},
            {'kind': 'return', 'id': 13, 'value': 1},
            {'kind': 'enter', 'id': 14},
            {'kind': 'return', 'id': 14, 'value': 0},
            {'kind': 'return', 'id': 12, 'value': 1},
            {'kind': 'enter', 'id': 15},
            {'kind': 'return', 'id': 15, 'value': 1},
            {'kind': 'return', 'id': 11, 'value': 2},
            {'kind': 'return', 'id': 1, 'value': 5}],
 'children': {'1': [2, 11],
              '2': [3, 8],
              '3': [4, 7],
              '4': [5, 6],
              '8': [9, 10],
              '11': [12, 15],
              '12': [13, 14]},
 'leaf_order': [5, 6, 7, 9, 10, 13, 14, 15],
 'summary': {'call_count': 15,
             'base_count': 8,
             'max_depth': 5,
             'label_counts': {'fib(5)': 1,
                              'fib(4)': 1,
                              'fib(3)': 2,
                              'fib(2)': 3,
                              'fib(1)': 5,
                              'fib(0)': 3},
             'enter_return_alternates': True}}
