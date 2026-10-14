"""Explicit harmless private-repository publication within standing demo scope."""

import probe_copilot_credentials as probe
import smoke_test_sandbox as smoke


def perform(*args, **kwargs):
    return probe.perform(*args, **kwargs, publication_probe=True, retry_owned_empty=True)


if __name__ == "__main__":
    raise SystemExit(smoke.main(performer=perform))
