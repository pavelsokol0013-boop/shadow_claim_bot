import time
from admin_bot import admin_bot, register_approve_command
from main import user_bot

print("🛠 Admin Bot запускается")

register_approve_command(user_bot)

while True:
    try:
        admin_bot.polling(none_stop=True)
    except Exception as e:
        print("❌ Admin bot error:", e)
        time.sleep(5)