"""Models for AndrewsArnold."""

from __future__ import annotations
from typing import Optional

from dataclasses import dataclass, field

from mashumaro import field_options
from mashumaro.mixins.orjson import DataClassORJSONMixin


@dataclass
class QuotaResponse(DataClassORJSONMixin):
    """QuotaResponse model."""

    quotas: Optional[list[Quota]] = field(
        default=None, metadata=field_options(alias="quota")
    )
    error: Optional[str] = None


@dataclass
class Quota(DataClassORJSONMixin):
    """Quota model."""

    service_id: str = field(metadata=field_options(alias="ID"))
    quota_monthly: str = field(metadata=field_options(alias="quota_monthly"))
    quota_remaining: str = field(metadata=field_options(alias="quota_remaining"))
