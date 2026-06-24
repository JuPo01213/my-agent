/**
 * agent_core/static/bubble-sample.js
 *
 * 前端事件契约样本数据，基于真实实验日志简化而成。
 * 遵循 agent_core/frontend/events.py 的 schema：
 *   - 必有 type / ts / run_id
 *   - 时间戳为模拟 ISO-8601
 *   - 字段名统一 snake_case
 */

const SAMPLE_RUN_ID = 'sample-2026-06-24-01';

const SAMPLE_EVENTS = [
  // 1. 用户输入
  {
    type: 'user.input',
    ts: '2026-06-24T10:23:00.000Z',
    run_id: SAMPLE_RUN_ID,
    content: '200人研发团队6个月完成AI转型，预算1500万，请给出5项核心能力、预算分配和里程碑。',
    meta: '10:23 · 用户',
  },

  // 2. 调度器选中 advisor
  {
    type: 'agent.activate',
    ts: '2026-06-24T10:23:00.120Z',
    run_id: SAMPLE_RUN_ID,
    agent: 'advisor',
    role: '资深AI转型顾问',
    step: 0,
    can_activate: ['advisor'],
    meta: '10:23 · Activate',
  },

  // 3. advisor 思考
  {
    type: 'llm.thought',
    ts: '2026-06-24T10:23:00.240Z',
    run_id: SAMPLE_RUN_ID,
    agent: 'advisor',
    step: 1,
    content: '用户要求预算分配并验证总和。我需要先列出5项能力，再计算各项百分比。',
    meta: '10:23 · Thought',
  },

  // 4. 工具调用：calculator
  {
    type: 'tool.call',
    ts: '2026-06-24T10:23:00.360Z',
    run_id: SAMPLE_RUN_ID,
    agent: 'advisor',
    step: 1,
    name: 'calculator',
    args: { expression: '600 / 1500 * 100' },
    meta: '10:23 · Action',
  },

  // 5. 工具观察
  {
    type: 'tool.observation',
    ts: '2026-06-24T10:23:00.500Z',
    run_id: SAMPLE_RUN_ID,
    agent: 'advisor',
    step: 1,
    name: 'calculator',
    observation: '计算结果：40.0',
    meta: '10:23 · Observation',
  },

  // 6. advisor 继续思考
  {
    type: 'llm.thought',
    ts: '2026-06-24T10:23:00.620Z',
    run_id: SAMPLE_RUN_ID,
    agent: 'advisor',
    step: 2,
    content: '招聘 40%，继续计算培训、工具、咨询的占比。',
    meta: '10:23 · Thought',
  },

  // 7. advisor 最终答案
  {
    type: 'llm.final',
    ts: '2026-06-24T10:23:45.000Z',
    run_id: SAMPLE_RUN_ID,
    agent: 'advisor',
    step: 6,
    content: '## 5项核心AI能力\n1. LLM应用开发与工程化\n2. RAG开发与优化\n3. AI系统架构设计\n4. 模型微调与适配\n5. MLOps与AI工程化\n\n## 预算分配（已验证）\n- 招聘：40%\n- 培训：25%\n- 工具：20%\n- 外部咨询：15%\n\n## 里程碑\n- 阶段1（第1-2月）：基础能力建设\n- 阶段2（第3-4月）：规模化应用\n- 阶段3（第5-6月）：优化迭代与组织固化',
    meta: '10:23 · Final',
  },

  // 8. 调度器选中 strategist
  {
    type: 'agent.activate',
    ts: '2026-06-24T10:23:45.200Z',
    run_id: SAMPLE_RUN_ID,
    agent: 'strategist',
    role: '转型策略规划专家',
    step: 1,
    can_activate: ['strategist'],
    meta: '10:23 · Activate',
  },

  // 9. strategist 思考
  {
    type: 'llm.thought',
    ts: '2026-06-24T10:23:45.320Z',
    run_id: SAMPLE_RUN_ID,
    agent: 'strategist',
    step: 1,
    content: '基于 advisor 的事实，我需要重新梳理执行计划与风险控制点，给出可落地的6个月推进节奏。',
    meta: '10:23 · Thought',
  },

  // 10. 工具调用：calculator
  {
    type: 'tool.call',
    ts: '2026-06-24T10:23:45.440Z',
    run_id: SAMPLE_RUN_ID,
    agent: 'strategist',
    step: 1,
    name: 'calculator',
    args: { expression: '600 / 1500 * 100' },
    meta: '10:23 · Action',
  },

  // 11. 工具观察
  {
    type: 'tool.observation',
    ts: '2026-06-24T10:23:45.560Z',
    run_id: SAMPLE_RUN_ID,
    agent: 'strategist',
    step: 1,
    name: 'calculator',
    observation: '计算结果：40.0',
    meta: '10:23 · Observation',
  },

  // 12. strategist 最终答案
  {
    type: 'llm.final',
    ts: '2026-06-24T10:23:52.000Z',
    run_id: SAMPLE_RUN_ID,
    agent: 'strategist',
    step: 1,
    content: '执行计划：\n- 第1月：完成核心团队20-30人AI能力认证\n- 第2月：落地3-5个试点场景\n- 第3月：建成统一AI开发平台\n- 第4月：推广至50%研发团队\n- 第5月：建立MLOps体系\n- 第6月：完成全员技能评估与组织架构调整',
    meta: '10:23 · Final',
  },

  // 13. 调度器选中 writer
  {
    type: 'agent.activate',
    ts: '2026-06-24T10:23:52.200Z',
    run_id: SAMPLE_RUN_ID,
    agent: 'writer',
    role: '技术文档写作专家',
    step: 1,
    can_activate: ['writer'],
    meta: '10:23 · Activate',
  },

  // 14. writer 最终答案
  {
    type: 'llm.final',
    ts: '2026-06-24T10:24:05.000Z',
    run_id: SAMPLE_RUN_ID,
    agent: 'writer',
    step: 1,
    content: '## 200人研发团队6个月AI转型方案（正式版）\n\n...（writer 输出略，用于展示最终答案气泡）...',
    meta: '10:24 · Final',
  },

  // 15. 整次 run 结束
  {
    type: 'run.done',
    ts: '2026-06-24T10:24:10.000Z',
    run_id: SAMPLE_RUN_ID,
    status: 'solved',
    meta: '10:24 · Done',
  },
];
