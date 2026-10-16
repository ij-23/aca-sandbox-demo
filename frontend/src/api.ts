import { InteractionRequiredAuthError, PublicClientApplication } from '@azure/msal-browser';

export type Config = {tenant_id: string; spa_client_id: string; api_scope: string; live_execution_enabled: boolean; allowed_repositories: string[]; publication_owner: string; publication_enabled: boolean; retain_sandboxes?: boolean};
export type Event = {event_id: number; run_id: string; timestamp: string; sandbox_role: string; sandbox_id: string | null; type: string; step_id: string | null; payload: Record<string, unknown>};
export type Finding = {id:string; severity:string; file:string; line:number; explanation:string; recommendation:string; verification_status:string; evidence:string; confidence:string};
export type Report = {status:string; tests_passed?:number; tests_failed?:number; tests_skipped?:number; health?:string; findings?:Finding[]; checks?:{name:string; status:string; exit_code:number|null; duration_ms:number; detail:string}[]; limitations:string[]; diff?:string; publication_status?:string; fixed_repository_url?:string; fixed_commit_sha?:string};
export type Run = {run_id:string; repository_url:string; commit_sha:string; status:string; created_at:string; finished_at?:string; remediation_attempted:boolean; event_delivery_failed?:boolean; cleanup_pending?:boolean; retained_sandbox_ids?:string[]; reports:Record<string,Report>};

export type SessionState = 'signed_out' | 'signed_in' | 'expired';
export class AuthenticationRequired extends Error {
  constructor() { super('Your Microsoft session has expired or needs attention. Sign in again to continue.'); }
}
let identity: PublicClientApplication | undefined;
let scope = '';
let initialization: Promise<void> | undefined;
let session: SessionState = 'signed_out';
let generation = 0;
let interacting = false;
const listeners = new Set<() => void>();
export function sessionState() { return session; }
export function subscribeSession(listener:()=>void) { listeners.add(listener); return ()=>{listeners.delete(listener);}; }
function setSession(value:SessionState) {
  if (session === value) return;
  session = value;
  if (value !== 'signed_in') generation++;
  for (const listener of listeners) listener();
}
export async function initialize(config:Config) {
  if (!config.tenant_id || !config.spa_client_id) return;
  if (!initialization) initialization = initializeOnce(config).catch(()=>{
    initialization = undefined;
    setSession('signed_out');
    throw new Error('Microsoft sign-in could not be initialized. Try signing in again.');
  });
  return initialization;
}
async function initializeOnce(config:Config) {
  scope = config.api_scope;
  identity = new PublicClientApplication({auth:{clientId:config.spa_client_id, authority:`https://login.microsoftonline.com/${config.tenant_id}`, redirectUri:`${location.origin}/`, postLogoutRedirectUri:`${location.origin}/`}, cache:{cacheLocation:'sessionStorage'}});
  await identity.initialize();
  const result = await identity.handleRedirectPromise();
  if (result) identity.setActiveAccount(result.account);
  else if (identity.getAllAccounts().length === 1) identity.setActiveAccount(identity.getAllAccounts()[0]);
  setSession(identity.getActiveAccount() ? 'signed_in' : 'signed_out');
}
export function signedIn() { return session === 'signed_in'; }
export async function login() {
  if (!identity || !initialization) throw new Error('Entra sign-in has not been configured.');
  await initialization;
  if (interacting) return;
  interacting = true;
  try { await identity.loginRedirect({scopes:[scope], prompt:'select_account'}); }
  catch { throw new Error('Microsoft sign-in could not start. Reload the page and try again.'); }
  finally { interacting = false; }
}
export async function logout() {
  if (!identity || !initialization) return;
  await initialization;
  if (interacting) return;
  interacting = true;
  const account = identity.getActiveAccount();
  setSession('signed_out');
  try { await identity.logoutRedirect({account, postLogoutRedirectUri:`${location.origin}/`}); }
  catch {
    // Use MSAL's supported cache API; never wipe unrelated application storage.
    try { await identity.clearCache({account}); }
    catch { throw new Error('Microsoft sign-out could not clear this app session. Reload the page and try again.'); }
    finally { identity.setActiveAccount(null); }
    throw new Error('Signed out of this app. Microsoft sign-out could not finish; you can sign in again.');
  } finally { interacting = false; }
}
function requireCurrent(requestGeneration:number) {
  if (requestGeneration !== generation || !signedIn()) throw new AuthenticationRequired();
}
async function bearer(forceRefresh=false) {
  if (!signedIn()) throw new AuthenticationRequired();
  if (!identity?.getActiveAccount()) { setSession('expired'); throw new AuthenticationRequired(); }
  const requestGeneration = generation;
  try {
    const result = await identity.acquireTokenSilent({scopes:[scope], account:identity.getActiveAccount()!, forceRefresh});
    requireCurrent(requestGeneration);
    return result.accessToken;
  } catch (error) {
    requireCurrent(requestGeneration);
    if (error instanceof InteractionRequiredAuthError) {
      setSession('expired');
      throw new AuthenticationRequired();
    }
    // MSAL exception text can contain identity details. Do not render it.
    throw new Error('Microsoft session renewal is temporarily unavailable. Retry or sign out and sign in again.');
  }
}
async function authorizedFetch(path:string, init:RequestInit={}) {
  const requestGeneration = generation;
  const send = async(forceRefresh=false) => {
    const token = await bearer(forceRefresh);
    requireCurrent(requestGeneration);
    const response = await fetch(path,{...init, headers:{...init.headers, Authorization:`Bearer ${token}`}});
    requireCurrent(requestGeneration);
    return response;
  };
  let response = await send();
  // Retry read-only requests once with a fresh token. Never replay a mutation.
  if (response.status === 401 && (!init.method || init.method === 'GET')) {
    await response.body?.cancel();
    response = await send(true);
  }
  if (response.status === 401) {
    setSession('expired');
    throw new AuthenticationRequired();
  }
  return response;
}
export async function api<T>(path:string, body?:unknown):Promise<T> {
  const requestGeneration = generation;
  const response = await authorizedFetch(`/api${path}`, {method:body === undefined?'GET':'POST', ...(body === undefined?{}:{headers:{'Content-Type':'application/json'},body:JSON.stringify(body)})});
  if (!response.ok) { const detail = await response.json().catch(()=>({})); throw new Error(typeof detail.detail === 'string' ? detail.detail : `Request failed (${response.status})`); }
  const result = await response.json();
  requireCurrent(requestGeneration);
  return result;
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
  const response = await authorizedFetch(`/api/runs/${id}/events`, {signal, headers:{'Last-Event-ID':String(after)}});
  if (!response.ok || !response.body) throw new Error(`Event connection failed (${response.status})`);
  connected();
  const reader=response.body.getReader(), decoder=new TextDecoder();
  let buffer='';
  try { while(true) { const {done,value}=await reader.read(); if(done)break; buffer+=decoder.decode(value,{stream:true}); const parsed=decodeSSE(buffer); buffer=parsed.remainder; for(const event of parsed.events)receive(event); } }
  finally {reader.releaseLock();}
}
