from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from .views import WireWariantListView, WireTypeListView

app_name = 'wire'
urlpatterns = [
    path('variants/', WireWariantListView.as_view(), name='variant-list'),
    path('types/', WireTypeListView.as_view(), name='type-list'),
    
]