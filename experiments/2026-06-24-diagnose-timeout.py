import sys
sys.path.insert(0, ".")
from agent_core.multi_agent.relationship import Blackboard, Command, ControlShell, KnowledgeSource, RelationshipEngine, _parse_precondition

def loop_a(bb, eng):
    return Command(update={"facts": {"result::a": "x"}}, terminate=False)

def loop_b(bb, eng):
    return Command(update={"facts": {"result::b": "x"}}, terminate=False)

ks_a = KnowledgeSource(
    name="a", role="a",
    preconditions=_parse_precondition("facts.has('result::b')"),
    action=loop_a,
)
ks_b = KnowledgeSource(
    name="b", role="b",
    preconditions=_parse_precondition("facts.has('result::a')"),
    action=loop_b,
)
engine = RelationshipEngine(client=None, model="test", agents=[ks_a, ks_b])
shell = ControlShell(Blackboard(), engine.agents, engine, max_steps=4)
bb = shell.run()
print("status:", repr(bb.status))
print("facts keys:", list(bb.facts.keys()))
print("current_step:", bb.current_step)
print("activated:", shell._activated)
