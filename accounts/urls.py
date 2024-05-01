from django.urls import path, include

from . import views


app_name = 'accounts'

urlpatterns = [
    path('users/activate/<uid>/<token>', views.ActivateUser.as_view({'get': 'activation'}), name='activation'),
    path('', include('djoser.urls')),
    path('', include('djoser.urls.authtoken')),
    
    path('types/', views.TypeUserView.as_view(), name='user-type'),
    path('contacts/', views.ContactView.as_view({'get': 'list', 'post': 'create', 'put': 'update', 'delete': 'destroy'}), name='contact'),
    path('avatars/', views.AvatarView.as_view({'get': 'list', 'put': 'update', 'delete': 'destroy'}), name='avatar'),
    
]
