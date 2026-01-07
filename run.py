from flask import Flask, request
import telebot
import os
import time
import traceback

from main import user_bot
from admin_bot import admin_bot, register_approve_command

app = Flask(__name__)

PORT = int(os.getenv("PORT")) 
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not WEBHOOK_URL:
    raise ValueError("❌ WEBHOOK_URL не задан в переменных окружения!")

register_approve_command(user_bot)

@app.route("/webhook", methods=["POST"])
def user_webhook():
    try:
        update = request.get_json()
        if update:
            user_bot.process_new_updates([
                telebot.types.Update.de_json(update)
            ])
    except Exception as e:
        print("⚠️ Ошибка при обработке webhook:")
        traceback.print_exc()
    return "OK", 200

if __name__ == "__main__":
    print(f"🚀 Railway Flask started on port {PORT}")

    # Устанавливаем webhook с логами
    for attempt in range(3):
        try:
            user_bot.remove_webhook()
            user_bot.set_webhook(url=WEBHOOK_URL)
            print("✅ Webhook успешно установлен для user_bot")
            break
        except Exception as e:
            print(f"⚠️ Попытка {attempt+1} не удалась: {e}")
            traceback.print_exc()
            time.sleep(5)
    else:
        print("❌ Не удалось установить webhook после 3 попыток")

    app.run(host="0.0.0.0", port=PORT)