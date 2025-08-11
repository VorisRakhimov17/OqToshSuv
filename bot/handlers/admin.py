from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.models import Order, TelegramUser
from asgiref.sync import sync_to_async

# ==========================================
# ✅ 1. BARCHA BUYURTMALAR - faqat ko‘rish
# ==========================================

async def show_all_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['view_index'] = 0
    await send_view_order(update, context)


async def send_view_order(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    orders = await sync_to_async(list)(
        Order.objects.select_related('product', 'user', 'driver').order_by('-created_at')
    )

    if not orders:
        if hasattr(update_or_query, 'callback_query') and update_or_query.callback_query:
            await update_or_query.callback_query.edit_message_text("📭 Yangi buyurtmalar qolmadi.")
        elif hasattr(update_or_query, 'message') and update_or_query.message:
            await update_or_query.message.reply_text("📭 Yangi buyurtmalar qolmadi.")
        return

    index = context.user_data.get('view_index', 0)
    index = max(0, min(index, len(orders) - 1))
    context.user_data['view_index'] = index

    order = orders[index]

    keyboard = []

    # Sahifalash
    nav_buttons = []
    if index > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Oldingi", callback_data="view_prev"))
    if index < len(orders) - 1:
        nav_buttons.append(InlineKeyboardButton("➡️ Keyingi", callback_data="view_next"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    # Google Maps tugmasi
    if order.latitude and order.longitude:
        maps_url = f"https://www.google.com/maps?q={order.latitude},{order.longitude}"
        keyboard.append([InlineKeyboardButton("📍 Manzilni ko‘rish", url=maps_url)])

    text = (
        f"📦 <b>Buyurtma soni: {index + 1} / {len(orders)}</b>\n"
        f"🛒 O'lchami: {order.product.size}\n"
        f"🔢 Miqdori: {order.quantity}\n"
        f"💵 Jami summa: {order.product.price * order.quantity}\n"
        f"👤 Mijoz: {order.user.full_name}\n"
        f"📅 Sana: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"🚛 Haydovchi: {order.driver.full_name if order.driver else '❌ Biriktirilmagan'}\n"
        f"📌 Status: <b>{order.status}</b>"
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    if hasattr(update_or_query, 'callback_query') and update_or_query.callback_query:
        await update_or_query.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        await update_or_query.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )


# ==========================================
# ✅ 2. HAYDOVCHIGA BIRIKTIRISH - sahifalash bilan
# ==========================================

async def show_driver_assignment_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['assign_index'] = 0
    await send_assignable_order(update, context)


async def send_assignable_order(update_or_query, context: ContextTypes.DEFAULT_TYPE):
    orders = await sync_to_async(list)(
        Order.objects.select_related('product', 'user', 'driver')
        .filter(status='yangi')
        .order_by('-created_at')
    )

    if not orders:
        if hasattr(update_or_query, 'callback_query') and update_or_query.callback_query:
            await update_or_query.callback_query.edit_message_text("📭 Yangi buyurtmalar qolmadi.")
        elif hasattr(update_or_query, 'message') and update_or_query.message:
            await update_or_query.message.reply_text("📭 Yangi buyurtmalar qolmadi.")
        return

    index = context.user_data.get('assign_index', 0)
    index = max(0, min(index, len(orders) - 1))
    context.user_data['assign_index'] = index
    order = orders[index]

    drivers = await sync_to_async(list)(TelegramUser.objects.filter(role='haydovchi'))

    # Haydovchi tugmalari
    keyboard = [
        [InlineKeyboardButton(driver.full_name, callback_data=f"assign_driver:{order.id}:{driver.user_id}")]
        for driver in drivers
    ]

    # Sahifalash
    nav_buttons = []
    if index > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Oldingi", callback_data="assign_prev"))
    if index < len(orders) - 1:
        nav_buttons.append(InlineKeyboardButton("➡️ Keyingi", callback_data="assign_next"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    # Google Maps
    if order.latitude and order.longitude:
        maps_url = f"https://www.google.com/maps?q={order.latitude},{order.longitude}"
        keyboard.append([InlineKeyboardButton("📍 Manzilni ko‘rish", url=maps_url)])

    text = (
        f"🆕 <b>Yangi buyurtma {index + 1} / {len(orders)}</b>\n"
        f"🛒 O'lchami: {order.product.size}\n"
        f"🔢 Miqdori: {order.quantity}\n"
        f"💵 Jami summa: {order.product.price * order.quantity}\n"
        f"👤 Mijoz: {order.user.full_name}\n"
        f"📅 Sana: {order.created_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"🚛 Haydovchi: {order.driver.full_name if order.driver else '❌ Biriktirilmagan'}"
    )

    reply_markup = InlineKeyboardMarkup(keyboard)

    if hasattr(update_or_query, 'callback_query') and update_or_query.callback_query:
        await update_or_query.callback_query.edit_message_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        await update_or_query.message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )


# ==========================================
# ✅ CALLBACK HANDLER - barcha tugmalar uchun
# ==========================================

async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    # Barcha buyurtmalar sahifalash
    if data == "view_next":
        context.user_data['view_index'] += 1
        await send_view_order(update, context)
    elif data == "view_prev":
        context.user_data['view_index'] -= 1
        await send_view_order(update, context)

    # Haydovchi biriktirish sahifalash
    elif data == "assign_next":
        context.user_data['assign_index'] += 1
        await send_assignable_order(update, context)
    elif data == "assign_prev":
        context.user_data['assign_index'] -= 1
        await send_assignable_order(update, context)

    # Haydovchi biriktirish
    elif data.startswith("assign_driver:"):
        try:
            _, order_id, driver_user_id = data.split(":")
            order = await sync_to_async(Order.objects.get)(id=order_id)
            driver = await sync_to_async(TelegramUser.objects.get)(user_id=driver_user_id)

            order.driver = driver
            order.status = 'jo‘natildi'
            await sync_to_async(order.save)()

            await send_assignable_order(update, context)

        except Exception as e:
            print("❌ Xatolik:", e)
            await query.edit_message_text("❌ Xatolik yuz berdi.")
