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
