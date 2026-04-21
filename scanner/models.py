from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class Finding:
    id: str
    severity: str
    category: str
    title: str
    evidence: str
    recommendation: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)
