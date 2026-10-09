from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🗺️ My Chart", callback_data="menu_my_chart"),
                InlineKeyboardButton(text="📅 Daily Briefing", callback_data="menu_daily_briefing")
            ],
            [
                InlineKeyboardButton(text="✨ AI Astrologer", callback_data="menu_ai_chat"),
                InlineKeyboardButton(text="⏳ Muhurta", callback_data="menu_muhurta")
            ],
            [
                InlineKeyboardButton(text="⚙️ Settings", callback_data="menu_settings")
            ]
        ]
    )

def skip_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Skip for now", callback_data="skip_birth_data")]]
    )
