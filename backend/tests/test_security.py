import asyncio
import time
from uuid import uuid4

import jwt
import pytest
from app.auth import EntraVerifier
from app.config import Settings
from app.main import create_app
from app.security import redact, repository_parts
from conftest import MemoryStore
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

TENANT, API, USER = (str(uuid4()) for _ in range(3))
KEY = rsa.generate_private_key(public_exponent=65537, key_size=2048)
SETTINGS = Settings(tenant_id=TENANT, api_client_id=API, authorized_users=(USER,), public_origin="https://demo.example")


def token(**changes):
    claims = dict(iss=f"https://login.microsoftonline.com/{TENANT}/v2.0", aud=API,
                  tid=TENANT, oid=USER, scp="access_as_user", iat=int(time.time()),
                  nbf=int(time.time())-1, exp=int(time.time())+120)
    claims.update(changes)
    return jwt.encode(claims, KEY, algorithm="RS256", headers={"kid": "test-key"})


def client(store=None):
    verifier = EntraVerifier(SETTINGS)
    verifier.keys = [{**jwt.algorithms.RSAAlgorithm.to_jwk(KEY.public_key(), as_dict=True), "kid": "test-key"}]
    verifier.expires = time.monotonic()+3600
    verifier.last_fetch = time.monotonic()
    return TestClient(create_app(SETTINGS, store=store or MemoryStore(), verifier=verifier))


def test_authentication_rejects_spoofed_proxy_headers():
    with client() as c:
        assert c.get("/api/runs", headers={"X-MS-CLIENT-PRINCIPAL-ID": USER}).status_code == 401


@pytest.mark.parametrize("claims", [dict(aud=str(uuid4())), dict(tid=str(uuid4())), dict(exp=1),
                                   dict(scp="other"), dict(iss="https://attacker.example")])
def test_signed_but_invalid_claims_are_rejected(claims):
    with client() as c:
        assert c.get("/api/me", headers={"Authorization": "Bearer "+token(**claims)}).status_code == 401


def test_signed_valid_user_and_allowlist():
    with client() as c:
        assert c.get("/api/me", headers={"Authorization": "Bearer "+token()}).json() == {"object_id": USER}
        assert c.get("/api/me", headers={"Authorization": "Bearer "+token(oid=str(uuid4()))}).status_code == 403


def test_owner_and_explicit_live_gate():
    store = MemoryStore()
    identifier = str(uuid4())
    asyncio.run(store.save_run({"run_id": identifier, "owner_id": "someone-else"}))
    with client(store) as c:
        auth = {"Authorization": "Bearer "+token()}
        assert c.get(f"/api/runs/{identifier}", headers=auth).status_code == 404
        assert c.get(f"/api/runs/{identifier}/events", headers=auth).status_code == 404
        assert c.post("/api/runs", headers=auth, json={"repository_url": "https://github.com/a/b"}).status_code == 503


def test_origin_and_body_size_guards():
    with client() as c:
        assert c.post("/api/runs", headers={"Origin": "https://attacker.example"}, json={}).status_code == 403
        assert c.post("/api/runs", content=b"x"*17000).status_code == 413


@pytest.mark.parametrize("url", ["http://github.com/a/b", "https://github.com@localhost/a/b", "https://github.com/a/b?x=1",
                                "https://github.com/a/..", "https://github.com/a/b.git", "https://github.com/a/b%2f..",
                                "https://github.com/a/b/", "https://github.com/a/b#fragment"])
def test_repository_tricks_rejected(url):
    with pytest.raises(ValueError):
        repository_parts(url, (url,))


def test_unapproved_repository_rejected():
    with pytest.raises(ValueError):
        repository_parts("https://github.com/a/b", ())
    assert repository_parts("https://github.com/a/b", ("https://github.com/a/b",)) == ("a", "b")


def test_redaction_nested_and_logs():
    value = redact({"token": "opaque", "nested": {"message": "ghp_TESTTOKEN and Bearer TOKEN", "password": "opaque"}})
    assert value == {"token": "[REDACTED]", "nested": {"message": "[REDACTED] and [REDACTED]", "password": "[REDACTED]"}}
