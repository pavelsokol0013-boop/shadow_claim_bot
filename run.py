import threading
import time
from main import user_bot
from admin_bot import admin_bot, register_approve_command

if __name__ == "__main__":
    # Регистрируем команды approve для админ-бота
    register_approve_command(user_bot)

    # Функции для polling
    def run_user_bot():
        print("🚀 User Bot запускается...")
        user_bot.polling(none_stop=True, skip_pending=True)

    def run_admin_bot():
        print("🛠 Admin Bot запускается...")
        admin_bot.polling(none_stop=True, skip_pending=True)

    # Запуск ботов в отдельных потоках
    t1 = threading.Thread(target=run_user_bot, daemon=True)
    t2 = threading.Thread(target=run_admin_bot, daemon=True)

    t1.start()
    t2.start()

    # Периодическая проверка в главном потоке
    while True:
        time.sleep(5)
        print("User Bot активен ✅")
        print("Admin Bot активен ✅")