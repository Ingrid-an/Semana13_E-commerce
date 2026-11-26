from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from drf_spectacular.views import (SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView)
from rest_framework.authtoken.views import obtain_auth_token
urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="inicio"),
    path("admin/", admin.site.urls),
    path("api/", include("tienda.urls")),
    path("api/auth/token/", obtain_auth_token, name="obtain-token"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api-auth/", include("rest_framework.urls")),
]
