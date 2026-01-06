import time
from main import user_bot

print("🚀 User Bot запускается")

while True:
    try:
        user_bot.polling(none_stop=True)
    except Exception as e:
        print("❌ User bot error:", e)
        time.sleep(5)