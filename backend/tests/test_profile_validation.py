from datetime import date

import pytest
from pydantic import ValidationError

from backend.api.profile import ProfileCreateUpdate


def valid_payload(**overrides):
    data = {
        "name": " Test User ",
        "birth_date": "1990-01-02",
        "birth_time_str": "14:30",
        "lat": 55.75,
        "lon": 37.61,
        "timezone": "Europe/Moscow",
    }
    data.update(overrides)
    return data


def test_profile_normalizes_name_and_accepts_valid_birth_data():
    profile = ProfileCreateUpdate(**valid_payload())
    assert profile.name == "Test User"
    assert profile.birth_date == "1990-01-02"
    assert profile.birth_time_str == "14:30"


@pytest.mark.parametrize("birth_date", [
    "not-a-date",
    "1990-1-2",
    (date.today().replace(year=date.today().year + 1)).isoformat(),
])
def test_profile_rejects_invalid_or_future_birth_date(birth_date):
    with pytest.raises(ValidationError):
        ProfileCreateUpdate(**valid_payload(birth_date=birth_date))


@pytest.mark.parametrize("birth_time", ["25:00", "9:30", "12:60", "noon"])
def test_profile_rejects_invalid_birth_time(birth_time):
    with pytest.raises(ValidationError):
        ProfileCreateUpdate(**valid_payload(birth_time_str=birth_time))


@pytest.mark.parametrize("name", ["", "   ", "x" * 121])
def test_profile_rejects_blank_or_overlong_name(name):
    with pytest.raises(ValidationError):
        ProfileCreateUpdate(**valid_payload(name=name))


def test_profile_rejects_out_of_range_coordinates():
    with pytest.raises(ValidationError):
        ProfileCreateUpdate(**valid_payload(lat=91))
