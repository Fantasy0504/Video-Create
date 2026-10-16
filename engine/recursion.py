"""通用递归模板：真实事件驱动，代码位置必须由制作者显式映射。"""
from manimlib import *
from .scene import AlgoScene
from .tree import TreeSpec
from .stack_state import CallStack
from .panel import curtain, complexity_row, wrapped_rows
from . import theme


class RecursionScene(AlgoScene):
    TRACE = {}
    # 0-based C++ 物理行号；值可以是连续多行的列表。
    # enter / return / leaf_return 对应事件；call 按子调用次序映射。
    CODE_LINES = {}
    # 由制作者按算法填写；不从一次小输入的调用记录猜测渐近复杂度。
    SUMMARY_DATA = None
    PARAM_NAMES = ()
    RECEIVERS = ()  # 子调用结果真实接收变量；留空则只展示返回数据

    def line_for(self, event, nodes, children):
        if "line" in event:
            return event["line"]
        nid = event["id"]
        if event["kind"] == "enter":
            parent = nodes[nid]["parent"]
            if parent is None:
                key = "enter"
            else:
                order = children[parent].index(nid)
                calls = self.CODE_LINES.get("call", [])
                if order >= len(calls):
                    raise ValueError("请为每类子调用映射 call 行号，或给事件显式设置 line")
                return calls[order]
        else:
            key = "return" if children.get(nid) else "leaf_return"
        if key not in self.CODE_LINES:
            raise ValueError(f"缺少 {key} 的代码位置映射；不能从调用记录猜测 C++ 执行行")
        return self.CODE_LINES[key]

    def validate_trace(self):
        nodes = {n["id"]: n for n in self.TRACE["nodes"]}
        children = {int(k): v for k, v in self.TRACE["children"].items()}
        stack, entered = CallStack(), set()
        for event in self.TRACE["events"]:
            node = nodes[event["id"]]
            line = self.line_for(event, nodes, children)
            lines = line if isinstance(line, (list, tuple)) else [line]
            if not lines or any(not isinstance(i, int) or not 0 <= i < len(self.CODE_SOURCE) for i in lines):
                raise ValueError("代码位置映射越界")
            if event["kind"] == "enter":
                if event["id"] in entered:
                    raise ValueError("调用编号重复")
                parent = stack.current.call_id if stack.current else None
                if node["parent"] != parent or node["depth"] != len(stack.frames):
                    raise ValueError("调用关系或深度与真实栈不一致")
                entered.add(event["id"])
                stack.push(event["id"], node["label"])
            elif event["kind"] == "return":
                stack.pop(event["id"])
            else:
                raise ValueError("模板仅处理 enter/return；更细的算法步骤请扩展分镜")
        if stack.current or entered != set(nodes):
            raise ValueError("调用记录不完整")
        return nodes, children

    def validate_summary(self):
        data = self.SUMMARY_DATA
        if not isinstance(data, dict) or not data.get('result'):
            raise ValueError("结尾必须填写本期实际结果 SUMMARY_DATA.result")
        for key in ('time', 'space'):
            row = data.get(key)
            if not isinstance(row, (list, tuple)) or len(row) != 3 or not all(isinstance(v, str) for v in row):
                raise ValueError("结尾 time/space 须填写 [说明标签, 指数底数或空串, 指数或复杂度正文]")
            if not row[0] or not row[2]:
                raise ValueError("结尾必须完整填写时间和空间复杂度，不能留空")

    def show_conclusion(self):
        """参考 3162.mp4：过程压暗，结果、要点、时间和空间依次居中。"""
        self.hint.clear()
        curtain(self, opacity=0.96, run_time=0.70)
        data = self.SUMMARY_DATA
        result_rows = wrapped_rows(data['result'], theme.SIZE_RESULT, 11.8)
        result = VGroup(*result_rows).arrange(DOWN, buff=0.12)
        if result.get_height() > 1.05:
            raise ValueError("结尾结果过长，请在结果页保留简洁输出，详细内容另行展示")
        result.move_to(UP * 1.42)
        self.play(FadeIn(result), run_time=self.CONCLUSION.run_time)
        self.wait(1.2)
        note = data.get('takeaway', '')
        if note:
            note_rows = wrapped_rows(note, theme.SIZE_HEADING, 11.8)
            group = VGroup(*note_rows).arrange(DOWN, buff=0.10)
            if group.get_height() > 0.60:
                raise ValueError("结尾要点过长，请缩短为一句关键说明")
            group.move_to(UP * 0.37)
            self.play(FadeIn(group), run_time=0.50)
            self.wait(1.2)
        rows = VGroup(complexity_row(*data['time'], theme.WHITE),
                      complexity_row(*data['space'], theme.WHITE))
        if rows.get_width() > 11.8:
            raise ValueError("复杂度说明过长，请将详细推导移到前一分镜")
        rows.arrange(DOWN, buff=0.35).move_to(DOWN * 1.10)
        self.play(FadeIn(rows), run_time=0.70)
        self.wait(self.CONCLUSION.hold)

    def build(self):
        self.validate_summary()
        nodes, children = self.validate_trace()
        spec = TreeSpec([(n['id'], n['label'], n['depth'], n['parent'])
                         for n in self.TRACE['nodes']], children, self.TRACE['leaf_order'])
        self.add_title()
        self.add_code()
        self.add_hint()
        panel = self.add_stack()
        tree = self.add_tree(spec)
        call_sites = {}
        for event in self.TRACE['events']:
            nid = event['id']
            node = nodes[nid]
            line = self.line_for(event, nodes, children)
            if event['kind'] == 'enter':
                call_sites[nid] = line
                if panel.stack.current:
                    self.hint.set(event.get('caption', '保存当前栈帧，等待子调用返回'))
                    self.code.focus(self, line)
                    panel.update(state='等待子调用返回')
                    self.wait(self.NORMAL.hold)
                params = {self.PARAM_NAMES[i] if i < len(self.PARAM_NAMES) else f'参数{i+1}': value
                          for i, value in enumerate(node.get('args', []))}
                panel.push(nid, node['label'], params, event.get('locals'))
                if node['parent'] is None:
                    tree.root(run_time=self.NORMAL.run_time)
                else:
                    tree.enter(nid, run_time=self.NORMAL.run_time)
                # 子调用进入后定位函数入口，若有精细语句事件，应在本期分镜中补充。
                self.code.focus(self, event.get('entry_line', self.CODE_LINES.get('enter', line)))
                self.hint.set(event.get('caption', f'进入第{len(panel.stack.frames)}层调用'))
                self.wait(self.NORMAL.hold)
            else:
                has_value = event.get('has_value', event.get('value') is not None)
                value = event.get('value')
                self.code.focus(self, line)
                panel.update(locals=event.get('locals'), state='准备返回')
                self.hint.set(event.get('caption', '当前调用完成，返回直接调用者' if node['parent'] is not None
                                         else '最外层调用完成，活动调用栈即将清空'))
                tree.return_value(nid, f'返回 {value}' if has_value else '完成',
                                  hold=self.FIRST.hold, run_time=self.NORMAL.run_time)
                receiver = event.get('receiver')
                if receiver is None and node['parent'] is not None:
                    order = children[node['parent']].index(nid)
                    if order < len(self.RECEIVERS):
                        receiver = self.RECEIVERS[order]
                panel.pop(nid, value, receiver=receiver, has_value=has_value)
                if panel.stack.current:
                    # 显式恢复父调用暂停的调用语句，细化后的下一语句可由 resume_line 指定。
                    self.code.focus(self, event.get('resume_line', call_sites[nid]))
                    self.hint.set(f'返回第{len(panel.stack.frames)}层，恢复该栈帧继续执行')
                    self.wait(self.NORMAL.hold)
        self.code.focus_now([])
        self.show_conclusion()
