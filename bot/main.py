import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OqToshSuv.settings')
django.setup()

from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ConversationHandler
)
from bot.handlers.start import start
from bot.handlers.contact import handle_contact
from bot.handlers.order_menu import show_order_menu
from bot.handlers.menu import send_main_menu
from bot.handlers.quantity import show_product_detail, handle_quantity_change
from bot.handlers.submit_order import handle_submit, save_location, ASK_LOCATION
from bot.handlers.admin import show_all_orders, admin_callback_handler, show_driver_assignment_menu
from bot.handlers.driver import (
    show_driver_orders, confirm_delivery, show_delivered_orders, show_location, paginate_driver_orders
)
from bot.handlers.user import show_user_orders

TOKEN = '8348687758:AAHTV_AwLBMfAqpRU2YazFzUq66zlknrsYI'

def main():
    app = Application.builder().token(TOKEN).build()

    # ✅ Asosiy komandalar
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.Regex("^📝 Buyurtmalarim$"), show_user_orders))

    # ✅ Rolga mos menyular
    app.add_handler(MessageHandler(filters.Regex("^📋 Barcha buyurtmalar$"), show_all_orders))
    app.add_handler(MessageHandler(filters.Regex("^📋 Haydovchi biriktirish$"), show_driver_assignment_menu))
    app.add_handler(CallbackQueryHandler(admin_callback_handler, pattern="^(view_|assign_|assign_driver:)"))
    app.add_handler(MessageHandler(filters.Regex("^📦 Mening buyurtmalarim$"), show_driver_orders))
    app.add_handler(MessageHandler(filters.Regex("^📁 Yetkazib bo‘linganlar$"), show_delivered_orders))
    app.add_handler(CallbackQueryHandler(confirm_delivery, pattern="^delivered:"))

    # ✅ Buyurtma qilish - ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^📦 Buyurtma berish$"), show_order_menu)
        ],
        states={
            ASK_LOCATION: [MessageHandler(filters.LOCATION, save_location)],
        },
        fallbacks=[
            MessageHandler(filters.Regex("^🔙 Ortga$"), send_main_menu)
        ],
        map_to_parent={},
    )
    app.add_handler(conv_handler)

    # ✅ Inline tugmalar (miqdor va yuborish)
    app.add_handler(CallbackQueryHandler(handle_quantity_change, pattern="^(increase|decrease)$"))
    app.add_handler(CallbackQueryHandler(handle_submit, pattern="^submit$"))
    app.add_handler(MessageHandler(filters.LOCATION, save_location))
    app.add_handler(CallbackQueryHandler(confirm_delivery, pattern="^delivered:"))
    app.add_handler(CallbackQueryHandler(paginate_driver_orders, pattern="^(next_order|prev_order)$"))
    app.add_handler(CallbackQueryHandler(show_location, pattern="^showloc:"))
    app.add_handler(CallbackQueryHandler(confirm_delivery, pattern="^delivered:"))


    # ✅ Mahsulot tanlanganda detal ko‘rsatish (oxirida bo‘lishi kerak!)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, show_product_detail))


    print("✅ Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
