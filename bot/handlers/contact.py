# bot/handlers/contact.py

from telegram import Update
from telegram.ext import ContextTypes
from app.models import TelegramUser
from asgiref.sync import sync_to_async
from bot.handlers.menu import send_main_menu

@sync_to_async
def save_phone(user_id, phone):
    TelegramUser.objects.filter(user_id=user_id).update(phone=phone)

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    if contact:
        await save_phone(contact.user_id, contact.phone_number)
        await update.message.reply_text("📲 Telefon raqamingiz saqlandi!")
        await send_main_menu(update, context)
