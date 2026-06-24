# 构建自己的技能体：技术细节补充资料

> **说明**：本文件为《写一个自己的智能体：完整调研与最佳实践报告》的技术细节补充，所有内容均来自 2026-06-24 的联网检索与现有工作区资料综合整理。
> 
> **检索来源**：arXiv、MCP 官方规范、ANP 白皮书、ARD 标准公告、Nacos AI Registry、LangChain 官方文档、OpenAI Agents SDK 文档、CSDN/掘金社区工程实践、Google Cloud Agent Registry 文档等。

---

## 目录

1. [技能体注册发现协议](#一技能体注册发现协议)
2. [MCP 协议技术规范](#二mcp-协议技术规范)
3. [记忆系统工程实现](#三记忆系统工程实现)
4. [安全护栏技术实现](#四安全护栏技术实现)
5. [技能体工程化框架](#五技能体工程化框架)

---

## 一、技能体注册发现协议

### 1.1 ANP Agent Discovery Protocol

ANP（Agent Network Protocol）定义了 Agent 如何互相发现的标准化协议。

**主动发现（Active Discovery）**：
- 基于 Web well-known path 约定
- 默认路径：`/.well-known/agentdescriptions`
- 返回 JSON-LD manifest，包含所有 agent description 的 URL
- 支持分页（`next` 字段）以应对大规模 agent 场景

**被动发现（Passive Discovery）**：
- Agent 主动向搜索服务注册
- 类似搜索引擎索引网页

**关键实现细节**：
- 每个 agent 有唯一的 description document
- Manifest 类型为 `CollectionPage`
- 支持增量加载（incremental loading）

### 1.2 ARD（Agentic Resource Discovery）标准

**发布时间**：2026-06-22
**参与方**：Google、Microsoft、GoDaddy、Hugging Face、NVIDIA、Salesforce、ServiceNow、Databricks、Snowflake、GitHub、Cisco

**核心架构**：
```
┌─────────────────────────────────────────────┐
│  注册表（Registry）                          │
│  • 爬取并索引目录文件                        │
│  • 验证发布者身份                            │
│  • 返回带元数据的匹配能力信息                 │
├─────────────────────────────────────────────┤
│  发布者（Publisher）                         │
│  • 在自有域名下托管 ai-catalog.json          │
│  • 域名即信任锚点（DNS 模型）                 │
└─────────────────────────────────────────────┘
```

**目录结构示例**：
```json
{
  "agents": [
    {
      "name": "research-agent",
      "description": "信息检索智能体",
      "capabilities": ["web_search", "summarize"],
      "endpoint": "https://example.com/agents/research"
    }
  ]
}
```

**企业级控制措施**：
- 智能体身份认证
- 信任清单（trust list）
- 出口策略（egress policy）
- 工具锁定（tool pinning）

### 1.3 Nacos AI Registry

Nacos 3.2 内置了 AI Registry，提供五类 AI 资源的统一治理：

| 资源类型 | 说明 |
|----------|------|
| Skill Registry | 技能的安全审核、版本锁定、灰度发布 |
| MCP Registry | MCP Server 的服务发现 |
| Agent Registry | 基于 A2A 协议的 Agent 互相发现 |
| Prompt Registry | Prompt 的工程化管理（模板变量、语义化版本、热加载） |
| AgentSpec | Agent 能力规格与组装描述 |

**安全审核流水线**：
1. Prompt 注入扫描
2. 敏感数据泄露检测
3. 数据外发检查
4. 恶意代码检测
5. 依赖漏洞扫描

**关键特性**：
- 命名空间隔离（按团队隔离）
- 权限落到单个 Skill
- 版本治理（语义化版本号、灰度发布）
- nacos-cli 一条命令分发

### 1.4 Agent Skills 三层加载机制

这是 Claude / VS Code Copilot / Cursor 通用的技能加载模型：

**层级 1：技能发现**
- AI 先读取所有技能的元数据（`name` 和 `description`）
- 判断任务是否相关
- 这些元数据始终在系统提示中

**层级 2：加载核心指令**
- 如果相关，AI 自动读取 `SKILL.md` 的正文内容
- 获取详细指导

**层级 3：加载资源文件**
- 只在需要时读取额外文件（脚本、示例）
- 或通过工具执行脚本

**核心价值**：
- **渐进式披露（Progressive Disclosure）**：只加载需要的部分，避免上下文窗口溢出
- **跨平台**：同一个 Skill 可以在 Claude、VS Code Copilot、Cursor 中使用

### 1.5 Skill 技术栈分类

| 层级 | 技术方向 | 代表项目 |
|------|----------|----------|
| 协议层 | Skill/Tool 标准化协议 | MCP, OpenAPI, LangChain Tools |
| 框架层 | Agent 框架（Skill 编排） | LangChain, AutoGen, CrewAI, OpenAI Assistants |
| 技能层 | 具体 Skill 实现 | LangChain Tools, MCP Servers, OpenAI Plugins |
| 发现层 | Skill 市场/仓库 | MCP Server Registry, ToolHouse, Composio |
| 基础设施层 | Skill 运行环境 | E2B, Modal, AWS Lambda |

---

## 二、MCP 协议技术规范

### 2.1 协议栈结构

```
┌─────────────────────────────────────────────┐
│   AI Model / Agent                          │
├─────────────────────────────────────────────┤
│   MCP Application Layer                     │  ← MCP 核心定义
├─────────────────────────────────────────────┤
│   JSON-RPC 2.0                              │
├─────────────────────────────────────────────┤
│   Transport (HTTP / SSE / STDIO /           │
│   Streamable HTTP)                          │
├─────────────────────────────────────────────┤
│   OS / Network                              │
└─────────────────────────────────────────────┘
```

**关键设计**：
- MCP 不是传输层协议，而是**语义层通信规范**
- 不重新发明传输协议，专注于定义**交互语义和能力模型**

### 2.2 三层架构

**MCP Host（主机）**：
- 接收用户指令
- 驱动 Agent 做规划与决策
- 创建、管理 MCP Client 实例
- 控制权限与会话生命周期

**MCP Client（客户端）**：
- 与 Server 建立 1:1 会话
- 做能力协商（Capability Negotiation）
- 将 Agent 的工具调用指令转为 JSON-RPC 2.0 标准请求
- 接收 Server 响应并解析，返回给 Host/Agent

**MCP Server（服务器）**：
- 封装并标准化暴露外部能力
- 统一提供 Resources、Tools、Prompts 三类能力
- 实现"一次开发、多模型通用"

### 2.3 三类一等原语（Primitives）

**1. Tool（工具）**
```json
{
  "name": "search_orders",
  "description": "Search orders by user id",
  "inputSchema": {
    "type": "object",
    "properties": {
      "userId": { "type": "string" }
    }
  }
}
```

**2. Resource（资源）**
```json
{
  "uri": "file:///docs/manual.pdf",
  "mimeType": "application/pdf"
}
```
- 提供上下文数据（文件、数据库记录）
- 支持增量授权、链接、URI 模式

**3. Prompt（提示模板）**
```json
{
  "name": "summarize_document",
  "arguments": ["language"]
}
```
- 服务器可公开结构化的提示模板和工作流
- 供 LLM 使用

### 2.4 通信格式与生命周期

**基础通信**：完全基于 JSON-RPC 2.0
- Request：有 `id`，需要响应
- Response：响应请求
- Notification：无 `id`，不需要响应

**会话初始化流程**：
1. Client → `initialize` → Server
2. Client ← `capabilities` ← Server
3. Client → `initialized` → Server
4. 后续交互

**能力协商**：客户端和服务端在连接时协商支持的功能

### 2.5 传输层选项

| 传输方式 | 适用场景 | 特点 |
|----------|----------|------|
| Streamable HTTP | 远程服务、Web 部署 | 单端点、支持流式 |
| stdio | 本地子进程 | 低延迟、进程间通信 |
| SSE | 服务端推送 | 实时事件流 |

### 2.6 安全机制

**授权与安全**：
- 强制使用 OAuth 2.1（含 PKCE、HTTPS）
- 支持 OpenID Connect Discovery
- 强调**用户明确同意**（explicit consent）
- 数据隐私和工具安全

**工具描述长度限制**：
- 超过 1,200 字符可能导致 `400 Invalid "tools.function.description": string too long` 错误
- 工具描述需简洁精准

### 2.7 FastMCP 生产级框架

FastMCP 是目前 Python 构建 MCP 服务器最主流的框架：

```python
from fastmcp import FastMCP

mcp = FastMCP("Demo Server 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers and return the result"""
    return a + b

if __name__ == "__main__":
    mcp.run()
```

**关键特性**：
- 自动完成 Tool Schema 生成
- Protocol 实现
- Transport 通信
- Tool Discovery
- Runtime 接入
- 企业身份认证
- 客户端库
- 测试工具
- API 文档自动生成

**部署方式**：
```python
mcp.run(transport="http", host="127.0.0.1", port=8000, path="/mcp")
```

---

## 三、记忆系统工程实现

### 3.1 记忆四层架构

| 层级 | 名称 | 时间尺度 | Agent 实现 | 存储方式 |
|------|------|----------|------------|----------|
| L1 | 工作记忆（Working Memory） | 毫秒级·单次调用 | 当前对话上下文 | LLM Prompt |
| L2 | 短期记忆（Short-term Memory） | 会话级 | 最近 N 轮对话 | 上下文/Redis |
| L3 | 长期记忆（Long-term Memory） | 跨会话 | 向量数据库 | Vector DB |
| L4 | 程序记忆（Procedural Memory） | 跨任务 | Skills/Tools | Git/Prompt Registry |

### 3.2 记忆类型的认知科学映射

| 人类记忆类型 | Agent 记忆类型 | 存储内容 | 实现方式 |
|--------------|----------------|----------|----------|
| Working Memory | 工作记忆 | 当前对话上下文 | 上下文窗口 |
| Short-term Memory | 短期记忆 | 最近 N 轮对话 | 滑动窗口/摘要 |
| Episodic Memory | 情景记忆 | 历史交互轨迹 | 向量数据库+元数据 |
| Semantic Memory | 语义记忆 | 事实/知识/偏好 | 知识图谱/RAG |
| Procedural Memory | 程序记忆 | 行为规范/工作流 | Skill Registry |

### 3.3 分层记忆系统实现（Python）

```python
from dataclasses import dataclass, field
from typing import Optional
import time

@dataclass
class Memory:
    content: str
    memory_type: str  # working, short_term, long_term
    importance: float  # 0-1
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0
    embedding: Optional[list] = None

class TieredMemorySystem:
    """分层记忆系统——模拟人类记忆层次"""
    
    def __init__(self, embedding_model, vector_store):
        self.working = []          # 当前对话（最多10条）
        self.short_term = []       # 最近1小时
        self.long_term = vector_store  # 向量数据库
        self.embedding_model = embedding_model
    
    async def store(self, content: str, importance: float = 0.5):
        memory = Memory(
            content=content,
            memory_type="working",
            importance=importance
        )
        memory.embedding = await self.embedding_model.embed(content)
        
        # 始终存入 working memory
        self.working.append(memory)
        
        # 溢出策略
        if len(self.working) > 10:
            overflow = self.working.pop(0)
            await self._consolidate(overflow)
    
    async def _consolidate(self, memory: Memory):
        """记忆巩固：决定是遗忘还是升级到长期记忆"""
        if memory.importance > 0.7:
            # 存入长期记忆
            await self.long_term.add(memory)
        else:
            # 进入短期记忆（1小时过期）
            memory.memory_type = "short_term"
            self.short_term.append(memory)
```

### 3.4 记忆系统的关键权衡

| 对立约束 | 说明 |
|----------|------|
| 记忆完整性 vs Context 效率 | 记住越多，越需要占用有限的 Context Window，信噪比下降 |
| 检索精准度 vs 检索延迟 | 向量相似度搜索精准但慢（~50-200ms），关键词匹配快但召回率低 |
| 持久化可靠性 vs 写入性能 | 每次 Agent 行动后同步写磁盘安全但阻塞，异步写快但存在丢失风险 |
| 长期记忆容量 vs 遗忘代价 | 无限存储带来检索噪声，强制遗忘可能丢失关键知识 |

### 3.5 写入策略

**什么该存**：
- 高重要性信息（用户明确要求记住的偏好、关键决策）
- 成功/失败的工具调用模式
- 用户纠正的错误

**什么不该存**：
- 临时中间结果（任务完成后可丢弃）
- 敏感信息（PII、密钥）
- 过时的知识（有版本控制需求的应走版本系统）

### 3.6 检索机制

**分层检索**：
1. **Working Memory**：全部返回（当前对话上下文）
2. **Short-term Memory**：语义搜索最近 1 小时
3. **Long-term Memory**：向量检索 + 元数据过滤（时间、权限、业务类型）

**检索时机**：
- Agent 执行前注入相关记忆
- 执行后提取并存储新知识

### 3.7 LangGraph 记忆系统

**Short-term Memory**：
- Thread-scoped（线程作用域）
- 作为 Agent state 的一部分
- 通过 checkpointer 持久化到数据库
- 支持断点恢复

**Long-term Memory**：
- 基于自定义 namespace 存储
- 跨会话共享
- 可被任何 thread 召回
- 存储为 JSON documents

### 3.8 OpenClaw Memory System 核心设计

**设计哲学**：**不存所有，只存重要；不读全部，只读相关**

**关键概念**：
- **Working Memory**：当前 Agent 会话的活跃上下文缓冲区
- **Episodic Memory**：结构化历史 Agent 行为轨迹（Action-Observation 对）
- **Semantic Memory**：向量化知识库（领域知识、用户偏好）
- **Procedural Memory**：成功执行模式的抽象（"怎么做某件事"）

---

## 四、安全护栏技术实现

### 4.1 纵深防御三层模型

**第 1 层：传统确定性控制**
- 运行时政策强制执行
- 访问权限控制
- 硬性限制（无论模型行为如何，均可正常运行）

**第 2 层：基于推理的防御措施**
- 模型强化
- 分类器保护
- 对抗性训练

**第 3 层：持续保证**
- 红队测试
- 回归测试
- 变体分析

### 4.2 Local Defender Agent

Google 提出的 Local Contextualized Defender Agent 提供**同接口带内保护**：

**职责**：
- 执行最小权限工具权限
- 验证 function-call schemas 和值范围
- 净化输入和输出
- 应用执行和检索护栏
- 重写或隔离高风险上下文
- 确保工具执行适当的授权和认证

**防御部署位置**：
- 工具调用层（guided generation in LLM call）
- 工具实现层（Pydantic typing in Python MCP calls）
- 或两者兼有

### 4.3 OpenAI Agents SDK Guardrails

```python
from agents import Agent, ModelSettings
from agents.guardrails import Guardrail, GuardrailResult

# 输入 Guardrail：验证用户输入
input_guardrail = Guardrail(
    name="profanity_check",
    logic=lambda input: not contains_profanity(input),
    action="block"
)

# 输出 Guardrail：验证模型输出
output_guardrail = Guardrail(
    name="data_leak_check",
    logic=lambda output: not contains_sensitive_data(output),
    action="redact"
)

agent = Agent(
    name="SafeAgent",
    instructions="...",
    input_guardrails=[input_guardrail],
    output_guardrails=[output_guardrail]
)
```

**关键特性**：
- Guardrails 在 Agent 层面配置，不是应用层事后检查
- 支持 `block`（阻止）、`redact`（脱敏）、`modify`（修改）等动作
- 输入和输出分别配置

### 4.4 工具调用三重校验

**1. 权限校验**：Agent 是否有调用该工具的权限
**2. 参数校验**：调用参数是否符合预设的范围
**3. 风险校验**：该操作是否符合当前上下文的业务逻辑

**高风险工具人工审核节点**：
- 修改生产数据
- 转账
- 下单
- 删除操作

### 4.5 Nacos 五重安全扫描

所有 Skill 发布前必须经过：
1. **Prompt 注入扫描**
2. **敏感数据泄露检测**
3. **数据外发检查**
4. **恶意代码检测**
5. **依赖漏洞扫描**

扫描未通过无法发布，owner 决策全程留痕。

### 4.6 Falco YAML 策略（运行时拦截）

Prempti 项目展示了使用 Falco YAML 拦截 Claude Code 工具调用：

```yaml
rules:
  - name: block_dangerous_shell
    condition: >
      tool.name = "shell" and 
      (tool.input_command contains "rm -rf" or 
       tool.input_command contains "curl")
    action: deny
```

**可拦截的 agent-specific 字段**：
- `tool.name`
- `tool.input_command`
- `tool.file_path`

### 4.7 Model Armor（Google）

Google Cloud 的 Model Armor 提供：
- 提示注入过滤
- 敏感数据过滤
- 有害内容过滤

**配置示例**：
```python
from model_armor import ProtectionTemplate

template = ProtectionTemplate(
    name="customer_service",
    input_filters=["prompt_injection", "pii"],
    output_filters=["data_leak", "harmful_content"]
)
```

### 4.8 沙箱隔离策略

| 隔离手段 | 实现方式 | 适用场景 |
|----------|----------|----------|
| 容器/VM 隔离 | Docker、Firecracker | 代码执行、文件操作 |
| 网络策略 | 默认断网，显式声明 egress | 防止数据外发 |
| 资源限制 | CPU/内存/磁盘配额 | 防止 Agent 资源耗尽 |
| 文件系统只读 | 根文件系统只读 + 临时挂载点 | 防止持久化污染 |
| 能力降级 | cap_drop ALL | 最小权限原则 |

---

## 五、技能体工程化框架

### 5.1 技能体元数据规范（SKILL.md Frontmatter）

```yaml
---
name: my-skill
display_name: "中文显示名"
description_zh: "中文描述，必须包含触发词"
description_en: "English description"
version: "1.2.0"           # 语义版本
visibility: "public"       # public / internal / private
applyTo:                   # 文件作用域
  - "**/*.py"
  - "docs/**"
capabilities:
  - name: summarize
    description: "总结文本"
    parameters:
      type: object
      required: [text]
      properties:
        text: 
          type: string 
          maxLength: 4000
inputs:
  - type: text
    required: true
outputs:
  - type: markdown
    required: true
dependencies:
  python:
    - requests>=2.31
    - openai>=1.0
permissions:
  scopes:
    - web.search.read
  requires_human_approval: false
author: "团队名"
lifecycle:
  deprecated: false
  sunset_date: null
---
```

**关键字段说明**：
- `description` / `description_zh`：发现层，必须包含触发词
- `capabilities`：运行层，用于 schema 校验、参数提示、权限拦截
- `applyTo`：决定是否常驻上下文；`**` 会浪费上下文

### 5.2 技能体目录结构

```
.github/skills/<skill-name>/
├── SKILL.md               # 必需
├── CHANGELOG.md            # 强烈建议
├── references/             # 参考资料
│   └── api-spec.md
├── templates/              # 输出模板
│   └── report.md
├── scripts/                # 辅助脚本
│   ├── validate.py
│   └── run.py
├── tests/                  # 技能测试
│   ├── unit/
│   └── adversarial/
├── schemas/                # 能力参数 schema
│   └── args.json
└── assets/                 # 静态资源
```

### 5.3 技能体版本化与兼容性

| 场景 | 处理方式 |
|------|----------|
| 新增 capability | minor 版本；旧调用方继续兼容 |
| 删除 capability | major 版本；旧调用方报错或降级 |
| 参数必填项变化 | major 版本 |
| 修复提示词 typo | patch 版本 |
| 废弃旧能力 | `lifecycle.deprecated: true` + `sunset_date` |

### 5.4 技能体注册表（Registry）

```json
{
  "version": "1.0.0",
  "skills": [
    {
      "name": "my-skill",
      "path": ".github/skills/my-skill/SKILL.md",
      "version": "1.2.0",
      "display_name": "中文名",
      "description_zh": "一句话描述，含触发词",
      "applyTo": ["**/*.py"],
      "last_updated": "2026-06-24",
      "capabilities": ["summarize", "translate"]
    }
  ]
}
```

### 5.5 技能体调用协议

**调用前校验**：
1. skill 在 registry 且版本未过期
2. capability 在 `skill.metadata.capabilities` 中
3. caller_role 有该 capability 权限
4. 若 `requires_human_approval` → 暂停等待人工确认

**调用后处理**：
5. 输出经过 schema 校验
6. 写入审计日志（含 `skill_name`, `capability`, `args_hash`, `output_hash`）

### 5.6 技能体测试体系

| 层级 | 内容 | 工具 |
|------|------|------|
| schema 测试 | `args` 必须通过 JSON Schema | jsonschema / pydantic |
| 单元测试 | `scripts/` 函数级覆盖 | pytest |
| 集成测试 | 调用完整 skill 返回结构 | pytest + mock LLM |
| 对抗测试 | prompt injection / 参数越界 | 自定义 suite |
| 回归测试 | 版本升级后旧能力行为不变 | golden case |

### 5.7 CI/CD 治理流程

```yaml
# .github/workflows/skill-ci.yml
name: Skill CI
on:
  push:
    paths: ['.github/skills/**']
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python scripts/validate_registry.py
      - run: pytest .github/skills/*/tests/
  publish:
    needs: validate
    if: github.ref == 'refs/heads/main'
    steps:
      - run: python scripts/publish_skill.py --output .github/skills/registry.json
```

**治理 checklist**：
- [ ] frontmatter 必填字段齐全
- [ ] `description_zh` 包含触发词
- [ ] `capabilities[*].parameters` 可被 JSON Schema 解析
- [ ] `tests/` 覆盖率 ≥ 阈值
- [ ] 无硬编码密钥
- [ ] 生命周期状态不是 deprecated 或 sunset 已过

---

## 六、关键代码片段

### 6.1 Skill Loader（Python）

```python
"""skills/runtime/loader.py"""
from pathlib import Path
import frontmatter
from typing import Any

class SkillLoader:
    def __init__(self, registry_path: str):
        self.registry_path = Path(registry_path)
        self._cache: dict[str, dict] = {}

    def load(self, name: str) -> dict[str, Any]:
        if name in self._cache:
            return self._cache[name]
        post = frontmatter.load(self.registry_path.parent / f"{name}/SKILL.md")
        skill = {
            "metadata": post.metadata,
            "body": post.content,
            "name": name,
        }
        self._cache[name] = skill
        return skill

    def resolve(self, user_input: str, file_path: str) -> list[dict]:
        candidates = []
        for entry in self._iter_registry():
            meta = entry["metadata"]
            apply_to = meta.get("applyTo", [])
            desc_zh = meta.get("description_zh", "")
            desc_en = meta.get("description", "")
            if self._matches(user_input, desc_zh, desc_en) or self._matches(file_path, apply_to):
                candidates.append(entry)
        return candidates
```

### 6.2 A2A AgentCard 示例

```python
from a2a.types import AgentCard, AgentSkill

def make_skill(skill_id, name, description, tags):
    s = AgentSkill()
    s.id = skill_id
    s.name = name
    s.description = description
    s.tags.extend(tags)
    return s

research_card = AgentCard()
research_card.name = "research-agent"
research_card.description = "Gathers factual background on technical topics"
research_card.skills.append(
    make_skill("research", "Research", "Collect key facts on a topic", 
               ["research", "facts"])
)
```

### 6.3 MCP Tool 声明示例

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("demo-server")

@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="search_orders",
            description="Search orders by user id",
            inputSchema={
                "type": "object",
                "properties": {
                    "userId": {"type": "string"}
                },
                "required": ["userId"]
            }
        )
    ]
```

### 6.4 Guardrail 系统示例

```python
from enum import Enum
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Callable

class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ValidationResult:
    is_valid: bool
    risk_level: RiskLevel
    message: str
    sanitized_output: Optional[Any] = None
    action_taken: Optional[str] = None  # "blocked", "modified", "approved"

class GuardrailSystem:
    """多层护栏系统"""
    def __init__(self, config):
        self.config = config
        self.pii_detector = PIIDetector(config.pii_config)
        self.content_filter = ContentFilter(config.content_policy)
        self.permission_checker = PermissionChecker(config.rbac_config)
        self.audit_logger = AuditLogger(config.audit_config)
    
    async def validate_input(self, user_input: str, user_role: str, session_id: str) -> ValidationResult:
        # 1.1 长度检查
        if len(user_input) > self.config.max_input_length:
            return ValidationResult(
                is_valid=False,
                risk_level=RiskLevel.MEDIUM,
                message=f"Input too long: {len(user_input)} > {self.config.max_input_length}"
            )
        # 1.2 Prompt Injection检测
        injection_result = await self._detect_prompt_injection(user_input)
        if injection_result.detected:
            await self.audit_logger.log_security_event(
                event_type="prompt_injection",
                session_id=session_id,
                detail=injection_result
            )
            return ValidationResult(
                is_valid=False,
                risk_level=RiskLevel.HIGH,
                message="Prompt injection detected",
                action_taken="blocked"
            )
        return ValidationResult(is_valid=True, risk_level=RiskLevel.LOW, message="OK")
```

---

## 七、审计日志格式

### 7.1 技能体调用日志

```jsonl
{"ts":"2026-06-24T10:00:00Z","event":"skill.invoke.start","run_id":"r-001","skill":"my-skill","capability":"summarize","args_hash":"sha256:abc"}
{"ts":"2026-06-24T10:00:01Z","event":"skill.invoke.success","run_id":"r-001","latency_ms":120,"output_hash":"sha256:def"}
{"ts":"2026-06-24T10:00:01Z","event":"guardrail.permission_denied","run_id":"r-001","skill":"risky-skill","capability":"deploy","reason":"human_approval_required"}
```

### 7.2 最小观测字段

- `run_id`
- `skill`
- `capability`
- `args_hash`
- `output_hash`
- `latency_ms`
- `status`
- `error`

---

## 八、参考来源

### 协议与标准
- ANP（Agent Network Protocol）Technical White Paper：arXiv 2508.00007
- ARD（Agentic Resource Discovery）标准公告：2026-06-22，Google/Microsoft 联合发布
- MCP 官方规范（2025-11-25）：https://modelcontextprotocol.io
- MCP GitHub：https://github.com/modelcontextprotocol

### 企业级平台
- Nacos AI Registry：http://www.nacos.io/ai-registry/
- Google Cloud Agent Registry：https://docs.cloud.google.com/agent-registry/overview
- Google Model Armor Codelab：https://codelabs.developers.google.cn/secure-customer-service-agent

### 框架与实现
- FastMCP：https://github.com/fastmcp/fastmcp
- OpenAI Agents SDK：https://github.com/openai/openai-agents-python
- LangGraph Memory：https://docs.langchain.com/oss/javascript/concepts/memory
- OpenClaw Memory System：社区 RFC 整理

### 社区实践
- Agent Skills 开源标准：https://github.com/agentskills/agentskills
- CSDN《开源 Skill 技术梳理》：2026-06-20
- CSDN《MCP 协议详解》：2026-05-14
- CSDN《AI Agent 安全体系》：2026-05-22
- 掘金《A2A 协议——Agent 与 Agent 如何协作》：2026-06-03

---

## 九、使用建议

1. **优先阅读**：章节一（注册发现）和章节二（MCP 规范）是构建技能体的协议基础
2. **工程参考**：章节五（工程化框架）可直接用于制定团队技能开发规范
3. **安全落地**：章节四（安全护栏）和第 9 章（安全护栏与合规落地）配合使用
4. **代码复用**：章节六的代码片段已针对 Python 3.10+ 优化，可直接集成

---

*本文件将随调研深入持续更新。*
