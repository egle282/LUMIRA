"""Response models for life-area readings.

This module intentionally contains no fabricated readings. The real calculation
must be derived from a user's saved birth profile and the astrology engine.
"""
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field


class LifeAreaAnalysis(BaseModel):
    area_name: str = Field(..., description="Name of the life area")
    current_state: str = Field(..., description="Qualitative summary")
    astrological_factors: List[str] = Field(default_factory=list)
    active_periods: List[str] = Field(default_factory=list)
    active_transits: List[str] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    ai_explanation: Optional[str] = None


class LifeAreasState(BaseModel):
    career: Optional[LifeAreaAnalysis] = None
    finance: Optional[LifeAreaAnalysis] = None
    relationships: Optional[LifeAreaAnalysis] = None
    family: Optional[LifeAreaAnalysis] = None
    health: Optional[LifeAreaAnalysis] = None
    education: Optional[LifeAreaAnalysis] = None
    travel: Optional[LifeAreaAnalysis] = None
    business: Optional[LifeAreaAnalysis] = None
    spirituality: Optional[LifeAreaAnalysis] = None
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


def evaluate_life_areas(birth_data: dict, current_time: datetime) -> LifeAreasState:
    """Fail closed rather than return fictional astrological placements.

    The endpoint must not present hard-coded sample readings as personalized
    calculations. Implementing houses, dashas, and transit mapping is a separate
    required calculation step.
    """
    raise NotImplementedError(
        "Personalized life-area calculations are not yet implemented. "
        "No mock reading is returned."
    )
