/**
 * agent_core/static/bubble-adapter.js
 *
 * 将前端事件契约中的标准事件映射为 Vue 气泡组件所需的数据结构。
 * 保持 bubble.html 不感知任何后端字段，仅处理前端标准 type。
 */

/**
 * 将一个标准前端事件映射为 Vue bubble 所需对象。
 * @param {object} event - 标准前端事件，必有 type/ts/run_id
 * @returns {object} bubble 数据
 */
function mapEventToBubble(event) {
  const type = event.type || event.kind || 'system';

  // 基础属性
  const bubble = {
    id: event.ts + '-' + (event.agent || event.name || 'evt') + '-' + Math.random(),
    type: 'system',
    content: '',
    name: '',
    args: '',
    observation: '',
    meta: event.meta || formatMeta(event),
  };

  switch (type) {
    case 'user.input':
      bubble.type = 'user';
      bubble.content = event.content || '';
      break;

    case 'agent.activate':
      bubble.type = 'system';
      bubble.content = formatAgentActivate(event);
      break;

    case 'llm.thought':
      bubble.type = 'thinking';
      bubble.content = event.content || '';
      break;

    case 'tool.call':
      bubble.type = 'tool';
      bubble.name = event.name || '';
      bubble.args = formatArgs(event.args);
      break;

    case 'tool.observation':
      bubble.type = 'tool';
      bubble.name = event.name || '';
      bubble.observation = typeof event.observation === 'string'
        ? event.observation
        : JSON.stringify(event.observation, null, 2);
      break;

    case 'llm.final':
      bubble.type = 'final';
      bubble.content = event.content || '';
      break;

    case 'run.done':
      bubble.type = 'system';
      bubble.content = 'Run finished · status=' + (event.status || 'unknown');
      break;

    default:
      bubble.type = 'system';
      bubble.content = JSON.stringify(event);
  }

  return bubble;
}

/**
 * 格式化 agent.activate 气泡内容
 */
function formatAgentActivate(event) {
  const can = Array.isArray(event.can_activate) ? event.can_activate.join(', ') : '';
  return (
    'Agent activate\n' +
    '- agent: ' + (event.agent || '') + '\n' +
    '- role: ' + (event.role || '') + '\n' +
    '- step: ' + (event.step || 0) + '\n' +
    (can ? '- can_activate: ' + can + '\n' : '')
  );
}

/**
 * 格式化 tool args 用于展示
 */
function formatArgs(args) {
  if (!args) return '';
  if (typeof args === 'string') return args;
  try {
    return JSON.stringify(args, null, 2);
  } catch (e) {
    return String(args);
  }
}

/**
 * 从事件字段生成 meta 字符串
 */
function formatMeta(event) {
  const parts = [];
  if (event.ts) parts.push(event.ts.replace('T', ' ').replace('Z', ''));
  if (event.agent) parts.push(event.agent);
  if (event.step !== undefined) parts.push('step=' + event.step);
  if (event.name) parts.push(event.name);
  return parts.join(' · ');
}
