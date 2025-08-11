# app/admin.py

from django.contrib import admin
from .models import TelegramUser, Product, Order
from decimal import Decimal

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("avatar", "full_name", "username", "formatted_phone", "role", "created_at")
    search_fields = ("full_name", "username")
    list_filter = ('role',)


    @admin.display(description="Phone")
    def formatted_phone(self, obj):
        phone = obj.phone
        if phone and phone.startswith("+998") and len(phone) == 13:
            return f"{phone[:4]} ({phone[4:6]}) {phone[6:9]} {phone[9:11]} {phone[11:]}"
        return phone or "-"

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "formatted_price", "image", "default_driver", "description")
    search_fields = ("name", "price")

    @admin.display(description="Narx")
    def formatted_price(self, obj):
        if obj.price:
            return f"{obj.price:,.0f}".replace(",", " ")
        return "-"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'product_info', 'quantity', 'status', 'driver')
    list_filter = ('status',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "driver":
            kwargs["queryset"] = TelegramUser.objects.filter(role='haydovchi')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description="Phone")
    def phone_number(self, obj):
        phone = obj.user.phone if obj.user and obj.user.phone else ""
        if phone.startswith('+998') and len(phone) == 13:
            return f"{phone[:4]} ({phone[4:6]}) {phone[6:9]} {phone[9:11]} {phone[11:]}"
        return phone or "-"

    @admin.display(description="Product")
    def product_info(self, obj):
        if obj.product:
            price = f"{obj.product.price:,.0f}".replace(",", " ")
            return f"{obj.product.name} – {price} so'm"
        return "-"


