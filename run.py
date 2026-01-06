import threading, time
from main import user_bot
from admin_bot import admin_bot, register_approve_command

if __name__ == "__main__":
    # Регистрируем approve
    register_approve_command(user_bot)

    # Запуск ботов
    threading.Thread(target=lambda: user_bot.polling(none_stop=True, skip_pending=True), daemon=True).start()
    threading.Thread(target=lambda: admin_bot.polling(none_stop=True, skip_pending=True), daemon=True).start()

    print("🚀 User Bot и Admin Bot запущены")

    # Главный цикл для логов
    while True:
        time.sleep(10)
        print("User Bot активен ✅")
        print("Admin Bot активен ✅")