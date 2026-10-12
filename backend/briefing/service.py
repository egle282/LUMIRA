from datetime import datetime, time, timezone
from zoneinfo import ZoneInfo
import logging
import os

import swisseph as swe
from sqlalchemy import select

from backend.briefing.schemas import DailyBriefing, PanchangaSummary, TransitSummary
from backend.astrology.engine import engine
from backend.ai.orchestrator import AIOrchestrator
from backend.ai.openrouter_provider import OpenRouterProvider
from backend.ai.gemini_provider import GeminiProvider
from backend.database.database import AsyncSessionLocal
from backend.database.models import Profile
from backend.database.tenant import set_tenant_context
from backend.core.config import settings

logger = logging.getLogger("lumira_backend")

SIGNS_RU = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]
PLANETS_RU = {"Sun": "Солнце", "Moon": "Луна", "Mars": "Марс", "Mercury": "Меркурий", "Jupiter": "Юпитер", "Venus": "Венера", "Saturn": "Сатурн", "Rahu": "Раху", "Ketu": "Кету"}
TITHIS = ["Пратипада", "Двития", "Трития", "Чатуртхи", "Панчами", "Шаштхи", "Саптами", "Аштами", "Навами", "Дашами", "Экадаши", "Двадаши", "Трайодаши", "Чатурдаши", "Пурнима", "Пратипада", "Двития", "Трития", "Чатуртхи", "Панчами", "Шаштхи", "Саптами", "Аштами", "Навами", "Дашами", "Экадаши", "Двадаши", "Трайодаши", "Чатурдаши", "Амавасья"]
VARAS = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
NAKSHATRAS = ["Ашвини", "Бхарани", "Криттика", "Рохини", "Мригашира", "Ардра", "Пунарвасу", "Пушья", "Ашлеша", "Магха", "Пурва Пхалгуни", "Уттара Пхалгуни", "Хаста", "Читра", "Свати", "Вишакха", "Анурадха", "Джьештха", "Мула", "Пурва Ашадха", "Уттара Ашадха", "Шравана", "Дханишта", "Шатабхиша", "Пурва Бхадрапада", "Уттара Бхадрапада", "Ревати"]
YOGAS = ["Вишкамбха", "Прити", "Аюшман", "Саубхагья", "Шобхана", "Атиганда", "Сукарма", "Дхрити", "Шула", "Ганда", "Вриддхи", "Дхрува", "Вьягхата", "Харшана", "Ваджра", "Сиддхи", "Вьятипата", "Варияна", "Паригха", "Шива", "Сиддха", "Садхья", "Шубха", "Шукла", "Брахма", "Индра", "Вайдхрити"]
FAVORABLE_TITHIS = {2, 3, 5, 7, 10, 11, 13, 15, 17, 18, 20, 22, 25, 27, 29, 30}
FAVORABLE_NAKSHATRAS = {1, 4, 5, 7, 8, 13, 14, 17, 21, 22, 23, 26, 27}

class BriefingService:
    def __init__(self, user_id: str, tenant_id: str):
        self.user_id = user_id
        self.tenant_id = tenant_id

    async def generate_daily_briefing(self, target_date: datetime | None) -> DailyBriefing:
        logger.info("Generating daily briefing for user_id=%s date=%s", self.user_id, target_date.date() if target_date else "profile-local-today")
        async with AsyncSessionLocal() as session:
            await set_tenant_context(session, self.tenant_id)
            result = await session.execute(select(Profile).where(Profile.user_id == self.user_id).limit(1))
            profile = result.scalars().first()
        if profile is None:
            raise ValueError("Birth profile not found. Save birth date, time, location and timezone first.")

        try:
            zone = ZoneInfo(profile.timezone)
        except Exception as exc:
            raise ValueError("The birth profile has an invalid timezone.") from exc

        # Birth date is stored as a naive datetime and birth clock time separately.
        # Use both fields so the daily briefing's ascendant and houses match the profile.
        birth_date = profile.birth_date.date() if isinstance(profile.birth_date, datetime) else profile.birth_date
        birth_clock = time.fromisoformat(profile.birth_time_str)
        local_birth = datetime.combine(birth_date, birth_clock, tzinfo=zone)
        birth_utc = local_birth.astimezone(timezone.utc)
        local_date = target_date.date() if target_date else datetime.now(zone).date()
        local_target = datetime.combine(local_date, time(12, 0), tzinfo=zone)
        target_utc = local_target.astimezone(timezone.utc)

        panchanga_data = engine.calculate_panchanga(target_utc, profile.lon, profile.lat)
        tithi = int(panchanga_data["tithi"])
        nakshatra = int(panchanga_data["nakshatra"])
        yoga = int(panchanga_data["yoga"])
        tithi_name = TITHIS[(tithi - 1) % 15]
        paksha = "Шукла (растущая Луна)" if tithi <= 15 else "Кришна (убывающая Луна)"
        score = 5 + (2 if tithi in FAVORABLE_TITHIS else 0) + (2 if nakshatra in FAVORABLE_NAKSHATRAS else 0)
        score = max(1, min(9, score))
        panchanga = PanchangaSummary(
            tithi=f"{tithi_name} · {paksha}",
            vara=VARAS[local_target.weekday()],
            nakshatra=NAKSHATRAS[(nakshatra - 1) % 27],
            yoga=YOGAS[(yoga - 1) % 27],
            karana=f"Карана #{panchanga_data['karana']}",
            auspiciousness_score=score,
        )

        natal = engine.calculate_natal_chart(birth_utc, profile.lon, profile.lat)
        asc_jd = swe.julday(
            birth_utc.year, birth_utc.month, birth_utc.day,
            birth_utc.hour + birth_utc.minute / 60 + birth_utc.second / 3600,
        )
        _, angles = swe.houses_ex(asc_jd, profile.lat, profile.lon, b"W", swe.FLG_SIDEREAL)
        asc_sign = int(angles[0] % 360 // 30)
        transit_data = engine.calculate_natal_chart(target_utc, profile.lon, profile.lat)

        transits = []
        for planet in ("Moon", "Mercury", "Venus", "Sun", "Jupiter", "Saturn"):
            position = transit_data["positions"][planet]
            sign_index = int(position["longitude"] % 360 // 30)
            house = (sign_index - asc_sign) % 12 + 1
            impact = "Традиционно поддерживающая тема" if planet in {"Jupiter", "Venus", "Moon"} else "Тема для осознанного внимания"
            transits.append(TransitSummary(
                planet=PLANETS_RU[planet],
                current_sign=SIGNS_RU[sign_index],
                house_transiting=house,
                impact=impact,
            ))

        deterministic = {
            "panchanga": panchanga.model_dump(),
            "transits": [item.model_dump() for item in transits],
            "birth_chart": natal,
            "target_local_date": local_target.isoformat(),
        }
        ai_text = (
            f"На выбранную дату Луна находится в накшатре {panchanga.nakshatra}; "
            f"титхи — {panchanga.tithi}. По целознаковому отсчёту от вашего Лагна "
            f"Луна проходит {transits[0].house_transiting}-й дом. Рассматривайте это как "
            "традиционную астрологическую символику, а не как гарантированный прогноз."
        )
        focus_areas = ["Самонаблюдение", "Планирование", "Коммуникация"]
        recommendations = ["Сверьте планы с реальными обстоятельствами.", "Выберите одно конкретное дело и доведите его до конца."]
        cautions = ["Не принимайте медицинские, юридические или финансовые решения только на основе астрологии."]
        is_mock = True

        try:
            if settings.OPENROUTER_API_KEY:
                provider = OpenRouterProvider(
                    api_key=settings.OPENROUTER_API_KEY,
                    model_name="meta-llama/llama-3.1-8b-instruct:free",
                )
            elif settings.LLM_API_KEY:
                provider = GeminiProvider(api_key=settings.LLM_API_KEY)
            else:
                provider = None
            if provider:
                orchestrator = AIOrchestrator(primary_provider=provider)
                ai_output = await orchestrator.generate_daily_briefing_interpretation(
                    panchanga.model_dump(), [item.model_dump() for item in transits]
                )
                ai_text = ai_output.interpretation
                focus_areas = ai_output.focus_areas
                recommendations = ai_output.recommendations
                cautions = ai_output.cautions
                is_mock = False
        except Exception:
            logger.exception("AI briefing generation failed; returning deterministic interpretation")

        return DailyBriefing(
            date=target_utc,
            user_id=self.user_id,
            panchanga=panchanga,
            key_transits=transits,
            focus_life_areas=focus_areas,
            ai_interpretation=ai_text,
            recommendations=recommendations,
            cautions=cautions,
            is_mock=is_mock,
        )
