from backend.astrology.muhurta_api import TITHI_NAMES
from backend.briefing.service import TITHIS


def test_muhurta_tithi_names_cover_both_pakshas_and_amavasya():
    assert len(TITHI_NAMES) == 30
    assert TITHI_NAMES[14] == "Purnima"
    assert TITHI_NAMES[15] == "Krishna Pratipada"
    assert TITHI_NAMES[29] == "Amavasya"


def test_daily_briefing_tithi_names_distinguish_amavasya():
    assert len(TITHIS) == 30
    assert TITHIS[14] == "Пурнима"
    assert TITHIS[15] == "Пратипада"
    assert TITHIS[29] == "Амавасья"


def test_panchanga_uses_local_weekday_when_provided():
    from datetime import datetime, timezone
    from backend.astrology.engine import engine

    moment = datetime(2026, 10, 12, 12, tzinfo=timezone.utc)  # Monday in UTC
    local_sunday = engine.calculate_panchanga(
        moment, 37.6173, 55.7558, local_weekday=6
    )
    assert local_sunday["vara"] == 0  # Sunday
    assert local_sunday["karana_name"] in {
        "Kimstughna", "Bava", "Balava", "Kaulava", "Taitila",
        "Gara", "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga",
    }
    assert 1 <= local_sunday["karana"] <= 60
