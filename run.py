import threading
import time

from main import user_bot
from admin_bot import admin_bot, register_approve_command  # <-- важно импортировать функцию

if __name__ == "__main__":
    # Регистрируем обработчик approve до запуска polling
    register_approve_command(user_bot)

    def run_user_bot():
        print("🤖 Основной бот запущен")
        try:
            user_bot.polling(none_stop=True, skip_pending=True)
        except Exception as e:
            print(f"[ERROR] Основной бот упал: {e}")

    def run_admin_bot():
        print("🛠 Админ-бот запущен")
        try:
            admin_bot.polling(none_stop=True, skip_pending=True)
        except Exception as e:
            print(f"[ERROR] Админ-бот упал: {e}")

    t1 = threading.Thread(target=run_user_bot, daemon=True)
    t2 = threading.Thread(target=run_admin_bot, daemon=True)

    t1.start()
    t2.start()

    print("🚀 Оба бота работают. Нажми Ctrl+C для выхода")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⛔ Остановка ботов")
        