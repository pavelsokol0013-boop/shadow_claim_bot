from flask import Flask, request
from main import user_bot
from admin_bot import admin_bot, register_approve_command
import os

PORT = int(os.getenv("PORT", 8080))
WEBHOOK_URL_USER = os.getenv("WEBHOOK_URL_USER")
WEBHOOK_URL_ADMIN = os.getenv("WEBHOOK_URL_ADMIN")

app = Flask(__name__)

# Регистрируем команды админа
register_approve_command(user_bot)

# Webhook маршруты
@app.route("/user_webhook", methods=["POST"])
def user_webhook():
    update = request.get_json()
    if update:
        user_bot.process_new_updates([user_bot.types.Update.de_json(update)])
    return "OK", 200

@app.route("/admin_webhook", methods=["POST"])
def admin_webhook():
    update = request.get_json()
    if update:
        admin_bot.process_new_updates([admin_bot.types.Update.de_json(update)])
    return "OK", 200

# Установка webhook
user_bot.remove_webhook()
user_bot.set_webhook(url=WEBHOOK_URL_USER)

admin_bot.remove_webhook()
admin_bot.set_webhook(url=WEBHOOK_URL_ADMIN)

if __name__ == "__main__":
    print(f"🚀 Flask сервер запущен на порту {PORT}, Webhooks готовы")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)