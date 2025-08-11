from rest_framework import viewsets, serializers, routers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"

class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all().order_by("id")
    serializer_class = ProductSerializer

router = routers.DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")