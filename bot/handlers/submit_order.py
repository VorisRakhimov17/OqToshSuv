# bot/handlers/submit_order.py

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from app.models import Order, Product, TelegramUser
from bot.handlers.menu import send_main_menu
from asgiref.sync import sync_to_async

ASK_LOCATION = 10  # location step

# 📍 Lokatsiyani so‘rash
async def handle_submit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Mahsulot va miqdor tekshiruvi
    product = context.user_data.get("product")
    quantity = context.user_data.get("quantity")

    if not product or not quantity:
        await query.message.reply_text("❌ Mahsulot yoki miqdor topilmadi. Qayta urinib ko‘ring.")
        return ConversationHandler.END

    await query.message.reply_text(
        "📍 Iltimos, mahsulotni yetkazish manzilini yuboring.",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("📍 Lokatsiyani yuborish", request_location=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )

    return ASK_LOCATION


# 📍 Lokatsiyani qabul qilish va buyurtmani saqlash
async def save_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    user_id = update.effective_user.id

    if not location:
        await update.message.reply_text("❌ Lokatsiya olinmadi. Qaytadan urinib ko‘ring.")
        return ConversationHandler.END

    # user_data dan ma’lumotlarni olish
    product = context.user_data.get("product")
    quantity = context.user_data.get("quantity")

    context.user_data["product"] = product  # to‘g‘ridan model instance
    context.user_data["quantity"] = 1

    if not product or not quantity:
        await update.message.reply_text("❌ Mahsulot yoki miqdor topilmadi. Qayta urinib ko‘ring.")
        return ConversationHandler.END

    # TelegramUser modelidan foydalanuvchini olish
    user = await sync_to_async(TelegramUser.objects.get)(user_id=user_id)

    # Buyurtmani saqlash
    await sync_to_async(Order.objects.create)(
        user=user,
        product=product,
        quantity=quantity,
        latitude=location.latitude,
        longitude=location.longitude,
        status='yangi'
    )

    await update.message.reply_text("✅ Buyurtmangiz qabul qilindi!")
    await send_main_menu(update, context)
    return ConversationHandler.END
