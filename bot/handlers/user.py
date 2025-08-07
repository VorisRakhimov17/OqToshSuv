from telegram import Update
from telegram.ext import ContextTypes
from app.models import TelegramUser, Order
from asgiref.sync import sync_to_async


# ✅ Buyurtmalarni product va driver bilan birga olish (select_related bilan)
@sync_to_async
def get_user_orders(user_id):
    try:
        user = TelegramUser.objects.get(user_id=user_id)
        return list(
            Order.objects
            .filter(user=user)
            .select_related('product', 'driver')  # <-- asosiy yechim shu
            .order_by('-id')
        )
    except TelegramUser.DoesNotExist:
        return []


async def show_user_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    orders = await get_user_orders(user_id)

    if not orders:
        await update.message.reply_text("❌ Sizda buyurtmalar mavjud emas.")
        return

    for order in orders:
        # Mahsulot nomi
        product_name = order.product.name if order.product else "❌ Mahsulot topilmadi"

        # Haydovchi ismi
        driver_name = order.driver.full_name if order.driver else "❌ Biriktirilmagan"

        # Lokatsiya
        latitude = order.latitude
        longitude = order.longitude
        if latitude and longitude:
            location_link = f"https://yandex.com/maps/?pt={longitude},{latitude}&z=16&l=map"
            location_text = f"<a href='{location_link}'>Yandex xaritada ochish</a>"
        else:
            location_text = "❌ Koordinatalar mavjud emas"

        # Status
        status = order.status.capitalize()

        # Xabar matni
        order_text = (
            f"🧾 <b>Buyurtma maʼlumotlari</b>\n\n"
            f"📦 <b>Mahsulot:</b> {product_name}\n"
            f"🔢 <b>Miqdor:</b> {order.quantity} dona\n"
            f"📍 <b>Manzil:</b> {location_text}\n"
            f"🚚 <b>Haydovchi:</b> {driver_name}\n"
            f"📌 <b>Status:</b> {status}"
        )

        await update.message.reply_text(order_text, parse_mode='HTML', disable_web_page_preview=True)
