from django.urls import path
from .views import PedidoCreateView

urlpatterns = [
    path("pedidos/", PedidoCreateView.as_view()),
]
