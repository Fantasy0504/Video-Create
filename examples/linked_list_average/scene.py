"""递归求链表平均值：按真实语句顺序展示调用、赋值、恢复和返回。"""
from pathlib import Path
from fractions import Fraction
import sys
import json
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'engine').is_dir())
sys.path.insert(0, str(ROOT))
from manimlib import *
from engine import AlgoScene, LinkedListView, curtain, complexity_row, theme, recursion_arrow
from engine.stack_state import CallStack


class LinkedListAverage(AlgoScene):
    TITLE_TEXT = '例6  递归求链表平均值'
    CODE_CENTER = (-4.05, 1.35)
    CODE_SOURCE = (
        'double GetAverage(LinkList p, int n) {',
        '  if (!p->next) return p->data;',
        '  else {',
        '    double ave =',
        '        GetAverage(p->next, n-1);',
        '    return (ave*(n-1)+p->data)/n;',
        '  }',
        '}',
    )

    def txt(self, s, size=23, color=None):
        return Text(s, font=theme.pick_font(s), font_size=size).set_color(color or theme.WHITE)

    def replace(self, attr, new, time=0.35):
        old = getattr(self, attr, None)
        if old is not None:
            self.play(FadeOut(old), run_time=time/2)
            self.remove(old)
        setattr(self, attr, new)
        self.play(FadeIn(new), run_time=time/2)

    def caption(self, text, hold=2.3):
        self.hint.set(text)
        self.wait(hold)

    def build(self):
        self.calls = CallStack()
        self.records = []
        self.events = []
        self.call_edges = {}
        self.add_title()
        self.add_code(size=23, max_width=5.7, line_buff=0.14)
        self.add_hint()
        self.list = LinkedListView(self, [1,2,3], center=(2.4,2.05),
                                   node_w=1.0, node_h=0.65, gap=0.75, show_index=False)
        for link in self.list.arrows:
            link.become(recursion_arrow(link.get_start(),link.get_end()).set_color(theme.WHITE))
        self.list.appear()
        end = self.list.boxes[-1].get_right()
        arrow = recursion_arrow(end, end+RIGHT*0.65).set_color(theme.WHITE)
        null = self.txt('NULL', 20).next_to(arrow, RIGHT, buff=0.08)
        self.play(GrowArrow(arrow), FadeIn(null), run_time=0.5)
        self.legend = self.txt('蓝色箭头：向下调用    绿色箭头：向上返回', 20)
        self.legend.move_to([2.55,3.48,0])
        self.history_title = self.txt('调用记录（绿色条目已返回）', 22)
        self.history_title.move_to([2.7,0.8,0])
        self.play(FadeIn(self.legend), FadeIn(self.history_title), run_time=0.5)
        self.caption('链表为 1 → 2 → 3；p 指向首结点，n = 3', 3)
        self.caption('n 表示从当前 p 开始，剩余链表的结点数', 3)
        answer = self.solve(0, 3)
        assert answer == 2 and not self.calls.frames
        assert [r['result'] for r in self.records] == [2, 2.5, 3]
        self.code.focus(self,5)
        self.caption('根调用返回 2，活动调用栈已清空', 3)
        out=Path(__file__).parent/'execution_trace.json'
        out.write_text(json.dumps(self.events, ensure_ascii=False, indent=2), encoding='utf-8')
        self.conclusion()

    def stage(self, text, green=False):
        new=self.txt(text, 24, theme.GREEN if green else theme.BLUE)
        new.move_to([2.7,2.85,0])
        self.replace('stage_mob', new)

    def pointer(self, i):
        box=self.list.boxes[i]
        label=self.txt('p',23,theme.BLUE).move_to(box.get_bottom()+DOWN*0.5)
        arrow=recursion_arrow(label.get_top(),box.get_bottom(),buff=0.03)
        self.replace('pointer_mob',VGroup(arrow,label))
        self.play(*[b.animate.set_stroke(theme.BLUE if j==i else
                   theme.GREEN if any(r['idx']==j and r['done'] for r in self.records)
                   else theme.WHITE, width=2.2) for j,b in enumerate(self.list.boxes)], run_time=0.3)

    def current(self):
        f=self.calls.current
        if f is None:
            rows=[self.txt('活动调用栈已清空',24,theme.GREEN)]
        else:
            ave=f.locals.get('ave','未声明')
            rows=[self.txt(f'当前调用  第 {len(self.calls.frames)} 层',24,theme.BLUE),
                  self.txt(f"p->data = {f.params['data']}     n = {f.params['n']}",22),
                  self.txt(f'ave = {ave}',22, theme.GREEN if isinstance(ave,(int,float)) else theme.WHITE),
                  self.txt(f.state,21)]
        block=VGroup(*rows).arrange(DOWN,aligned_edge=LEFT,buff=0.18)
        block.shift(np.array([-6.5,-0.65,0])-block.get_corner(UL))
        self.replace('current_mob',block)

    def history(self):
        rows=[]
        active_id=self.calls.current.call_id if self.calls.current else None
        for r in self.records:
            color=theme.GREEN if r['done'] else theme.BLUE
            status=f"返回 {r['result']:g}" if r['done'] else (
                f"ave = {r['ave']:g}" if r['ave'] is not None else 'ave 等待赋值' if r['n']>1 else '直接返回')
            label=self.txt(f"{r['id']:02d}   p → {r['idx']+1}    n = {r['n']}    {status}",21,color)
            box=RoundedRectangle(width=6.65,height=0.58,corner_radius=0.04)
            box.set_fill(theme.BG,opacity=1).set_stroke(color,width=1.4)
            label.move_to(box)
            row=VGroup(box,label).move_to([2.65,0.15-(r['id']-1)*0.8,0])
            rows.append(row)
        self.replace('history_mob',VGroup(*rows))

    def flow_arrow(self, child_id, *, returning=False, value=None):
        """调用框右侧独立通道：蓝色向下调用，绿色沿原关系向上返回。"""
        parent_y = 0.15 - (child_id-2)*0.8
        child_y = parent_y - 0.8
        edge_x, lane_x = 5.975, 6.40
        color = theme.GREEN if returning else theme.BLUE
        start_y, end_y = (child_y, parent_y) if returning else (parent_y, child_y)
        if returning:
            old = self.call_edges.pop(child_id)
            self.play(FadeOut(old), run_time=0.2)
            self.remove(old)
        source = Line([edge_x,start_y,0], [lane_x,start_y,0]).set_stroke(color,width=1.6)
        arrow = recursion_arrow([lane_x,start_y,0], [lane_x,end_y,0], returning=returning)
        target = Line([lane_x,end_y,0], [edge_x,end_y,0]).set_stroke(color,width=1.6)
        self.play(ShowCreation(source),run_time=0.18)
        self.play(GrowArrow(arrow),run_time=0.75,rate_func=linear)
        self.play(ShowCreation(target),run_time=0.18)
        edge = VGroup(source,arrow,target)
        self.call_edges[child_id] = edge
        marker = Dot([lane_x,start_y,0], radius=0.035).set_color(color)
        self.add(marker)
        if returning:
            tag=self.txt(f'返回 {float(value):g}',18,theme.GREEN)
            tag.move_to([5.32,(start_y+end_y)/2,0])
            self.play(FadeIn(tag),run_time=0.2)
        self.play(marker.animate.move_to([lane_x,end_y,0]),run_time=0.65,rate_func=linear)
        self.remove(marker)
        self.wait(0.55)
        if returning:
            self.play(FadeOut(tag),run_time=0.2)
        self.events.append(dict(event='arrow_return' if returning else 'arrow_call',
                                source=child_id if returning else child_id-1,
                                target=child_id-1 if returning else child_id,
                                value=float(value) if returning else None,
                                direction='up' if returning else 'down'))

    def equation(self, text):
        new=self.txt(text,27,theme.GREEN)
        new.move_to([2.6,-2.25,0])
        self.replace('equation_mob',new)

    def solve(self,i,n):
        ident=i+1
        r=dict(id=ident,idx=i,n=n,ave=None,done=False,result=None)
        self.records.append(r)
        self.calls.push(ident,'GetAverage',params={'data':i+1,'n':n})
        self.events.append(dict(event='enter',id=ident,data=i+1,n=n))
        self.history()
        if i:
            self.flow_arrow(ident)
        self.stage('01  递归进入' if n>1 else '02  到达链尾')
        self.code.focus(self,0)
        self.pointer(i)
        self.current()
        self.caption(f'进入第 {ident} 层：p 指向 {i+1}，这一层的 n = {n}')
        self.code.focus(self,1)
        if n==1:
            self.calls.update(state='尾结点：直接返回 p->data')
            self.current()
            self.equation('return 3')
            self.caption('p->next 为空，直接返回 3；本层不声明 ave',3)
            result=Fraction(i+1)
        else:
            self.caption('当前结点不是尾结点，继续递归处理后面的链表')
            self.code.focus(self,[3,4])
            self.calls.update(locals={'ave':'等待子调用返回'},state='等待递归结果，保留本层 p 和 n')
            self.current(); self.history()
            self.caption(f'将 p->next 和 n-1 = {n-1} 传入下一层',2.8)
            child=self.solve(i+1,n-1)
            self.stage('03  逐层返回',True)
            self.pointer(i)
            self.code.focus(self,[3,4])
            self.calls.update(locals={'ave':float(child)},state='子调用完成，ave 赋值完毕',changed='ave')
            r['ave']=float(child)
            self.events.append(dict(event='assign',id=ident,ave=float(child),data=i+1,n=n))
            self.current(); self.history()
            self.equation(f'ave = {float(child):g}')
            self.caption(f'恢复第 {ident} 层：ave = {float(child):g}，p 仍指向 {i+1}，n 仍是 {n}',3.2)
            self.code.focus(self,5)
            self.equation(f'{float(child):g} × {n-1} = {float(child*(n-1)):g}')
            self.caption(f'后面 {n-1} 个结点的平均值乘以个数，得到它们的总和',3)
            result=(child*(n-1)+(i+1))/n
            self.equation(f'({float(child):g} × {n-1} + {i+1}) / {n} = {float(result):g}')
            self.caption(f'加上当前数据 {i+1}，再除以本层结点数 {n}，返回 {float(result):g}',3.2)
        r['done']=True; r['result']=float(result)
        self.list.mark(i)
        self.history()
        self.caption(f'第 {ident} 层返回 {float(result):g}' + ('，交回调用者' if i else '，整条链表计算完成'),2.3)
        if i:
            self.flow_arrow(ident, returning=True, value=result)
        self.calls.pop(ident,float(result),receiver='ave' if i else None)
        self.events.append(dict(event='return',id=ident,value=float(result)))
        self.current()
        return result

    def conclusion(self):
        curtain(self,opacity=0.98)
        result=self.txt('链表平均值 = 2',48).move_to([0,1.8,0])
        check=self.txt('(1 + 2 + 3) / 3 = 2',29,theme.GREEN).move_to([0,0.85,0])
        takeaway=self.txt('先求后面链表的平均值，再还原总和并计入当前结点',25)
        takeaway.move_to([0,-0.05,0])
        time=complexity_row('时间复杂度','', 'n',theme.RED)
        space=complexity_row('辅助空间（调用栈）','', 'n',theme.GREEN)
        time[1].set_color(theme.RED); space[1].set_color(theme.GREEN)
        costs=VGroup(time,space).arrange(DOWN,buff=0.35).move_to([0,-1.5,0])
        assumption=self.txt('前提：p 非空，n 等于从 p 开始的实际结点数',21)
        assumption.move_to([0,-2.7,0])
        for mob in [result,check,takeaway,costs,assumption]:
            self.play(FadeIn(mob),run_time=0.65)
            self.wait(0.8)
        self.wait(4)
