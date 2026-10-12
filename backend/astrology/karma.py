"""Experimental karma-timeline module.

No stable API currently exposes this module. Until transit hits and dasha weighting
are implemented and tested, it must not return synthetic personalized events.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional


class KarmaEvent:
    def __init__(self, date: datetime, theme: str, intensity: int, explanation: str, factors: List[str]):
        self.date = date
        self.theme = theme
        self.intensity = intensity
        self.explanation = explanation
        self.factors = factors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date.isoformat(),
            "theme": self.theme,
            "intensity": self.intensity,
            "explanation": self.explanation,
            "factors": self.factors,
        }


class KarmaTimelineEngine:
    """Reserved for a future validated transit-and-dasha timeline implementation."""

    def calculate_timeline(
        self,
        birth_date: datetime,
        lat: float,
        lon: float,
        start_date: datetime,
        end_date: datetime,
    ) -> List[Dict[str, Any]]:
        if end_date < start_date:
            raise ValueError("end_date must not precede start_date")
        raise NotImplementedError(
            "Karma Timeline is experimental and unavailable; no synthetic events are returned."
        )

    def _calculate_sade_sati(self, natal_moon_lon: float, current_date: datetime) -> Optional[Dict[str, Any]]:
        raise NotImplementedError(
            "Sade Sati timing has not yet been validated against transit calculations."
        )
