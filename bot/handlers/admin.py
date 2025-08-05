# bot/handlers/admin.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.models import Order, TelegramUser
from asgiref.sync import sync_to_async

# 🟩 Admin uchun barcha buyurtmalarni ko‘rsatish
async def show_all_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = await sync_to_async(list)(
        Order.objects.select_related('product', 'user')
        .order_by('-created_at')[:5]
    )

    if not orders:
        await update.message.reply_text("📭 Hech qanday buyurtma yo'q.")
        return

    for order in orders:
        keyboard = []
        drivers = await sync_to_async(list)(TelegramUser.objects.filter(role='haydovchi'))

        for driver in drivers:
            callback_data = f'assign:{order.id}:{driver.user_id}'
            keyboard.append([InlineKeyboardButton(driver.full_name, callback_data=callback_data)])

        reply_markup = InlineKeyboardMarkup(keyboard)
        text = (
            f"🛒 {order.product.name} x {order.quantity}\n"
            f"👤 {order.user.full_name}\n"
            f"📅 {order.created_at.strftime('%Y-%m-%d')}\n"
            f"🚛 Haydovchi: {order.driver.full_name if order.driver else 'Biriktirilmagan'}"
        )

        await update.message.reply_text(text, reply_markup=reply_markup)

# 🟩 InlineButton bosilganda haydovchini biriktirish
async def assign_driver_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("assign:"):
        try:
            _, order_id, driver_user_id = query.data.split(":")
            order = await sync_to_async(Order.objects.get)(id=order_id)
            driver = await sync_to_async(TelegramUser.objects.get)(user_id=driver_user_id)

            order.driver = driver
            order.status = 'jo‘natildi'  # ✅ bu sizning modelga mos
            await sync_to_async(order.save)()

            await query.edit_message_text(f"✅ Haydovchi ({driver.full_name}) biriktirildi.")
        except Exception as e:
            print("Xatolik:", e)
            await query.edit_message_text("❌ Xatolik yuz berdi.")
