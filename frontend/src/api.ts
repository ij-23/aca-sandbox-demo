import { PublicClientApplication } from '@azure/msal-browser';

export type Config = {tenant_id: string; spa_client_id: string; api_scope: string; live_execution_enabled: boolean; allowed_repositories: string[]; publication_owner: string; publication_enabled: boolean; retain_sandboxes?: boolean; repository_modes?: string[]; public_metadata_enabled?: boolean; public_execution_blockers?: string[]};
export type Event = {event_id: number; run_id: string; timestamp: string; sandbox_role: string; sandbox_id: string | null; type: string; step_id: string | null; payload: Record<string, unknown>};
export type Finding = {id:string; severity:string; file:string; line:number; explanation:string; recommendation:string; verification_status:string; evidence:string; confidence:string};
export type Report = {status:string; tests_passed?:number; tests_failed?:number; tests_skipped?:number; health?:string; findings?:Finding[]; checks?:{name:string; status:string; exit_code:number|null; duration_ms:number; detail:string}[]; limitations:string[]; diff?:string; publication_status?:string; fixed_repository_url?:string; fixed_commit_sha?:string};
export type Run = {run_id:string; repository_url:string; commit_sha:string; status:string; created_at:string; finished_at?:string; remediation_attempted:boolean; event_delivery_failed?:boolean; cleanup_pending?:boolean; retained_sandbox_ids?:string[]; reports:Record<string,Report>};

let identity: PublicClientApplication | undefined;
let scope = '';
let initialization: Promise<void> | undefined;
export async function initialize(config:Config) {
  if (!config.tenant_id || !config.spa_client_id) return;
  if (initialization) return initialization;
  initialization = initializeOnce(config);
  return initialization;
}
async function initializeOnce(config:Config) {
  scope = config.api_scope;
  identity = new PublicClientApplication({auth:{clientId:config.spa_client_id, authority:`https://login.microsoftonline.com/${config.tenant_id}`, redirectUri:`${location.origin}/`}, cache:{cacheLocation:'sessionStorage'}});
  await identity.initialize();
  const result = await identity.handleRedirectPromise();
  if (result) identity.setActiveAccount(result.account);
  else if (identity.getAllAccounts().length === 1) identity.setActiveAccount(identity.getAllAccounts()[0]);
}
export function signedIn() { return !!identity?.getActiveAccount(); }
export async function login() {
  if (!identity) throw new Error('Entra sign-in has not been configured.');
  await identity.loginRedirect({scopes:[scope]});
}
async function bearer() {
  if (!identity?.getActiveAccount()) throw new Error('Sign in to continue.');
  return (await identity.acquireTokenSilent({scopes:[scope], account:identity.getActiveAccount()!})).accessToken;
}
export async function api<T>(path:string, body?:unknown):Promise<T> {
  const response = await fetch(`/api${path}`, {method:body === undefined?'GET':'POST', headers:{Authorization:`Bearer ${await bearer()}`, ...(body === undefined?{}:{'Content-Type':'application/json'})}, ...(body === undefined?{}:{body:JSON.stringify(body)})});
  if (!response.ok) { const detail = await response.json().catch(()=>({})); throw new Error(typeof detail.detail === 'string' ? detail.detail : `Request failed (${response.status})`); }
  return response.json();
}
export function decodeSSE(buffer:string): {events:Event[]; remainder:string} {
  const frames = buffer.split('\n\n');
  const remainder = frames.pop() ?? '';
  const events:Event[] = [];
  for (const frame of frames) {
    const line = frame.split('\n').find(l=>l.startsWith('data: '));
    if (line) events.push(JSON.parse(line.slice(6)));
  }
  return {events, remainder};
}
export async function observe(id:string, after:number, signal:AbortSignal, receive:(event:Event)=>void, connected:()=>void=()=>{}) {
  const response = await fetch(`/api/runs/${id}/events`, {signal, headers:{Authorization:`Bearer ${await bearer()}`, 'Last-Event-ID':String(after)}});
  if (!response.ok || !response.body) throw new Error(`Event connection failed (${response.status})`);
  connected();
  const reader=response.body.getReader(), decoder=new TextDecoder();
  let buffer='';
  try { while(true) { const {done,value}=await reader.read(); if(done)break; buffer+=decoder.decode(value,{stream:true}); const parsed=decodeSSE(buffer); buffer=parsed.remainder; for(const event of parsed.events)receive(event); } }
  finally {reader.releaseLock();}
}
