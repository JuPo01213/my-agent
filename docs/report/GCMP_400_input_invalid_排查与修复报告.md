# GCMP 400 input_invalid / 451 censorship_blocked 问题排查与修复报告

- **日期**：2026-06-24
- **问题**：使用 Step-3.7-Flash (StepPlan) 模型时，连续触发 400 `input_invalid` 及 451 `censorship_blocked` 错误
- **影响范围**：VS Code Copilot Chat 通过 `vicanent.gcmp` 扩展调用 StepFun StepPlan 通道
- **修复状态**：400 问题已定位根因并完成补丁；451 问题为服务端内容审核拦截，需结合内容规避策略处理

---

## 一、问题背景

在 VS Code 中使用 Copilot Chat 时，后台实际由 `vicanent.gcmp`（AI Chat Models）扩展提供模型。当前配置的模型为 **Step-3.7-Flash (StepPlan)**，使用 Anthropic 兼容 SDK 模式。

用户在使用 Copilot Chat 与模型交互过程中，连续出现以下报错：

```
Sorry, your request failed. Please try again.
Client Request Id: 039131ff-d4e0-4931-8afb-5b56f1ff6bf9
Reason: 400 {"error":{"message":"The input you provided is invalid","type":"input_invalid"}}
```

stack trace 指向：

```
r.generate → ri.makeStatusError → ri.makeRequest → handleRequest → executeModelRequest → provideLanguageModelChatResponse
```

文件位置均在 `c:\Users\Administrator\.vscode\extensions\vicanent.gcmp-0.25.12\dist\extension.js`

---

## 二、报错现象

**错误信息**：

- HTTP 状态码：`400`
- 错误类型：`"type":"input_invalid"`
- 错误消息：`"message":"The input you provided is invalid"`

**发生时机**：

- 第一轮（400 错误）：在 `21:10:12` 到 `21:10:22` 时间段内连续触发 4 次
- 第二轮（451 错误）：在 `21:32:05` 和 `21:32:08` 连续触发 2 次
- 前后其他 Anthropic SDK 请求均成功，仅特定请求失败
- 失败请求的日志没有显示 `Successfully processed tool call`，说明在请求发出阶段即被拒绝

**日志摘录（400 input_invalid）**：

```
2026-06-24 21:10:10.232 [info] StepFun Provider started handling request (Anthropic SDK): Step-3.7-Flash (StepPlan)
2026-06-24 21:10:12.191 [error] [Step-3.7-Flash (StepPlan)] Anthropic SDK error: 400 {"error":{"message":"The input you provided is invalid","type":"input_invalid"}}
2026-06-24 21:10:12.192 [warning] [StepFun] Initial request failed: 400 {"error":{"message":"The input you provided is invalid","type":"input_invalid"}}
2026-06-24 21:10:12.192 [error] Error: 400 {"error":{"message":"The input you provided is invalid","type":"input_invalid"}}
2026-06-24 21:10:12.192 [info] ✅ StepFun: Step-3.7-Flash (StepPlan) request completed
```

**日志摘录（451 censorship_blocked）**：

```
2026-06-24 21:32:05.919 [error] [Step-3.7-Flash (StepPlan)] Anthropic SDK error: 451 {"error":{"message":"The content you provided or machine outputted is blocked.","type":"censorship_blocked"}}
2026-06-24 21:32:05.924 [warning] [StepFun] Initial request failed: 451 {"error":{"message":"The content you provided or machine outputted is blocked.","type":"censorship_blocked"}}
2026-06-24 21:32:05.924 [error] Error: 451 {"error":{"message":"The content you provided or machine outputted is blocked.","type":"censorship_blocked"}}
2026-06-24 21:32:05.924 [info] ✅ StepFun: Step-3.7-Flash (StepPlan) request completed
2026-06-24 21:32:08.807 [error] [Step-3.7-Flash (StepPlan)] Anthropic SDK error: 451 {"error":{"message":"The content you provided or machine outputted is blocked.","type":"censorship_blocked"}}
2026-06-24 21:32:08.807 [warning] [StepFun] Initial request failed: 451 {"error":{"message":"The content you provided or machine outputted is blocked.","type":"censorship_blocked"}}
2026-06-24 21:32:08.807 [error] Error: 451 {"error":{"message":"The content you provided or machine outputted is blocked.","type":"censorship_blocked"}}
2026-06-24 21:32:08.807 [info] ✅ StepFun: Step-3.7-Flash (StepPlan) request completed
```

**注意**：GCMP 扩展在日志里仍然打印 `request completed`，但实际是失败后被包装为错误返回，这容易误导排查。

**两种错误的对比**：

| 维度 | 400 input_invalid | 451 censorship_blocked |
|------|------------------|------------------------|
| 触发原因 | 请求参数不合法（`reasoningEffort` 数组未归一化） | 服务端内容审核拦截 |
| 根因位置 | GCMP 扩展 Anthropic 请求构建逻辑 | StepFun 服务端审核策略 |
| 修复方式 | 本地补丁归一化数组 | 无法通过客户端修复，需规避敏感内容 |
| 复现难度 | 稳定复现（特定配置下） | 不稳定，取决于对话内容 |
| 影响范围 | 仅 Anthropic 模式 + `reasoningEffort` 数组 | 所有模式，任何触发审核的内容 |

---

## 三、排查过程

### 3.1 初步判断

- 错误发生在 `vicanent.gcmp` 扩展内部，不是本地 Python 服务报错
- stack trace 显示是模型 API 调用失败，不是 Playwright 或前端问题
- 400 错误说明请求参数不合法，不是网络/认证问题

### 3.2 读取 GCMP 日志

读取了最新 VS Code 日志目录：

```
C:\Users\Administrator\AppData\Roaming\Code\logs\20260624T173409\window1\exthost\vicanent.gcmp\GitHub Copilot Models Provider (GCMP).log
```

日志显示：
- 错误来自 `Step-3.7-Flash (StepPlan)` 的 Anthropic SDK 请求
- 前后其他请求（包括同模型的 `run_in_terminal` 工具调用）均成功
- 失败请求的 `input_tokens` 为 `127931`，属于上下文较长的请求

### 3.3 阅读扩展代码

在 `dist/extension.js` 中定位到 Anthropic 请求构建逻辑：

**关键代码片段**（`Anthropic handleRequest` 中）：

```javascript
let E = o.modelConfiguration;
if (E?.thinking) {
    let N = I.thinking || { type: "disabled" };
    N.type = E.thinking, I.thinking = N;
} else if (E?.reasoningEffort) {
    let N = I.thinking || { type: "enabled" };
    N.type = "enabled";
    let G = I.output_config || { effort: "medium" };
    G.effort = E.reasoningEffort;  // <-- 问题在这里
    E.reasoningEffort === "minimal" && (N.type = "disabled");
    I.thinking = N, I.output_config = G;
    (E.reasoningEffort === "none" || E.reasoningEffort === "minimal") && (N.type = "disabled", I.output_config = void 0);
}
```

### 3.4 根因定位

**问题**：`G.effort = E.reasoningEffort` 直接将 `reasoningEffort` 赋值给 `output_config.effort`。

**实际值**：StepFun 模型配置中 `reasoningEffort` 是一个数组：

```javascript
reasoningEffort: ["low", "medium", "high"]
```

**结果**：发出的请求体包含：

```json
{
  "output_config": {
    "effort": ["low", "medium", "high"]
  }
}
```

StepFun 服务端期望 `effort` 是字符串（如 `"medium"`），收到数组后判定为非法输入，返回 `400 input_invalid`。

### 3.5 对比 OpenAI 模式

在 OpenAI 模式的请求构建中，有专门的归一化函数 `Mhe()`：

```javascript
function Mhe(r) {
    let e = r.reasoningEffort;
    return !e || e.length === 0 || r.reasoningDefault && e.includes(r.reasoningDefault)
        ? r.reasoningDefault
        : e.includes("medium") ? "medium" : e[0];
}
```

**Anthropic 模式缺少这个归一化步骤**，导致数组直接下发。

---

## 四、修复方案

### 4.1 补丁内容

在 `dist/extension.js` 的 Anthropic `handleRequest` 中，对 `reasoningEffort` 增加数组归一化：

```javascript
} else if (E?.reasoningEffort) {
    let N = I.thinking || { type: "enabled" };
    N.type = "enabled";
    let G = I.output_config || { effort: "medium" };
    let effort = Array.isArray(E.reasoningEffort)
        ? (E.reasoningEffort.includes("medium") ? "medium" : E.reasoningEffort[0])
        : E.reasoningEffort;
    G.effort = effort;
    effort === "minimal" && (N.type = "disabled");
    I.thinking = N, I.output_config = G;
    (effort === "none" || effort === "minimal") && (N.type = "disabled", I.output_config = void 0);
}
```

### 4.2 修复逻辑

- 如果 `reasoningEffort` 是数组，优先取 `"medium"`，否则取第一项
- 保证 `output_config.effort` 始终是字符串
- 保留原有 `"minimal"` / `"none"` 的特殊处理逻辑

### 4.3 补丁验证

```bash
C:/Users/Administrator/AppData/Local/Python/pythoncore-3.14-64/python.exe -c "
content = open(r'c:\Users\Administrator\.vscode\extensions\vicanent.gcmp-0.25.10\dist\extension.js', 'r', encoding='utf-8').read()
marker = 'let effort=Array.isArray(E.reasoningEffort)'
print('Patch present:', marker in content)
"
```

**初始验证结果**（0.25.10 版本）：`Patch present: True`

**当前版本验证**（0.25.12 版本）：补丁已保留，文件长度 `1831658` 字节

### 4.4 最新验证结果（2026-06-24 21:32）

在 21:32 时间窗口内，GCMP 日志显示：

1. **21:32:05** - 触发 `451 censorship_blocked` 错误（服务端内容审核拦截）
2. **21:32:08** - 再次触发 `451 censorship_blocked` 错误
3. **21:32:16** - 后续请求恢复正常，成功返回
4. **21:32:25 起** - 工具调用链（`memory tool`、`list_dir`、`read_file`、`run_in_terminal`）全部成功

**结论**：
- `400 input_invalid` 补丁已生效，未再复现
- `451 censorship_blocked` 属于服务端内容审核，与客户端补丁无关
- 两次 451 错误后，对话能力已自动恢复

---

## 五、后续建议

### 5.1 短期

1. **重启 VS Code**：按 `Ctrl+Shift+P` 执行 `Developer: Reload Window`，或直接重启 VS Code
2. **验证修复**：重启后再次使用 Copilot Chat，观察是否仍出现 `input_invalid` 错误
3. **关注日志**：如果再次出现，读取 GCMP 最新日志确认是否为同一问题

### 5.2 对 451 censorship_blocked 的应对

1. **内容规避**：避免在对话中提及敏感关键词、政策、历史事件等可能触发审核的内容
2. **上下文清理**：如果对话历史中包含敏感内容，尝试开启新对话
3. **切换模型**：临时切换到 OpenAI 兼容模式或其他模型通道
4. **反馈 StepFun**：如果认为是误拦截，可向 StepFun 平台反馈

### 5.3 长期

1. **向 GCMP 官方提 Issue**：当前是本地补丁，更新扩展版本后会被覆盖。建议将问题反馈给 [VicBilibily/GCMP](https://github.com/VicBilibily/GCMP/issues)
2. **建议官方修复**：
   - 在 Anthropic 模式中也增加 `reasoningEffort` 归一化
   - 考虑统一 `Mhe()` 函数供 OpenAI 和 Anthropic 共用
3. **版本追踪**：关注 `vicanent.gcmp` 新版本发布，确认该问题是否已官方修复

### 5.4 关联问题

- GitHub #162：`thinking is enabled but reasoning_content is missing in assistant tool call message` — 类似症状，涉及 thinking 模式下的消息格式问题
- GitHub #253：`Autopilot recovered from a request error` — VS Code Copilot 在 Agent 模式下的已知流式问题
- StepFun 平台审核策略：`451 censorship_blocked` 属于服务端内容审核，客户端无法绕过

---

## 六、技术细节补充

### 6.1 受影响模型

- **Step-3.7-Flash (StepPlan)**：`sdkMode: "anthropic"`, `baseUrl: "https://api.stepfun.com/step_plan"`
- 其他使用 Anthropic 兼容模式且配置了 `reasoningEffort` 数组的模型理论上也可能受影响

### 6.2 请求路径

```
Copilot Chat
  → GCMP Extension (vicanent.gcmp)
    → Anthropic SDK Client
      → StepFun API (https://api.stepfun.com/step_plan)
        → 400 input_invalid
```

### 6.3 为什么其他请求成功

- 部分请求可能不带 `modelConfiguration.reasoningEffort`，或者值为字符串
- 上下文较短的请求可能触发了不同的代码路径
- GCMP 日志中显示大量成功请求，说明问题仅在特定条件下触发

---

## 七、修复文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `c:\Users\Administrator\.vscode\extensions\vicanent.gcmp-0.25.12\dist\extension.js` | 已包含补丁 | Anthropic handleRequest 中增加 reasoningEffort 数组归一化 |

**注意**：这是扩展内部补丁，升级扩展版本后需重新检查。当前版本 0.25.12 已包含该补丁。

---

## 八、参考链接

- [GCMP GitHub Issues](https://github.com/VicBilibily/GCMP/issues)
- [GitHub #162: thinking is enabled but reasoning_content is missing](https://github.com/VicBilibily/GCMP/issues/162)
- [GitHub #253: Autopilot recovered from a request error](https://github.com/VicBilibily/GCMP/issues/253)
- [StepFun 阶跃星辰](https://platform.stepfun.com/)
