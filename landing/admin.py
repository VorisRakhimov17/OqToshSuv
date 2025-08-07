from django.contrib import admin
from .models import Testimonial, News

# Register your models here.
@admin.register(Testimonial)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("user", "message",)
    search_fields = ("user",)

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "content", "created_at")
    search_fields = ("title",)