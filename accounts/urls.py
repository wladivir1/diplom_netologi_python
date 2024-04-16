from django.urls import path, include

from . import views


app_name = 'accounts'

urlpatterns = [
    path('users/activate/<uid>/<token>', views.ActivateUser.as_view({'get': 'activation'}), name='activation'),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    path('types/', views.TypeUserView.as_view(), name='user-type'),
    path('contacts/', views.ContactView.as_view({'get':'list'}), name='contact'),
    path('contacts/create/', views.ContactView.as_view({'post': 'create'}), name='contact-create'),
    path('contacts/update/<int:pk>/', views.ContactView.as_view({'put': 'update'}), name='contact-update'),
    path('contacts/destroy/<int:pk>/', views.ContactView.as_view({'delete': 'destroy'}), name='contact-destroy'),
]
