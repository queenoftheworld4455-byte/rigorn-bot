import asyncio
from flask import Flask
from threading import Thread
import os

from config import BOT_TOKEN
from db import save_to_db, create_table, create_files_table, save_file, get_file
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove
)
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    t = Thread(target=run)
    t.start()

# =========================
# BOT
# =========================

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher(storage=MemoryStorage())

ADMINS = [
    6362983797,
    1050628887
]

# =========================
# FILE UPLOAD
# =========================

@dp.message(F.document)
async def upload_file(message: Message):

    print("FILE RECEIVED")

    if message.from_user.id not in ADMINS:
        return

    code = message.caption

    if not code:
        await message.answer(
            "کد فایل را در کپشن بنویس.\n\nمثال:\nguide1"
        )
        return

    file_id = message.document.file_id

    save_file(code, file_id)

    print(code)
    print(file_id)

    deep_link = (
        f"https://t.me/Rigorn_bot?start={code}"
    )

    await message.answer(
        f"✅ فایل ذخیره شد.\n\n"
        f"کد: {code}\n\n"
        f"لینک:\n{deep_link}"
    )

# =========================
# STATES
# =========================

class Form(StatesGroup):
    interest = State()
    city = State()
    budget = State()
    payment = State()
    phone = State()
    extra = State()
    request_text = State()

    catalog_phone = State()


# =========================
# TEXTS
# =========================

texts = {

    "ru": {

        "welcome": """Здравствуйте👋🏻

Я бот агентства недвижимости Rigorn, предлагающего выгодные условия рассрочки.

Заполните короткую форму, и менеджер свяжется с вами в соответствии с вашими потребностями.""", 

        "interest": "1/6. Что вас интересует?",

        "interest_buttons": [
            "Квартира",
            "Дом",
            "Коммерческая",
        ],

        "city": "2/6. В каком городе?",
        
        "city_buttons": [
          "Дубай",
          "Абу-Даби"
        ],
        
        "budget": "3/6.Бюджет (например: 5 000000 доллар $)?",

        "payment": "4/6. Способ оплаты?",

        "payment_buttons": [
            "Рассрочка",
            "Кэш / полная оплата"
        ],

        "phone": "5/6. Оставьте номер телефона или нажмите «Поделиться».",

        "share_contact": "Поделиться номером",

        "extra": "6/6. Дополнительные пожелания?",

        "extra_buttons": [
            "нет",
            "да"
        ],
        
        "write_request": "Напишите ваш запрос?",

       "done": """✅ Спасибо! Ваша заявка отправлена.

Ваш запрос зарегистрирован.
Наши специалисты свяжутся с вами в ближайшее время.

Подпишитесь на наш канал, чтобы получать информацию о последних проектах:

https://t.me/rigorn_invest"""
    },

    "en": {

        "welcome": """Hello👋🏻

I'm a Rigorn bot, a real estate agency offering favorable installment plans.

Fill out the short form, and a manager will contact you to discuss your needs.""",

        "interest": "1/6. What are you interested in?",

        "interest_buttons": [
            "Apartment",
            "House",
            "Commercial",
        ],

        "city": "2/6. In which city?",
        
        "city_buttons": [
          "Dubai",
          "Abu Dhabi"
        ],

        "budget": "3/6.Budget (for example: 5,000,000 dollars $)?",

        "payment": "4/6. Payment method?",
 "payment_buttons": [
            "Installment",
            "Cash / Full payment"
        ],

        "phone": '5/6. Leave your phone number or click "Share."',

        "share_contact": "Share phone number",

        "extra": '6/6. Any additional requests?',

        "extra_buttons": [
            "No",
            "Yes"
        ],
        
        "write_request": "Write your request?",

    "done": """✅ Thank you! Your application has been submitted.

Your request has been registered.
Our experts will contact you soon.

Subscribe to our channel to receive information about the latest projects:

https://t.me/rigorn_invest"""
    }
}

# =========================
# START
# =========================

@dp.message(F.text.startswith("/start"))
async def start_handler(message: Message, state: FSMContext):

    parts = message.text.split()

    if len(parts) > 1:

        code = parts[1]

        file_id = get_file(code)

        if file_id:

            await message.answer_document(
                document=file_id
            )

            return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Русский",
                    callback_data="lang_ru"
                ),
                InlineKeyboardButton(
                    text="English",
                    callback_data="lang_en"
                )
            ]
        ]
    )

    await message.answer(
        "Please choose your language:\nПожалуйста, выберите язык:",
        reply_markup=kb
    )


# =========================
# LANGUAGE SELECT
# =========================

@dp.callback_query(F.data.startswith("lang_"))
async def language_selected(callback: CallbackQuery, state: FSMContext):

    lang = callback.data.split("_")[1]

    await state.update_data(lang=lang)

    t = texts[lang]

    kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=t["interest_buttons"][0]),
            KeyboardButton(text=t["interest_buttons"][1]),
        ],
        [
            KeyboardButton(text=t["interest_buttons"][2]),
        ]
    ],
    resize_keyboard=True
)

    await callback.message.answer(
        f"{t['welcome']}\n\n{t['interest']}",
        reply_markup=kb
    )

    await state.set_state(Form.interest)

    await callback.answer()


# =========================
# INTEREST
# =========================

@dp.message(Form.interest)
async def interest_handler(message: Message, state: FSMContext):

    await state.update_data(interest=message.text)

    data = await state.get_data()
    lang = data["lang"]

    t = texts[lang]

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t["city_buttons"][0]),
                KeyboardButton(text=t["city_buttons"][1])
            ]
        ],
        resize_keyboard=True
    )

    await message.answer(
        t["city"],
        reply_markup=kb
    )

    await state.set_state(Form.city)


# =========================
# CITY
# =========================

@dp.message(Form.city)
async def city_handler(message: Message, state: FSMContext):

    await state.update_data(city=message.text)

    data = await state.get_data()
    lang = data["lang"]

    t = texts[lang]

    await message.answer(
    t["budget"],
    reply_markup=ReplyKeyboardRemove()
)

    await state.set_state(Form.budget)


# =========================
# BUDGET
# =========================

@dp.message(Form.budget)
async def budget_handler(message: Message, state: FSMContext):

    await state.update_data(budget=message.text)

    data = await state.get_data()
    lang = data["lang"]

    t = texts[lang]

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t["payment_buttons"][0])
            ],
            [
                KeyboardButton(text=t["payment_buttons"][1])
            ]
        ],
        resize_keyboard=True
    )

    await message.answer(
        t["payment"],
        reply_markup=kb
    )

    await state.set_state(Form.payment)
# =========================
# PAYMENT
# =========================

@dp.message(Form.payment)
async def payment_handler(message: Message, state: FSMContext):

    await state.update_data(payment=message.text)

    data = await state.get_data()
    lang = data["lang"]

    t = texts[lang]

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text=t["share_contact"],
                    request_contact=True
                )
            ]
        ],
        resize_keyboard=True
    )

    await message.answer(
        t["phone"],
        reply_markup=kb
    )

    await state.set_state(Form.phone)


# =========================
# PHONE
# =========================
@dp.message(Form.phone)
async def phone_handler(message: Message, state: FSMContext):

    phone = ""

    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text

    await state.update_data(phone=phone)

    data = await state.get_data()
    lang = data["lang"]

    t = texts[lang]

    kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=t["extra_buttons"][0]),
                KeyboardButton(text=t["extra_buttons"][1])
            ]
        ],
        resize_keyboard=True
    )

    await message.answer(
        t["extra"],
        reply_markup=kb
    )

    await state.set_state(Form.extra)


# =========================
# EXTRA
# =========================

@dp.message(Form.extra)
async def extra_handler(message: Message, state: FSMContext):

    data = await state.get_data()
    lang = data["lang"]

    t = texts[lang]

    answer = message.text.lower()

    # اگر YES یا ДА بود
    if answer in ["yes", "да"]:

        await message.answer(
            t["write_request"],
            reply_markup=ReplyKeyboardRemove()
        )

        await state.set_state(Form.request_text)

    else:

        await state.update_data(extra="No")

        data = await state.get_data()

        save_to_db(data)

        await message.answer(
            t["done"],
            reply_markup=ReplyKeyboardRemove()
        )

        await state.clear()

# =========================
# REQUEST TEXT
# =========================

@dp.message(Form.request_text)
async def request_text_handler(message: Message, state: FSMContext):

    await state.update_data(extra=message.text)

    data = await state.get_data()

    save_to_db(data)

    lang = data["lang"]
    t = texts[lang]

    await message.answer(
        t["done"],
        reply_markup=ReplyKeyboardRemove()
    )

    await state.clear()
    
# =========================
# MAIN
# =========================

async def main():

    create_table()
    create_files_table()

    print("Tables created")

    await dp.start_polling(bot)


if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())


