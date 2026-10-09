from datetime import datetime
from backend.briefing.schemas import DailyBriefing, PanchangaSummary, TransitSummary
from backend.astrology.engine import engine
from backend.ai.orchestrator import AIOrchestrator
from backend.ai.openrouter_provider import OpenRouterProvider
from backend.database.database import AsyncSessionLocal
from backend.database.models import Profile
from sqlalchemy.future import select
import os
import logging

logger = logging.getLogger("lumira_backend")

class BriefingService:
    def __init__(self, user_id: str):
        self.user_id = user_id

    async def generate_daily_briefing(self, target_date: datetime) -> DailyBriefing:
        """
        Orchestrates the deterministic generation of Panchanga, Transits,
        and Life Areas, then requests AI to synthesize the final briefing.
        """
        logger.info(f"Generating daily briefing for user_id={self.user_id} on {target_date.date()}")
        
        # 1. Fetch User Data (Birth Chart Profile)
        lat, lon = 28.6139, 77.2090 # default to New Delhi
        async with AsyncSessionLocal() as session:
            stmt = select(Profile).where(Profile.user_id == self.user_id)
            result = await session.execute(stmt)
            profile = result.scalars().first()
            if profile:
                lat = profile.lat
                lon = profile.lon
        
        # 2. Get Panchanga for target_date from deterministic engine
        panchanga_data = engine.calculate_panchanga(target_date, lon, lat)
        
        # Simple mapping for display purposes
        tithis = ["Пратипада", "Двития", "Трития", "Чатуртхи", "Панчами", "Шаштхи", "Саптами", "Аштами", "Навами", "Дашами", "Экадаши", "Двадаши", "Трайодаши", "Чатурдаши", "Пурнима", "Пратипада", "Двития", "Трития", "Чатуртхи", "Панчами", "Шаштхи", "Саптами", "Аштами", "Навами", "Дашами", "Экадаши", "Двадаши", "Трайодаши", "Чатурдаши", "Амавасья"]
        varas = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        nakshatras = ["Ашвини", "Бхарани", "Криттика", "Рохини", "Мригашира", "Ардра", "Пунарвасу", "Пушья", "Ашлеша", "Магха", "Пурва Пхалгуни", "Уттара Пхалгуни", "Хаста", "Читра", "Свати", "Вишакха", "Анурадха", "Джьештха", "Мула", "Пурва Ашадха", "Уттара Ашадха", "Шравана", "Дханишта", "Шатабхиша", "Пурва Бхадрапада", "Уттара Бхадрапада", "Ревати"]
        yogas = ["Вишкамбха", "Прити", "Аюшман", "Саубхагья", "Шобхана", "Атиганда", "Сукарма", "Дхрити", "Шула", "Ганда", "Вриддхи", "Дхрува", "Вьягхата", "Харшана", "Ваджра", "Сиддхи", "Вьятипата", "Варияна", "Паригха", "Шива", "Сиддха", "Садхья", "Шубха", "Шукла", "Брахма", "Индра", "Вайдхрити"]
        karanas = ["Бава", "Балава", "Каулава", "Таитила", "Гара", "Ваниджа", "Вишти", "Шакуни", "Чатушпада", "Нага", "Кинстугхна"]

        t_idx = min(max(panchanga_data['tithi'] - 1, 0), 29)
        n_idx = min(max(panchanga_data['nakshatra'] - 1, 0), 26)
        y_idx = min(max(panchanga_data['yoga'] - 1, 0), 26)
        
        panchanga = PanchangaSummary(
            tithi=tithis[t_idx] + (" (Шукла/Растущая)" if t_idx < 15 else " (Кришна/Убывающая)"),
            vara=varas[panchanga_data['vara']],
            nakshatra=nakshatras[n_idx],
            yoga=yogas[y_idx],
            karana=f"Карана {panchanga_data['karana']}",
            auspiciousness_score=8
        )
        
        # 3. Get Key Transits for target_date from deterministic engine
        transit_data = engine.calculate_natal_chart(target_date, lon, lat)
        zodiac_signs = ["Овен", "Телец", "Близнецы", "Рак", "Лев", "Дева", "Весы", "Скорпион", "Стрелец", "Козерог", "Водолей", "Рыбы"]
        planet_names_ru = {"Sun": "Солнце", "Moon": "Луна", "Mars": "Марс", "Mercury": "Меркурий", "Jupiter": "Юпитер", "Venus": "Венера", "Saturn": "Сатурн", "Rahu": "Раху", "Ketu": "Кету"}
        
        transits = []
        # We pick a couple of key planets for the daily briefing
        for planet in ["Moon", "Mercury", "Venus", "Sun"]:
            if planet in transit_data["positions"]:
                lon = transit_data["positions"][planet]["longitude"]
                sign_idx = int(lon / 30)
                # Calculate a mock house based on Aries rising just for display until we have user's natal chart
                mock_house = (sign_idx + 1) % 12
                if mock_house == 0: mock_house = 12
                
                transits.append(TransitSummary(
                    planet=planet_names_ru.get(planet, planet),
                    current_sign=zodiac_signs[sign_idx],
                    house_transiting=mock_house,
                    impact="Позитивно" if planet in ["Venus", "Jupiter", "Moon"] else "Нейтрально"
                ))
        
        # 4. Synthesize AI Interpretation
        openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
        if openrouter_key:
            try:
                # We use meta-llama/llama-3.1-8b-instruct:free as it's reliable for JSON on OpenRouter
                provider = OpenRouterProvider(api_key=openrouter_key, model_name="meta-llama/llama-3.1-8b-instruct:free")
                orchestrator = AIOrchestrator(primary_provider=provider)
                
                panchanga_dict = panchanga.model_dump()
                transits_dict = [t.model_dump() for t in transits]
                
                ai_output = await orchestrator.generate_daily_briefing_interpretation(panchanga_dict, transits_dict)
                
                ai_text = ai_output.interpretation
                focus_areas = ai_output.focus_areas
                recommendations = ai_output.recommendations
                cautions = ai_output.cautions
            except Exception as e:
                logger.error(f"AI Briefing generation failed: {e}")
                # Fallback to mock
                ai_text = f"Сегодня {planet_names_ru['Moon']} проходит через ваш {transits[0].house_transiting}-й дом в знаке {transits[0].current_sign}."
                focus_areas = ["Семья", "Обучение", "Духовность"]
                recommendations = ["Проведите время с семьей."]
                cautions = ["Избегайте споров."]
        else:
            # Mock fallback if no API key
            ai_text = f"Сегодня {planet_names_ru['Moon']} проходит через ваш {transits[0].house_transiting}-й дом в знаке {transits[0].current_sign}. Это смещает фокус на дом, семью и эмоциональное благополучие. Активна накшатра {nakshatras[n_idx]} — отличный день для обучения, духовных практик и консультаций с наставниками."
            focus_areas = ["Семья", "Обучение", "Духовность"]
            recommendations = ["Проведите время с семьей или займитесь обустройством дома.", "Начните новый обучающий курс или почитайте развивающую книгу."]
            cautions = ["Избегайте излишне логичных споров с близкими, проявите эмпатию."]
        
        return DailyBriefing(
            date=target_date,
            user_id=self.user_id,
            panchanga=panchanga,
            key_transits=transits,
            focus_life_areas=focus_areas,
            ai_interpretation=ai_text,
            recommendations=recommendations,
            cautions=cautions
        )
