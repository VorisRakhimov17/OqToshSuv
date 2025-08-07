from django.shortcuts import render
from app.models import Product
from landing.models import Testimonial, News

# Create your views here.
def home(request):
    products = Product.objects.all()
    testimonials = Testimonial.objects.all()
    news = News.objects.all()
    return render(request, 'landing/home.html', {'products': products,
                                                 'testimonials': testimonials,
                                                 'news': news})
