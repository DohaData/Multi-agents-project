from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, field_validator


class OrderSize(str):
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


class QuoteRequestSample(BaseModel):
    """Matches quote_requests_sample.csv"""

    job: str
    need_size: str
    event: str
    request: str
    request_date: datetime

    @field_validator("need_size", mode="before")
    @classmethod
    def parse_need_size(cls, v: Any) -> str:
        v = str(v).strip().lower()
        if v not in ("small", "medium", "large"):
            raise ValueError(f"Invalid need_size '{v}'")
        return v

    @field_validator("request_date", mode="before")
    @classmethod
    def parse_request_date(cls, v: Any) -> datetime:
        if isinstance(v, datetime):
            return v
        for fmt in ("%m/%d/%y", "%Y-%m-%d", "%m/%d/%Y"):
            try:
                return datetime.strptime(str(v), fmt)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(str(v))
        except Exception:
            raise ValueError(f"Could not parse request_date: {v}")


class QuoteRequest(BaseModel):
    """Matches quote_requests.csv"""

    mood: Optional[str]
    job: str
    need_size: str
    event: str
    response: str

    @field_validator("need_size", mode="before")
    @classmethod
    def parse_need_size(cls, v: Any) -> str:
        v = str(v).strip().lower()
        if v not in ("small", "medium", "large"):
            raise ValueError(f"Invalid need_size '{v}'")
        return v


class Quote(BaseModel):
    """Matches quotes.csv rows (after reading). request_metadata is parsed to dict"""

    total_amount: float
    quote_explanation: str
    request_metadata: dict[str, Any]

    @field_validator("request_metadata", mode="before")
    @classmethod
    def parse_metadata(cls, v: Any) -> dict[str, Any]:
        import ast

        if isinstance(v, dict):
            return v
        if isinstance(v, str):
            try:
                return ast.literal_eval(v)
            except Exception:
                return {}
        return {}


class ErrorResponse(BaseModel):
    """Standardized error response from agents/orchestrator."""

    error: str
    context: Optional[str] = None

    def __str__(self) -> str:
        if self.context:
            return f"ERROR ({self.context}): {self.error}"
        return f"ERROR: {self.error}"
