"""No Azure calls: verify exact ownership and deletion evidence with test doubles."""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))
from cleanup_orphans import candidates, delete_exact, ownership  # noqa: E402
from smoke_test_sandbox import OWNER  # noqa: E402


def evidence():
    return {
        "group": "/subscriptions/11111111-1111-1111-1111-111111111111/resourceGroups/rg-test/providers/Microsoft.App/sandboxGroups/sbg-test",
        "run_id": "a" * 32,
        "create_requests": 1,
        "labels": {"owner": OWNER, "smoke-run": "a" * 32},
        "before": [{"id": "protected"}],
        "sandbox_id": "owned",
    }


class Client:
    def __init__(self, labels):
        self.labels, self.deleted = labels, False

    def get(self):
        if self.deleted:
            error = RuntimeError("TEST DOUBLE")
            error.status_code = 404
            raise error
        return SimpleNamespace(labels=self.labels)

    def delete(self):
        self.deleted = True


def test_protected_and_nonmatching_ids_are_never_candidates():
    data = evidence()
    group = SimpleNamespace(
        list_sandboxes=lambda: [
            SimpleNamespace(id="protected", labels=data["labels"]),
            SimpleNamespace(id="another-run", labels={"owner": OWNER, "smoke-run": "b" * 32}),
            SimpleNamespace(id="owned", labels=data["labels"]),
        ]
    )
    assert candidates(group, data) == ["owned"]
    with pytest.raises(ValueError, match="pre-existing"):
        delete_exact(group, data, ["protected"])
    del data["before"]
    with pytest.raises(ValueError):
        ownership(data)


def test_live_labels_checked_and_exact_404_required():
    data = evidence()
    client = Client({"owner": "another-owner"})
    group = SimpleNamespace(get_sandbox_client=lambda _: client)
    with pytest.raises(ValueError, match="ownership"):
        delete_exact(group, data, ["owned"])
    assert not client.deleted
    client.labels = data["labels"]
    assert delete_exact(group, data, ["owned"]) == ["owned"]
    assert delete_exact(group, data, ["owned"]) == ["owned"]  # Safe repeated exact GET 404.
