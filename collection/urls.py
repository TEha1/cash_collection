from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter

from collection.views import (
    CashCollectorViewSet,
    ManagerViewSet,
    TaskViewSet,
    CollectionViewSet,
    DeliveryCreateAPIView,
)

router = DefaultRouter()
router.register(r"cash-collectors", CashCollectorViewSet, basename="cash_collector")
router.register(r"managers", ManagerViewSet, basename="manager")
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"collections", CollectionViewSet, basename="collection")

urlpatterns = [
    path("", include(router.urls)),
    path("pay/", DeliveryCreateAPIView.as_view(), name="pay"),
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
]
