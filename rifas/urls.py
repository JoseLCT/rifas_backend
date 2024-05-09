from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from rifas.api import RifaViewSet, UsuarioViewSet

router = routers.DefaultRouter()
router.register(r'rifas', RifaViewSet)
router.register(r'usuarios', UsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api-token-auth/', views.obtain_auth_token)
]
