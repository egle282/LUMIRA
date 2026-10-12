"""Deterministic life-area signals based on Swiss Ephemeris and whole-sign houses.
Interpretations follow traditional Jyotish symbolism; they are not guarantees or professional advice.
"""
from datetime import datetime, timezone
from typing import List, Optional
from zoneinfo import ZoneInfo
import swisseph as swe
from pydantic import BaseModel, Field
from backend.astrology.engine import engine

class LifeAreaAnalysis(BaseModel):
    area_name: str = Field(..., description="Life area")
    current_state: str = Field(..., description="Traditional Jyotish summary")
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

SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")
NAK_LORDS = ("Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury")
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
DASHA_SEQ = tuple(DASHA_YEARS)
PLANETS = ("Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu")
THEMES = {"Sun":"purpose and visibility","Moon":"emotions and habits","Mars":"initiative and conflict","Mercury":"analysis and communication","Jupiter":"growth and guidance","Venus":"harmony and relationships","Saturn":"discipline and sustained effort","Rahu":"ambition and novelty","Ketu":"detachment and introspection"}
AREAS = {
 "career":("Career",(10,),"work, reputation and responsibilities"),
 "finance":("Finance",(2,11),"resources, income and gains"),
 "relationships":("Relationships",(7,),"partnership and cooperation"),
 "family":("Family",(4,),"home, roots and emotional security"),
 "health":("Health and vitality",(1,6),"vitality and routines; not a medical assessment"),
 "education":("Education",(5,9),"learning and higher knowledge"),
 "travel":("Travel",(3,9,12),"movement and long journeys"),
 "business":("Business",(7,10,11),"clients, work and networks"),
 "spirituality":("Spirituality",(8,9,12),"inner work, philosophy and retreat"),
}

def _sign(longitude: float) -> int:
    return int((longitude % 360) // 30)

def _house(longitude: float, asc_sign: int) -> int:
    return (_sign(longitude) - asc_sign) % 12 + 1

def _birth_utc(data: dict) -> datetime:
    try:
        local = datetime.fromisoformat(f"{data['birth_date']}T{data['birth_time']}").replace(tzinfo=ZoneInfo(str(data["timezone"])))
        return local.astimezone(timezone.utc)
    except (KeyError, ValueError, TypeError) as exc:
        raise ValueError("Birth date, time and valid IANA timezone are required") from exc

def _mahadasha(moon_lon: float, birth: datetime, now: datetime) -> str:
    width = 360 / 27
    index = int((moon_lon % 360) / width)
    lord = NAK_LORDS[index % 9]
    remaining = DASHA_YEARS[lord] * (1 - (moon_lon % width) / width)
    elapsed = max(0, (now - birth).total_seconds() / 86400 / 365.2425) + DASHA_YEARS[lord] - remaining
    i = DASHA_SEQ.index(lord)
    while elapsed >= DASHA_YEARS[DASHA_SEQ[i]]:
        elapsed -= DASHA_YEARS[DASHA_SEQ[i]]
        i = (i + 1) % len(DASHA_SEQ)
    return DASHA_SEQ[i]

def evaluate_life_areas(birth_data: dict, current_time: datetime) -> LifeAreasState:
    """Compute natal planetary house placements, current transits and Vimshottari Mahadasha."""
    birth = _birth_utc(birth_data)
    now = current_time.replace(tzinfo=timezone.utc) if current_time.tzinfo is None else current_time.astimezone(timezone.utc)
    lat, lon = float(birth_data["lat"]), float(birth_data["lon"])
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("Birth coordinates outside valid latitude/longitude ranges")
    natal = engine.calculate_natal_chart(birth, lon, lat)
    transits = engine.calculate_natal_chart(now, lon, lat)
    jd = swe.julday(birth.year, birth.month, birth.day, birth.hour + birth.minute / 60 + birth.second / 3600)
    _, angles = swe.houses_ex(jd, lat, lon, b"W", swe.FLG_SIDEREAL)
    asc = _sign(angles[0])
    natal_houses = {p: _house(v["longitude"], asc) for p, v in natal["positions"].items()}
    transit_houses = {p: _house(v["longitude"], asc) for p, v in transits["positions"].items()}
    dasha = _mahadasha(natal["positions"]["Moon"]["longitude"], birth, now)
    readings = {}
    for key, (label, houses, theme) in AREAS.items():
        factors = [f"{p} in {SIGNS[_sign(natal['positions'][p]['longitude'])]} (whole-sign house {natal_houses[p]}; {THEMES[p]})" for p in PLANETS if natal_houses[p] in houses]
        active = [f"{p} transiting whole-sign house {transit_houses[p]} ({THEMES[p]})" for p in PLANETS if transit_houses[p] in houses]
        if not factors:
            factors = [f"No tracked planet occupies houses {', '.join(map(str, houses))}; house-lord analysis is not included."]
        if not active:
            active = ["No tracked planet currently transits these whole-sign houses."]
        readings[key] = LifeAreaAnalysis(
            area_name=label,
            current_state=f"Traditional Jyotish themes: {theme}. Read in context of the full chart and real-world circumstances.",
            astrological_factors=factors,
            active_periods=[f"Vimshottari Mahadasha: {dasha} ({THEMES[dasha]})"],
            active_transits=active,
            risks=["Astrological symbolism is not certainty; do not use it as a substitute for medical, legal or financial advice."],
            opportunities=[f"Reflect on {theme} and choose practical actions based on evidence."],
        )
    return LifeAreasState(**readings, generated_at=now)
