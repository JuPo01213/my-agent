"""临时脚本：验证 core.run_loop 的 return_trace 与解耦性。"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent_core.core.react_agent import run_loop
import agent_core.core.react_agent as core_mod
import agent_core.multi_agent.relationship as rel_mod


# 1. 核心层不应知道 frontend 存在
src = open(core_mod.__file__, 'r', encoding='utf-8').read()
print('=== 1. 解耦检查 ===')
print('core/react_agent.py 引用 frontend?', 'frontend' in src)
print('core/react_agent.py 引用 EventBus?', 'EventBus' in src)
print('core/react_agent.py 引用 make_*?', 'make_' in src)
print()


# 2. return_trace=False (原版行为)
class _Msg:
    content = 'hi'
    tool_calls = None
    reasoning_content = None


class _Choice:
    message = _Msg()


class _Resp:
    choices = [_Choice()]


class _Completions:
    def create(self, **kwargs):
        return _Resp()


class _Chat:
    completions = _Completions()


class _FakeClient:
    chat = _Chat()


fc = _FakeClient()
text = run_loop('test', fc, 'm', max_steps=3, return_trace=False)
print('=== 2. return_trace=False（原版行为）===')
print('  返回类型:', type(text).__name__, '值:', repr(text))
print()


# 3. return_trace=True
text2, tr = run_loop('test', fc, 'm', max_steps=3, return_trace=True)
print('=== 3. return_trace=True ===')
print('  返回类型:', type(text2).__name__, ' final:', repr(text2))
print('  trace 长度:', len(tr))
print('  trace kinds:', [t['kind'] for t in tr])
print('  trace[0] 样例:', tr[0])
print()


# 4. 验证 default (不传 return_trace) 也是 str（向后兼容）
text3 = run_loop('test', fc, 'm', max_steps=3)
print('=== 4. 默认参数（向后兼容）===')
print('  返回类型:', type(text3).__name__, '值:', repr(text3))
