# 代码走读 — relationship.py（关系驱动多 Agent 引擎）

## 当前状态
**mock 模式**：本走读完全基于静态代码阅读，未连接真实 LLM。运行时演示请用 `agent_core/demos/relationship_demo.py`。

## 入口
用户问题："从零讲清楚 RelationshipEngine 怎么把 3 个 KnowledgeSource 串起来协作"

## 走读路径（6 步）

---

## 第 1 步：构造 KnowledgeSource（定义 Agent）

**目的**：注册 3 个 Agent 专家到内存，**不执行任何 LLM 调用**。

**位置**：[relationship.py L175-196](file:///c:\Users\Administrator\Desktop\my-agent/agent_core/multi_agent/relationship.py#L175-L196)（KnowledgeSource 构造函数）

**代码**：

```python
@dataclass
class KnowledgeSource:
    name: str
    role: str
    goal: str
    backstory: str
    tools: list[str] = field(default_factory=list)
    preconditions: Callable = _parse_precondition("True")
    system_prompt: str = ""
    max_tokens: int = 1024
    action: Callable = _default_action    # ← 默认 action 函数
```

**demo 里的调用**（[relationship_demo.py L145-170](file:///c:\Users\Administrator\Desktop\my-agent/agent_core/demos/relationship_demo.py#L145-L170)）：

```python
researcher = KnowledgeSource(
    name="researcher", tools=["search"],
    role="高级研究员", goal="收集关于 {user_query} 的最新信息",
    backstory="清华 AI 实验室研究员",
)
analyst = KnowledgeSource(
    name="analyst", tools=["calculator"],
    role="数据分析师", goal="分析研究数据",
    preconditions=_parse_precondition("facts.has('result::researcher')"),  # ← 关键
)
writer = KnowledgeSource(
    name="writer", tools=[],
    role="技术作家", goal="写出结构化报告",
    preconditions=_parse_precondition("facts.has('result::analyst')"),     # ← 关键
)
```

**关键点**：
- `preconditions` 决定了**谁在什么时候被激活**——这是协作顺序的声明
- `action` 默认指向 `_default_action`（可被覆盖为自定义函数）
- 第 1 步执行完，内存里只有 3 个**配置对象**，没 LLM 调用

---

## 第 2 步：装进 RelationshipEngine

**目的**：把 3 个 KS 装入引擎，准备启动 OODA 循环。

**位置**：[relationship_demo.py L170-185](file:///c:\Users\Administrator\Desktop\my-agent/agent_core/demos/relationship_demo.py#L170-L185)

**代码**：

```python
engine = RelationshipEngine(
    client=client,
    model="mock-model",
    agents=[researcher, analyst, writer],
    max_steps=10,
)
blackboard = engine.run(
    user_query="调研 2024 年 LLM Agent 领域的最新进展",
    strategy="priority",
    metadata={"priority": {"researcher": 1, "analyst": 2, "writer": 3}},
)
```

**engine.run() 内部**（[relationship.py L434-466](file:///c:\Users\Administrator\Desktop\my-agent/agent_core/multi_agent/relationship.py#L434-L466)）：

```python
def run(self, user_query, strategy, metadata, done_when) -> Blackboard:
    # 1. 构造黑板
    blackboard = Blackboard(metadata={"user_query": user_query, **(metadata or {})})
    # 2. 构造 ControlShell（调度器）
    shell = ControlShell(blackboard, sources=self.agents, engine=self, ...)
    # 3. 启动 OODA 循环
    return shell.run()
```

**第 2 步执行后内存状态**：
- `blackboard.facts = {}`（空）
- `blackboard.status = "running"`
- `blackboard.metadata = {"user_query": "...", "priority": {...}}`
- `shell._activated = set()`（空，防死循环）

---

## 第 3 步：选第一个激活的 Agent

**目的**：从 3 个 KS 中选出本轮要执行的 1 个。

**位置**：[relationship.py L290-342](file:///c:\Users\Administrator\Desktop\my-agent/agent_core/multi_agent/relationship.py#L290-L342)（`_select_source` 方法）

**两阶段策略**：

### 3.1 过滤（_activated + preconditions）

```python
eligible = []
for s in self.sources:
    if s.name in self._activated:           # 已激活过的跳过
        continue
    if s.preconditions(self.blackboard):   # 前置条件检查
        eligible.append(s)
```

**第一次循环状态**（`_activated = {}`）：

| Agent | _activated? | preconditions 表达式 | 求值结果 | 加入 eligible? |
|-------|------------|---------------------|----------|----------------|
| researcher | 否 | `"True"` | True | ✓ |
| analyst | 否 | `facts.has('result::researcher')` | False | ✗ |
| writer | 否 | `facts.has('result::analyst')` | False | ✗ |

→ `eligible = [researcher]`

### 3.2 排序选一个

`strategy = "priority"`，按 priority_map 数字升序排：

```python
priority_map = {researcher: 1, analyst: 2, writer: 3}
eligible.sort(key=lambda s: priority_map.get(s.name, 999))
return eligible[0]    # → researcher
```

**第 3 步产出**：`source = researcher`

---

## 第 4 步：source.action() 让研究员干活

**目的**：调用 LLM 拿到研究员的回复。

**位置**：[relationship.py L122-170](file:///c:\Users\Administrator\Desktop\my-agent/agent_core/multi_agent/relationship.py#L122-L170)（`_default_action` 函数）

**4 个子步骤**：

### 4.1 构造 prompt（L127-141）

```python
facts_str = "\n".join(
    f"- {k}: {str(v)[:200]}"
    for k, v in blackboard.facts.items()
) or "（暂无）"

prompt = f"""
角色: {source.role}
目标: {source.goal}
背景: {source.backstory}

任务: {blackboard.metadata.get('user_query', '')}

已有的事实:
{facts_str}

请基于你的角色完成相关工作，输出最终结论（不要调用工具）。
"""
```

**第一次运行时**：`facts_str = "（暂无）"`，prompt 包含研究员人设 + 用户问题。

### 4.2 调 LLM（L144-156）

```python
messages = [
    {"role": "system", "content": source.system_prompt},
    {"role": "user", "content": prompt},
]
response = engine.client.chat.completions.create(
    model=engine.model,
    messages=messages,
    max_tokens=source.max_tokens,
)
final_text = response.choices[0].message.content.strip()
```

**这是真实的 OpenAI 兼容 API 调用**（mock 模式下不会发 HTTP）。

### 4.3 包装成 Command（L161-170）

```python
return Command(
    goto=None,                                # 不指定下一个
    update={f"result::{source.name}": final_text},  # 写回黑板
    terminate=False,
    source=source.name,
)
```

### 4.4 OODA 循环处理 Command（L370）

```python
# source.action() 返回 Command
# mock 模式会简化为直接返回字符串
self._activated.add(source.name)    # 标记 researcher 已激活
```

**第 4 步执行后黑板状态**：

```python
blackboard.facts = {
    "result::researcher": "LLM Agent 领域的最新研究进展...",
}
blackboard.history += [{"step": 0, "agent": "researcher", ...}]
```

---

## 第 5 步：第二轮循环，选 analyst

**目的**：在 researcher 已经写好结果的前提下，选 analyst 激活。

**第 5 步开始时状态**：
- `_activated = {"researcher"}`
- `facts = {"result::researcher": "..."}`

**过滤阶段**：

| Agent | _activated? | preconditions | 结果 |
|-------|------------|--------------|------|
| researcher | **是** | — | 跳过（_activated） |
| analyst | 否 | `facts.has('result::researcher')` → True | ✓ |
| writer | 否 | `facts.has('result::analyst')` → False | ✗ |

→ `eligible = [analyst]`

**排序**：priority_map 中 analyst=2，eligible 里只有 1 个。

→ `source = analyst`

**第 5 步执行后黑板状态**：

```python
blackboard.facts = {
    "result::researcher": "...",
    "result::analyst": "基于研究结果，2024 年趋势是...",
}
_activated = {"researcher", "analyst"}
```

---

## 第 6 步：第三轮循环，选 writer + 终止

**过滤后**：`eligible = [writer]`

**writer 跑完**：
- `facts` 多了 `result::writer`
- `_activated = {"researcher", "analyst", "writer"}`

**第 7 轮（如果有）**：
- `_activated` 已包含全部 3 个 → `eligible = []`
- `_select_source()` 返回 `None` → 状态置为 `solved`，break

**实际会触发 `done_when` 检查**（如果传入了），提前结束。

---

## 关键设计点

| 设计 | 位置 | 作用 |
|------|------|------|
| **Blackboard 共享状态** | [L41-49](file:///c:\Users\Administrator\Desktop\my-agent/agent_core/multi_agent/relationship.py#L41-L49) | facts / open_questions / history 三个容器 |
| **Command 原语** | [L51-65](file:///c:\Users\Administrator\Desktop\my-agent/agent_core/multi_agent/relationship.py#L51-L65) | goto + update + terminate 一体化（借鉴 LangGraph） |
| **preconditions 强约束** | [L77-115](file:///c:\Users\Administrator\Desktop\my-agent/agent_core/multi_agent/relationship.py#L77-L115) | `_parse_precondition` 解析表达式，**不用 eval()**（防注入） |
| **_activated 防死循环** | [L288](file:///c:\Users\Administrator\Desktop\my-agent/agent_core/multi_agent/relationship.py#L288) | 已激活过的 KS 不会自动再次激活 |
| **YAML 驱动配置** | [L467-](file:///c:\Users\Administrator\Desktop\my-agent/agent_core/multi_agent/relationship.py#L467-) | `from_yaml` 工厂方法，零改 Python 改流程 |

---

## 常见疑问

**Q1：为什么 researcher 先激活？**
A：它 preconditions=True（默认），不受依赖约束。其他两个依赖它的事实。

**Q2：analyst 怎么"看到"researcher 的输出？**
A：通过 Blackboard 共享状态。`_default_action` 把 facts 拼进 prompt。

**Q3：preconditions 字符串怎么解析的？**
A：用 `_parse_precondition()`（[L77-115](file:///c:\Users\Administrator\Desktop\my-agent/agent_core/multi_agent/relationship.py#L77-L115)），**不是 eval()**。

**Q4：怎么让一个 Agent 跑多次？**
A：返回 `Command(goto="itself")` 显式转交，让 _activated 检查放行。

**Q5：怎么插入并行？**
A：当前 v1.0 不支持，v2.0 会加。需要并行时多个 KS 各自的 preconditions 互相独立即可。

---

## 接下来

走读到这，你已经能：
- 读懂 3 个 KS 怎么协作
- 知道 Blackboard / Command / OODA 是什么
- 知道 _activated 防死循环的机制

**真跑一遍**会更直观。要跑吗？

---

## 实战修正记录（2026-06-24 验证后追加）

> 本走读最初基于静态代码 + `demos/relationship_demo.py` mock 模式编写。2026-06-24 用真实 StepFun API 跑通后，发现以下细节需修正或补充：

### 修正 1：L221-222 history 实际字段格式

**走读原文**：
```python
blackboard.history += [{"step": 0, "agent": "researcher", ...}]
```

**实际代码**（[relationship.py:333](../../agent_core/multi_agent/relationship.py#L333)）：
```python
self.blackboard.update(fk, fv, source="command")
```
- `source` 字段**硬编码为 `"command"`**，不是 agent 名
- agent 标识在 `key` 字段里：`"result::<agent_name>"`
- 实际格式：`{"step": N, "source": "command", "key": "result::<name>"}`

**修正后**：
```python
blackboard.history += [{
    "step": 0,
    "source": "command",      # 硬编码
    "key": "result::researcher",  # agent 名在 key 里
}]
```

**KPI 校验代码应据此改**（用 `key` 判断而不是 `source`）：
```python
# 正确
if h.get("op") == "update" and h.get("key") == f"result::{agent}":
# 错误
if h.get("op") == "update" and h.get("source") == agent:
```

### 修正 2：终止条件实际来自 YAML 而非 `_activated` 集合

**走读原文**（第 6 步）："_select_source() 返回 None → 状态置为 solved，break"

**实际**：终止由 `relationships.yaml` 的 `termination:` 字段控制（如 `facts.has('result::writer')`），不是 `_activated` 全激活后无候选。

实测：
```yaml
# 2026-06-24-tool-scenario-relationships.yaml
termination:
  - "facts.has('result::writer')"
```

### 补充 1：tools 字段缺省的隐性陷阱（见 ADR-008）

走读未涉及 `tools` 字段在 `from_yaml` 时的默认行为。实际：
- `[relationship.py:533](../agent_core/multi_agent/relationship.py#L533)`：`tools=cfg.get("tools", [])` 缺省空列表
- LLM 看不到任何工具 → 不会发起 tool_call
- 必须显式列 `tools: [calculator, get_time]` 才能让 LLM 看到工具
- 第二场实验 (`2026-06-24-tool-scenario.py`) 验证：8 LLM + 10 工具调用

### 补充 2：完整流程参考

- 第一场（无工具）：`experiments/2026-06-24-scenario.log`（175.08s，19750 字产出）
- 第二场（有工具）：`experiments/2026-06-24-tool-scenario.log`（35.03s，10 次工具调用）
- 完整原文存档：`experiments/outputs/`
- 走读 vs 实战的差异在 `memories/session/2026-06-24-09.md` 完整记录

### 补充 3：LoggingClient 是测试基础设施，非 core

走读未涉及的 `LoggingClient`（包装 `OpenAI.chat.completions.create`）只用于实验日志，**不并入 core/**——保持 ADR-005 "核心只做一件事"原则。
