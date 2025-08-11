
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app.api import router as app_router
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", include(app_router.urls)),
    path("api/auth/jwt/create/", TokenObtainPairView.as_view()),
    path("api/auth/jwt/refresh/", TokenRefreshView.as_view()),


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
