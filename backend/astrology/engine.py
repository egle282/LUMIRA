import swisseph as swe
from datetime import datetime
import math

class AstrologyEngine:
    def __init__(self):
        # Set ephemeris path if you have downloaded ephe files, otherwise uses Moshier
        # swe.set_ephe_path('/path/to/ephe')
        
        # Set sidereal mode to Lahiri (typical for Vedic Astrology)
        swe.set_sid_mode(swe.SIDM_LAHIRI)

    def _get_julian_day(self, dt: datetime, lon: float, lat: float) -> float:
        # Convert datetime to Julian Day
        year, month, day, hour, minute, second = dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second
        # Assuming dt is UTC
        time_in_hours = hour + minute / 60.0 + second / 3600.0
        return swe.julday(year, month, day, time_in_hours)

    def calculate_natal_chart(self, dt: datetime, lon: float, lat: float) -> dict:
        """
        Calculate basic planetary positions for a given time and location.
        """
        jd = self._get_julian_day(dt, lon, lat)
        
        # Calculate Ayanamsa for the date
        ayanamsa = swe.get_ayanamsa_ut(jd)
        
        planets = {
            "Sun": swe.SUN,
            "Moon": swe.MOON,
            "Mars": swe.MARS,
            "Mercury": swe.MERCURY,
            "Jupiter": swe.JUPITER,
            "Venus": swe.VENUS,
            "Saturn": swe.SATURN,
            "Rahu": swe.MEAN_NODE, # True node can also be used
        }
        
        results = {"ayanamsa": ayanamsa, "positions": {}}
        
        for name, planet_id in planets.items():
            # Use SEFLG_SIDEREAL for Vedic (sidereal) zodiac
            flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
            calc, ret_flag = swe.calc_ut(jd, planet_id, flag)
            
            # calc[0] is longitude
            lon_sidereal = calc[0]
            
            # Determine Nakshatra (each is 13 degrees 20 minutes)
            nakshatra_num = int(lon_sidereal / (360 / 27))
            nakshatra_pada = int((lon_sidereal % (360 / 27)) / (360 / 108)) + 1
            
            results["positions"][name] = {
                "longitude": lon_sidereal,
                "speed": calc[3], # calc[3] is speed in longitude
                "nakshatra_index": nakshatra_num,
                "pada": nakshatra_pada
            }
            
        # Calculate Ketu based on Rahu (180 degrees apart)
        rahu_lon = results["positions"]["Rahu"]["longitude"]
        ketu_lon = (rahu_lon + 180) % 360
        ketu_nak = int(ketu_lon / (360 / 27))
        ketu_pada = int((ketu_lon % (360 / 27)) / (360 / 108)) + 1
        
        results["positions"]["Ketu"] = {
            "longitude": ketu_lon,
            "nakshatra_index": ketu_nak,
            "pada": ketu_pada
        }
        
        return results

    def calculate_panchanga(self, dt: datetime, lon: float, lat: float) -> dict:
        """
        Calculate Panchanga (Tithi, Vara, Nakshatra, Yoga, Karana).
        """
        jd = self._get_julian_day(dt, lon, lat)
        
        flag = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
        sun_calc, _ = swe.calc_ut(jd, swe.SUN, flag)
        moon_calc, _ = swe.calc_ut(jd, swe.MOON, flag)
        
        sun_lon = sun_calc[0]
        moon_lon = moon_calc[0]
        
        # Tithi: 1 Tithi = 12 degrees difference between Moon and Sun
        diff = moon_lon - sun_lon
        if diff < 0:
            diff += 360
        tithi = int(diff / 12) + 1
        
        # Karana: 1 Karana = 6 degrees difference (Half of Tithi)
        karana = int(diff / 6) + 1
        
        # Yoga: 1 Yoga = 13 deg 20 min sum of longitudes
        yoga_sum = (sun_lon + moon_lon) % 360
        yoga = int(yoga_sum / (360 / 27)) + 1
        
        # Nakshatra
        nakshatra = int(moon_lon / (360 / 27)) + 1
        
        # Vara (Day of week)
        vara = (dt.weekday() + 1) % 7 # 0=Monday, 6=Sunday -> Map to Vedic days
        
        return {
            "tithi": tithi,
            "vara": vara,
            "nakshatra": nakshatra,
            "yoga": yoga,
            "karana": karana
        }
        
engine = AstrologyEngine()
