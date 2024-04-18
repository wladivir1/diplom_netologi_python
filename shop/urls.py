from django.urls import path

from . import views


app_name = 'shop'

urlpatterns = [
    path('partner/update', views.PartnerUpdate.as_view(), name='partner-update'),
    path('partner/status', views.PartnerStatus.as_view(), name='partner-status'),
    path('partner/orders', views.PartnerOrders.as_view(), name='partner-orders'),
    path('categories', views.CategoryView.as_view(), name='categories'),
    path('shops', views.ShopListView.as_view(), name='shops'),
    path('products', views.ProductInfoView.as_view(), name='products'),
    path('basket', views.BasketView.as_view({'post':'create', 'get':'list', 'delete':'destroy', 'put':'update'}), name='orders'),
    path('orders', views.OrderView.as_view(), name='confirmation-order'),
]