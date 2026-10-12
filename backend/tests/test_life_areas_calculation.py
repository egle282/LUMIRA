from datetime import datetime, timezone
import unittest

from backend.astrology.life_areas import evaluate_life_areas


class LifeAreasCalculationTests(unittest.TestCase):
    def setUp(self):
        self.birth_data = {
            "birth_date": "1990-01-01",
            "birth_time": "12:00",
            "timezone": "Europe/Moscow",
            "lat": 55.7558,
            "lon": 37.6173,
        }

    def test_returns_calculated_areas_and_real_transit_fields(self):
        result = evaluate_life_areas(
            self.birth_data, datetime(2026, 10, 12, 12, tzinfo=timezone.utc)
        )
        self.assertIsNotNone(result.career)
        self.assertIsNotNone(result.finance)
        self.assertTrue(result.career.astrological_factors)
        self.assertTrue(result.career.active_periods)
        self.assertTrue(result.career.active_transits)
        self.assertEqual(result.generated_at, datetime(2026, 10, 12, 12, tzinfo=timezone.utc))

    def test_rejects_invalid_coordinates(self):
        invalid = {**self.birth_data, "lat": 95}
        with self.assertRaises(ValueError):
            evaluate_life_areas(invalid, datetime.now(timezone.utc))

    def test_rejects_invalid_timezone(self):
        invalid = {**self.birth_data, "timezone": "Not/A_Timezone"}
        with self.assertRaises(ValueError):
            evaluate_life_areas(invalid, datetime.now(timezone.utc))


if __name__ == "__main__":
    unittest.main()
