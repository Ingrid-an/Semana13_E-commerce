"""ViewSets - Caso 2 E-commerce. Filtros avanzados, throttling custom, @actions."""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from rest_framework.throttling import ScopedRateThrottle
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, NumberFilter
from .models import Producto, Resena, Orden, ItemOrden
from .serializers import ProductoSerializer, ResenaSerializer, OrdenSerializer


class ProductoFilter(FilterSet):
    """RF1 - Filtro por rango de precio."""
    precio_min = NumberFilter(field_name="precio", lookup_expr="gte")
    precio_max = NumberFilter(field_name="precio", lookup_expr="lte")
    class Meta:
        model = Producto
        fields = ["categoria", "marca", "precio_min", "precio_max"]


class ProductoViewSet(viewsets.ModelViewSet):
    """RF1 - CRUD de productos con filtrado avanzado y throttle de búsqueda."""
    queryset = Producto.objects.select_related("categoria").all()
    serializer_class = ProductoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductoFilter
    search_fields = ["nombre", "descripcion", "marca"]
    ordering_fields = ["precio", "creado"]
    throttle_scope = "search"
    throttle_classes = [ScopedRateThrottle]

    @action(detail=True, methods=["get"])
    def resenas(self, request, pk=None):
        """GET /api/productos/{id}/resenas/ — reseñas de un producto."""
        producto = self.get_object()
        ser = ResenaSerializer(producto.resenas.all(), many=True, context={"request": request})
        return Response(ser.data)


class ResenaViewSet(viewsets.ModelViewSet):
    """RF4 - CRUD de reseñas. El usuario se asigna automáticamente."""
    queryset = Resena.objects.select_related("producto", "usuario").all()
    serializer_class = ResenaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class OrdenViewSet(viewsets.ModelViewSet):
    """RF3 - Órdenes con @actions cancelar y mis-ordenes."""
    serializer_class = OrdenSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["estado"]
    ordering_fields = ["fecha_creacion", "total"]

    def get_queryset(self):
        # el usuario ve solo sus órdenes; admin ve todas
        qs = Orden.objects.select_related("usuario").prefetch_related("items")
        if self.request.user.is_staff:
            return qs
        return qs.filter(usuario=self.request.user)

    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        """POST /api/ordenes/{id}/cancelar/ — solo si está pendiente."""
        orden = self.get_object()
        if orden.estado != "pendiente":
            return Response({"detail": "Solo se pueden cancelar órdenes pendientes."},
                            status=status.HTTP_400_BAD_REQUEST)
        orden.estado = "cancelada"; orden.save()
        return Response({"detail": "Orden cancelada."})

    @action(detail=False, methods=["get"])
    def mis_ordenes(self, request):
        """GET /api/ordenes/mis_ordenes/ — órdenes del usuario autenticado."""
        qs = Orden.objects.filter(usuario=request.user).prefetch_related("items")
        ser = self.get_serializer(qs, many=True)
        return Response(ser.data)
