"""复制后填写的通用递归场景模板；也可使用 tools/scaffold.py 生成。

不预设算法、分支数量、变量名或合并方式。未填写前不可渲染。
"""
import sys
from pathlib import Path

_ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'engine').is_dir())
sys.path.insert(0, str(_ROOT))
from engine import RecursionScene


class MyRecursion(RecursionScene):
    TITLE_TEXT = '递归算法'
    TITLE_TAG = ''
    CODE_SOURCE = ()  # 逐行填写真实 C++，仅核心函数
    CODE_LINES = {}   # enter/call/return/leaf_return，或事件内的 line
    PARAM_NAMES = ()  # 与 trace 的 args 顺序一致
    RECEIVERS = ()    # 可选：真实接收变量；不预设 left/right
    TRACE = {}        # nodes/children/leaf_order/events 的真实执行记录

    # 如需补充基本条件判断、循环或撤销操作，覆写 build() 分镜。
    # 当前栈帧接口：
    # panel = self.add_stack()
    # panel.push(call_id, function_name, params={...}, locals={...})
    # panel.update(state='等待子调用返回')
    # panel.pop(call_id, value, receiver='真实变量名')
    # 无返回值：panel.pop(call_id, has_value=False)
    # 详细用法见 docs/recursion-template.md。
