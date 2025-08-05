# bot/handlers/menu.py

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from asgiref.sync import sync_to_async
from app.models import TelegramUser


# ✅ TelegramUser jadvalidan foydalanuvchining rolini olish
@sync_to_async
def get_user_role(user_id):
    user = TelegramUser.objects.filter(user_id=user_id).first()
    return user.role if user else 'mijoz'  # Agar topilmasa, mijoz deb olinadi


# ✅ Rolga qarab menyuni yuborish
async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    role = await get_user_role(user_id)

    if role == 'admin':
        buttons = [
            [KeyboardButton("📋 Barcha buyurtmalar")],
            [KeyboardButton("👤 Haydovchi biriktirish")]
        ]
    elif role == 'haydovchi':
        buttons = [
            [KeyboardButton("📦 Mening buyurtmalarim")],
            [KeyboardButton("📁 Yetkazib bo‘linganlar")]
        ]
    else:  # mijoz (default)
        buttons = [
            [KeyboardButton("📦 Buyurtma berish")],
            [KeyboardButton("📝 Buyurtmalarim")]
        ]

    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)

    await update.effective_message.reply_text(
        "👇 Kerakli bo‘limni tanlang:",
        reply_markup=markup
    )
