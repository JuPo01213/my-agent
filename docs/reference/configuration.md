# 配置参考

本文档描述 my-agent 项目的配置文件结构和用法。

## 配置文件列表

| 文件 | 用途 |
|------|------|
| `config/agents.yaml` | Agent 定义（role / goal / backstory / tools / max_iter / preconditions） |
| `config/relationships.yaml` | 关系定义（priority / termination） |

## agents.yaml 结构

```yaml
agents:
  - id: advisor
    role: 顾问
    goal: 分析问题并提供建议
    backstory: 你是一个经验丰富的顾问
    tools: [search, get_time]
    max_iter: 5
    preconditions: "open_questions == []"
    system_prompt: |
      你是顾问 Agent，负责分析用户问题...
```

## relationships.yaml 结构

```yaml
relationships:
  - strategy: priority
    termination:
      type: max_steps
      value: 10
    agents: [advisor, strategist, writer]
```

## 关键字段说明

- **tools**：Agent 可使用的工具列表，必须显式声明
- **preconditions**：激活条件，支持 `facts.has('key')` 和 `and` 组合
- **strategy**：调度策略，可选 `first_match` / `priority` / `round_robin`
- **termination**：终止条件，支持 `max_steps` / `all_solved` / `custom`

## 搜索后端配置

项目支持可插拔搜索后端，默认通过 StepSearch MCP 提供搜索能力。

### 后端列表

| 后端名称 | 类型 | 配置方式 |
|----------|------|----------|
| `stepsearch` | MCP / HTTP | 环境变量 `STEPSEARCH_MCP_URL` 或 `.vscode/mcp.json` |
| `placeholder` | 本地占位 | 自动注册，无需配置 |
| 自定义后端 | 任意 | 代码注册 `register_backend()` |

### 环境变量

```bash
# StepSearch MCP 配置
STEPSEARCH_MCP_URL=https://api.stepfun.com/step_plan/v1/mcp/web_search/mcp
STEPSEARCH_MCP_HEADS={"Authorization": "Bearer YOUR_TOKEN"}

# 或通过 .vscode/mcp.json 配置（项目已包含）
```

### 代码注册自定义后端

```python
from agent_core.core.search_backends import SearchBackend, SearchResult, register_backend, set_default_backend

class MyBackend(SearchBackend):
    name = "my_backend"
    
    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        # 实现搜索逻辑，调用任意 API 或本地数据
        return [SearchResult(title="...", url="...", snippet="...")]

register_backend(MyBackend())
set_default_backend("my_backend")
```

### 非 MCP 方案

如果不使用 MCP，可以直接实现 `SearchBackend` 接口，通过 HTTP 调用搜索引擎 REST API：

```python
import requests
from agent_core.core.search_backends import SearchBackend, SearchResult

class TavilyHTTPBackend(SearchBackend):
    name = "tavily"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://api.tavily.com/search"
    
    def search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        resp = requests.post(self.endpoint, json={
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results
        })
        data = resp.json()
        return [
            SearchResult(
                title=r["title"],
                url=r["url"],
                snippet=r["content"],
                source=self.name
            )
            for r in data.get("results", [])
        ]
```

## 注意事项

- YAML 中 `tools` 字段必须显式声明，缺省时为 `[]`（LLM 看不到任何工具）
- preconditions 表达式仅支持安全子集，不引入 eval()
- 修改 YAML 即可改变协作流程，零改 Python 代码
- 搜索后端支持热切换：注册新后端后调用 `set_default_backend()` 即可
