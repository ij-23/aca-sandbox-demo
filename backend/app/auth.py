"""Entra access-token validation. Proxy principal headers are never trusted."""

import asyncio
import time
from dataclasses import dataclass

import httpx
import jwt
from fastapi import HTTPException, Request

from .config import Settings


@dataclass(frozen=True)
class Principal:
    object_id: str
    tenant_id: str


class EntraVerifier:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.keys: list[dict] = []
        self.expires = 0.0
        self.last_fetch = 0.0
        self.lock = asyncio.Lock()

    async def __call__(self, request: Request) -> Principal:
        header = request.headers.get("authorization", "")
        if not header.startswith("Bearer ") or len(header) > 16000:
            raise HTTPException(401, "Entra access token required")
        token = header[7:]
        try:
            meta = jwt.get_unverified_header(token)
            if meta.get("alg") != "RS256" or not isinstance(meta.get("kid"), str):
                raise ValueError("Invalid token header")
            if not self.settings.tenant_id or not self.settings.api_client_id:
                raise ValueError("Authentication is not configured")
            async with self.lock:
                current = time.monotonic()
                missing = not any(k.get("kid") == meta["kid"] for k in self.keys)
                if current >= self.expires or (missing and current - self.last_fetch > 60):
                    self.last_fetch = current
                    async with httpx.AsyncClient(timeout=10, follow_redirects=False, trust_env=False) as client:
                        response = await client.get(
                            f"https://login.microsoftonline.com/{self.settings.tenant_id}/discovery/v2.0/keys"
                        )
                        response.raise_for_status()
                        self.keys = response.json()["keys"]
                    self.expires = current + 3600
                key = next(k for k in self.keys if k.get("kid") == meta["kid"])
            claims = jwt.decode(
                token,
                jwt.PyJWK(key).key,
                algorithms=["RS256"],
                audience=self.settings.api_client_id,
                issuer=f"https://login.microsoftonline.com/{self.settings.tenant_id}/v2.0",
                options={"require": ["exp", "iat", "nbf", "oid", "tid", "aud", "iss", "scp"]},
            )
            if claims["tid"] != self.settings.tenant_id or "access_as_user" not in claims["scp"].split():
                raise ValueError("Invalid tenant or delegated scope")
            if claims["oid"] not in self.settings.authorized_users:
                raise HTTPException(403, "User is not authorized")
            return Principal(claims["oid"], claims["tid"])
        except HTTPException:
            raise
        except Exception:
            # Never include tokens, decoded claims or network exception bodies in responses/logs.
            raise HTTPException(401, "Invalid or unavailable Entra authentication") from None
