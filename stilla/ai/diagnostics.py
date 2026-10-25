"""Local provider capability diagnostics without implicit fallback or model downloads."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from stilla.ai.local_client import ProviderConnectionError
from stilla.ai.providers import ProviderConfig, ProviderKind, select_provider


class ModelLister(Protocol):
    def list_models(self) -> object:
        """Return model identifiers from the configured provider."""


@dataclass(frozen=True, slots=True)
class ProviderDiagnostics:
    """A safe summary of local-provider reachability and discovered model IDs."""

    configured: bool
    reachable: bool
    provider_kind: str
    base_url: str
    models: tuple[str, ...] = ()
    message: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "configured": self.configured,
            "reachable": self.reachable,
            "provider_kind": self.provider_kind,
            "base_url": self.base_url,
            "models": list(self.models),
            "message": self.message,
        }


def diagnose_local_provider(config: ProviderConfig, client: ModelLister) -> ProviderDiagnostics:
    """Check a selected local provider by listing models; never contacts remote APIs.

    The base URL is shown only after validation has restricted the provider to loopback.
    Errors are reduced to safe status text and never include response bodies or secrets.
    """
    selected = select_provider(config)
    if selected.kind is not ProviderKind.LOCAL_OPENAI_COMPATIBLE:
        raise ValueError("Diagnostics currently support only the local provider")
    if not selected.enabled:
        return ProviderDiagnostics(
            configured=False, reachable=False, provider_kind=selected.kind.value,
            base_url=selected.base_url, message="Local provider is disabled",
        )
    try:
        discovered = client.list_models()
    except (ProviderConnectionError, TimeoutError, OSError, ValueError):
        return ProviderDiagnostics(
            configured=True, reachable=False, provider_kind=selected.kind.value,
            base_url=selected.base_url,
            message="Cannot reach local AI server; confirm Bionic is running",
        )
    if isinstance(discovered, dict):
        data = discovered.get("data")
        discovered = [
            item.get("id") for item in data
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        ] if isinstance(data, list) else []
    if not isinstance(discovered, (list, tuple)):
        return ProviderDiagnostics(
            configured=True, reachable=True, provider_kind=selected.kind.value,
            base_url=selected.base_url, message="Server responded with an unsupported model-list format",
        )
    models = tuple(
        item.strip() for item in discovered
        if isinstance(item, str) and item.strip() and len(item.strip()) <= 200
    )
    return ProviderDiagnostics(
        configured=True, reachable=True, provider_kind=selected.kind.value,
        base_url=selected.base_url, models=models,
        message=("Local AI server is ready" if models else "Server is reachable but no models were discovered"),
    )
