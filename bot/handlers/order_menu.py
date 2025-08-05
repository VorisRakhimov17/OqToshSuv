# bot/handlers/order_menu.py

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from app.models import Product
from asgiref.sync import sync_to_async

@sync_to_async
def get_product_names():
    return list(Product.objects.values_list('name', flat=True))

def make_rows(items, per_row=3):
    """Mahsulot nomlarini gorizontal ravishda guruhlaydi"""
    return [ [KeyboardButton(name) for name in items[i:i+per_row]] for i in range(0, len(items), per_row) ]

async def show_order_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_names = await get_product_names()

    # 🔘 Tugmalarni dinamik va gorizontal holatda joylaymiz
    buttons = make_rows(product_names, per_row=3)
    buttons.append([KeyboardButton("🔙 Ortga")])  # Pastki qatorda "Ortga"

    markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(
        "🛒 Buyurtma qilmoqchi bo‘lgan mahsulotni tanlang:",
        reply_markup=markup
    )
