import telebot
import shutil
import psutil  
import requests
import subprocess

token = ('YOUR_BOT_TOKEN')
MY_ID = 'YOUR_ID'

bot = telebot.TeleBot(token)

def get_disk_info():
    total, used, free = shutil.disk_usage("/")
    total_gb = total / (1024 ** 3)
    used_gb = used / (1024 ** 3)
    free_gb = free / (1024 ** 3)
    percent_used = (used / total) * 100
    message = (
        "============================\n"
        f"Total: {total_gb:.2f} G \n"
        f"Busy: {used_gb:.2f} G \n"
        f"Free: {free_gb:.2f} G \n"
        F"Free in percentage: {100 - percent_used:.1f} % \n"
        "============================"
    )
    return message

bot_commands = [
    telebot.types.BotCommand("/start", "Launch the bot"),
    telebot.types.BotCommand("/disk_info", "Retrieving data from the disk"),
    telebot.types.BotCommand("/net", "Retrieving data from network traffic"),
    telebot.types.BotCommand("/ram", "Retrieving data from RAM"),
    telebot.types.BotCommasn("/journal", "Show the last n log lines (default 10)")  
    ]
bot.set_my_commands(bot_commands)

@bot.message_handler(commands=['start'])
def start(msg):
    print(f"/start. ID_USER: {msg.from_user.id}")
    if msg.from_user.id == MY_ID:
        bot.reply_to(msg, "Hello! Use /disk_info , /net or /ram")
    else:
        bot.reply_to(msg, f"Error")

@bot.message_handler(commands=['disk_info'])
def df_info(msg):
    print(f"/disk_info. ID_USER: {msg.from_user.id}")
    if msg.from_user.id != MY_ID:
        bot.reply_to(msg, "Access denied")
        return
    try:
        info = get_disk_info()
        bot.reply_to(msg, info)
    except Exception as e:
        bot.reply_to(msg, f"Error: {e}")

@bot.message_handler(commands=['net'])
def net(msg):
    print(f"/net. ID_USER: {msg.from_user.id}")
    if msg.from_user.id != MY_ID:
        bot.reply_to(msg, "Access denied")
        return
    try:
        requests.get("https://google.com", timeout=3)
        internet = " Аvailable "
    except:
        internet =" not available "
    
    net_io = psutil.net_io_counters()
    sent_mb = net_io.bytes_sent / (1024**2)
    recv_mb = net_io.bytes_recv / (1024**2)
    
    info = (
        "============================\n"
        f"Internet: {internet}\n"
        f"Sent: {sent_mb:.2f} M \n"
        f"recieve: {recv_mb:.2f} M \n"
        "============================"
    )
    bot.reply_to(msg, info)

@bot.message_handler(['ram'])
def ram(msg):
    print(f"/ram. ID_USER: {msg.from_user.id}")
    if msg.from_user.id != MY_ID:
        bot.reply_to(msg, "Access denied")
        return
    mem = psutil.virtual_memory()
    total_mb = mem.total / (1024 ** 2)
    used_md = mem.used / (1024**2)
    free_mb = mem.available / (1024 ** 2)
    per = mem.percent
    info = (
        "============================\n"
        f"total_memory: {total_mb:.2f} Mb\n"
        f"used: {used_md:.2f} Mb \n"
        f"free: {free_mb:.2f} Mb \n"
        f"used_persent: {per}% \n"
        "============================"
    )
    bot.reply_to(msg, info)
@bot.message_handler(["/journal"])
def journalctl(msg):
    print(f"/journal. ID_USER: {msg.from_user.id}")
    if msg.from_user.id != MY_ID:
        bot.reply_to(msg, "Access denied")
        return
    p = msg.text.split(' ')
    
    if len(p) > 1:
        lines = p[1]
    else:
        lines = "10"
    try:
        result = subprocess.run(
            ["journalctl", "-n", lines, "--no-pager"],
            capture_output=True,
            text=True,
            timeout=5
        )
        output = result.stdout.strip()
        if len(output) > 3500:
            output = "...\n" + output[-3500:]
        bot.reply_to(msg, f"journalctl ({lines} lines):\n{output}")
    except Exception as e:
        bot.reply_to(msg, f"ERROR: {e}")

bot.infinity_polling()