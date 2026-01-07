import os
from dotenv import load_dotenv
import telebot
from main import user_bot
from admin_bot import admin_bot, register_approve_command
from flask import Flask, request

load_dotenv()

WEBHOOK_URL_USER = os.getenv("WEBHOOK_URL_USER")
WEBHOOK_URL_ADMIN = os.getenv("WEBHOOK_URL_ADMIN")
PORT = int(os.environ.get("PORT", 5000))

app = Flask(__name__)

# Регистрируем обработчики админа
register_approve_command(user_bot)

# -------------------- Webhook маршруты --------------------
@app.route("/user_webhook", methods=["POST"])
def user_webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        user_bot.process_new_updates([update])
        return "", 200
    return "Invalid request", 400

@app.route("/admin_webhook", methods=["POST"])
def admin_webhook():
    if request.headers.get("content-type") == "application/json":
        json_string = request.get_data().decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        admin_bot.process_new_updates([update])
        return "", 200
    return "Invalid request", 400

# -------------------- Установка Webhook --------------------
user_bot.remove_webhook()
user_bot.set_webhook(url=WEBHOOK_URL_USER)

admin_bot.remove_webhook()
admin_bot.set_webhook(url=WEBHOOK_URL_ADMIN)

if __name__ == "__main__":
    print(f"🚀 Flask сервер запущен на порту {PORT}, Webhooks готовы")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)