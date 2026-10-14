import { defineWorkflow, joinSession } from '@github/copilot-sdk/extension';
import { execFile } from 'node:child_process';
const workflow=defineWorkflow({meta:{name:'credential-probe',description:'Read-only same-PAT owner check',phases:[]},run:async ctx=>{
  if(ctx.args.publication_probe === true) return await ctx.step('verify.private.publication',()=>new Promise((resolve,reject)=>{
    execFile('python3',['publication-probe.py', ...(ctx.args.retry_owned_empty === true ? ['retry-owned-empty'] : [])],{timeout:160000,maxBuffer:10000},(error,stdout)=>error?reject(Error('Publication probe failed')):resolve(JSON.parse(stdout)));
  }));
  return await ctx.step('verify.owner',async()=>{
    const token=process.env.COPILOT_GITHUB_TOKEN;
    if(!token)return {credential_set:false};
    const response=await fetch('https://api.github.com/user',{headers:{Authorization:`Bearer ${token}`,Accept:'application/vnd.github+json'},signal:AbortSignal.timeout(15000),redirect:'error'});
    if(response.status!==200)return {credential_set:true,http_status:response.status};
    const user=await response.json();
    return {credential_set:true,http_status:200,login:user.login,account_type:user.type};
  });
}});
await joinSession({workflows:[workflow],requestedEnvironmentVariables:['COPILOT_GITHUB_TOKEN']});
