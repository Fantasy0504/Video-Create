"""复制后填写的通用递归场景模板；也可使用 tools/scaffold.py 生成。

不预设算法、分支数量、变量名或合并方式。未填写前不可渲染。
"""
import sys
from pathlib import Path

_ROOT = next(p for p in Path(__file__).resolve().parents if (p / 'engine').is_dir())
sys.path.insert(0, str(_ROOT))
from engine import RecursionScene, recursion_arrow


class MyRecursion(RecursionScene):
    TITLE_TEXT = '递归算法'
    TITLE_TAG = ''
    CODE_SOURCE = ()  # 逐行填写真实 C++，仅核心函数
    CODE_LINES = {}   # enter/call/return/leaf_return，或事件内的 line
    PARAM_NAMES = ()  # 与 trace 的 args 顺序一致
    RECEIVERS = ()    # 可选：真实接收变量；不预设 left/right
    # 必填：使用实际结果、算法渐近时间与辅助空间；不是渲染程序的开销。
    SUMMARY_DATA = None
    # 结构：{'result': '本期实际结果', 'takeaway': '一句关键结论',
    #        'time': ['时间复杂度', '', '按算法填写'],
    #        'space': ['辅助空间', '', '按算法填写']}
    # 指数公式通过 time/space 的后两项拆开排版，不能用普通同行文字伪造上标。
    TRACE = {}        # nodes/children/leaf_order/events 的真实执行记录

    # 如需补充基本条件判断、循环或撤销操作，覆写 build() 分镜。
    # 当前栈帧接口：
    # panel = self.add_stack()
    # panel.push(call_id, function_name, params={...}, locals={...})
    # panel.update(state='等待子调用返回')
    # panel.pop(call_id, value, receiver='真实变量名')
    # 无返回值：panel.pop(call_id, has_value=False)
    # TreeView 已默认使用动态细箭头：蓝色指向子调用，绿色指回直接调用者。
    # 手写栈/调用记录可复用统一样式，start/end 应位于框外且不穿过文字：
    # call = recursion_arrow(parent_border, child_border)
    # self.play(GrowArrow(call), run_time=0.65)
    # ret = recursion_arrow(child_border, parent_border, returning=True)
    # self.play(FadeOut(call), run_time=0.2)  # 先移除旧箭头，避免方向重叠
    # self.play(GrowArrow(ret), run_time=0.65)
    # GrowArrow/FadeOut 由 from manimlib import GrowArrow, FadeOut 导入。
    # 不要用 stroke_width 调整实心箭身；统一参数见 engine/flow.py。
    # 详细用法见 docs/recursion-template.md。
