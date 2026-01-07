import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random, string, re
from datetime import datetime, timezone
from pymongo import MongoClient
from utils import delete_process_technical
from admin_bot import send_to_admin
import os

# -------------------- Настройки --------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")  # теперь берем из .env
MANAGER_ID = int(os.getenv("MANAGER_ID", 0))

user_bot = telebot.TeleBot(BOT_TOKEN, threaded=False)  # threaded=False для Webhook

# -------------------- MongoDB --------------------
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.shadow_bot
orders_col = db.orders
config_col = db.config

# -------------------- Хранилища --------------------
user_data = {}
attempts_data = {}
last_message = {}
start_message_id = {}

# -------------------- Получение актуального кошелька и суммы --------------------
def get_current_payment_config():
    config = config_col.find_one()
    if not config:
        return {
            "payment_amount": 20,
            "wallet": "TJcWGwkKNYCmpt6otaM7vf1gj1KBEsdzNX"
        }
    return {
        "payment_amount": config.get("amount", 20),
        "wallet": config.get("wallet", "TJcWGwkKNYCmpt6otaM7vf1gj1KBEsdzNX")
    }

# -------------------- Утилиты --------------------
def send_clean_message(chat_id, text, keyboard=None):
    if chat_id in last_message:
        try:
            if last_message[chat_id] != start_message_id.get(chat_id):
                user_bot.delete_message(chat_id, last_message[chat_id])
        except:
            pass
    msg = user_bot.send_message(chat_id, text, reply_markup=keyboard, parse_mode="Markdown")
    last_message[chat_id] = msg.message_id
    return msg

def generate_order_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# -------------------- Меню --------------------
def main_menu(chat_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Удалить профиль", callback_data="erase_account"))
    kb.add(InlineKeyboardButton("Удалить чат", callback_data="erase_chat"))
    kb.add(InlineKeyboardButton("Удалить канал", callback_data="erase_channel"))
    kb.add(InlineKeyboardButton("Помощь", callback_data="help"))
    kb.add(InlineKeyboardButton("Как это работает", callback_data="protocol_info"))
    send_clean_message(chat_id, "Выберите действие:", kb)

# -------------------- Старт --------------------
@user_bot.message_handler(commands=['start', 'erase_chat'])
def universal_handler(message):
    chat_id = message.chat.id
    if message.text == "/start":
        start_bot(message)
    elif message.text == "/erase_chat":
        erase_chat_command(message)

def start_bot(message):
    chat_id = message.chat.id
    username = message.from_user.first_name
    msg = user_bot.send_message(
        chat_id,
        f"Привет, {username}!\nТы вошёл в Shadow Protocol.\n⚠️ Действия необратимы.\n⚠️ Логи не сохраняются."
    )
    start_message_id[chat_id] = msg.message_id

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Ознакомиться с ботом", callback_data="about_bot"))
    send_clean_message(chat_id, "Нажмите кнопку ниже, чтобы ознакомиться с ботом:", kb)

    attempts_data[chat_id] = {"erase_account":3, "erase_chat":3, "erase_channel":3}

def erase_chat_command(message):
    chat_id = message.chat.id
    deleted_count = 0
    for msg_id in range(last_message.get(chat_id, 0), 0, -1):
        try:
            user_bot.delete_message(chat_id, msg_id)
            deleted_count += 1
        except:
            pass
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu"))
    send_clean_message(chat_id, f"✅ Удаление завершено. Бот удалил {deleted_count} своих сообщений.", kb)

# -------------------- Callback --------------------
@user_bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id

    if call.data == "about_bot":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Список команд", callback_data="menu"))
        send_clean_message(chat_id, "Shadow Protocol — бот для удаления профилей, чатов и каналов Telegram.\n⚠️ Действия необратимы.", kb)
        return

    if call.data == "menu":
        main_menu(chat_id)
        return

    if call.data == "help":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu"))
        send_clean_message(chat_id, "Для поддержки напишите: @YourSupportUsername", kb)
        return

    if call.data == "protocol_info":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu"))
        info_text = (
            "Shadow Protocol — бот для безопасного удаления профилей, чатов и каналов Telegram.\n"
            "⚠️ Все действия необратимы.\n"
            "💡 Порядок работы:\n"
            "1️⃣ Вы выбираете действие\n"
            "2️⃣ Вводите @username\n"
            "3️⃣ Подтверждаете оплату\n"
            "4️⃣ Админ проверяет скрин и подтверждает\n"
            "5️⃣ Действие выполнено"
        )
        send_clean_message(chat_id, info_text, kb)
        return

    if call.data in ["erase_account", "erase_chat", "erase_channel"]:
        if chat_id not in attempts_data:
            attempts_data[chat_id] = {"erase_account":3, "erase_chat":3, "erase_channel":3}
        if attempts_data[chat_id][call.data] <= 0:
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu"))
            send_clean_message(chat_id, "Попытки исчерпаны.", kb)
            return
        action_name = {"erase_account": "профиль", "erase_chat": "чат", "erase_channel": "канал"}[call.data]
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Отмена / Вернуться в меню", callback_data="menu"))
        send_clean_message(chat_id, f"Введите юзернейм для удаления {action_name} в формате @username:", kb)
        user_data[chat_id] = {"action": call.data, "action_waiting": True}

    if call.data == "paid":
        send_clean_message(chat_id, "📸 Отправьте скриншот оплаты.")

# -------------------- Подтверждение юзернейма --------------------
@user_bot.message_handler(func=lambda m: m.chat.id in user_data and user_data[m.chat.id].get("action_waiting"))
def confirm_username(message):
    chat_id = message.chat.id
    action_type = user_data[chat_id]["action"]
    username = message.text.strip()

    if not re.match(r"^@\w{5,32}$", username):
        attempts_data[chat_id][action_type] -= 1
        remaining = attempts_data[chat_id][action_type]
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Отмена / Вернуться в меню", callback_data="menu"))
        if remaining > 0:
            send_clean_message(chat_id, f"Юзер введён неверно. Осталось {remaining} попытки.", kb)
        else:
            send_clean_message(chat_id, "Попытки исчерпаны.", kb)
            user_data.pop(chat_id, None)
        return

    order_id = generate_order_id()
    order_doc = {
        "order_id": order_id,
        "chat_id": chat_id,
        "username": username,
        "action": action_type,
        "status": "await_payment",
        "created_at": datetime.now(timezone.utc)
    }
    orders_col.insert_one(order_doc)
    print(f"[DEBUG] Заказ создан: {order_doc}")

    # Получаем актуальные кошелек и сумму
    config = get_current_payment_config()
    PAYMENT_AMOUNT = config["payment_amount"]
    TRON_WALLET = config["wallet"]

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Я оплатил", callback_data="paid"))
    kb.add(InlineKeyboardButton("Вернуться в меню", callback_data="menu"))

    send_clean_message(
        chat_id,
        f"🆔 Заявка: {order_id}\n👤 {username}\n💰 Сумма: {PAYMENT_AMOUNT} USDT\n"
        f"🏦 Кошелек:\n`{TRON_WALLET}`\nПосле оплаты нажмите «Я оплатил» и отправьте скриншот.",
        kb
    )

# -------------------- Скриншоты --------------------
@user_bot.message_handler(content_types=['photo', 'document'])
def screenshot(message):
    chat_id = message.chat.id
    payment = orders_col.find_one({"chat_id": chat_id, "status": "await_payment"})
    if not payment:
        send_clean_message(chat_id, "⚠️ Нет активных заказов для проверки.")
        return

    try:
        if message.content_type == 'photo' and message.photo:
            file_info = user_bot.get_file(message.photo[-1].file_id)
            downloaded_file = user_bot.download_file(file_info.file_path)
            file_name = f"{payment['order_id']}.jpg"
        elif message.content_type == 'document' and message.document:
            file_info = user_bot.get_file(message.document.file_id)
            downloaded_file = user_bot.download_file(file_info.file_path)
            file_name = f"{payment['order_id']}_{message.document.file_name}"
        else:
            send_clean_message(chat_id, "⚠️ Нужно отправить фото или документ.")
            return

        with open(file_name, "wb") as f:
            f.write(downloaded_file)

        orders_col.update_one(
            {"order_id": payment["order_id"]},
            {"$set": {"status": "on_review", "photo_file_id": file_name}}
        )

        send_clean_message(chat_id, "⏳ Платёж отправлен на проверку админом.")

        # -------------------- Отправка админу --------------------
        send_to_admin(payment['order_id'], payment['username'], file_name)

    except Exception as e:
        print(f"[ERROR] Ошибка при отправке скрина: {e}")
        send_clean_message(chat_id, "❌ Ошибка при отправке скрина. Попробуйте ещё раз.")