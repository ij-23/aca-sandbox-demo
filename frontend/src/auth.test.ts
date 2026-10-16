import { beforeEach, afterEach, describe, expect, it, vi } from 'vitest';

// Explicit unit-test identity/transport doubles. No Entra token or Azure operation.
const msal = vi.hoisted(()=>({
  account: {homeAccountId:'test-account'} as {homeAccountId:string}|null,
  initialize:vi.fn(), handleRedirectPromise:vi.fn(), acquireTokenSilent:vi.fn(),
  loginRedirect:vi.fn(), logoutRedirect:vi.fn(), clearCache:vi.fn(),
}));
vi.mock('@azure/msal-browser',()=>({
  InteractionRequiredAuthError:class extends Error {},
  PublicClientApplication:class {
    initialize=msal.initialize;
    handleRedirectPromise=msal.handleRedirectPromise;
    acquireTokenSilent=msal.acquireTokenSilent;
    loginRedirect=msal.loginRedirect;
    logoutRedirect=msal.logoutRedirect;
    clearCache=msal.clearCache;
    getActiveAccount(){return msal.account;}
    getAllAccounts(){return msal.account?[msal.account]:[];}
    setActiveAccount(account:typeof msal.account){msal.account=account;}
  },
}));
const config={tenant_id:'test-tenant',spa_client_id:'test-spa',api_scope:'test-scope',live_execution_enabled:true,allowed_repositories:[],publication_owner:'test',publication_enabled:true};
async function ready(){const auth=await import('./api');await auth.initialize(config);return auth;}
beforeEach(()=>{
  vi.resetModules();vi.resetAllMocks();msal.account={homeAccountId:'test-account'};
  msal.acquireTokenSilent.mockResolvedValue({accessToken:'unit-test-token'});
  vi.stubGlobal('location',{origin:'https://demo.example'});
  vi.stubGlobal('fetch',vi.fn());
});
afterEach(()=>vi.unstubAllGlobals());

describe('Microsoft session recovery',()=>{
  it('initializes once, including duplicate React bootstrap calls',async()=>{
    const auth=await import('./api');await Promise.all([auth.initialize(config),auth.initialize(config)]);
    expect(msal.initialize).toHaveBeenCalledTimes(1);expect(auth.signedIn()).toBe(true);
  });
  it('allows retry after redirect initialization fails, without exposing details',async()=>{
    msal.handleRedirectPromise.mockRejectedValueOnce(new Error('private identity diagnostic'));
    const auth=await import('./api');await expect(auth.initialize(config)).rejects.toThrow('could not be initialized');
    await auth.initialize(config);expect(auth.signedIn()).toBe(true);
  });
  it('expires the cached session when silent renewal requires interaction',async()=>{
    const auth=await ready();const changed=vi.fn();auth.subscribeSession(changed);
    const {InteractionRequiredAuthError}=await import('@azure/msal-browser');
    msal.acquireTokenSilent.mockRejectedValue(new InteractionRequiredAuthError('login_required'));
    await expect(auth.api('/runs')).rejects.toBeInstanceOf(auth.AuthenticationRequired);
    expect(auth.sessionState()).toBe('expired');expect(auth.signedIn()).toBe(false);
    expect(changed).toHaveBeenCalledOnce();expect(fetch).not.toHaveBeenCalled();
    await expect(auth.api('/runs')).rejects.toBeInstanceOf(auth.AuthenticationRequired);
    expect(msal.acquireTokenSilent).toHaveBeenCalledTimes(1);
    await auth.login();expect(msal.loginRedirect).toHaveBeenCalledWith({scopes:['test-scope'],prompt:'select_account'});
  });
  it('refreshes a rejected read once and keeps the session when it succeeds',async()=>{
    const auth=await ready();vi.mocked(fetch).mockResolvedValueOnce(new Response('',{status:401})).mockResolvedValueOnce(Response.json([]));
    expect(await auth.api('/runs')).toEqual([]);
    expect(msal.acquireTokenSilent.mock.calls.map(c=>c[0].forceRefresh)).toEqual([false,true]);
    expect(auth.signedIn()).toBe(true);
  });
  it('stops after a second read rejection and signals sign-in required',async()=>{
    const auth=await ready();vi.mocked(fetch).mockImplementation(async()=>new Response('',{status:401}));
    await expect(auth.api('/runs')).rejects.toBeInstanceOf(auth.AuthenticationRequired);
    expect(fetch).toHaveBeenCalledTimes(2);expect(auth.sessionState()).toBe('expired');
  });
  it('never automatically retries a cost-incurring or publishing mutation',async()=>{
    const auth=await ready();vi.mocked(fetch).mockResolvedValue(new Response('',{status:401}));
    await expect(auth.api('/runs',{repository_url:'test-fixture'})).rejects.toBeInstanceOf(auth.AuthenticationRequired);
    expect(fetch).toHaveBeenCalledTimes(1);expect(auth.sessionState()).toBe('expired');
  });
  it('does not treat forbidden authorization as an expired token or retry it',async()=>{
    const auth=await ready();vi.mocked(fetch).mockResolvedValue(Response.json({detail:'User is not authorized'},{status:403}));
    await expect(auth.api('/runs')).rejects.toThrow('User is not authorized');
    expect(fetch).toHaveBeenCalledOnce();expect(auth.signedIn()).toBe(true);
  });
  it('preserves event resume cursor when refreshing a rejected SSE connection',async()=>{
    const auth=await ready();const receive=vi.fn(),connected=vi.fn();
    vi.mocked(fetch).mockResolvedValueOnce(new Response('',{status:401})).mockResolvedValueOnce(new Response('data: {"event_id":8}\n\n'));
    await auth.observe('test-run',7,new AbortController().signal,receive,connected);
    expect(receive).toHaveBeenCalledWith({event_id:8});expect(connected).toHaveBeenCalledOnce();
    expect(vi.mocked(fetch).mock.calls[1][1]?.headers).toMatchObject({'Last-Event-ID':'7'});
  });
  it('signals session expiry from SSE before invoking connected',async()=>{
    const auth=await ready();const connected=vi.fn();
    vi.mocked(fetch).mockImplementation(async()=>new Response('',{status:401}));
    await expect(auth.observe('test-run',7,new AbortController().signal,vi.fn(),connected)).rejects.toBeInstanceOf(auth.AuthenticationRequired);
    expect(connected).not.toHaveBeenCalled();expect(auth.signedIn()).toBe(false);
  });
  it('provides sign-out without acquiring a token, even for an expired session',async()=>{
    const auth=await ready();vi.mocked(fetch).mockResolvedValue(new Response('',{status:401}));
    await expect(auth.api('/runs',{})).rejects.toBeInstanceOf(auth.AuthenticationRequired);
    msal.acquireTokenSilent.mockClear();await auth.logout();
    expect(msal.acquireTokenSilent).not.toHaveBeenCalled();expect(auth.sessionState()).toBe('signed_out');
    expect(msal.logoutRedirect).toHaveBeenCalledWith({account:{homeAccountId:'test-account'},postLogoutRedirectUri:'https://demo.example/'});
  });
  it('clears the app cache if server logout cannot start and permits a new login',async()=>{
    const auth=await ready();msal.logoutRedirect.mockRejectedValue(new Error('private diagnostic'));
    await expect(auth.logout()).rejects.toThrow('Signed out of this app');
    expect(msal.clearCache).toHaveBeenCalledWith({account:{homeAccountId:'test-account'}});
    expect(msal.account).toBeNull();expect(auth.signedIn()).toBe(false);
    await auth.login();expect(msal.loginRedirect).toHaveBeenCalledOnce();
  });
  it('discards a pending API response after local sign-out',async()=>{
    const auth=await ready();let finish!:(response:Response)=>void;
    vi.mocked(fetch).mockImplementation(()=>new Promise(resolve=>{finish=resolve;}));
    const pending=auth.api('/runs');const rejected=expect(pending).rejects.toBeInstanceOf(auth.AuthenticationRequired);
    await vi.waitFor(()=>expect(fetch).toHaveBeenCalled());await auth.logout();finish(Response.json([{run_id:'private-run'}]));
    await rejected;expect(auth.sessionState()).toBe('signed_out');
  });
  it('leaves sign-out available for temporary renewal failures without leaking diagnostics',async()=>{
    const auth=await ready();msal.acquireTokenSilent.mockRejectedValue(new Error('private diagnostic'));
    await expect(auth.api('/runs')).rejects.toThrow('temporarily unavailable');expect(auth.signedIn()).toBe(true);
    await auth.logout();expect(auth.signedIn()).toBe(false);
  });
});
