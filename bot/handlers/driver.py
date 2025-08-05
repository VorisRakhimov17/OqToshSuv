from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from app.models import Order, TelegramUser
from asgiref.sync import sync_to_async

@sync_to_async
def get_driver_orders(user_id):
    driver = TelegramUser.objects.get(user_id=user_id)
    return list(Order.objects.filter(driver=driver, status='jo‘natildi').select_related('product', 'user'))

# 🔹 Yangi buyurtmalarni sahifalab ko‘rsatish
async def show_driver_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    orders = await get_driver_orders(user_id)

    if not orders:
        await update.message.reply_text("📦 Sizga biriktirilgan yangi buyurtmalar yo‘q.")
        return

    context.user_data["driver_orders"] = orders
    context.user_data["driver_orders_page"] = 0
    await send_driver_order(update, context)

# 🔹 Bitta buyurtmani ko‘rsatish (sahifa)
async def send_driver_order(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    orders = context.user_data.get("driver_orders", [])
    index = context.user_data.get("driver_orders_page", 0)

    if not orders or index >= len(orders):
        return

    order = orders[index]
    message = (
        f"📦 <b>Mahsulot:</b> {order.product.name}\n"
        f"🔢 <b>Miqdor:</b> {order.quantity}\n"
        f"👤 <b>Mijoz:</b> {order.user.full_name}\n"
        f"📅 <b>Sana:</b> {order.created_at.strftime('%Y-%m-%d %H:%M')}"
    )

    buttons = [
        [
            InlineKeyboardButton("📍 Lokatsiya", callback_data=f"showloc:{order.id}"),
            InlineKeyboardButton("✅ Yetkazdim", callback_data=f"delivered:{order.id}")
        ]
    ]

    nav_buttons = []
    if index > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Oldingi", callback_data="prev_order"))
    if index < len(orders) - 1:
        nav_buttons.append(InlineKeyboardButton("Keyingi ➡️", callback_data="next_order"))
    if nav_buttons:
        buttons.append(nav_buttons)

    if hasattr(update_or_query, "message"):
        await update_or_query.message.reply_text(
            text=message,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="HTML"
        )
    elif hasattr(update_or_query, "reply_text"):
        await update_or_query.reply_text(
            text=message,
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="HTML"
        )

# 🔹 Sahifani o‘zgartirish (Keyingi / Oldingi)
async def paginate_driver_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    page = context.user_data.get("driver_orders_page", 0)

    if query.data == "next_order":
        page += 1
    elif query.data == "prev_order":
        page -= 1

    user_id = query.from_user.id
    orders = await get_driver_orders(user_id)

    if page < 0:
        page = 0
    if page >= len(orders):
        page = len(orders) - 1

    context.user_data["driver_orders"] = orders
    context.user_data["driver_orders_page"] = page

    await query.message.delete()
    await send_driver_order(query, context)

# 🔹 Lokatsiyani yuborish
async def show_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    order_id = int(query.data.split(":")[1])
    order = await sync_to_async(Order.objects.get)(id=order_id)

    if not order.latitude or not order.longitude:
        await query.message.reply_text("❌ Lokatsiya mavjud emas.")
        return

    await query.message.reply_location(latitude=order.latitude, longitude=order.longitude)

# 🔹 Yetkazdim tugmasi
async def confirm_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data.startswith("delivered:"):
        order_id = int(query.data.split(":")[1])

        try:
            # 1. Buyurtmani yangilash
            order = await sync_to_async(Order.objects.get)(id=order_id)
            order.status = 'yetkazildi'
            await sync_to_async(order.save)()

            # 2. Buyurtmalar ro‘yxatini yangilash
            user_id = query.from_user.id
            orders = await get_driver_orders(user_id)

            # 3. Qaysi sahifadaligini aniqlash
            index = context.user_data.get("driver_orders_page", 0)
            if index >= len(orders):
                index = max(0, len(orders) - 1)

            context.user_data["driver_orders"] = orders
            context.user_data["driver_orders_page"] = index

            await query.message.delete()

            if orders:
                await send_driver_order(query, context)
            else:
                await query.message.reply_text("✅ Bu buyurtma 'Yetkazildi' deb belgilandi.\n📭 Boshqa yangi buyurtma qolmagan.")
        except Exception as e:
            print("Xatolik:", e)
            await query.edit_message_text("❌ Xatolik yuz berdi.")


# 🔹 Yetkazilgan buyurtmalar
async def show_delivered_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    orders = await sync_to_async(list)(
        Order.objects.select_related('product', 'user')
        .filter(driver__user_id=user_id, status='yetkazildi')
        .order_by('-created_at')
    )

    if not orders:
        await update.message.reply_text("📭 Siz hali hech qanday buyurtmani yetkazmagansiz.")
        return

    for order in orders:
        await update.message.reply_text(
            f"🛒 Mahsulot: {order.product.name}\n"
            f"🔢 Miqdor: {order.quantity}\n"
            f"👤 Mijoz: {order.user.full_name}\n"
            f"📆 Sana: {order.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
