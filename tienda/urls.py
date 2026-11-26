from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductoViewSet, ResenaViewSet, OrdenViewSet

router = DefaultRouter()
router.register(r"productos", ProductoViewSet, basename="producto")
router.register(r"resenas", ResenaViewSet, basename="resena")
router.register(r"ordenes", OrdenViewSet, basename="orden")
urlpatterns = [path("", include(router.urls))]
