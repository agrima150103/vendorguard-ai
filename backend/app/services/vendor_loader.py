from __future__ import annotations

import json
from pathlib import Path

from app.config import settings
from app.models.schemas import RiskTier, VendorListItem, VendorProfile


VENDOR_REGISTRY: dict[str, dict[str, str]] = {
    "cloudnova-001": {
        "folder": "cloudnova",
        "name": "CloudNova Solutions Ltd",
        "risk_tier": "LOW",
        "description": "Cloud provider with comparatively complete security evidence.",
    },
    "paysphere-002": {
        "folder": "paysphere",
        "name": "PaySphere Technologies Inc",
        "risk_tier": "MEDIUM",
        "description": "Payment provider with missing PCI and incident-response evidence.",
    },
    "dataquick-003": {
        "folder": "dataquick",
        "name": "DataQuick Analytics GmbH",
        "risk_tier": "HIGH",
        "description": "PII processor with contradictions and a prompt-injection attempt.",
    },
}


class VendorNotFoundError(ValueError):
    pass


class VendorDataError(RuntimeError):
    pass


def _vendor_folder(vendor_id: str) -> Path:
    item = VENDOR_REGISTRY.get(vendor_id)
    if item is None:
        raise VendorNotFoundError(f"Unknown vendor: {vendor_id}")
    folder = settings.resolved_sample_data_path / item["folder"]
    if not folder.is_dir():
        raise VendorDataError(f"Vendor folder not found: {folder}")
    return folder


def get_vendor_list() -> list[VendorListItem]:
    return [
        VendorListItem(
            vendor_id=vendor_id,
            name=item["name"],
            risk_tier=RiskTier(item["risk_tier"]),
            description=item["description"],
        )
        for vendor_id, item in VENDOR_REGISTRY.items()
    ]


def load_vendor_profile(vendor_id: str) -> VendorProfile:
    path = _vendor_folder(vendor_id) / "vendor_profile.json"
    if not path.is_file():
        raise VendorDataError(f"Profile missing: {path}")
    try:
        return VendorProfile.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        raise VendorDataError(f"Invalid profile for {vendor_id}: {exc}") from exc


def load_vendor_documents(vendor_id: str) -> dict[str, str]:
    documents: dict[str, str] = {}
    for path in sorted(_vendor_folder(vendor_id).glob("*.txt")):
        documents[path.name] = path.read_text(encoding="utf-8")
    return documents
