from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Авторизація Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("UserEmails").sheet1

# Стани
user_states = {}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_states[user.id] = {"stage": "awaiting_button", "username": user.username}
    keyboard = [[InlineKeyboardButton("Provide Email", callback_data="provide_email")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"Hi {user.first_name}! 🎉\n\nCongrats on winning the quiz!\nSubmit your email below so we can credit your free spins 💫",
        reply_markup=reply_markup,
    )

# Обробка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "provide_email":
        user_states[user_id]["stage"] = "awaiting_email"
        await query.message.reply_text("Please enter your email address:")

    elif query.data == "confirm_email":
        email = user_states[user_id].get("email")
        username = user_states[user_id].get("username")
        sheet.append_row([username, email])
        await query.message.reply_text("✅ Thank you! Your email has been saved.")
        user_states.pop(user_id)

    elif query.data == "cancel_email":
        user_states[user_id]["stage"] = "awaiting_button"
        keyboard = [[InlineKeyboardButton("Provide Email", callback_data="provide_email")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text("❌ Email entry canceled. You can try again:", reply_markup=reply_markup)

# Обробка введення e-mail
async def email_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id in user_states and user_states[user_id]["stage"] == "awaiting_email":
        user_states[user_id]["email"] = update.message.text
        user_states[user_id]["stage"] = "awaiting_confirmation"
        keyboard = [
            [InlineKeyboardButton("Yes", callback_data="confirm_email"),
             InlineKeyboardButton("No", callback_data="cancel_email")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Just to confirm — is this your correct email?\n\n{update.message.text}",
            reply_markup=reply_markup,
        )

# Запуск бота
def main():
    app = ApplicationBuilder().token("7593429309:AAFeJT_aJmyBnUZornrgm1xMJJj3dzFDVqE").build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, email_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

