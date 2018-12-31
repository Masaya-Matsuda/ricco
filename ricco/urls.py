from trade import views
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", views.index, name="index"),
    path("trade/", include("trade.urls")),
    path("analysis/", include("analysis.urls")),
    path("accounts/", include("accounts.urls")),
    path("admin/", admin.site.urls),
]

