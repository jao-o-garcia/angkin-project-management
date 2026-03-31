"""Pydantic models for LLM extraction output."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class BOQItem(BaseModel):
    trade: str
    scope: str = ""
    work_item: str
    quantity: float
    unit: str
    basis: str = ""
    source: str = "vision"

    @field_validator("trade")
    @classmethod
    def validate_trade(cls, v: str) -> str:
        valid = {"Civil / Structural", "Architectural / Finishing"}
        if v not in valid:
            # Fuzzy assignment — structural keywords go to Civil
            structural_kw = ("civil", "structural", "concrete", "footing", "slab", "column", "beam")
            return "Civil / Structural" if any(k in v.lower() for k in structural_kw) else "Architectural / Finishing"
        return v

    @field_validator("quantity")
    @classmethod
    def positive_quantity(cls, v: float) -> float:
        return max(v, 0.0)

    @field_validator("unit")
    @classmethod
    def normalize_unit(cls, v: str) -> str:
        return v.strip() or "lot"

    def to_dict(self) -> dict:
        return self.model_dump()
