import threading
import time

from main import user_bot  # <-- в main.py у тебя user_bot = telebot.TeleBot(BOT_TOKEN)
from admin_bot import admin_bot, register_approve_command

if __name__ == "__main__":
    # ✅ Регистрируем обработчик approve до запуска polling
    register_approve_command(user_bot)

    def run_user_bot():
        print("🤖 Основной бот запущен")
        user_bot.polling(none_stop=True, skip_pending=True)

    def run_admin_bot():
        print("🛠 Админ-бот запущен")
        admin_bot.polling(none_stop=True, skip_pending=True)

    # создаём обычные потоки (без daemon=True!)
    t1 = threading.Thread(target=run_user_bot)
    t2 = threading.Thread(target=run_admin_bot)

    t1.start()
    t2.start()

    print("🚀 Оба бота работают. Нажми Ctrl+C для выхода")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⛔ Остановка ботов")