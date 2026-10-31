"""Logical V9 identities mapped to one configured inference backend."""
from __future__ import annotations

from dataclasses import dataclass
from io import StringIO
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from modelrouter.providers.registry import V9_MODEL_IDS


DEFAULT_BACKEND_DEPLOYMENT_STATUS = "API_IDENTITY_ONLY_UNVERIFIED_PHYSICAL_BACKEND"


@dataclass(frozen=True)
class AliasMapping:
    backend_model_id: str
    base_url: Optional[str] = None
    effective_native_effort: str = "none"
    cost_status: str = "MAPPED_EXPERIMENT_PRICE"

    def resolve(self, selected_model_id: str, requested_native_effort: str) -> Optional[Dict[str, Any]]:
        """Return configured execution facts; leave other models unchanged."""
        if selected_model_id not in V9_MODEL_IDS:
            return None
        return {
            "selected_model_id": selected_model_id,
            "actual_backend_model_id": self.backend_model_id,
            "requested_native_effort": requested_native_effort,
            "effective_native_effort": self.effective_native_effort,
            "execution_mode": "ALIAS_SMOKE",
            "cost_status": self.cost_status,
            "context_resend_required": None,
            "context_resend_status": "UNKNOWN",
        }


def alias_provider(config: dict, api_key=None):
    """Use the same configured Provider in local and Harbor episodes."""
    from modelrouter.providers.provider import OpenAICompatibleProvider

    credential = api_key
    if credential is None:
        credential = os.environ.get(config.get("api_key_env", "MODELROUTER_ALIAS_API_KEY"))
        if not credential and config.get("credential_file"):
            source = Path(config["credential_file"])
            if source.suffix.lower() == ".toml":
                import tomllib
                with source.open("rb") as handle:
                    credential = tomllib.load(handle)
            elif source.suffix.lower() == ".env":
                from dotenv import dotenv_values
                field = config["credential_field"]
                with source.open(encoding="utf-8") as handle:
                    selected = next((line for line in handle if
                                     line.partition("=")[0].strip().removeprefix("export ").strip() == field), "")
                credential = dotenv_values(stream=StringIO(selected), interpolate=False)
            else:
                credential = json.loads(source.read_text(encoding="utf-8"))
            for part in config["credential_field"].split("."):
                credential = credential[part]
            if not isinstance(credential, str):
                raise ValueError("Configured credential field must be a string")
    mapping = AliasMapping(config["actual_backend_model_id"], config["base_url"],
                           effective_native_effort=config.get("effective_native_effort", "none"),
                           cost_status="MAPPED_EXPERIMENT_PRICE")
    return OpenAICompatibleProvider(
        base_url=config["base_url"], alias_mapping=mapping,
        api_key=credential if credential is not None else "",
    )
