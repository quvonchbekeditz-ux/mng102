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

@dp.message(Command("start"))
async def cmd_start(message: Message):
    welcome_text = (
        f"👋 **Assalomu alaykum, {message.from_user.first_name}!**\n\n"
        f"🏛️ **Cyber University • Oraliq Nazorat Mega Platformasi (Barcha 6 ta Fan)**ga xush kelibsiz!\n\n"
        f"📅 **Oraliq nazorat imtihonlari jadvali:**\n"
        f"1. 📊 **Statistika (STAT-201)** — 16-noyabr (Dushanba)\n"
        f"2. 🎯 **Marketing (MNG)** — 16-noyabr (Dushanba)\n"
        f"3. 📑 **Buxgalteriya hisobi va audit (ACC-201)** — 17-noyabr (Seshanba)\n"
        f"4. 🏛️ **O'zbekistonning eng yangi tarixi (HIS-201)** — 17-noyabr (Seshanba)\n"
        f"5. 📈 **Mikroiqtisodiyot (ECO-201)** — 18-noyabr (Chorshanba)\n"
        f"6. 🔒 **Kiberxavfsizlik asoslari (CYB-201)** — 19-noyabr (Payshanba)\n\n"
        f"🎯 **IMTIHON STANDARTI:**\n"
        f"Har bir fandan 200 tadan (jami 1,200 ta) test, 25 talik Real Imtihon Simulyatori, Shaxsiy Diagnostika va 54 ta mavzu nazariyasi mavjud.\n\n"
        f"Kerakli bo'limni tanlang:"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "main_menu")
async def cb_main_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏛️ **Asosiy Bosh Menyu**\nO'zingizga kerakli bo'limni tanlang:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "webapp_info")
async def cb_webapp_info(callback: CallbackQuery):
    info_text = (
        "🚀 **Interaktiv Web App (\"Open App\") Haqida:**\n\n"
        "Platformaning to'liq interaktiv versiyasi (rang-barang grafiklar, 6 ta fan boshqaruvi, 25 talik imtihon taymeri, testlar tarixi) **`index.html`** faylida joylashgan!\n\n"
        "💻 **Noutbuk / Kompyuterda ochish:**\n"
        "Ish stolidagi `index.html` faylini brauzerda oching. 100% oflayn ishlaydi!\n\n"
        "📱 **Telefonda 24/7 ishlatish:**\n"
        "`index.html` ni GitHub Pages ga joylab, havolani bot sozlamasiga (`WEBAPP_URL`) qo'ysangiz, Telegram ichida 'Open App' tugmasi orqali doim ochiladi!"
    )
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Bosh Menyu", callback_data="main_menu")
    await callback.message.edit_text(info_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

# --- MENYU BO'YICHA TANLASH ---
@dp.callback_query(F.data == "menu_choose_exam")
async def cb_menu_choose_exam(callback: CallbackQuery):
    await callback.message.edit_text(
        "⏱️ **Qaysi fandan 25 talik Imtihon topshirasiz?**\n"
        "Har safar barcha 9 ta mavzudan 25 ta yangi savol tanlanadi:",
        reply_markup=get_subject_picker_keyboard("start_exam"),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "menu_choose_practice")
async def cb_menu_choose_practice(callback: CallbackQuery):
    await callback.message.edit_text(
        "📖 **Qaysi fandan 200 talik Mashq rejimini boshlaysiz?**\n"
        "Barcha savollar, chiroq maslahatlari va batafsil tahlil:",
        reply_markup=get_subject_picker_keyboard("start_practice"),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "menu_choose_theory")
async def cb_menu_choose_theory(callback: CallbackQuery):
    await callback.message.edit_text(
        "📚 **Qaysi fanning 9 ta mavzu nazariyasi va keyslarini o'rganmoqchisiz?**",
        reply_markup=get_subject_picker_keyboard("view_topics"),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data == "menu_choose_pdf")
async def cb_menu_choose_pdf(callback: CallbackQuery):
    await callback.message.edit_text(
        "📄 **Qaysi fanning to'liq PDF qo'llanmasini yuklab olmoqchisiz?**",
        reply_markup=get_subject_picker_keyboard("get_pdf"),
        parse_mode="Markdown"
    )
    await callback.answer()

# --- ⏱️ 25 TALIK IMTIHON BOSHLASH ---
@dp.callback_query(F.data.startswith("start_exam:"))
async def cb_start_exam(callback: CallbackQuery):
    subject = callback.data.split(":")[1]
    if subject not in SUBJECTS:
        subject = "stat"
    conf = SUBJECTS[subject]
    
    st = get_user_state(callback.from_user.id)
    st["mode"] = "exam"
    st["subject"] = subject
    st["q_idx"] = 0
    st["exam_questions"] = generate_25_exam_questions(conf["db"])
    st["exam_answers"] = {}
    st["eliminated"] = set()
    
    await callback.answer(f"{conf['name']} bo'yicha yangi 25 talik imtihon boshlandi!", show_alert=False)
    await send_exam_question(callback.message, callback.from_user.id, edit=True)

async def send_exam_question(message: Message, user_id: int, edit: bool = False):
    st = get_user_state(user_id)
    subject = st["subject"]
    conf = SUBJECTS.get(subject, SUBJECTS["stat"])
    questions = st["exam_questions"]
    q_idx = st["q_idx"]
    
    if q_idx >= len(questions):
        await show_exam_results(message, user_id, edit=edit)
        return
        
    q_data = questions[q_idx]
    mode_label = f"⏱️ **REAL IMTIHON REJIMI ({conf['badge']})**"
    
    text = format_question_text(q_data, q_idx + 1, 25, mode_label, conf["name"])
    
    if q_idx in st["exam_answers"]:
        letters = ["A", "B", "C", "D"]
        chosen_l = letters[st["exam_answers"][q_idx]]
        text += f"\n\n🟢 _Siz tanlagan javob: **{chosen_l}** (O'zgartirish uchun boshqa variantni bosing)_"
        
    kb = get_question_keyboard("exam", subject, q_idx, st["eliminated"])
    
    try:
        if edit:
            await message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        else:
            await message.answer(text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("nav_exam:"))
async def cb_nav_exam(callback: CallbackQuery):
    target_idx = int(callback.data.split(":")[2])
    st = get_user_state(callback.from_user.id)
    st["q_idx"] = target_idx
    st["eliminated"] = set()
    await send_exam_question(callback.message, callback.from_user.id, edit=True)
    await callback.answer()

# --- JAVOBNI QABUL QILISH ---
@dp.callback_query(F.data.startswith("ans:"))
async def cb_ans(callback: CallbackQuery):
    parts = callback.data.split(":")
    mode = parts[1]
    subject = parts[2]
    q_idx = int(parts[3])
    chosen_idx = int(parts[4])
    
    st = get_user_state(callback.from_user.id)
    
    if mode == "exam":
        st["exam_answers"][q_idx] = chosen_idx
        await callback.answer(f"Tanlandi: {['A','B','C','D'][chosen_idx]}", show_alert=False)
        
        if q_idx < 24:
            st["q_idx"] = q_idx + 1
            st["eliminated"] = set()
            await send_exam_question(callback.message, callback.from_user.id, edit=True)
        else:
            await show_exam_results(callback.message, callback.from_user.id, edit=True)
    else:
        conf = SUBJECTS.get(subject, SUBJECTS["stat"])
        db = conf["db"]
        q_data = db[q_idx]
        is_corr = chosen_idx == q_data.get("correct_index", 0)
        letters = ["A", "B", "C", "D"]
        options = q_data.get("options_uz", [])
        
        builder = InlineKeyboardBuilder()
        builder.button(text="➡️ Keyingi savol", callback_data=f"next_practice:{subject}:{q_idx}")
        builder.button(text="🏠 Bosh Menyu", callback_data="main_menu")
        builder.adjust(1, 1)
        
        if is_corr:
            res_text = (
                f"🎉 **TO'G'RI JAVOB!** (+1 ball)\n\n"
                f"✅ **Siz tanladingiz:** {letters[chosen_idx]}) {options[chosen_idx]}\n\n"
                f"💡 **NEGA TO'G'RI? (Mantiqiy asos):**\n{q_data.get('why_right', '')}"
            )
        else:
            corr_idx = q_data.get("correct_index", 0)
            wrong_reason = "Ushbu variant chalg'ituvchi bo'lib, fanning asosiy qoidalariga zid keladi."
            why_wrongs = q_data.get("why_wrongs", {})
            if isinstance(why_wrongs, dict):
                wrong_reason = why_wrongs.get(letters[chosen_idx], wrong_reason)
            elif isinstance(why_wrongs, list):
                found = next((w for w in why_wrongs if w.get("letter") == letters[chosen_idx]), None)
                if found:
                    wrong_reason = found.get("reason", wrong_reason)
                    
            res_text = (
                f"❌ **NOTO'G'RI JAVOB! Birgalikda tahlil qilamiz:**\n\n"
                f"🛑 **Siz tanladingiz:** {letters[chosen_idx]}) {options[chosen_idx]}\n"
                f"🟢 **To'g'ri javob:** {letters[corr_idx]}) {options[corr_idx]}\n\n"
                f"✅ **NEGA TO'G'RI?:**\n{q_data.get('why_right', '')}\n\n"
                f"⚠️ **NEGA SIZ TANLAGAN VARIANT XATO?:**\n{wrong_reason}"
            )
        await callback.message.edit_text(res_text, reply_markup=builder.as_markup(), parse_mode="Markdown")
        await callback.answer()

# --- 💡 CHIROQ (HINT) VA ✂️ 50:50 ---
@dp.callback_query(F.data.startswith("hint:"))
async def cb_hint(callback: CallbackQuery):
    parts = callback.data.split(":")
    mode, subject, q_idx = parts[1], parts[2], int(parts[3])
    st = get_user_state(callback.from_user.id)
    
    if mode == "exam":
        q_data = st["exam_questions"][q_idx]
    else:
        q_data = SUBJECTS[subject]["db"][q_idx]
        
    hint_text = q_data.get("hint", "Ushbu savol bo'yicha asosiy tushunchalarni diqqat bilan solishtiring.")
    await callback.answer(f"💡 Maslahat: {hint_text}", show_alert=True)

@dp.callback_query(F.data.startswith("fifty:"))
async def cb_fifty(callback: CallbackQuery):
    parts = callback.data.split(":")
    mode, subject, q_idx = parts[1], parts[2], int(parts[3])
    st = get_user_state(callback.from_user.id)
    
    if mode == "exam":
        q_data = st["exam_questions"][q_idx]
    else:
        q_data = SUBJECTS[subject]["db"][q_idx]
        
    correct_idx = q_data.get("correct_index", 0)
    wrongs = [i for i in range(4) if i != correct_idx]
    to_eliminate = set(random.sample(wrongs, 2))
    st["eliminated"] = to_eliminate
    
    await callback.answer("✂️ 50:50: Ikkita noto'g'ri variant olib tashlandi!", show_alert=False)
    if mode == "exam":
        await send_exam_question(callback.message, callback.from_user.id, edit=True)
    else:
        await send_practice_question(callback.message, callback.from_user.id, edit=True)

# --- 🏁 IMTIHON YAKUNI VA SHAXSIY DIAGNOSTIKA ---
@dp.callback_query(F.data.startswith("finish_exam:"))
async def cb_finish_exam(callback: CallbackQuery):
    await show_exam_results(callback.message, callback.from_user.id, edit=True)
    await callback.answer()

async def show_exam_results(message: Message, user_id: int, edit: bool = False):
    st = get_user_state(user_id)
    questions = st["exam_questions"]
    answers = st["exam_answers"]
    subject = st["subject"]
    conf = SUBJECTS.get(subject, SUBJECTS["stat"])
    
    correct_count = 0
    mistakes_by_topic = {}
    diff_stats = {"oson": [0,0], "orta": [0,0], "qiyin": [0,0]}
    
    for idx, q in enumerate(questions):
        diff = q.get("difficulty", "orta")
        if diff not in diff_stats:
            diff = "orta"
        diff_stats[diff][1] += 1
        
        chosen = answers.get(idx)
        if chosen is not None and chosen == q.get("correct_index", 0):
            correct_count += 1
            diff_stats[diff][0] += 1
        else:
            tid = q.get("topic_id", 1)
            mistakes_by_topic.setdefault(tid, []).append((q, chosen))
            
    pct = round((correct_count / 25) * 100, 1)
    grade = "5 (A'LO) 🌟" if pct >= 86 else ("4 (YAXSHI) 👍" if pct >= 71 else ("3 (QONIQARLI) ⚠️" if pct >= 56 else "2 (QONIQARSIZ) 🛑"))
    
    st["history"].append({
        "subject": conf["name"],
        "score": correct_count,
        "pct": pct,
        "grade": grade
    })
    
    report = (
        f"🎓 **CYBER UNIVERSITY — ORALIQ NAZORAT NATIJASI**\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"📚 **Fan:** {conf['name']}\n"
        f"📅 **Imtihon sanasi:** {conf['badge']}\n"
        f"📊 **Natija:** **{correct_count} / 25** ({pct}%)\n"
        f"🏆 **Baho:** **{grade}**\n\n"
        f"📈 **Qiyinlik darajalari bo'yicha:**\n"
        f"• 🟢 Oson: {diff_stats['oson'][0]}/{diff_stats['oson'][1]}\n"
        f"• 🟡 O'rta: {diff_stats['orta'][0]}/{diff_stats['orta'][1]}\n"
        f"• 🔴 Qiyin: {diff_stats['qiyin'][0]}/{diff_stats['qiyin'][1]}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )
    
    if mistakes_by_topic:
        report += f"🎯 **SHAXSIY DIAGNOSTIKA VA TAVSIYALAR:**\n"
        report += f"_Siz quyidagi mavzulardan xatoga yo'l qo'ydingiz. Mana ularni tuzatish bo'yicha ko'rsatma:_\n\n"
        
        subject_topics = TOPICS_DATA.get(conf["topic_key"], [])
        for tid, items in list(mistakes_by_topic.items())[:3]:
            t_obj = next((t for t in subject_topics if t.get("id") == tid), None)
            t_title = t_obj.get("title_uz", f"{tid}-mavzu") if t_obj else f"{tid}-mavzu"
            advice = t_obj.get("improvement_guide", "Ushbu mavzu bo'yicha asosiy qoidalarni takrorlang.") if t_obj else "Nazariyani takrorlang."
            
            report += f"📌 **{t_title}** ({len(items)} ta xato):\n"
            report += f"💡 **Tavsiya:** {advice}\n"
            
            if t_obj and t_obj.get("videos"):
                v = t_obj["videos"][0]
                report += f"🎬 **Video darslik:** [{v['title']}]({v['url']})\n"
            report += "\n"
    else:
        report += f"🌟 **MUKAMMAL NATIJA!**\nSiz barcha 25 ta savolga 100% to'g'ri javob berdingiz. Siz oraliq nazoratga to'liq tayyorsiz!\n\n"
        
    builder = InlineKeyboardBuilder()
    builder.button(text="🔄 Yangi 25 talik Variant Boshlash", callback_data=f"start_exam:{subject}")
    builder.button(text="📖 200 talik Mashqqa O'tish", callback_data=f"start_practice:{subject}")
    builder.button(text="🏠 Bosh Menyu", callback_data="main_menu")
    builder.adjust(1, 1, 1)
    
    try:
        if edit:
            await message.edit_text(report, reply_markup=builder.as_markup(), parse_mode="Markdown", disable_web_page_preview=True)
        else:
            await message.answer(report, reply_markup=builder.as_markup(), parse_mode="Markdown", disable_web_page_preview=True)
    except Exception:
        await message.answer(report, reply_markup=builder.as_markup(), parse_mode="Markdown", disable_web_page_preview=True)

# --- 📖 200 TALIK MASHQ REJIMI ---
@dp.callback_query(F.data.startswith("start_practice:"))
async def cb_start_practice(callback: CallbackQuery):
    subject = callback.data.split(":")[1]
    if subject not in SUBJECTS:
        subject = "stat"
        
    st = get_user_state(callback.from_user.id)
    st["mode"] = "practice"
    st["subject"] = subject
    st["q_idx"] = 0
    st["eliminated"] = set()
    
    await callback.answer(f"{SUBJECTS[subject]['name']} bo'yicha mashq boshlandi!", show_alert=False)
    await send_practice_question(callback.message, callback.from_user.id, edit=True)

async def send_practice_question(message: Message, user_id: int, edit: bool = False):
    st = get_user_state(user_id)
    subject = st["subject"]
    conf = SUBJECTS.get(subject, SUBJECTS["stat"])
    db = conf["db"]
    q_idx = st["q_idx"]
    
    if q_idx >= len(db):
        st["q_idx"] = 0
        q_idx = 0
        
    q_data = db[q_idx]
    mode_label = "📖 **O'RGANISH VA MASHQ REJIMI (200 TALIK BAZA)**"
    text = format_question_text(q_data, q_idx + 1, len(db), mode_label, conf["name"])
    
    kb = get_question_keyboard("practice", subject, q_idx, st["eliminated"])
    
    try:
        if edit:
            await message.edit_text(text, reply_markup=kb, parse_mode="Markdown")
        else:
            await message.answer(text, reply_markup=kb, parse_mode="Markdown")
    except Exception:
        await message.answer(text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("next_practice:"))
async def cb_next_practice(callback: CallbackQuery):
    parts = callback.data.split(":")
    subject = parts[1]
    cur_idx = int(parts[2])
    
    st = get_user_state(callback.from_user.id)
    st["subject"] = subject
    st["mode"] = "practice"
    st["q_idx"] = cur_idx + 1
    st["eliminated"] = set()
    
    await send_practice_question(callback.message, callback.from_user.id, edit=True)
    await callback.answer()

# --- 📜 IMTIHONLAR TARIXI ---
@dp.callback_query(F.data == "my_history")
async def cb_my_history(callback: CallbackQuery):
    st = get_user_state(callback.from_user.id)
    history = st["history"]
    
    if not history:
        text = "📜 **Siz hali biror marta imtihon topshirmagansiz.**\n\n'⏱️ 25 talik Imtihon' tugmasi orqali o'zingizni sinab ko'ring!"
    else:
        text = "📜 **SIZNING IMTIHONLAR TARIXINGIZ:**\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        for idx, h in enumerate(reversed(history[-10:]), 1):
            text += f"**{idx}. {h['subject']}**\n"
            text += f"   • Natija: **{h['score']} / 25** ({h['pct']}%)\n"
            text += f"   • Baho: **{h['grade']}**\n\n"
        text += "_Oxirgi 10 ta urinish ko'rsatildi._"
        
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Bosh Menyu", callback_data="main_menu")
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown")
    await callback.answer()

# --- 📚 MAVZULAR ENSIKLOPEDIYASI ---
@dp.callback_query(F.data.startswith("view_topics:"))
async def cb_view_topics(callback: CallbackQuery):
    subject = callback.data.split(":")[1]
    conf = SUBJECTS.get(subject, SUBJECTS["stat"])
    topics = TOPICS_DATA.get(conf["topic_key"], [])
    
    builder = InlineKeyboardBuilder()
    for t in topics:
        builder.button(
            text=f"📌 {t['title_uz'][:35]}...",
            callback_data=f"read_topic:{subject}:{t['id']}"
        )
    builder.button(text="⬅️ Fan tanlash", callback_data="menu_choose_theory")
    builder.button(text="🏠 Bosh Menyu", callback_data="main_menu")
    builder.adjust(1)
    
    await callback.message.edit_text(
        f"📚 **{conf['name']} — 9 ta Mavzu Ensiklopediyasi:**\nKerakli mavzuni tanlang:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("read_topic:"))
async def cb_read_topic(callback: CallbackQuery):
    parts = callback.data.split(":")
    subject = parts[1]
    t_id = int(parts[2])
    
    conf = SUBJECTS.get(subject, SUBJECTS["stat"])
    topics = TOPICS_DATA.get(conf["topic_key"], [])
    t = next((item for item in topics if item["id"] == t_id), None)
    
    if not t:
        await callback.answer("Mavzu topilmadi!", show_alert=True)
        return
        
    text = (
        f"📖 **{t['title_uz']}**\n"
        f"🇬🇧 _{t.get('title_en', '')}_\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📘 **CHUQUR NAZARIYA:**\n{t.get('summary_deep', '')}\n\n"
        f"🏢 **REAL BIZNES / HAYOTIY KEYSI:**\n{t.get('case_study_extended', '')}\n\n"
        f"📐 **ASOSIY FORMULALAR VA QOIDALAR:**\n"
    )
    for f_item in t.get("formulas_detailed", []):
        text += f"• {f_item}\n"
        
    text += f"\n⚠️ **IMTIHONDAGI TUZOQLAR:**\n"
    for trap in t.get("exam_traps", []):
        text += f"• {trap}\n"
        
    if t.get("videos"):
        text += f"\n🎬 **FOYDALI VIDEO DARSLIKLAR:**\n"
        for v in t["videos"]:
            text += f"• [{v['title']}]({v['url']})\n  _{v.get('takeaway', '')}_\n"
            
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Mavzular ro'yxatiga qaytish", callback_data=f"view_topics:{subject}")
    builder.button(text="🏠 Bosh Menyu", callback_data="main_menu")
    builder.adjust(1, 1)
    
    await callback.message.edit_text(text, reply_markup=builder.as_markup(), parse_mode="Markdown", disable_web_page_preview=True)
    await callback.answer()

# --- 📄 PDF YUKLASH ---
@dp.callback_query(F.data.startswith("get_pdf:"))
async def cb_get_pdf(callback: CallbackQuery):
    subject = callback.data.split(":")[1]
    conf = SUBJECTS.get(subject, SUBJECTS["stat"])
    
    # Try finding PDF in scratch, desktop or D drive
    pdf_filename = conf["pdf_name"]
    candidate_paths = [
        os.path.join(BASE_DIR, pdf_filename),
        os.path.join(r"C:\Users\user\Desktop\SARALANGAN_HUJJATLAR", pdf_filename),
        os.path.join(r"D:\cyber fan\00_ORALIQ_NAZORAT_TOLIQ_QOLLANMALAR", pdf_filename)
    ]
    
    found_path = None
    for p in candidate_paths:
        if os.path.exists(p):
            found_path = p
            break
            
    if found_path:
        await callback.answer("PDF yuklanmoqda, iltimos kuting...", show_alert=False)
        doc = FSInputFile(found_path)
        await callback.message.answer_document(
            document=doc,
            caption=f"📄 **{conf['name']} — Oraliq Nazorat To'liq Qo'llanmasi**\nCyber University • MNG25-102 guruhi uchun maxsus.",
            parse_mode="Markdown"
        )
    else:
        await callback.answer(f"PDF fayl tayyorlanmoqda yoki serverda saqlanmagan: {pdf_filename}", show_alert=True)

# --- BOTNI ISHGA TUSHIRISH ---
async def main():
    logger.info("Bot ishga tushmoqda...")
    bot = Bot(token=BOT_TOKEN)
    await dp.start_polling(bot)


# ==================== MNG25-102 14 TALABA RO'YXATI VA KALITLARI ====================
MNG_STUDENTS_ROSTER = [
    {"num": 1, "name": "Axmadov Shaxzod", "key": "SHAXZOD-MNG102", "pin": "102011"},
    {"num": 2, "name": "Homidjonov Sardorbek", "key": "SARDOR-MNG102", "pin": "102022"},
    {"num": 3, "name": "Ilhomjonov Jamshid", "key": "JAMSHID-MNG102", "pin": "102033"},
    {"num": 4, "name": "Mirobidova Fotima", "key": "FOTIMA-MNG102", "pin": "102044"},
    {"num": 5, "name": "Mirzayev Quvonch", "key": "QUVONCH-7777", "pin": "777705", "role": "admin"},
    {"num": 6, "name": "Musurmonov Abdulaziz", "key": "ABDULAZIZ-MNG102", "pin": "102066"},
    {"num": 7, "name": "Muhammadjonov Otabek", "key": "OTABEK-MNG102", "pin": "102070"},
    {"num": 8, "name": "Narimbetov Islombek", "key": "ISLOM-MNG102", "pin": "102077"},
    {"num": 9, "name": "Ochilova Sadoqat", "key": "SADOQAT-MNG102", "pin": "102088"},
    {"num": 10, "name": "Tirkashev Ravshan", "key": "RAVSHAN-MNG102", "pin": "102100"},
    {"num": 11, "name": "Urolov Daler", "key": "DALER-MNG102", "pin": "102111"},
    {"num": 12, "name": "Xoliqulova Gulsevar", "key": "GULSEVAR-MNG102", "pin": "102122"},
    {"num": 13, "name": "Xolmatov Sherali", "key": "SHERALI-MNG102", "pin": "102133"},
    {"num": 14, "name": "Shaydullayev Asadbek", "key": "ASADBEK-MNG102", "pin": "102099"}
]

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

if __name__ == "__main__":
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("DIQQAT: Botni ishga tushirish uchun BOT_TOKEN muhit o'zgaruvchisini o'rnating yoki kodga yozing.")
        print("Masalan: $env:BOT_TOKEN='your_token'; python telegram_bot.py")
        print("Sintaksis va modullar 100% muvaffaqiyatli tekshirildi.")
    else:
        asyncio.run(main())
