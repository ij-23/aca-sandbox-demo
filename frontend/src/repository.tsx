import type {Config} from './api';

export type RepositoryMetadata = {
  schema_version: 1; repository_id: number; repository_url: string;
  full_name: string; commit_sha: string; archived: boolean;
  license_spdx: string | null; default_branch: string; limitations: string[];
};

export function fixtureAllowed(url:string, config?:Config) {
  return !!config?.allowed_repositories.some(candidate=>candidate.toLowerCase()===url.toLowerCase());
}

export function RepositoryDetails({value}:{value:RepositoryMetadata}) {
  return <section className="panel" aria-label="Public repository metadata">
    <div className="panel-heading"><div><span className="eyebrow">PUBLIC REPOSITORY · METADATA ONLY</span><h2>{value.full_name}</h2></div></div>
    <p>Repository ID: <code>{value.repository_id}</code> · Commit: <code>{value.commit_sha}</code></p>
    <p>License reported by GitHub: {value.license_spdx??'Not identified'}{value.archived?' · Archived repository':''}</p>
    <p>No Sandbox was created and no code was executed. Public analysis and builds remain unavailable until worker isolation and integration checks pass.</p>
    {value.limitations.map((item,index)=><p className="limitation" key={index}>{item}</p>)}
  </section>;
}
