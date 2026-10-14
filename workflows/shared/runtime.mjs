// Trusted control code. Uploaded outside the submitted repository.
import { appendFileSync } from 'node:fs';
import { execFile } from 'node:child_process';
export function runtime(ctx) {
  const input = ctx.args;
  if (!/^[0-9a-f-]{36}$/.test(input.run_id) || !/^[0-9a-f]{40}$/.test(input.commit_sha)) throw Error('Invalid provenance');
  const emit = (type, step_id, payload) => appendFileSync('events.jsonl', JSON.stringify({
    run_id: input.run_id, workflow_run_id: ctx.runId, timestamp: new Date().toISOString(), type, step_id, payload,
  }) + '\n');
  const command = async (action, data = {}) => {
    // Argument data uses stdin, never interpolated into shell code.
    const child = execFile('python3', ['operations.py', action], {
      timeout: 240000, killSignal: 'SIGKILL', maxBuffer: 300000, signal: ctx.signal,
    });
    child.stdin.end(JSON.stringify({ ...input, workflow_run_id: ctx.runId, ...data }));
    const result = await new Promise((resolve, reject) => {
      let output = ''; child.stdout.on('data', b => { output += b; });
      child.on('error', reject);
      child.on('close', code => code === 0 ? resolve(output) : reject(Error(`Trusted operation ${action} failed (${code})`)));
    });
    return JSON.parse(result);
  };
  const step = async (name, fn, kind = 'deterministic') => {
    const start = Date.now(); emit('step.started', name, { status: 'running', kind });
    try {
      const result = await ctx.step(name, fn);
      emit('step.completed', name, { status: result?.status ?? 'passed', kind, duration_ms: Date.now() - start });
      return result;
    } catch (error) { emit('step.failed', name, { status: 'failed', kind, duration_ms: Date.now() - start }); throw error; }
  };
  const agent = async (name, prompt, schema) => {
    emit('step.started', name, {status: 'running', kind: 'ai'});
    const start = Date.now();
    try {
      const result = await ctx.agent(prompt, {label: name, schema});
      if (result === null) throw Error('Agent returned no structured result');
      emit('step.completed', name, {status: 'passed', kind: 'ai', duration_ms: Date.now() - start});
      return result;
    } catch (error) { emit('step.failed', name, {status: 'failed', kind: 'ai'}); throw error; }
  };
  return { input, emit, command, step, agent };
}
export const limits = { maxConcurrentSubagents: 1, maxTotalSubagents: 3, timeoutSeconds: 720 };
