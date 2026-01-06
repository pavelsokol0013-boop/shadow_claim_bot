import time
import random
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def delete_process_technical(bot, chat_id, username, cleanup_message_id=None):
    if cleanup_message_id:
        try:
            bot.delete_message(chat_id, cleanup_message_id)
        except:
            pass

    steps = ["INIT_SESSION","COLLECT_METADATA","SEND_REPORT_BATCH (x32)","TRIGGER_REVIEW_LOOP","INVALIDATE_HISTORY","FINALIZE"]
    percents = [17, 39, 62, 91, 98, 100]
    step_times = [datetime.now().strftime("%H:%M:%S") for _ in steps]

    msg = bot.send_message(chat_id, f"[ShadowNode‑12]\nOperation: ERASE_OBJECT\nTarget: {username}\n")

    for idx, (step, percent) in enumerate(zip(steps, percents)):
        time.sleep(random.uniform(0.8, 1.5))
        text = f"[ShadowNode‑12]\nOperation: ERASE_OBJECT\nTarget: {username}\n\n"
        for i in range(idx + 1):
            bar = "▮" * (percents[i] // 10) + "▯" * (10 - percents[i] // 10)
            text += f"[{step_times[i]}] {steps[i]}\n{bar} {percents[i]}%\n"
        try:
            bot.edit_message_text(text, chat_id, msg.message_id)
        except:
            pass

    try:
        bot.delete_message(chat_id, msg.message_id)
    except:
        pass

    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("Вернуться к действиям", callback_data="menu"))
    msg_end = bot.send_message(chat_id, f"✅ {username} удалён.", reply_markup=kb)
