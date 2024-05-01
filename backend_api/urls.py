"""
URL configuration for backend_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from accounts import views

urlpatterns = [
    path(r'jet/', include('jet.urls', 'jet')),  # Django JET URLS
    path(r'jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')), # Django JET dashboard URLS
    path('admin/', admin.site.urls),
    path('drf_auth/', include('rest_framework.urls'), name='api_auth'),
    path('api/v1/', include('accounts.urls', namespace='accounts')),
    path("api/v1/", include("shop.urls", namespace="shop")),
    path('auth/', include('social_django.urls', namespace='social')),
    path('media/<str:size>/<path:path>', views.AvatarView.as_view({'get': 'list'}), name='avatar_list'),
    #path('auth/logout/', logout, {'next_page': settings.LOGOUT_REDIRECT_URL}, name='logout'),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
