"""Non-secret configuration; explicit gates prevent accidental paid execution."""
import os
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Settings:
    tenant_id: str = ""
    api_client_id: str = ""
    spa_client_id: str = ""
    authorized_users: tuple[str, ...] = ()
    allowed_repositories: tuple[str, ...] = ()
    storage_account: str = ""
    managed_identity_client_id: str = ""
    subscription_id: str = ""
    resource_group: str = ""
    sandbox_group: str = ""
    credential_connection_id: str = ""
    region: str = "swedencentral"
    public_origin: str = ""
    live_execution_enabled: bool = False
    max_run_seconds: int = 900
    event_retention_limit: int = 10000
    publication_owner: str = ""

    @classmethod
    def from_env(cls):
        values = {}
        for name in cls.__dataclass_fields__:
            value = os.environ.get(name.upper())
            if value is None:
                continue
            if name in ("authorized_users", "allowed_repositories"):
                values[name] = tuple(v.strip() for v in value.split(",") if v.strip())
            elif name == "live_execution_enabled":
                values[name] = value.lower() == "true"
            elif name in ("max_run_seconds", "event_retention_limit"):
                values[name] = int(value)
            else:
                values[name] = value
        settings = cls(**values)
        for value in (settings.tenant_id, settings.api_client_id, settings.spa_client_id,
                      *settings.authorized_users):
            if value:
                UUID(value)
        if not 30 <= settings.max_run_seconds <= 1800:
            raise ValueError("Run timeout must be 30–1800 seconds")
        if not 100 <= settings.event_retention_limit <= 20000:
            raise ValueError("Event limit must be 100–20000")
        return settings
