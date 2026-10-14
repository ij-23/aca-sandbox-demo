# Genuine prerecorded A/B/C evidence

[replay-events.jsonl](./replay-events.jsonl) contains the 95 actual persisted Azure events from run `ffe4af9f-f911-491b-b00c-327b3d84605f` on 2026-10-14. It is a recording, never live execution.

- Source: public trusted fixture `ij-23/academo-fastapi-fixture`, pinned SHA `c1c3d2bcd0f33eddfd77d29249c3a04c0130da1e`.
- A source evidence verified; B expected 2 passed/2 failed before fixing.
- One Fix confirmation starts C: 4 tests passed, 2 targeted regressions passed, localhost health passed.
- C created private `ij-23/academo-fastapi-fixture-fixed`; verified commit `d84155b39cd758e6e22b8db51036d72eda5c9f3d`. The private link requires owner access.
- All three disposable Sandboxes deleted and exact-ID404 verified. Source unchanged.
- Retrieved from private Blob using deployed app UAMI. Also stored with reports in private replay Blob. No fixture code ran on the host, local computer or CI runner.

The recording retains real timestamps, including the human/configuration gap before C. Dashboard playback takes 4m33s at1x. The final reports are explicitly labelled as final results during playback. Playback creates no Sandboxes or repositories.

SHA256: `dcf5e60178df13fb99f212fcdb03182ab7fe814a2f90eeb13bef71a13deaac04`.
