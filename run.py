from flask import Flask, request
import telebot
import os
import time

from main import user_bot
from admin_bot import admin_bot, register_approve_command

app = Flask(__name__)

PORT = int(os.getenv("PORT", 5000))
WEBHOOK_URL_USER = os.getenv("WEBHOOK_URL_USER")
WEBHOOK_URL_ADMIN = os.getenv("WEBHOOK_URL_ADMIN")

register_approve_command(user_bot)

@app.route("/user_webhook", methods=["POST"])
def user_webhook():
    update = request.get_json()
    if update:
        user_bot.process_new_updates([
            telebot.types.Update.de_json(update)
        ])
    return "OK", 200

@app.route("/admin_webhook", methods=["POST"])
def admin_webhook():
    update = request.get_json()
    if update:
        admin_bot.process_new_updates([
            telebot.types.Update.de_json(update)
        ])
    return "OK", 200

if __name__ == "__main__":
    print(f"🚀 Railway Flask started on port {PORT}")

    # Устанавливаем webhook с повторной попыткой
    for attempt in range(3):
        try:
            user_bot.remove_webhook()
            user_bot.set_webhook(url=WEBHOOK_URL_USER)

            admin_bot.remove_webhook()
            admin_bot.set_webhook(url=WEBHOOK_URL_ADMIN)
            print("✅ Webhook успешно установлен")
            break
        except Exception as e:
            print(f"⚠️ Попытка {attempt+1} не удалась: {e}")
            time.sleep(5)
    else:
        print("❌ Не удалось установить webhook после 3 попыток")

    app.run(host="0.0.0.0", port=PORT)