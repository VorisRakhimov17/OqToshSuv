from django.db import models
from app.models import TelegramUser

# Create your models here.
class Testimonial(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    message = models.TextField()

    def __str__(self):
        return self.user.full_name

class News(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    image = models.ImageField(upload_to='news/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title