"""
agent_core.multi_agent.relationship - 关系驱动多 Agent 协作引擎
============================================================

核心抽象（借鉴业界成熟实践）：
- Blackboard：共享状态（所有 Agent 读/写）。借鉴 Blackboard 模式（callisphere.ai）。
- Command：路由原语（goto + update + terminate）。借鉴 LangGraph Command。
- KnowledgeSource：知识/能力源（preconditions + action）。借鉴 Blackboard + CrewAI。
- ControlShell：调度器（OODA 循环，激活 KS）。借鉴 Blackboard Control Shell。
- RelationshipEngine：整体协调器（YAML 驱动）。借鉴 SALLMA 目录化 + CrewAI YAML。

设计原则：
1. 完全 Pythonic，零 LangGraph 依赖（除 openai SDK 外只依赖 pyyaml）
2. 关系由 YAML 声明，零改代码重配置
3. preconditions 子集化：不引入 eval()，避免任意代码执行
4. 默认 action 走 Layer 2 的 run_react_agent，结构清晰
5. 完整中文注释，便于学习和维护
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable


# ============================================================
# 1. Blackboard：所有 Agent 共享的结构化状态
# ============================================================

@dataclass
class Blackboard:
    """
    共享黑板：所有 KnowledgeSource 读/写同一个 Blackboard 实例。

    字段说明：
    - facts：已确认的事实，key->value 结构
    - open_questions：待解的问题列表
    - history：操作历史（可审计、可调试）
    - current_step：当前执行步骤
    - status：running / solved / failed / timeout
    - metadata：任意扩展字段，注入 user_query / priority 等
    """
    facts: dict[str, Any] = field(default_factory=dict)
    open_questions: list[str] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)
    current_step: int = 0
    status: str = "running"
    metadata: dict[str, Any] = field(default_factory=dict)

    def update(self, key: str, value: Any, source: str = "") -> "Blackboard":
        """写入一个事实，自动记录历史。链式调用风格。"""
        self.facts[key] = value
        self.history.append({
            "step": self.current_step,
            "op": "update",
            "key": key,
            "source": source,
            "ts": time.time(),
        })
        return self

    def ask(self, question: str, source: str = "") -> "Blackboard":
        """登记一个待解问题。"""
        self.open_questions.append(question)
        self.history.append({
            "step": self.current_step,
            "op": "ask",
            "question": question,
            "source": source,
            "ts": time.time(),
        })
        return self

    def answer(self, question: str, answer: Any, source: str = "") -> "Blackboard":
        """回答一个待解问题，从 open_questions 移除并写入 facts。"""
        if question in self.open_questions:
            self.open_questions.remove(question)
        self.facts[f"answer::{question}"] = answer
        self.history.append({
            "step": self.current_step,
            "op": "answer",
            "question": question,
            "source": source,
            "ts": time.time(),
        })
        return self

    def snapshot(self) -> dict:
        """返回当前黑板的只读快照（用于 preconditions 判断）。"""
        return {
            "facts": dict(self.facts),
            "open_questions": list(self.open_questions),
            "current_step": self.current_step,
            "status": self.status,
        }

    def is_solved(self) -> bool:
        """判断是否已经解决：仅看 status 字段。
        不要再用 open_questions==[] 来推断 solved，因为初始黑板就没有
        open_questions，会导致 step 0 立刻被误判为 solved。终止逻辑
        改由 ControlShell 调用 Command.done() 显式触发。
        """
        return self.status == "solved"


# ============================================================
# 2. Command：LangGraph 风格的路由原语
# ============================================================

@dataclass
class Command:
    """
    路由原语：goto 指定下一个 Agent，update 携带状态增量，terminate 标记结束。

    借鉴 LangGraph 的 Command(goto, update) 设计，但用 Pythonic dataclass 表达，
    不依赖 LangGraph 框架。

    使用示例：
        # 转交给指定 Agent
        return Command.goto_agent("analyst", facts={"intermediate": "..."})

        # 流程结束
        return Command.done(facts={"final": "..."})
    """
    goto: str | None = None
    update: dict[str, Any] = field(default_factory=dict)
    terminate: bool = False

    @classmethod
    def goto_agent(cls, name: str, **update) -> "Command":
        """工厂方法：转交给指定 Agent，并附带状态更新。"""
        return cls(goto=name, update=update)

    @classmethod
    def done(cls, **update) -> "Command":
        """工厂方法：流程结束，可附带最终状态。"""
        return cls(goto=None, update=update, terminate=True)


# ============================================================
# 3. KnowledgeSource：Blackboard 模式的核心执行单元
# ============================================================

class KnowledgeSource:
    """
    知识源：一个 KnowledgeSource 代表一个"专家 Agent"。

    借鉴 Blackboard 模式：
    - preconditions：callable(blackboard_snapshot) -> bool
      声明"我在什么情况下可以被激活"
    - action：callable(blackboard, engine) -> Command
      我做什么事情，结果用 Command 表达

    借鉴 LangGraph Handoffs：
    - action 的返回值是 Command，可以是转交、可以是更新、可以是结束

    借鉴 CrewAI：
    - role + goal + backstory 三元组构造 LLM 人设
    """

    def __init__(
        self,
        name: str,
        role: str = "",
        goal: str = "",
        backstory: str = "",
        preconditions: Callable[[dict], bool] | None = None,
        action: Callable[["Blackboard", "RelationshipEngine"], Command] | None = None,
        tools: list[str] | None = None,
        system_prompt: str | None = None,
        max_iter: int = 10,
        allow_delegation: bool = False,
    ):
        self.name = name
        self.role = role or name
        self.goal = goal
        self.backstory = backstory
        # 默认 preconditions 永远为真
        self.preconditions = preconditions or (lambda snap: True)
        # 默认 action 走 run_react_agent
        self.action = action or self._default_action
        self.tools = tools or []
        self.system_prompt = system_prompt or self._build_default_prompt()
        self.max_iter = max_iter
        self.allow_delegation = allow_delegation

    def _build_default_prompt(self) -> str:
        """借鉴 CrewAI 的 role/goal/backstory 三元组构造默认 prompt。"""
        prompt_parts = [
            f"你是 {self.role}。",
        ]
        if self.goal:
            prompt_parts.append(f"目标：{self.goal}。")
        if self.backstory:
            prompt_parts.append(f"背景：{self.backstory}。")
        if self.tools:
            prompt_parts.append(f"你可以使用工具：{', '.join(self.tools)}。")
        else:
            prompt_parts.append("你没有外部工具，只能基于自身知识回答。")
        prompt_parts.append("完成任务后，直接给出最终答案，不要复述任务。")
        return "\n".join(prompt_parts)

    def _default_action(
        self, blackboard: "Blackboard", engine: "RelationshipEngine"
    ) -> Command:
        """
        默认 action：调 Layer 2 的 run_react_agent 跑一次 ReAct 循环。

        从黑板拼装 user_input（已知事实 + 待解问题 + 原始任务），
        把结果以 result::<agent_name> 写回黑板。
        """
        # 延迟导入避免循环依赖
        from .agent_api import run_react_agent

        # 拼装 user_input
        user_input_parts = []
        if blackboard.facts:
            user_input_parts.append("已知事实：")
            for k, v in blackboard.facts.items():
                user_input_parts.append(f"  - {k}: {v}")
        if blackboard.open_questions:
            user_input_parts.append("\n待解问题：")
            for q in blackboard.open_questions:
                user_input_parts.append(f"  - {q}")
        if blackboard.metadata.get("user_query"):
            user_input_parts.append(
                f"\n原始任务：{blackboard.metadata['user_query']}"
            )
        user_input = "\n".join(user_input_parts) or "（无任务）"

        # 调 LLM 跑 ReAct
        answer = run_react_agent(
            user_input=user_input,
            client=engine.client,
            model=engine.model,
            tools=self.tools or None,
            system_prompt=self.system_prompt,
            max_steps=self.max_iter,
        )

        # 把结果写回黑板
        return Command(
            goto=None,
            update={"facts": {f"result::{self.name}": answer}},
            terminate=False,
        )

    def can_activate(self, blackboard: "Blackboard") -> bool:
        """Control Shell 用这个方法判断是否激活我。"""
        return self.preconditions(blackboard.snapshot())


# ============================================================
# 4. ControlShell：调度器（OODA 循环）
# ============================================================

class ControlShell:
    """
    控制外壳：监听 Blackboard，匹配 preconditions，激活 KnowledgeSource。

    借鉴 Blackboard 模式的 Control Shell + OODA 循环。
    调度策略：
    - first_match：第一个满足 preconditions 的 KS 被激活
    - priority：按 metadata.priority 字段选优先级最高的
    - round_robin：轮询所有可激活的 KS
    """

    def __init__(
        self,
        blackboard: Blackboard,
        sources: list[KnowledgeSource],
        engine: "RelationshipEngine",
        max_steps: int = 50,
        strategy: str = "first_match",
        done_when: Callable[[Blackboard], bool] | None = None,
    ):
        self.blackboard = blackboard
        self.sources = sources
        self.engine = engine
        self.max_steps = max_steps
        self.strategy = strategy
        # 自定义终止条件：返回 True 时流程结束
        self.done_when = done_when
        self._round_robin_index = 0  # 用于 round_robin 策略
        # 记录已经被激活过的 Agent（避免 first_match 死循环）
        # 若需让某个 Agent 可被多次激活（如反思），使用 Command.goto 显式转交
        self._activated: set[str] = set()

    def _select_source(self) -> KnowledgeSource | None:
        """
        Decide 阶段：根据 strategy 选一个可激活的 KnowledgeSource。

        关键约束：已激活过的 Agent 不会被自动再次激活（避免死循环）。
        如果需要让 Agent 多次执行（如反思、迭代），必须用 Command.goto 显式转交。

        返回 None 表示没有可激活的，流程结束。
        """
        candidates = [
            s for s in self.sources
            if s.name not in self._activated and s.can_activate(self.blackboard)
        ]
        if not candidates:
            return None

        if self.strategy == "first_match":
            return candidates[0]

        if self.strategy == "priority":
            # 优先级：metadata.priority[agent_name] 数字小者优先
            priority_map = self.blackboard.metadata.get("priority", {})
            return sorted(
                candidates,
                key=lambda s: priority_map.get(s.name, 100),
            )[0]

        if self.strategy == "round_robin":
            # 轮询：从上次的位置下一个开始找
            for offset in range(len(self.sources)):
                idx = (self._round_robin_index + offset) % len(self.sources)
                if self.sources[idx] in candidates:
                    self._round_robin_index = (idx + 1) % len(self.sources)
                    return self.sources[idx]

        # 默认 fallback
        return candidates[0]

    def _apply_command(self, cmd: Command) -> None:
        """把 Command.update 写回黑板。"""
        for k, v in cmd.update.items():
            if k == "facts" and isinstance(v, dict):
                # facts 字段：逐个写入
                for fk, fv in v.items():
                    self.blackboard.update(fk, fv, source="command")
            elif k == "ask" and isinstance(v, list):
                # ask 字段：批量登记待解问题
                for q in v:
                    self.blackboard.ask(q, source="command")
            else:
                # 其他字段：直接写入
                self.blackboard.update(k, v, source="command")

    def run(self) -> Blackboard:
        """
        OODA 主循环：Observe → Orient → Decide → Act。

        循环条件：未达到 max_steps、未终止、仍有可激活的 KS。
        """
        for step in range(self.max_steps):
            self.blackboard.current_step = step

            # Observe + Orient + Decide：选 KS
            source = self._select_source()
            if source is None:
                # 没有 KS 可激活，结束
                self.blackboard.status = "solved"
                break

            # Act：执行 action
            try:
                cmd = source.action(self.blackboard, self.engine)
            except Exception as e:
                # 异常处理：记录错误，标记 failed
                self.blackboard.update(
                    f"error::{source.name}", str(e), source="control_shell"
                )
                self.blackboard.status = "failed"
                break

            # 标记为已激活
            self._activated.add(source.name)

            # 把 Command 写回黑板
            self._apply_command(cmd)

            # 检查终止条件
            if cmd.terminate or self.blackboard.is_solved():
                self.blackboard.status = "solved"
                break

            # 检查自定义 done_when 条件
            if self.done_when and self.done_when(self.blackboard):
                self.blackboard.status = "solved"
                break

            # 如果 Command.goto 有值：强行转交给指定 KS（绕过 preconditions）
            if cmd.goto:
                next_source = next(
                    (s for s in self.sources if s.name == cmd.goto), None
                )
                if next_source:
                    try:
                        next_cmd = next_source.action(self.blackboard, self.engine)
                        self._apply_command(next_cmd)
                        if next_cmd.terminate:
                            self.blackboard.status = "solved"
                            break
                    except Exception as e:
                        self.blackboard.update(
                            f"error::{next_source.name}", str(e), source="control_shell"
                        )
                        self.blackboard.status = "failed"
                        break
        else:
            # for 循环正常结束（未 break）→ 超时
            self.blackboard.status = "timeout"

        return self.blackboard


# ============================================================
# 5. RelationshipEngine：整体协调器（YAML 驱动）
# ============================================================

class RelationshipEngine:
    """
    关系驱动多 Agent 协作引擎。

    职责：
    1. 维护 KnowledgeSource 列表
    2. 构造 Blackboard 与 ControlShell
    3. 提供 YAML 驱动的工厂方法 from_yaml()
    4. 提供 run() 入口启动协作
    """

    def __init__(
        self,
        client: Any,
        model: str,
        agents: list[KnowledgeSource] | None = None,
        max_steps: int = 50,
    ):
        self.client = client
        self.model = model
        self.agents = agents or []
        self.max_steps = max_steps
        # 存储 YAML 里的关系（priority / termination 等）
        self._relationships: dict[str, Any] = {}

    def add_agent(self, agent: KnowledgeSource) -> "RelationshipEngine":
        """添加一个 KnowledgeSource，链式风格。"""
        self.agents.append(agent)
        return self

    def run(
        self,
        user_query: str,
        strategy: str = "first_match",
        metadata: dict | None = None,
        done_when: Callable[[Blackboard], bool] | None = None,
    ) -> Blackboard:
        """
        启动一次多 Agent 协作。

        Args:
            user_query：用户原始问题
            strategy：ControlShell 调度策略（first_match / priority / round_robin）
            metadata：注入黑板的额外元信息（如 priority 映射）
            done_when：自定义终止条件 callable(blackboard) -> bool

        Returns:
            最终的 Blackboard 实例（包含 facts / history / status）
        """
        # 1. 构造黑板
        blackboard = Blackboard(
            metadata={"user_query": user_query, **(metadata or {})}
        )

        # 2. 构造 ControlShell
        shell = ControlShell(
            blackboard=blackboard,
            sources=self.agents,
            engine=self,
            max_steps=self.max_steps,
            strategy=strategy,
            done_when=done_when,
        )

        # 3. 启动 OODA 循环
        return shell.run()

    @classmethod
    def from_yaml(
        cls,
        client: Any,
        model: str,
        agents_yaml_path: str,
        relationships_yaml_path: str | None = None,
    ) -> "RelationshipEngine":
        """
        YAML 驱动的工厂方法。

        读取 agents.yaml（必须）和 relationships.yaml（可选），
        构造完整的 RelationshipEngine 实例。

        agents.yaml 字段：
        - role / goal / backstory：CrewAI 风格人设三元组
        - tools：可调用工具名列表
        - max_iter：最大迭代步数
        - allow_delegation：是否允许转交（预留）
        - preconditions：激活条件表达式（子集化安全解析）
        - system_prompt：自定义系统提示（覆盖 role/goal/backstory）

        relationships.yaml 字段（可选）：
        - priority：{agent_name: priority_number}
        - termination：终止条件列表（暂仅支持 status == 'solved'）
        """
        import yaml  # PyYAML 唯一外部依赖

        # 1. 加载 agents 配置
        with open(agents_yaml_path, encoding="utf-8") as f:
            agents_cfg = yaml.safe_load(f) or {}

        # 2. 加载 relationships 配置（可选）
        rels_cfg: dict[str, Any] = {}
        if relationships_yaml_path:
            with open(relationships_yaml_path, encoding="utf-8") as f:
                rels_cfg = yaml.safe_load(f) or {}

        # 3. 构造 KnowledgeSource 实例
        sources: list[KnowledgeSource] = []
        for name, cfg in agents_cfg.items():
            # 解析 preconditions 表达式（安全子集）
            precond_str = cfg.get("preconditions", "True")
            precond = _parse_precondition(precond_str)

            sources.append(
                KnowledgeSource(
                    name=name,
                    role=cfg.get("role", name),
                    goal=cfg.get("goal", ""),
                    backstory=cfg.get("backstory", ""),
                    preconditions=precond,
                    tools=cfg.get("tools", []),
                    system_prompt=cfg.get("system_prompt"),
                    max_iter=cfg.get("max_iter", 10),
                    allow_delegation=cfg.get("allow_delegation", False),
                )
            )

        # 4. 构造 engine 并保存关系配置
        engine = cls(client=client, model=model, agents=sources)
        engine._relationships = rels_cfg
        return engine


# ============================================================
# 6. preconditions 安全表达式解析
# ============================================================

def _parse_precondition(expr: str) -> Callable[[dict], bool]:
    """
    把 YAML 里写的简单 preconditions 表达式编译为可调用对象。

    支持的子集（**不用 eval()，避免任意代码执行风险**）：
    - "True" → 永远为真
    - "False" → 永远为假
    - "facts.has('xxx')" → 检查黑板 facts 里是否有某 key
    - "'xxx' in open_questions" → 检查 open_questions 是否包含某字符串
    - "facts.has('a') and facts.has('b')" → 组合判断
    - 未识别的表达式 → 默认返回 True（放行）

    Args:
        expr：YAML 中写的表达式字符串

    Returns:
        callable(snapshot) -> bool
    """
    expr = (expr or "True").strip()
    if expr == "True":
        return lambda snap: True
    if expr == "False":
        return lambda snap: False

    # 提取单引号或双引号中的字符串字面量
    def _extract_str(e: str) -> str | None:
        if "'" in e:
            return e.split("'")[1]
        if '"' in e:
            return e.split('"')[1]
        return None

    # facts.has('xxx') 模式
    if "facts.has(" in expr and ")" in expr:
        key = _extract_str(expr)
        if key:
            return lambda snap, k=key: k in snap.get("facts", {})

    # 'xxx' in open_questions 模式
    if "open_questions" in expr and "in" in expr:
        target = _extract_str(expr)
        if target:
            return lambda snap, t=target: t in snap.get("open_questions", [])

    # 简单的 and 组合：facts.has('a') and facts.has('b')
    if " and " in expr and "facts.has(" in expr:
        # 提取所有 facts.has('xxx') 中的 key
        import re
        keys = re.findall(r"facts\.has\(['\"]([^'\"]+)['\"]\)", expr)
        if keys:
            return lambda snap, ks=keys: all(k in snap.get("facts", {}) for k in ks)

    # 默认放行
    return lambda snap: True


# ============================================================
# 模块公开 API
# ============================================================

__all__ = [
    "Blackboard",
    "Command",
    "KnowledgeSource",
    "ControlShell",
    "RelationshipEngine",
]
