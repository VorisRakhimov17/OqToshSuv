# bot/handlers/quantity.py

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from app.models import Product
from asgiref.sync import sync_to_async

@sync_to_async
def get_product_by_name(name):
    return Product.objects.filter(name=name).first()

async def show_product_detail(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_name = update.message.text
    product = await get_product_by_name(product_name)

    if not product:
        await update.message.reply_text("❌ Mahsulot topilmadi.")
        return

    # Boshlang'ich miqdor va product model obyektini saqlash
    context.user_data['product'] = product
    context.user_data['quantity'] = 1

    caption = f"📦 <b>{product.name}</b>\n\n💰 Narx: {product.price} so'm\n\n📄 {product.description or ''}"
    keyboard = [
        [InlineKeyboardButton("➖", callback_data='decrease'),
         InlineKeyboardButton("1", callback_data='none'),
         InlineKeyboardButton("➕", callback_data='increase')],
        [InlineKeyboardButton("✅ Yuborish", callback_data='submit')],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if product.image:
        try:
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

def update_quantity_buttons(quantity):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➖", callback_data='decrease'),
            InlineKeyboardButton(f"{quantity}", callback_data='none'),
            InlineKeyboardButton("➕", callback_data='increase')
        ],
        [InlineKeyboardButton("✅ Yuborish", callback_data='submit')]
    ])

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
