import {describe, expect, it} from 'vitest';
import {renderToStaticMarkup} from 'react-dom/server';
import type {Config} from './api';
import {fixtureAllowed, RepositoryDetails, RepositoryMetadata} from './repository';

describe('public metadata does not authorize execution',()=>{
  it('keeps missing and empty allowlists closed',()=>{
    expect(fixtureAllowed('https://github.com/a/b')).toBe(false);
    expect(fixtureAllowed('https://github.com/a/b',{allowed_repositories:[]} as unknown as Config)).toBe(false);
    expect(fixtureAllowed('https://github.com/a/b',{allowed_repositories:['https://github.com/A/B']} as unknown as Config)).toBe(true);
  });
  it('shows real identity with explicit limitations and no invented success',()=>{
    const value:RepositoryMetadata={schema_version:1,repository_id:12,repository_url:'https://github.com/a/b',full_name:'a/b',commit_sha:'a'.repeat(40),archived:false,license_spdx:null,default_branch:'main',limitations:['No license clearance']};
    const html=renderToStaticMarkup(<RepositoryDetails value={value}/>);
    expect(html).toContain('METADATA ONLY');
    expect(html).toContain('Not identified');
    expect(html).toContain('no code was executed');
    expect(html).toContain('No license clearance');
    expect(html).not.toContain('Fix Vulnerability');
  });
});
