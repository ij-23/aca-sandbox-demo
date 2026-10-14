import { defineWorkflow, joinSession } from '@github/copilot-sdk/extension';
import { runtime, limits } from '../../runtime.mjs';
const workflow = defineWorkflow({meta: {name: 'build-validation', phases: [], argsSchema: {type:"object"}, description: 'Bounded Python FastAPI build, pytest and conditional localhost health', limits}, run: async ctx => {
  const r = runtime(ctx); r.emit('workflow.started', null, {transport: 'sdk_file_polling'});
  await r.step('checkout', () => r.command('checkout'));
  const report = await r.step('validate', () => r.command('validate'));
  r.emit('workflow.branch', 'runtime.gate', {reason: report.health === 'skipped' ? 'Required build/test validation failed; runtime skipped' : 'Validation passed; localhost health checked'});
  const analysis = await r.agent('agent.analysis', 'Explain the actual validation result and its limitations. Do not claim unrun checks passed. Do not use tools. Return a concise summary. Evidence: ' + JSON.stringify(report),
    {type:'object', required:['summary'], properties:{summary:{type:'string',maxLength:2000}}});
  r.emit('workflow.log', 'agent.analysis', {text: String(analysis.summary).slice(0,2000)});
  r.emit('workflow.completed', 'complete', {status:report.status}); return report;
}});
await joinSession({workflows:[workflow]});
