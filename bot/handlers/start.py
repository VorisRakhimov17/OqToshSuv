# bot/handlers/start.py

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from app.models import TelegramUser
from asgiref.sync import sync_to_async
from bot.handlers.menu import send_main_menu

@sync_to_async
def get_or_create_user(user_id, full_name, username):
    user, created = TelegramUser.objects.get_or_create(
        user_id=user_id,
        defaults={"full_name": full_name, "username": username}
    )
    return user

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_or_create_user(
        update.effective_user.id,
        update.effective_user.full_name,
        update.effective_user.username
    )

    await send_main_menu(update, context)
