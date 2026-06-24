# 2026-06-24 场景实验 — 完整流程存档

**目的**：将"场景实验 — 6 个月 AI 转型路线图"完整跑通的工作流存档，含**使用的代码**与**模型返回的全部内容**，**未经任何摘要或清洗**。

**运行时间**：2026-06-24
**总耗时**：175.08s（advisor 33.78s + strategist 96.59s + writer 44.71s）
**模型**：step-3.7-flash（StepFun 推理模型）
**端点**：https://api.stepfun.com/step_plan/v1
**退出码**：0

---

## 一、使用的代码（完整原文，未删改）

| 文件 | 字节 | 说明 |
|---|---|---|
| [2026-06-24-scenario-script.py](2026-06-24-scenario-script.py) | 8138 | 主实验脚本：`engine.run` + OODA 循环 + KPI 校验 |
| [2026-06-24-scenario-agents.yaml](2026-06-24-scenario-agents.yaml) | 1782 | 3 个 Agent 配置（advisor / strategist / writer） |
| [2026-06-24-scenario-relationships.yaml](2026-06-24-scenario-relationships.yaml) | 214 | priority 与终止条件 |

完整原文件路径（与 outputs/ 内文件同源）：
- `experiments/2026-06-24-scenario.py`
- `experiments/2026-06-24-scenario.yaml`
- `experiments/2026-06-24-scenario-relationships.yaml`

---

## 二、模型返回的全部内容（**完整原文**）

| 阶段 | 文件 | 字符数 | Agent |
|---|---|---|---|
| 1. 能力模型 | [2026-06-24-advisor-output.md](2026-06-24-advisor-output.md) | **5043** 字 | advisor |
| 2. 6 个月计划 | [2026-06-24-strategist-output.md](2026-06-24-strategist-output.md) | **5873** 字 | strategist |
| 3. CEO 报告 | [2026-06-24-writer-output.md](2026-06-24-writer-output.md) | **8834** 字 | writer |
| **合计** | — | **19750** 字 | — |

每个 .md 文件的开头都标注了：
- 来源（`experiments/2026-06-24-scenario.log`）
- 字符数（与本次实测一致）
- 提取方式（banner 切分 + 正则捕获）

---

## 三、KPI 校验（实际跑出）

```
[OK  ] status == 'solved'
[OK  ] facts 含 result::advisor
[OK  ] facts 含 result::strategist
[OK  ] facts 含 result::writer
[OK  ] 顺序 advisor → strategist → writer
[OK  ] writer 报告 > 500 字
```

---

## 四、追溯工作流

`engine.run(strategy="priority", metadata={"priority": {"advisor":1,"strategist":2,"writer":3}})` 实际执行：

| OODA 步 | 选中 | 成本 | 写入 facts | terminate |
|---|---|---|---|---|
| 1 | advisor | 33.78s | `result::advisor` (5043 字) | — |
| 2 | strategist | 96.59s | `result::strategist` (5873 字) | — |
| 3 | writer | 44.71s | `result::writer` (8834 字) | ✓ |

3 个 Agent 都走**默认 ReAct 循环**（`action=KnowledgeSource._default_action` → `run_react_agent` → `run_loop`），未做任何工厂方法绕过。

---

## 五、再跑一次

```powershell
cd c:\Users\Administrator\Desktop\my-agent
python experiments/2026-06-24-scenario.py
```

输出会写到 `experiments/2026-06-24-scenario.log`，覆盖原文件。

---

# 第二场：工具调用场景 — ReAct 循环完整 Action/Observation 链路

**目的**：上一个场景跑了 0 次工具调用（YAML 没显式列 tools = LLM 看不到工具）。
本场**显式**给 agent 配置 `tools: [calculator, get_time]`，并用业务问题强制 LLM 必须用 calculator 计算。

**关键改进**：脚本包装 OpenAI client + TOOLS，把**每次 LLM 调用的完整 request body** 和**完整 response body**（含 `tool_calls` / `reasoning_content` / `finish_reason`）以 JSON 原样打印到日志。

**运行时间**：2026-06-24
**总耗时**：35.03s（analyst 24.19s + writer 10.84s）
**模型**：step-3.7-flash
**端点**：https://api.stepfun.com/step_plan/v1
**退出码**：0

### 代码

| 文件 | 字节 | 说明 |
|---|---|---|
| [2026-06-24-tool-scenario-script.py](2026-06-24-tool-scenario-script.py) | — | 包装 OpenAI client + 包装 TOOLS 的实验脚本 |
| [2026-06-24-tool-scenario-agents.yaml](2026-06-24-tool-scenario-agents.yaml) | — | analyst 配 `[calculator, get_time]`，writer 配 `[get_time]` |
| [2026-06-24-tool-scenario-relationships.yaml](2026-06-24-tool-scenario-relationships.yaml) | — | priority analyst=1, writer=2 |

### 模型产出

| 文件 | 字符数 | Agent |
|---|---|---|
| [2026-06-24-tool-analyst-output.md](2026-06-24-tool-analyst-output.md) | 498 字 | analyst（含 calculator 计算结果） |
| [2026-06-24-tool-writer-output.md](2026-06-24-tool-writer-output.md) | 963 字 | writer（CFO 简报） |

### 工具调用实测统计

| 项 | 数量 |
|---|---|
| LLM 调用次数 | **8** |
| 工具调用次数 | **10** |
| ├─ calculator | 8 次 |
| └─ get_time | 2 次 |
| finish_reason=tool_calls | 6 次 |
| finish_reason=stop（最终答案） | 2 次 |

### 完整流程（按时间顺序）

| 时刻 | 事件 | 详情 |
|---|---|---|
| t=0 | OODA → analyst | priority 选中 analyst |
| t=1 | LLM #1 | analyst 第 1 轮：返回 tool_calls（calculator × N） |
| t=2-5 | 工具执行 + LLM #2-5 | 4 轮 Thought → Action → Observation 循环 |
| t=6 | LLM #6 | analyst 第 5 轮：finish_reason=stop → 返回 498 字最终答案 |
| t=7 | OODA → writer | facts 含 result::analyst → 选中 writer |
| t=8 | LLM #7 | writer 第 1 轮：返回 tool_calls（get_time × 1） |
| t=9 | 工具执行 + LLM #8 | 1 轮 Tool → Observation → Final Answer |
| t=10 | 终止 | facts 含 result::writer → terminate |

### KPI 校验（实际跑出）

```
[OK  ] status == 'solved'
[OK  ] facts 含 result::analyst
[OK  ] facts 含 result::writer
[OK  ] 顺序 analyst → writer
[OK  ] writer 报告 > 300 字
```

### 再跑一次

```powershell
cd c:\Users\Administrator\Desktop\my-agent
python experiments/2026-06-24-tool-scenario.py
```

输出会写到 `experiments/2026-06-24-tool-scenario.log`，**完整保留每次 LLM 调用的 request/response 原始 JSON**。

---

# 三场演进对比 — ADR × KPI × 踩坑 一图速查

> 本节为后人查归档用的**导航索引**。每场实验对应一次"假设 → 实战 → 教训"的完整循环，对应一个或多个 ADR 的诞生。

## 演进时间轴

```
对话轮次            实验                     触发问题                 沉淀 ADR
─────────────────────────────────────────────────────────────────────────
Session 06    2026-06-24-relationship-real    step-3.7-flash 输出空？    ADR-006 (关系引擎)
Session 07    绕 ReAct 循环（被回退）         治标不治本               (无)
Session 08    scenario.py（默认 ReAct）       推理模型空 content bug   ADR-007
Session 09-1  scenario.log 重跑验证           KPI 6/6 全过（实测）       (验收)
Session 09-2  发现 0 次工具调用              YAML 默认 tools=[]       ADR-008
Session 09-3  tool-scenario.py               工具调用 10 次全跑通     (验收)
```

## ADR × 实验 验证矩阵

| ADR | 主题 | 在哪场实验验证 | 验证结果 |
|---|---|---|---|
| ADR-005 | core/ 与 multi_agent/ 分离 | 架构层，不直接对应 | (被 ADR-007/008 引用) |
| ADR-006 | 关系驱动多 Agent 协作引擎 | relationship-real.log | ✅ 3 个 Agent 走完 OODA |
| **ADR-007** | ReAct 兼容推理模型（reasoning_content） | scenario.log | ✅ 175.08s 跑通 19750 字 |
| **ADR-008** | YAML 缺省 tools 字段的隐性陷阱 | tool-scenario.log | ✅ 显式列 tools 后 10 次调用 |

## KPI × 实验 验证矩阵

| KPI | real | scenario | tool-scenario |
|---|---|---|---|
| status == 'solved' | ✅ | ✅ | ✅ |
| 顺序符合 priority | ✅ researcher→analyst→writer | ✅ advisor→strategist→writer | ✅ analyst→writer |
| 产出长度达标 | ❌ researcher 失败 / analyst 1276 字 / writer 1476 字 | ✅ 3 段均 > 5000 字 | ✅ analyst 498 字 / writer 963 字 |
| 工具调用正常 | ❌ 0 次（mock search 失败） | ❌ 0 次（YAML 没列 tools） | ✅ **10 次**（calculator × 8 + get_time × 2） |
| 含 finish_reason=tool_calls | — | — | ✅ 6 次 |
| 含 finish_reason=stop | — | — | ✅ 2 次 |

## 踩坑 × 实验 教训矩阵

| 踩坑 | 发现于 | 教训 | 解决位置 |
|---|---|---|---|
| 推理模型 content 为空 | relationship-real（researcher 失败） | ReAct 必须 fallback 到 reasoning_content | react_agent.py:101-103（ADR-007） |
| 绕过 ReAct 用工厂方法 | session 07（被回退） | **修核心不绕核心** | 重写为默认 ReAct（ADR-007 落地） |
| YAML tools 默认空列表 | scenario（0 工具调用） | 必须显式列 tools | experiments/tool-scenario.yaml 模板 |
| PowerShell `>` 重定向丢内容 | scenario.py | 用 Python logging 直写文件 | logging.FileHandler 模式 |
| 主脚本 KPI 段被截断 | scenario.log | KPI 段独立可重入 | 改用 Python logging |
| 走读 L221 source 字段不准 | scenario.log（实测对照） | 实战修正记录 | 走读文档"实战修正"小节 |

## 关键证据文件指引

| 想验证什么 | 打开什么文件 |
|---|---|
| ADR-007 修复后默认 ReAct 真的工作 | [2026-06-24-writer-output.md](2026-06-24-writer-output.md)（8834 字） |
| ADR-008：缺省 tools 的隐性陷阱 | [2026-06-24-scenario.log](../../experiments/2026-06-24-scenario.log) 中 grep `tool_call` = 0 次 |
| ADR-008 修复后：显式列 tools 真工作 | [2026-06-24-tool-scenario.log](../../experiments/2026-06-24-tool-scenario.log) |
| 完整 LLM Request/Response 原始 JSON | [2026-06-24-tool-scenario.log](../../experiments/2026-06-24-tool-scenario.log)（找 `┌─[LLM #` 块） |
| 真实 history 字段格式 | [2026-06-24-relationship-real.log](../../experiments/2026-06-24-relationship-real.log) L47-49 |
| 模型原文证据（任意 Agent） | [outputs/](./README.md) 内对应 `*-output.md` |
| 完整对话记录 | `memories/session/2026-06-24-0{1..9}.md` |
| 架构决策原因 | `memories/repo/架构决策记录.md` |
| 走读 vs 实战差异 | `docs/explain/代码走读-relationship.py-2026-06-24.md` 末尾"实战修正"小节 |

## 复用指南

```powershell
# 跑第一场（无工具，验证 ReAct + 推理模型）
cd c:\Users\Administrator\Desktop\my-agent
python experiments/2026-06-24-scenario.py
# 日志：experiments/2026-06-24-scenario.log
# 耗时：~175s（3 段 × 30~100s/段）

# 跑第二场（强制工具调用，验证 ReAct Action/Observation）
python experiments/2026-06-24-tool-scenario.py
# 日志：experiments/2026-06-24-tool-scenario.log
# 耗时：~35s（2 段 × 10~25s/段）
```

**对比原则**：
- 第一场验证**逻辑链**：OODA → 选 agent → run_loop → content 输出
- 第二场验证**调用链**：OODA → 选 agent → run_loop → tool_calls → 工具执行 → Observation → ... → stop

任何一场失败都可对照上表定位是哪一环出问题。