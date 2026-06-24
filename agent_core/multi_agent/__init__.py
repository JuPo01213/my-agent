"""
agent_core.multi_agent - 多 Agent 协作层
=======================================

**职责定位**：项目上层 API，封装 core/ 的能力为多 Agent 协作原语。

**何时用本层**：
  - 任务需要"分工协作"（如：研究 → 分析 → 写作）
  - 需要可配置的协作流程（YAML 驱动，不改代码改配置）
  - 需要调度策略（first_match / priority / round_robin）
  - 需要共享状态给多个 Agent 读写（Blackboard）

**何时不用本层**：
  - 单 Agent 任务直接用 `agent_core.core.run_loop`
  - 不需要协作的任务用本层反而增加复杂度

**核心原则**（依据 ADR-005 / ADR-006）：
  - 关系由 YAML 声明，零改代码重配置
  - preconditions 子集化：不引入 eval()，避免任意代码执行
  - core/ 负责"怎么做"，multi_agent/ 负责"怎么配置"
  - 单向依赖：multi_agent → core，不反向

**公开 API**（基础 ReAct 封装）：
  - run_react_agent: 跑一个独立 ReAct Agent
  - filter_tools_schema: 根据工具名列表过滤 OpenAI Schema
  - call_tool_safe: 安全工具调用包装

**公开 API**（关系驱动协作，v1.0）：
  - Blackboard: 共享状态（facts / open_questions / history / status）
  - Command: 路由原语（goto + update + terminate）
  - KnowledgeSource: Agent 单元（preconditions + action）
  - ControlShell: OODA 调度器
  - RelationshipEngine: YAML 驱动的协作引擎

**典型用法**（YAML 驱动）：
  ```python
  from agent_core.config import get_provider
  from agent_core.multi_agent import RelationshipEngine

  api_key, base_url, model = get_provider()
  from openai import OpenAI
  client = OpenAI(base_url=base_url, api_key=api_key)

  engine = RelationshipEngine.from_yaml(
      client=client,
      model=model,
      agents_yaml_path="config/agents.yaml",
      relationships_yaml_path="config/relationships.yaml",
  )
  blackboard = engine.run(user_query="调研 2024 年 LLM Agent 进展")
  print(blackboard.facts["result::writer"])
  ```

**演进路线**（ADR-002 / ADR-006）：
  - v1.0（当前）：关系驱动引擎，仅支持串行/优先级调度
  - v1.1：加并行执行（ThreadPoolExecutor）
  - v2.0：加 Swarm / Hierarchical 模式
  - v3.0：加自动反思与记忆
"""
from .agent_api import (
    DEFAULT_AGENT_SYSTEM_PROMPT,
    DEFAULT_MAX_STEPS,
    call_tool_safe,
    filter_tools_schema,
    run_react_agent,
)
from .relationship import (
    Blackboard,
    Command,
    ControlShell,
    KnowledgeSource,
    RelationshipEngine,
)

__all__ = [
    # 基础 ReAct API
    "run_react_agent",
    "filter_tools_schema",
    "call_tool_safe",
    "DEFAULT_AGENT_SYSTEM_PROMPT",
    "DEFAULT_MAX_STEPS",
    # 关系驱动 API
    "Blackboard",
    "Command",
    "KnowledgeSource",
    "ControlShell",
    "RelationshipEngine",
]
