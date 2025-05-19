from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from googletrans import Translator
import logging
import os
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
translator = Translator()

user_modes = {}

def get_language_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🇬🇧 Англ → Рус", callback_data="en-ru"),
        InlineKeyboardButton("🇷🇺 Рус → Англ", callback_data="ru-en")
    )
    return kb

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_modes[message.from_user.id] = "en-ru"
    await message.answer("Привет, солнышко! Выбери направление перевода:", reply_markup=get_language_menu())

@dp.callback_query_handler(lambda call: call.data in ["en-ru", "ru-en"])
async def mode_callback(call: types.CallbackQuery):
    current_mode = user_modes.get(call.from_user.id, "en-ru")

    if call.data == current_mode:
        # Не редактируем ничего, просто отвечаем
        await call.answer("Этот режим уже выбран 😊")
        return

    # Сохраняем новый режим
    user_modes[call.from_user.id] = call.data
    await call.answer(f"Режим установлен: {call.data.replace('-', ' → ')}")

    # Отправляем обновлённую клавиатуру
    try:
        await call.message.edit_reply_markup(reply_markup=get_language_menu())
    except Exception as e:
        # Подстраховка, если всё-таки что-то пошло не так
        print(f"Ошибка при редактировании клавиатуры: {e}")

@dp.message_handler()
async def translate_message(message: types.Message):
    mode = user_modes.get(message.from_user.id, "en-ru")
    src, dest = mode.split('-')

    try:
        result = translator.translate(message.text, src=src, dest=dest)
        await message.reply(f"🔤 Перевод:\n{result.text}")
    except Exception as e:
        await message.reply("Ой, что-то пошло не так… попробуй ещё раз, котик.")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
