from pydantic import BaseModel, Field
from typing import List

class AstrologyInterpretation(BaseModel):
    summary: str = Field(..., description="A short summary of the astrological interpretation.")
    factors: List[str] = Field(..., description="Key astrological factors considered (e.g. 'Moon in Aries').")
    risks: List[str] = Field(default_factory=list, description="Potential risks or negative influences.")
    opportunities: List[str] = Field(default_factory=list, description="Potential opportunities or positive influences.")
    timing: List[str] = Field(default_factory=list, description="Relevant timing or periods for the prediction.")
    recommendations: List[str] = Field(..., description="Actionable recommendations for the user.")
    confidence: float = Field(..., description="Confidence score of the interpretation (0.0 to 1.0).")
    disclaimer: str = Field(..., description="A mandatory disclaimer that this is astrological interpretation, not medical or financial advice.")

class DailyBriefingAIOutput(BaseModel):
    interpretation: str = Field(..., description="A short, personalized AI interpretation in Russian about the day's astrological transits and panchanga.")
    focus_areas: List[str] = Field(..., description="1 to 3 key life areas to focus on (e.g. 'Семья', 'Карьера').")
    recommendations: List[str] = Field(..., description="Actionable recommendations (what to DO) based on transits.")
    cautions: List[str] = Field(..., description="Actionable cautions (what NOT to DO) based on transits.")
