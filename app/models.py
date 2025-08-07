# app/models.py

from django.db import models

class TelegramUser(models.Model):
    ROLE_CHOICES = [
        ('mijoz', '🧑 Mijoz'),
        ('admin', '🛠 Admin'),
        ('haydovchi', '🚚 Haydovchi'),
    ]

    user_id = models.BigIntegerField(unique=True)
    full_name = models.CharField(max_length=200)
    username = models.CharField(max_length=150, null=True, blank=True)
    phone = models.CharField(max_length=30, null=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='mijoz')  # ✅ Yangi maydon
    created_at = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} (@{self.username}) – {self.role}"


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    default_driver = models.ForeignKey(
        TelegramUser,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        limit_choices_to={'role': 'haydovchi'},
        related_name='default_products',
        verbose_name="Defolt haydovchi"
    )

    def __str__(self):
        return f"{self.name} – {self.price} so'm"

class Order(models.Model):
    STATUS_CHOICES = [
        ('yangi', 'Yangi'),
        ('jo‘natildi', 'Jo‘natildi'),
        ('yetkazildi', 'Yetkazildi'),
    ]

    user = models.ForeignKey('TelegramUser', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='yangi')
    driver = models.ForeignKey('TelegramUser', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_driven')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name} — {self.product.name} × {self.quantity}"