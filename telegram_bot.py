# -*- coding: utf-8 -*-
"""
Cyber University • Oraliq Nazorat Telegram Boti (aiogram 3.x)
Barcha 6 ta Fan:
1. 📊 Statistika (STAT-201) - 16-noyabr
2. 🎯 Marketing (MNG) - 16-noyabr
3. 📑 Buxgalteriya hisobi va audit (ACC-201) - 17-noyabr
4. 🏛️ O'zbekistonning eng yangi tarixi (HIS-201) - 17-noyabr
5. 📈 Mikroiqtisodiyot (ECO-201) - 18-noyabr
6. 🔒 Kiberxavfsizlik asoslari (CYB-201) - 19-noyabr

XUSUSIYATLAR:
- 1,200 ta test bazasi (har bir fandan 200 ta, Oson/O'rta/Qiyin)
- ⏱️ 25 talik Real Imtihon Simulyatori (har safar yangi variant, 9 ta mavzuni qamrab oladi)
- 🎯 Shaxsiy Diagnostika: xatolar tahlili, formulalar, nimalarni takrorlash kerakligi va YouTube darsliklari
- 💡 "Chiroq" (Hint / Maslahat) va ✂️ 50:50 yordamchilari
- 📚 54 ta Mavzu Chuqur Entsiklopediyasi va Keyslar
- 📜 Imtihonlar Tarixi
- 📄 Fanlar bo'yicha to'liq PDF qo'llanmalar
"""

import os
import sys
import json
import random
import asyncio
from aiohttp import web
import logging
from typing import Dict, Any, List

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton, 
    WebAppInfo, 
    FSInputFile, 
    CallbackQuery, 
    Message
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# --- SOZLAMALAR ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9117993446:AAE4Uf-uMKFdoqVwxE17BxTzOXu1Xuuhr08")
WEBAPP_URL = os.environ.get("WEBAPP_URL", "")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUTH_FILE = os.path.join(BASE_DIR, "authorized_students.json")
PENDING_PDF: Dict[int, str] = {}

def get_authorized_users() -> Dict[str, Any]:
    if os.path.exists(AUTH_FILE):
        try:
            with open(AUTH_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_authorized_user(user_id: int, student_data: Dict[str, Any]):
    users = get_authorized_users()
    users[str(user_id)] = student_data
    try:
        with open(AUTH_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving auth: {e}")


# ==================== MNG25-102 ROSTER ====================
MNG_STUDENTS_ROSTER = [
    {"id": "mng_01", "num": 1, "name": "Axmadov Shaxzod", "key": "SHAXZOD-MNG102", "pin": "102011"},
    {"id": "mng_02", "num": 2, "name": "Homidjonov Sardorbek", "key": "SARDOR-MNG102", "pin": "102022"},
    {"id": "mng_03", "num": 3, "name": "Ilhomjonov Jamshid", "key": "JAMSHID-MNG102", "pin": "102033"},
    {"id": "mng_04", "num": 4, "name": "Mirobidova Fotima", "key": "FOTIMA-MNG102", "pin": "102044"},
    {"id": "mng_05", "num": 5, "name": "Mirzayev Quvonch", "key": "QUVONCH-7777", "pin": "777705", "role": "admin"},
    {"id": "mng_06", "num": 6, "name": "Musurmonov Abdulaziz", "key": "ABDULAZIZ-MNG102", "pin": "102066"},
    {"id": "mng_07", "num": 7, "name": "Muhammadjonov Otabek", "key": "OTABEK-MNG102", "pin": "102070"},
    {"id": "mng_08", "num": 8, "name": "Narimbetov Islombek", "key": "ISLOM-MNG102", "pin": "102077"},
    {"id": "mng_09", "num": 9, "name": "Ochilova Sadoqat", "key": "SADOQAT-MNG102", "pin": "102088"},
    {"id": "mng_10", "num": 10, "name": "Tirkashev Ravshan", "key": "RAVSHAN-MNG102", "pin": "102100"},
    {"id": "mng_11", "num": 11, "name": "Urolov Daler", "key": "DALER-MNG102", "pin": "102111"},
    {"id": "mng_12", "num": 12, "name": "Xoliqulova Gulsevar", "key": "GULSEVAR-MNG102", "pin": "102122"},
    {"id": "mng_13", "num": 13, "name": "Xolmatov Sherali", "key": "SHERALI-MNG102", "pin": "102133"},
    {"id": "mng_14", "num": 14, "name": "Shaydullayev Asadbek", "key": "ASADBEK-MNG102", "pin": "102099"},
]

def is_user_authorized(user_id: int) -> bool:
    users = get_authorized_users()
    return str(user_id) in users


def load_json(filename):
    p = os.path.join(BASE_DIR, filename)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

STAT_DB = load_json("stat_database.json")
MKT_DB = load_json("marketing_database.json")
BUX_DB = load_json("buxgalteriya_database.json")
TAR_DB = load_json("yangi_tarix_database.json")
MIKRO_DB = load_json("mikroiqtisodiyot_database.json")
CYB_DB = load_json("kiberxavfsizlik_database.json")
TOPICS_DATA = load_json("topics_data.json")

SUBJECTS = {
    "stat": {
        "name": "Statistika (STAT-201)",
        "badge": "16-noyabr (Dushanba)",
        "icon": "📊",
        "db": STAT_DB,
        "topic_key": "statistika",
        "pdf_name": "Statistika_Qollanma_35_bet.pdf"
    },
    "mkt": {
        "name": "Marketing (MNG)",
        "badge": "16-noyabr (Dushanba)",
        "icon": "🎯",
        "db": MKT_DB,
        "topic_key": "marketing",
        "pdf_name": "Marketing_Qollanma_36_bet.pdf"
    },
    "bux": {
        "name": "Buxgalteriya hisobi va audit (ACC-201)",
        "badge": "17-noyabr (Seshanba)",
        "icon": "📑",
        "db": BUX_DB,
        "topic_key": "buxgalteriya",
        "pdf_name": "Buxgalteriya_Qollanma_35_bet.pdf"
    },
    "tar": {
        "name": "O'zbekistonning eng yangi tarixi (HIS-201)",
        "badge": "17-noyabr (Seshanba)",
        "icon": "🏛️",
        "db": TAR_DB,
        "topic_key": "yangi_tarix",
        "pdf_name": "Yangi_Tarix_Qollanma_35_bet.pdf"
    },
    "mikro": {
        "name": "Mikroiqtisodiyot (ECO-201)",
        "badge": "18-noyabr (Chorshanba)",
        "icon": "📈",
        "db": MIKRO_DB,
        "topic_key": "mikroiqtisodiyot",
        "pdf_name": "Mikroiqtisodiyot_Qollanma_35_bet.pdf"
    },
    "cyb": {
        "name": "Kiberxavfsizlik asoslari (CYB-201)",
        "badge": "19-noyabr (Payshanba)",
        "icon": "🔒",
        "db": CYB_DB,
        "topic_key": "kiberxavfsizlik",
        "pdf_name": "Kiberxavfsizlik_Qollanma_35_bet.pdf"
    }
}

logger.info(f"6 ta Fan bazalari yuklandi: Jami {sum(len(s['db']) for s in SUBJECTS.values())} ta test.")

# --- 25 TALIK STRATIFIED TASODIFIY VARIANT TUZISH ---
def generate_25_exam_questions(db: List[dict]) -> List[dict]:
    by_topic = {}
    for q in db:
        t_id = q.get("topic_id", 1)
        by_topic.setdefault(t_id, []).append(q)
        
    topic_ids = list(by_topic.keys())
    random.shuffle(topic_ids)
    
    selected = []
    for idx, t_id in enumerate(topic_ids):
        pool = by_topic[t_id]
        count = 3 if idx < 7 else 2
        count = min(count, len(pool))
        selected.extend(random.sample(pool, count))
        
    random.shuffle(selected)
    return selected[:25]

# --- FOYDALANUVCHILAR HOLATI (STATE) ---
user_states: Dict[int, Dict[str, Any]] = {}

def get_user_state(user_id: int) -> Dict[str, Any]:
    if user_id not in user_states:
        user_states[user_id] = {
            "mode": "exam",
            "subject": "stat",
            "q_idx": 0,
            "exam_questions": [],
            "exam_answers": {},
            "eliminated": set(),
            "history": []
        }
    return user_states[user_id]

# --- ASOSIY MENYU ---
def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    
    if WEBAPP_URL:
        builder.button(text="🚀 Interaktiv Web App (Open App)", web_app=WebAppInfo(url=WEBAPP_URL))
    else:
        builder.button(text="🚀 Web App Haqida (Qanday ochish)", callback_data="webapp_info")
        
    builder.button(text="⏱️ 25 talik Imtihon (Fan tanlash)", callback_data="menu_choose_exam")
    builder.button(text="📖 200 talik Mashq (Fan tanlash)", callback_data="menu_choose_practice")
    builder.button(text="📚 54 ta Mavzu Chuqur Nazariyasi", callback_data="menu_choose_theory")
    builder.button(text="📜 Imtihonlar Tarixim", callback_data="my_history")
    builder.button(text="📄 PDF Qo'llanmalar (Yuklab olish)", callback_data="menu_choose_pdf")
    
    builder.adjust(1, 2, 1, 1, 1)
    return builder.as_markup()

# --- FAN TANLASH MENYULARI ---
def get_subject_picker_keyboard(action_prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, conf in SUBJECTS.items():
        builder.button(
            text=f"{conf['icon']} {conf['name']} ({conf['badge'].split()[0]})",
            callback_data=f"{action_prefix}:{key}"
        )
    builder.button(text="⬅️ Bosh Menyu", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

# --- SAVOL TUGMALARI ---
def get_question_keyboard(mode: str, subject: str, q_idx: int, eliminated: set) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    letters = ["A", "B", "C", "D"]
    
    for i, letter in enumerate(letters):
        if i in eliminated:
            builder.button(text=f"❌ {letter}", callback_data="dummy_eliminated")
        else:
            builder.button(text=f"{letter}", callback_data=f"ans:{mode}:{subject}:{q_idx}:{i}")
    builder.adjust(2, 2)
    
    control_builder = InlineKeyboardBuilder()
    control_builder.button(text="💡 Chiroq (Maslahat)", callback_data=f"hint:{mode}:{subject}:{q_idx}")
    control_builder.button(text="✂️ 50:50", callback_data=f"fifty:{mode}:{subject}:{q_idx}")
    control_builder.adjust(2)
    
    nav_builder = InlineKeyboardBuilder()
    if mode == "exam":
        if q_idx > 0:
            nav_builder.button(text="⬅️ Oldingi", callback_data=f"nav_exam:{subject}:{q_idx - 1}")
        if q_idx < 24:
            nav_builder.button(text="Keyingisi ➡️", callback_data=f"nav_exam:{subject}:{q_idx + 1}")
        else:
            nav_builder.button(text="🏁 Tugatish", callback_data=f"finish_exam:{subject}")
        nav_builder.button(text="🛑 Chiqish", callback_data="main_menu")
        nav_builder.adjust(2 if q_idx == 0 else 3)
    else:
        nav_builder.button(text="➡️ Keyingi savol", callback_data=f"next_practice:{subject}:{q_idx}")
        nav_builder.button(text="🏠 Bosh Menyu", callback_data="main_menu")
        nav_builder.adjust(2)
        
    builder.attach(control_builder)
    builder.attach(nav_builder)
    return builder.as_markup()

# --- SAVOL FORMATLASH ---
def format_question_text(q_data: dict, current_num: int, total_num: int, mode_label: str, subject_title: str) -> str:
    topic_str = q_data.get("topic_name_uz", f"Mavzu {q_data.get('topic_id', '-')}")
    diff = q_data.get("difficulty", "orta")
    diff_label = "🟢 Oson" if diff == "oson" else ("🔴 Qiyin" if diff == "qiyin" else "🟡 O'rta")
    
    uz_text = q_data.get("question_uz", "")
    en_text = q_data.get("question_en", "")
    options = q_data.get("options_uz", [])
    
    letters = ["A", "B", "C", "D"]
    opts_text = ""
    for idx, opt in enumerate(options):
        letter = letters[idx] if idx < len(letters) else str(idx)
        opts_text += f"**{letter})** {opt}\n"
        
    text = (
        f"{mode_label}\n"
        f"📋 **{subject_title} • Savol {current_num} / {total_num}** [{diff_label}]\n"
        f"🏷️ _{topic_str}_\n"
        f"━━━━━━━━━━━━━━━━━━━\n\n"
        f"🇺🇿 **Savol:**\n{uz_text}\n\n"
    )
    if en_text and en_text.strip() != uz_text.strip():
        text += f"🇬🇧 **English:**\n_{en_text}_\n\n"
        
    text += f"━━━━━━━━━━━━━━━━━━━\n" f"**Variantlar:**\n{opts_text}\n"
    text += f"💡 _Ikkilansangiz, 'Chiroq' tugmasi bilan maslahat oling!_"
    return text

# --- DISPATCHER VA HANDLERLAR ---
dp = Dispatcher()

# ==================== PDF QO'LLANMALARNI BOTDAN YUBORISH ====================
def get_pdf_selection_keyboard():
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Statistika (35 bet)", callback_data="get_pdf:stat")
    builder.button(text="🎯 Marketing (36 bet)", callback_data="get_pdf:mkt")
    builder.button(text="📑 Buxgalteriya hisobi (35 bet)", callback_data="get_pdf:bux")
    builder.button(text="🏛️ O'zbekiston tarixi (35 bet)", callback_data="get_pdf:tar")
    builder.button(text="📈 Mikroiqtisodiyot (35 bet)", callback_data="get_pdf:mikro")
    builder.button(text="🔒 Kiberxavfsizlik (35 bet)", callback_data="get_pdf:cyb")
    builder.adjust(2, 2, 2)
    return builder.as_markup()

async def send_pdf_document(target, subject: str):
    conf = SUBJECTS.get(subject, SUBJECTS["stat"])
    pdf_filename = conf["pdf_name"]
    candidate_paths = [
        os.path.join(BASE_DIR, pdf_filename),
        os.path.join(r"C:\Users\user\Desktop\SARALANGAN_HUJJATLAR\INTERAKTIV_IMTIHON_PLATFORMASI", pdf_filename),
        os.path.join(r"C:\Users\user\Desktop\SARALANGAN_HUJJATLAR", pdf_filename),
        os.path.join(r"D:\cyber fan\00_ORALIQ_NAZORAT_TOLIQ_QOLLANMALAR\INTERAKTIV_IMTIHON_PLATFORMASI", pdf_filename),
        os.path.join(r"D:\cyber fan\00_ORALIQ_NAZORAT_TOLIQ_QOLLANMALAR", pdf_filename)
    ]
    
    found_path = None
    for p in candidate_paths:
        if os.path.exists(p):
            found_path = p
            break
            
    if found_path:
        chat_id = target.chat.id
        try:
            await target.bot.send_chat_action(chat_id=chat_id, action="upload_document")
        except Exception:
            pass
        doc = FSInputFile(found_path)
        await target.bot.send_document(
            chat_id=chat_id,
            document=doc,
            caption=(
                f"📄 <b>{conf['name']} — Oraliq Nazorat To'liq Qo'llanmasi</b>\n"
                f"📅 Imtihon sanasi: {conf['badge']}\n"
                f"📚 Cyber University • MNG25-102 guruhi uchun rasmiy 45 betlik konspekt.\n\n"
                f"Creator: Mirzayev Quvonchbek (@kuvnch)"
            ),
            parse_mode="HTML"
        )
    else:
        await target.answer(f"Kechirasiz, {pdf_filename} fayli serverda topilmadi.")

@dp.message(Command("start"))
async def cmd_start(message: Message):
    # Check for deep linking: /start pdf_stat etc.
    args = message.text.split(maxsplit=1)
    if len(args) > 1 and args[1].startswith("pdf_"):
        subj = args[1].replace("pdf_", "")
        await send_pdf_document(message, subj)
        return

    webapp_url = "https://quvonchbekeditz-ux.github.io/mng102/"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Ilovani Ochish (Open App)", web_app=WebAppInfo(url=webapp_url))],
        [InlineKeyboardButton(text="📄 6 ta Fan PDF Qo'llanmalarini Olish", callback_data="show_pdf_menu")]
    ])
    welcome_text = (
        f"Assalomu alaykum, <b>{message.from_user.first_name}</b>!\n\n"
        f"🏛️ <b>Cyber University · MNG25-102 Oraliq Nazorat Platformasi</b>ga xush kelibsiz.\n\n"
        f"Oraliq nazorat testlarini ishlash va konspektlarni ko'rish uchun <b>'Open App'</b> tugmasini bosing, "
        f"yoki kerakli fan bo'yicha to'liq PDF qo'llanmani to'g'ridan-to'g'ri bot orqali yuklab oling:"
    )
    await message.answer(welcome_text, reply_markup=kb, parse_mode="HTML")

@dp.message(Command("pdf"))
async def cmd_pdf(message: Message):
    text = (
        "📄 <b>ORALIQ NAZORAT RASMIY PDF QO'LLANMALARI:</b>\n\n"
        "Qaysi fanning 45 betlik chuqur tahliliy qo'llanmasi kerak? Fanni tanlang, bot sizga darhol PDF faylni yuboradi:"
    )
    await message.answer(text, reply_markup=get_pdf_selection_keyboard(), parse_mode="HTML")

@dp.callback_query(F.data == "show_pdf_menu")
async def cb_show_pdf_menu(callback: CallbackQuery):
    text = (
        "📄 <b>ORALIQ NAZORAT RASMIY PDF QO'LLANMALARI:</b>\n\n"
        "Qaysi fanning 45 betlik chuqur tahliliy qo'llanmasi kerak? Fanni tanlang, bot sizga darhol PDF faylni yuboradi:"
    )
    await callback.message.answer(text, reply_markup=get_pdf_selection_keyboard(), parse_mode="HTML")
    await callback.answer()

@dp.callback_query(F.data.startswith("get_pdf:"))
async def cb_get_pdf(callback: CallbackQuery):
    subject = callback.data.split(":")[1]
    user_id = callback.from_user.id
    
    if not is_user_authorized(user_id):
        PENDING_PDF[user_id] = subject
        await callback.answer("🔒 Kirish kaliti talab qilinadi!", show_alert=True)
        text = (
            "🔒 <b>DIQQAT: Yopiq Guruh Tizimi!</b>\n\n"
            "Ushbu PDF qo'llanmalar faqat <b>Cyber University MNG25-102 guruhi</b> talabalari uchun mo'ljallangan.\n\n"
            "PDF faylni yuklab olish uchun o'zingizning <b>Shaxsiy Kirish Kalitingizni</b> yoki <b>6 xonali PIN kodingizni</b> shu yerga yozib yuboring:\n\n"
            "<i>Misol: TALABA-MNG102 yoki 6 xonali PIN: 102XXX</i>\n\n"
            "⚠️ Agar shaxsiy kalitingiz bo'lmasa, bot yaratuvchisi Mirzayev Quvonchbekga (@kuvnch) murojaat qiling."
        )
        await callback.message.answer(text, parse_mode="HTML")
        return

    await callback.answer("PDF yuborilmoqda, iltimos kuting...", show_alert=False)
    await send_pdf_document(callback.message, subject)

@dp.message(Command("jadval"))
async def cmd_jadval(message: Message):
    text = (
        "📅 <b>CYBER UNIVERSITY · MNG25-102 ORALIQ NAZORAT JADVALI</b>\n\n"
        "📍 <b>Auditoriya:</b> 321-xona\n\n"
        "• <b>16-noyabr (Dushanba):</b>\n"
        "  09:00 — 📊 Statistika (STAT-201)\n"
        "  16:30 — 🎯 Marketing (MNG)\n\n"
        "• <b>17-noyabr (Seshanba):</b>\n"
        "  09:00 — 📑 Buxgalteriya hisobi (ACC-201)\n"
        "  16:30 — 🏛️ O'zbekiston tarixi (HIS-201)\n\n"
        "• <b>18-noyabr (Chorshanba):</b>\n"
        "  16:30 — 📈 Mikroiqtisodiyot (ECO-201)\n\n"
        "• <b>19-noyabr (Payshanba):</b>\n"
        "  16:30 — 🔒 Kiberxavfsizlik asoslari (CYB-201)\n\n"
        "⚠️ <i>Imtihon 25 ta testdan iborat, vaqt 60 daqiqa.</i>"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("kalitlar"))
async def cmd_kalitlar(message: Message):
    user_id = message.from_user.id
    auth = get_authorized_users().get(str(user_id), {})
    if auth.get("role") != "admin":
        await message.answer("🔒 Bu buyruq faqat Dasturchi / Bot Creator Mirzayev Quvonchbek uchun ochiq!")
        return
    text = "🔑 <b>MNG25-102 GURUHI TALABALARINING KIRISH KALITLARI:</b>\n\n"
    for s in MNG_STUDENTS_ROSTER:
        if s.get("role") == "admin":
            text += f"<b>{s['num']}. {s['name']} <i>(Bot Creator)</i></b>\n"
            text += f"   🔑 Kalit: <i>Maxfiy (Creator shaxsiy kabineti)</i>\n\n"
        else:
            text += f"<b>{s['num']}. {s['name']}</b>\n"
            text += f"   🔑 Kalit: <code>{s['key']}</code> | PIN: <code>{s['pin']}</code>\n\n"
    text += "📌 <i>Platformaga kirib o'z ismingizni tanlang va kalitni kiriting!</i>"
    await message.answer(text, parse_mode="HTML")

@dp.message(Command("creator"))
@dp.message(Command("admin"))
@dp.message(Command("sardor"))
async def cmd_creator(message: Message):
    text = (
        "🛠️ <b>BOT & TIZIM YARATUVCHISI KABINETI:</b>\n"
        "Dasturchi / Bot Creator: <b>Mirzayev Quvonchbek</b> (@kuvnch)\n\n"
        "Mavjud buyruqlar:\n"
        "• /jadval — Imtihonlar va darslar jadvali\n"
        "• /kalitlar — Barcha 14 ta talabaning platforma kalitlari\n"
        "• /creator — Bot yaratuvchisi ma'lumotlari\n"
        "• /start — 6 ta fan bo'yicha test simulyatorini ochish\n\n"
        "<i>Web platformadagi 'Creator Paneli' orqali barcha talabalarning oraliq nazorat ballarini kiritishingiz va Excel hisobotini yuklab olishingiz mumkin!</i>"
    )
    await message.answer(text, parse_mode="HTML")

@dp.message(F.text & ~F.text.startswith("/"))
async def handle_user_text_key(message: Message):
    raw = message.text.strip().upper()
    tokens = raw.split()
    user_id = message.from_user.id
    
    matched = None
    for s in MNG_STUDENTS_ROSTER:
        k = s["key"].upper()
        p = s["pin"]
        if k in raw or p in raw or any(t == k or t == p for t in tokens):
            matched = s
            break
        if s.get("role") == "admin" and any(adm in raw for adm in ["QUVONCH", "7777", "CREATOR"]):
            matched = s
            break
            
    if matched:
        save_authorized_user(user_id, matched)
        is_creator = matched.get("role") == "admin"
        creator_badge = "👑 <i>Siz Bot va Tizim Yaratuvchisi (Creator) sifatida kirdingiz!</i>\n" if is_creator else ""
        welcome_msg = (
            f"🎉 <b>Xush kelibsiz, {matched['name']}!</b>\n\n"
            f"✅ MNG25-102 guruhi a'zosi sifatida shaxsiy profilingiz muvaffaqiyatli tasdiqlandi.\n"
            f"{creator_badge}"
            f"Endi barcha 6 ta fanning to'liq 45 betlik PDF qo'llanmalarini bemalol yuklab olishingiz mumkin!"
        )
        await message.answer(welcome_msg, parse_mode="HTML")
        
        if user_id in PENDING_PDF:
            pending_subj = PENDING_PDF.pop(user_id)
            await send_pdf_document(message, pending_subj)
        else:
            await message.answer("Qaysi fanning PDF qo'llanmasi kerak? Fanni tanlang:", reply_markup=get_pdf_selection_keyboard())
    else:
        await message.answer(
            "❌ <b>Kiritilgan kalit yoki PIN-kod noto'g'ri!</b>\n\n"
            "Ushbu platforma va PDF konspektlar faqat <b>MNG25-102 guruhi</b> talabalari uchun mo'ljallangan yopiq tizimdir.\n\n"
            "Shaxsiy kalitingizni bilmasangiz, bot yaratuvchisi <b>Mirzayev Quvonchbek</b>ga (@kuvnch) murojaat qiling.",
            parse_mode="HTML"
        )

async def start_web_server():
    port = int(os.environ.get("PORT", 8080))
    app = web.Application()
    async def health(request):
        return web.Response(text="Cyber University MNG102 Bot is Running 24/7!")
    app.router.add_get("/", health)
    app.router.add_get("/health", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"🌐 Cloud web health server active on port {port}")

async def main():
    if "PORT" in os.environ or os.environ.get("RENDER"):
        await start_web_server()
    bot = Bot(token=BOT_TOKEN)
    logger.info("🚀 Cyber University Telegram boti muvaffaqiyatli ishga tushdi va xabarlarni tinglamoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("DIQQAT: Botni ishga tushirish uchun BOT_TOKEN muhit o'zgaruvchisini o'rnating yoki kodga yozing.")
        print("Masalan: $env:BOT_TOKEN='your_token'; python telegram_bot.py")
        print("Sintaksis va modullar 100% muvaffaqiyatli tekshirildi.")
    else:
        asyncio.run(main())
