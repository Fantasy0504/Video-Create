"""无图形依赖的栈状态、真实事件和模板生成回归检查。"""
import ast
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


state = load('stack_state_test', 'engine/stack_state.py')
layout = load('text_layout_test', 'engine/text_layout.py')
scaffold = load('scaffold_test', 'tools/scaffold.py')


class StackTests(unittest.TestCase):
    def test_restore_each_frame_and_receive(self):
        stack = state.CallStack()
        stack.push(1, 'f', {'n': 3}, {'result': '未赋值'})
        stack.push(2, 'f', {'n': 2}, {'result': 9})
        self.assertEqual(stack.frames[0].state, '等待子调用返回')
        stack.pop(2, 7, receiver='result')
        self.assertEqual(stack.current.params, {'n': 3})
        self.assertEqual(stack.current.locals, {'result': 7})
        self.assertEqual(stack.current.changed, 'result')
        stack.pop(1, 7)
        self.assertIsNone(stack.current)

    def test_same_function_and_args_are_distinct(self):
        stack = state.CallStack()
        stack.push(1, 'f', {'n': 1})
        stack.push(2, 'f', {'n': 1})
        with self.assertRaises(ValueError):
            stack.pop(1)
        self.assertEqual(len(stack.frames), 2)

    def test_void_does_not_assign_result(self):
        stack = state.CallStack()
        stack.push(1, 'visit')
        stack.push(2, 'visit')
        stack.pop(2, receiver='fake', has_value=False)
        self.assertNotIn('fake', stack.current.locals)
        self.assertEqual(stack.current.received, '子调用完成')

    def test_deep_copy_params(self):
        params = {'path': [1]}
        stack = state.CallStack()
        stack.push(1, 'dfs', params)
        params['path'].append(2)
        self.assertEqual(stack.current.params['path'], [1])

    def test_false_is_a_returned_value(self):
        stack = state.CallStack()
        stack.push(1, 'search')
        stack.push(2, 'search')
        stack.pop(2, False, receiver='found')
        self.assertIs(stack.current.locals['found'], False)


class WrapTests(unittest.TestCase):
    def test_chinese_and_explicit_lines(self):
        lines = layout.wrap_text('当前调用正在等待子调用返回\n参数', 5, len)
        self.assertTrue(all(len(line) <= 5 for line in lines))
        self.assertEqual(''.join(lines), '当前调用正在等待子调用返回参数')

    def test_identifier_is_not_split(self):
        lines = layout.wrap_text('变量 current_value = 3', 14, len)
        self.assertTrue(any('current_value' in line for line in lines))
        self.assertTrue(all(len(line) <= 14 for line in lines))

    def test_oversized_token_fails_instead_of_clipping(self):
        with self.assertRaises(ValueError):
            layout.wrap_text('very_long_identifier', 5, len)


class TraceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 验证事件逻辑时替换图形依赖；不声称由此验证实际渲染布局。
        cls.saved = {k: sys.modules.get(k) for k in
                     ('manimlib', '_recursion_test', '_recursion_test.scene',
                      '_recursion_test.tree', '_recursion_test.stack_state')}
        sys.modules['manimlib'] = types.ModuleType('manimlib')
        pkg = types.ModuleType('_recursion_test')
        pkg.__path__ = []
        sys.modules['_recursion_test'] = pkg
        scene = types.ModuleType('_recursion_test.scene')
        scene.AlgoScene = type('AlgoScene', (), {})
        sys.modules['_recursion_test.scene'] = scene
        tree = types.ModuleType('_recursion_test.tree')
        tree.TreeSpec = type('TreeSpec', (), {'__init__': lambda self, *args: None})
        sys.modules['_recursion_test.tree'] = tree
        sys.modules['_recursion_test.stack_state'] = state
        cls.runtime = load('_recursion_test.recursion', 'engine/recursion.py')

    @classmethod
    def tearDownClass(cls):
        for name, mod in cls.saved.items():
            if mod is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = mod

    def make(self, payload):
        obj = self.runtime.RecursionScene()
        obj.TRACE = payload
        obj.CODE_SOURCE = ('entry', 'call1', 'call2', 'call3', 'ret', 'base')
        obj.CODE_LINES = {'enter': 0, 'call': [1, 2, 3], 'return': 4, 'leaf_return': 5}
        return obj

    def test_all_repository_traces(self):
        for path in (ROOT / 'traces').glob('*.json'):
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text())
                self.make(payload).validate_trace()

    def test_multiway_and_void(self):
        payload = {'nodes': [{'id': 1, 'label': 'root', 'depth': 0, 'parent': None}],
                   'children': {}, 'events': [{'kind': 'enter', 'id': 1}]}
        for i in (2, 3, 4):
            payload['nodes'].append({'id': i, 'label': 'visit', 'depth': 1, 'parent': 1})
            payload['events'] += [{'kind': 'enter', 'id': i}, {'kind': 'return', 'id': i, 'value': None}]
        payload['children'] = {'1': [2, 3, 4]}
        payload['events'].append({'kind': 'return', 'id': 1, 'value': None})
        self.make(payload).validate_trace()

    def test_full_replay_restores_stack_for_all_traces(self):
        class Panel:
            def __init__(self):
                self.stack = state.CallStack()
            def push(self, *args, **kwargs):
                self.stack.push(*args, **kwargs)
            def update(self, **kwargs):
                self.stack.update(**kwargs)
            def pop(self, *args, **kwargs):
                self.stack.pop(*args, **kwargs)
        for path in (ROOT / 'traces').glob('*.json'):
            with self.subTest(path=path.name):
                payload = json.loads(path.read_text())
                obj = self.make(payload)
                panel = Panel()
                returned = []
                noop = lambda *args, **kwargs: None
                obj.code = types.SimpleNamespace(focus=noop, focus_now=noop)
                obj.hint = types.SimpleNamespace(set=noop)
                obj.NORMAL = obj.FIRST = obj.CONCLUSION = types.SimpleNamespace(run_time=0.5, hold=2)
                obj.add_title = obj.add_code = obj.add_hint = obj.wait = noop
                obj.add_stack = lambda: panel
                def on_return(nid, text, **kwargs):
                    self.assertEqual(panel.stack.current.call_id, nid)
                    returned.append(nid)
                obj.add_tree = lambda spec: types.SimpleNamespace(root=noop, enter=noop, return_value=on_return)
                obj.build()
                self.assertFalse(panel.stack.frames)
                self.assertEqual(returned, [e['id'] for e in payload['events'] if e['kind'] == 'return'])

    def test_bad_return_order_rejected(self):
        payload = json.loads((ROOT / 'traces/fib.json').read_text())
        event = next(e for e in payload['events'] if e['kind'] == 'return')
        event['id'] = 1
        with self.assertRaises(ValueError):
            self.make(payload).validate_trace()

    def test_missing_mapping_and_out_of_range_rejected(self):
        payload = json.loads((ROOT / 'traces/fib.json').read_text())
        obj = self.make(payload)
        obj.CODE_LINES = {}
        with self.assertRaises(ValueError):
            obj.validate_trace()
        obj.CODE_LINES = {'enter': 100}
        with self.assertRaises(ValueError):
            obj.validate_trace()

    def test_generated_sources_all_parse_without_fake_math(self):
        for path in (ROOT / 'traces').glob('*.json'):
            payload = json.loads(path.read_text())
            source = scaffold.build_source(payload, 'Demo', '标题', '', ['void f() {}'],
                                           path.name, {'enter': 0, 'call': [0, 0, 0], 'return': 0, 'leaf_return': 0})
            ast.parse(source)
            self.assertNotIn('left + right', source)
            self.assertIn('RecursionScene', source)

    def test_generator_requires_real_code_and_mapping(self):
        with self.assertRaises(ValueError):
            scaffold.build_source({}, 'Demo', '', '', None, 'trace.json')
        with self.assertRaises(ValueError):
            scaffold.build_source({}, 'Demo', '', '', ['void f() {}'], 'trace.json')


class CodeFocusTests(unittest.TestCase):
    def test_focus_changes_text_restores_old_and_reuses_objects(self):
        saved = {k: sys.modules.get(k) for k in
                 ('manimlib', '_panel_test', '_panel_test.theme', '_panel_test.panel',
                  '_panel_test.text_layout', '_panel_test.stack_state')}
        try:
            sys.modules['manimlib'] = types.ModuleType('manimlib')
            pkg = types.ModuleType('_panel_test')
            pkg.__path__ = []
            sys.modules['_panel_test'] = pkg
            theme = load('_panel_test.theme', 'engine/theme.py')
            pkg.theme = theme
            sys.modules['_panel_test.text_layout'] = layout
            sys.modules['_panel_test.stack_state'] = state
            panel = load('_panel_test.panel', 'engine/panel.py')
            class Mob:
                @property
                def animate(self):
                    return self
                def set_color(self, color):
                    self.color = color
                    return self
                def set_stroke(self, **kw):
                    self.opacity = kw['opacity']
                    return self
            obj = panel.CodePanel.__new__(panel.CodePanel)
            obj._names = {'first': 0, 'next': 1}
            obj._focused = set()
            obj.lines = [Mob(), Mob(), Mob()]
            obj.cursors = [Mob(), Mob(), Mob()]
            identities = [id(m) for m in obj.lines]
            obj.focus_now('first')
            self.assertEqual(obj.lines[0].color, theme.BLUE)
            scene = types.SimpleNamespace(play=lambda *args, **kw: None)
            obj.focus(scene, [1, 2])
            self.assertEqual([m.color for m in obj.lines], [theme.WHITE, theme.BLUE, theme.BLUE])
            obj.focus_now([])
            self.assertTrue(all(m.color == theme.WHITE for m in obj.lines))
            self.assertEqual(identities, [id(m) for m in obj.lines])
            self.assertAlmostEqual(theme.SUBTITLE_HEIGHT * 135, 46)
            self.assertEqual(panel.HintLine.__init__.__kwdefaults__['center'], (0.0, -3.44))
        finally:
            for name, mod in saved.items():
                if mod is None:
                    sys.modules.pop(name, None)
                else:
                    sys.modules[name] = mod


if __name__ == '__main__':
    unittest.main()
