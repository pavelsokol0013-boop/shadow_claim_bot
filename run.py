import threading, time
from main import user_bot
from admin_bot import admin_bot, register_approve_command

if __name__ == "__main__":
    register_approve_command(user_bot)

    t1 = threading.Thread(target=lambda: user_bot.polling(none_stop=True, skip_pending=True), daemon=True)
    t2 = threading.Thread(target=lambda: admin_bot.polling(none_stop=True, skip_pending=True), daemon=True)

    t1.start()
    t2.start()

    while True:
        time.sleep(1)