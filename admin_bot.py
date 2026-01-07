import telebot
import os
from pymongo import MongoClient
from telebot import types
from dotenv import load_dotenv

load_dotenv()

ADMIN_BOT_TOKEN = os.getenv("8532357074:AAGLA8DtQdvhpw_OM2SxLDwHwGi7RhDOT4s")
MANAGER_ID = int(os.getenv("7667654870"))
admin_bot = telebot.TeleBot(ADMIN_BOT_TOKEN, threaded=False)

# Mongo
MONGO_URI = os.getenv("mongodb+srv://shadow_user:Z4absent@cluster0.xmn2jzp.mongodb.net/?appName=Cluster0")
client = MongoClient(MONGO_URI)
db = client.shadow_bot
orders_col = db.orders
config_col = db.config

# -------------------- Отправка скрина админу --------------------
def send_to_admin(order_id, username, file_path):
    with open(file_path, "rb") as f:
        admin_bot.send_photo(
            MANAGER_ID,
            f,
            caption=f"💰 Новый платёж\n🆔 {order_id}\n👤 {username}\n\n/approve {order_id}"
        )

# -------------------- Настройки --------------------
def send_config_buttons(chat_id):
    config = config_col.find_one({})
    amount = config.get("amount", "не установлено") if config else "не установлено"
    wallet = config.get("wallet", "не установлен") if config else "не установлен"
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(text=f"Сумма: {amount}", callback_data="show_amount"))
    markup.add(types.InlineKeyboardButton(text=f"Кошелек: {wallet}", callback_data="show_wallet"))
    markup.add(types.InlineKeyboardButton(text="Установить сумму", callback_data="set_amount"))
    markup.add(types.InlineKeyboardButton(text="Установить кошелек", callback_data="set_wallet"))
    admin_bot.send_message(chat_id, "Настройки бота:", reply_markup=markup)

# -------------------- Команды админа --------------------
def register_approve_command(user_bot):

    @admin_bot.message_handler(commands=["approve"])
    def approve(message):
        if message.from_user.id != MANAGER_ID:
            return
        parts = message.text.split()
        if len(parts) != 2:
            admin_bot.send_message(message.chat.id, "❌ Используй: /approve ORDER_ID")
            return

        order_id = parts[1]
        order = orders_col.find_one({"order_id": order_id})
        if not order:
            admin_bot.send_message(message.chat.id, "❌ Заказ не найден")
            return

        if order["status"] != "on_review":
            admin_bot.send_message(message.chat.id, f"⚠️ Заказ в статусе: {order['status']}")
            return

        orders_col.update_one({"order_id": order_id}, {"$set": {"status": "paid"}})

        chat_id = order["chat_id"]
        username = order["username"]

        try:
            if "photo_file_id" in order:
                user_bot.delete_message(chat_id, order.get("message_id_for_check", None))
        except:
            pass

        msg = user_bot.send_message(chat_id, f"✅ Оплата принята\n⏳ Процесс удаления начнётся через 5 секунд...")

        import threading
        from utils import delete_process_technical
        threading.Timer(5.0, delete_process_technical, args=(user_bot, chat_id, username)).start()

        admin_bot.send_message(message.chat.id, f"✅ Заказ {order_id} подтверждён. Процесс удаления запустится через 5 секунд.")

    @admin_bot.message_handler(commands=["config"])
    def config(message):
        if message.from_user.id != MANAGER_ID:
            return
        send_config_buttons(message.chat.id)

    @admin_bot.callback_query_handler(func=lambda call: call.from_user.id == MANAGER_ID)
    def callback_handler(call):
        if call.data == "show_amount":
            config = config_col.find_one({})
            amount = config.get("amount", "не установлено") if config else "не установлено"
            admin_bot.answer_callback_query(call.id, f"Текущая сумма: {amount}", show_alert=True)
        elif call.data == "show_wallet":
            config = config_col.find_one({})
            wallet = config.get("wallet", "не установлен") if config else "не установлен"
            admin_bot.answer_callback_query(call.id, f"Текущий кошелек: {wallet}", show_alert=True)
        elif call.data == "set_amount":
            msg = admin_bot.send_message(call.message.chat.id, "Введите новую сумму:")
            admin_bot.register_next_step_handler(msg, set_amount)
        elif call.data == "set_wallet":
            msg = admin_bot.send_message(call.message.chat.id, "Введите новый кошелек:")
            admin_bot.register_next_step_handler(msg, set_wallet)

    def set_amount(message):
        if message.from_user.id != MANAGER_ID:
            return
        try:
            amount = float(message.text)
            if amount <= 0:
                admin_bot.send_message(message.chat.id, "❌ Сумма должна быть положительным числом.")
                return
            config_col.update_one({}, {"$set": {"amount": amount}}, upsert=True)
            admin_bot.send_message(message.chat.id, f"✅ Сумма обновлена: {amount}")
        except ValueError:
            admin_bot.send_message(message.chat.id, "❌ Введите корректное число.")

    def set_wallet(message):
        if message.from_user.id != MANAGER_ID:
            return
        wallet = message.text.strip()
        if not wallet:
            admin_bot.send_message(message.chat.id, "❌ Кошелек не может быть пустым.")
            return
        config_col.update_one({}, {"$set": {"wallet": wallet}}, upsert=True)
        admin_bot.send_message(message.chat.id, f"✅ Кошелек обновлен: {wallet}")