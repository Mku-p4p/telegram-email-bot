import os
import json
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Логування
logging.basicConfig(level=logging.INFO)

# Авторизація Google Sheets через змінну середовища
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds_dict = json.loads(os.getenv("GOOGLE_CREDS_JSON"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("UserEmails").sheet1  # назва Google таблиці

# Стан користувача
user_states = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_states[user.id] = {"step": "waiting_for_email"}
    username = user.first_name or user.username or "there"

    keyboard = [[InlineKeyboardButton("Provide Email", callback_data="provide_email")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🎉 Hi {username}! Congratulations on winning the quiz!\nPlease click below to provide your email so we can send you your free spins!",
        reply_markup=reply_markup
    )

# Натискання кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = update.effective_user

    if query.data == "provide_email":
        user_states[user.id] = {"step": "waiting_for_email"}
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="✉️ Please enter your email:"
        )
   elif query.data == "confirm_email":
    email = user_states[user.id]["email"]
    full_name = user.full_name or "unknown"
    nickname = user.username or "no username"
    sheet.append_row([full_name, nickname, email])

    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="✅ Your email has been submitted successfully!"
    )
    user_states[user.id] = {"step": "done"}

        user_states[user.id] = {"step": "done"}
    elif query.data == "cancel_email":
        user_states[user.id] = {"step": "waiting_for_email"}
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="❌ Email entry canceled. Please enter your email again:"
        )

# Обробка тексту (емейл)
async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    state = user_states.get(user.id, {}).get("step")

    if state == "waiting_for_email":
        email = update.message.text.strip()
        user_states[user.id]["email"] = email

        keyboard = [
            [
                InlineKeyboardButton("✅ Yes", callback_data="confirm_email"),
                InlineKeyboardButton("❌ No", callback_data="cancel_email")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Is this your email?\n📧 {email}",
            reply_markup=reply_markup
        )

# Запуск
def main():
    token = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, email_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
