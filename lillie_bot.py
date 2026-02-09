import os
import random
import pandas as pd
import telebot
from dotenv import load_dotenv
import time

# Used @BotFather on Telegram to create a new bot and get the token
# In .env, paste BOT_TOKEN= token_from_Telegram

# Loading environment variables from .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in .env")

bot = telebot.TeleBot(BOT_TOKEN)

# Loading Goodreads CSV
books = pd.read_csv("goodreads_library_export.csv")

# Filtering only the "Want to Read" shelf
tbr = books[books["Exclusive Shelf"] == "to-read"]

# Keeping track of recently recommended books
recent_books = []
MAX_RECENT = 5  # number of books to remember to avoid repeats

# ---------------- COMMANDS ---------------- #

@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "Hi Elle, I can help you pick your next read!\n"
        "Use /nextread to get a book recommendation."
    )

@bot.message_handler(commands=["nextread"])
def recommend_book(message):
    if tbr.empty:
        bot.send_message(message.chat.id, "Your 'Want to Read' shelf is empty!")
        return

    # Random book
    book = tbr.sample(1).iloc[0]

    title = book.get("Title", "Unknown")
    author = book.get("Author", "Unknown")
    rating = book.get("Average Rating", "N/A")

    # Escape characters for MarkdownV2
    def escape_md(text):
        escape_chars = "_*[]()~`>#+-=|{}.!\\"
        return "".join(f"\\{c}" if c in escape_chars else c for c in str(text))

    reply = (
        f"📖 *Your next read:*\n\n"
        f"*Title:* {escape_md(title)}\n"
        f"*Author:* {escape_md(author)}\n"
        f"*Average Rating:* {escape_md(rating)}⭐"
    )

    bot.send_message(message.chat.id, reply, parse_mode="MarkdownV2")

# ---------------- RUN ---------------- #

# Resilient polling loop
while True:
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=10)
    except Exception as e:
        print(f"Polling error: {e}")
        time.sleep(5)

