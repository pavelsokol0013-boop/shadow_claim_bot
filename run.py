from flask import Flask, request
import telebot
import os

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

if WEBHOOK_URL_USER and WEBHOOK_URL_ADMIN:
    user_bot.remove_webhook()
    user_bot.set_webhook(url=WEBHOOK_URL_USER)

    admin_bot.remove_webhook()
    admin_bot.set_webhook(url=WEBHOOK_URL_ADMIN)

if __name__ == "__main__":
    print(f"🚀 Railway Flask started on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)