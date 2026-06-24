"""诊断三 key and 表达式"""
from agent_core.multi_agent.relationship import _parse_precondition
import re

# 复现三 key 场景
expr = "facts.has('a') and facts.has('b') and facts.has('c')"
fn = _parse_precondition(expr)
print("expr:", expr)
print("all in {a,b,c}:", fn({"facts": {"a": 1, "b": 2, "c": 3}}))
print("only a,b:", fn({"facts": {"a": 1, "b": 2}}))
print("only b,c:", fn({"facts": {"b": 2, "c": 3}}))

# 看 re.findall 抓到几个 key
keys = re.findall(r"facts\.has\(['\"]([^'\"]+)['\"]\)", expr)
print("re.findall keys:", keys)

# 看一下两 key 表达式
expr2 = "facts.has('a') and facts.has('b')"
fn2 = _parse_precondition(expr2)
print("2-key all:", fn2({"facts": {"a": 1, "b": 2}}))
print("2-key only a:", fn2({"facts": {"a": 1}}))
