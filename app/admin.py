# app/admin.py

from django.contrib import admin
from .models import TelegramUser, Product, Order

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ("full_name", "username", "phone", "role", "created_at")
    search_fields = ("full_name", "username")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "image", "description")
    search_fields = ("name", "price")

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity', 'status', 'driver')
    list_filter = ('status',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "driver":
            # Faqat rol = "driver" bo'lganlar chiqsin
            kwargs["queryset"] = TelegramUser.objects.filter(role='haydovchi')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

