"""独立于 Manim 的真实活动调用栈；历史帧不留在活动栈内。"""
from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class CallFrame:
    call_id: object
    name: str
    params: dict = field(default_factory=dict)
    locals: dict = field(default_factory=dict)
    state: str = "执行中"
    received: str = ""
    changed: str = ""


class CallStack:
    def __init__(self):
        self.frames = []

    @property
    def current(self):
        return self.frames[-1] if self.frames else None

    def push(self, call_id, name, params=None, locals=None):
        if any(f.call_id == call_id for f in self.frames):
            raise ValueError("不同调用必须使用独立编号")
        if self.current:
            self.current.state = "等待子调用返回"
            self.current.changed = ""
        frame = CallFrame(call_id, name, deepcopy(params or {}), deepcopy(locals or {}))
        self.frames.append(frame)
        return frame

    def update(self, *, locals=None, state=None, changed=""):
        if not self.current:
            raise ValueError("当前没有活动栈帧")
        if locals is not None:
            self.current.locals.update(deepcopy(locals))
        if state is not None:
            self.current.state = state
        self.current.changed = changed

    def pop(self, call_id, value=None, *, receiver=None, has_value=True):
        if not self.current or self.current.call_id != call_id:
            raise ValueError("只能从真实栈顶返回，不能越层出栈")
        finished = self.frames.pop()
        if self.current:
            self.current.state = "恢复执行"
            self.current.received = (f"子调用返回：{value}" if has_value else "子调用完成")
            self.current.changed = ""
            if receiver is not None and has_value:
                self.current.locals[receiver] = deepcopy(value)
                self.current.changed = receiver
        return finished
