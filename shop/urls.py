from django.urls import path

from . import views


app_name = 'shop'

urlpatterns = [
    path('partner/update', views.PartnerUpdate.as_view(), name='partner_update'),
    path('partner/status', views.PartnerStatus.as_view(), name='partner_status'),
    path('partner/orders', views.PartnerOrders.as_view(), name='partner_orders'),
    path('categories', views.CategoryView.as_view(), name="categories_list"),
    path('shops', views.ShopListView.as_view(), name="shops_list"),
    path('products', views.ProductInfoView.as_view(), name='products_list'),
    path('images/url/<int:pk>/', views.ImageUrlProductView.as_view({'get': 'list'}), name='product_images'),
    path('products/images/<int:pk>/', views.ImageProductView.as_view({'put': 'update', 'delete': 'destroy'}), name='product_images'),
    path('basket', views.BasketView.as_view({ 'get': 'list', 'post': 'create', 'delete': 'destroy', 'put': 'update'}), name='orders'),
    path('orders', views.OrderView.as_view(), name='confirmation-order'),
]