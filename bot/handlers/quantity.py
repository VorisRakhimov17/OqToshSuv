# bot/handlers/quantity.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.models import Product
from asgiref.sync import sync_to_async

@sync_to_async
def get_product_by_id(pid: int):
    return Product.objects.filter(id=pid).first()

@sync_to_async
def get_product_by_unique_size(size: str):
    # Agar sizda har bir size yagona bo'lsa ishlaydi; aks holda .first() tasodifiy tanlaydi
    return Product.objects.filter(size=size).order_by('name').first()

@sync_to_async
def get_product_by_name(name: str):
    return Product.objects.filter(name=name).first()

def update_quantity_buttons(quantity: int):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➖", callback_data='decrease'),
            InlineKeyboardButton(f"{quantity}", callback_data='none'),
            InlineKeyboardButton("➕", callback_data='increase')
        ],
        [InlineKeyboardButton("✅ Yuborish", callback_data='submit')]
    ])

async def show_product_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    ReplyKeyboard tugmasi matnidan productni aniqlaydi:
    1) Avval label_to_id xaritasidan ID ni oladi (eng to'g'ri usul)
    2) Xarita bo'lmasa, matnni size deb qabul qilib urinish qiladi
    3) Oxirgi zaxira: matnni name deb qabul qiladi
    """
    label = update.message.text

    # 1) Eng ishonchli: label -> id
    mapping = context.user_data.get("label_to_id", {})
    pid = mapping.get(label)
    product = None
    if pid:
        product = await get_product_by_id(pid)

    # 2) Xarita bo'lmasa yoki topilmasa: labelni size deb urinish
    if product is None:
        product = await get_product_by_unique_size(label)

    # 3) Hali ham topilmasa: labelni name deb urinish
    if product is None:
        product = await get_product_by_name(label)

    if not product:
        await update.message.reply_text("❌ Mahsulot topilmadi. Iltimos, tugmalardan birini bosing.")
        return

    # Boshlang'ich miqdor va product obyektini saqlash
    context.user_data['product'] = product
    context.user_data['quantity'] = 1

    caption = (
        f"📦 <b>{product.name}</b>\n"
        f"🔹 Hajm: {product.size or '-'}\n"
        f"💰 Narx: {product.price} so'm\n\n"
        f"📄 {product.description or ''}"
    )
    keyboard = [
        [InlineKeyboardButton("➖", callback_data='decrease'),
         InlineKeyboardButton("1", callback_data='none'),
         InlineKeyboardButton("➕", callback_data='increase')],
        [InlineKeyboardButton("✅ Yuborish", callback_data='submit')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if getattr(product, "image", None):
        try:
            # Agar ImageField bo'lsa:
            with open(product.image.path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode="HTML"
                )
        except Exception as e:
            await update.message.reply_text(f"⚠️ Rasm yuborishda xatolik: {e}")
            await update.message.reply_text(caption, reply_markup=reply_markup, parse_mode="HTML")
    else:
        await update.message.reply_text(caption, reply_markup=reply_markup, parse_mode="HTML")

async def handle_quantity_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    current_quantity = context.user_data.get('quantity', 1)

    if query.data == 'increase':
        current_quantity += 1
    elif query.data == 'decrease' and current_quantity > 1:
        current_quantity -= 1

    context.user_data['quantity'] = current_quantity

    await query.edit_message_reply_markup(
        reply_markup=update_quantity_buttons(current_quantity)
    )
