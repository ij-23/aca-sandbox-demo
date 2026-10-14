// Trusted SDK controller runs inside the disposable Sandbox, never in FastAPI.
import { CopilotClient, RuntimeConnection } from './sdk/node_modules/@github/copilot-sdk/dist/index.js';
import { readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';
import { setTimeout as delay } from 'node:timers/promises';

const input = JSON.parse(readFileSync('input.json', 'utf8'));
const name = input.workflow_name ?? 'remediation';
if (!['remediation', 'credential-probe'].includes(name)) throw Error('Untrusted extension');
const client = new CopilotClient({
  connection: RuntimeConnection.forStdio({path:resolve('cli/copilot'),args:['--experimental','--no-auto-update']}),
  workingDirectory:process.cwd(), mode:'empty', baseDirectory:resolve('sdk-session'),
});
let session;
try {
  session = await client.createSession({
    workingDirectory:process.cwd(), enableConfigDiscovery:true, requestExtensions:true,
    enableExperimentalMode:true, availableTools:[],
    onPermissionRequest: request => {
      const allowed = request.managedApprovalRequired !== true
        && request.kind === 'extension-env-access'
        && [name, `project:${name}`].includes(request.extensionName)
        && request.environmentVariables?.length === 1
        && request.environmentVariables[0] === 'COPILOT_GITHUB_TOKEN';
      console.log(JSON.stringify({type:'permission.decision',kind:request.kind,allowed}));
      return allowed ? {kind:'approve-once'} : {kind:'reject'};
    },
  });
  session.on(event => {
    // Keep native metadata only. Source/prompts/results use separate contracts.
    if (/^(workflow\.|subagent\.|session\.extensions_loaded)/.test(event.type))
      console.log(JSON.stringify({type:event.type}));
  });
  for(let i=0;i<20;i++) {
    const list = await session.rpc.extensions.list();
    console.log(JSON.stringify({type:'extension.status', list}));
    if (list.extensions.some(extension => extension.id === `project:${name}` && extension.status === 'running')) break;
    await delay(500);
  }
  const run = await session.workflow.run(name,{args:input,notifyOnComplete:false});
  console.log(JSON.stringify({type:'workflow.result',status:run.status}));
  if(run.status !== 'completed') throw Error('Workflow did not complete');
  writeFileSync('result.json',JSON.stringify(run.result));
} finally {
  if(session) await session.disconnect();
  await client.stop();
}
