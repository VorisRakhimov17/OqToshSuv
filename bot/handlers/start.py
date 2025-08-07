import os
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

@sync_to_async
def save_user_avatar(user, avatar_path):
    user.avatar = avatar_path
    user.save()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tg_user = update.effective_user
    user = await get_or_create_user(
        tg_user.id,
        tg_user.full_name,
        tg_user.username
    )

    # 🟢 1. Rasmni olish
    try:
        if not user.avatar:
            photos = await context.bot.get_user_profile_photos(tg_user.id, limit=1)
            if photos.total_count > 0:
                file_id = photos.photos[0][0].file_id
                file = await context.bot.get_file(file_id)

                # 📂 Papkani yaratamiz
                os.makedirs("media/avatars", exist_ok=True)

                avatar_path = f"avatars/{user.user_id}.jpg"
                full_path = os.path.join("media", avatar_path)

                # ✅ Faylni saqlaymiz
                await file.download_to_drive(full_path)

                # ✅ Django bazaga yozamiz
                await save_user_avatar(user, avatar_path)
    except Exception as e:
        print("Profil rasm olishda xatolik:", e)

    # 🟢 2. Telefon raqami yo‘q bo‘lsa, so‘raymiz
    if not user.phone:
        button = KeyboardButton("📱 Raqamni yuborish", request_contact=True)
        markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True)
        await update.message.reply_text(
            "📞 Iltimos, telefon raqamingizni yuboring:",
            reply_markup=markup
        )
        return  # ❗ Shundan keyin menyu chiqmasin

    # 🟢 3. Asosiy menyuni ko‘rsatamiz
    await send_main_menu(update, context)
