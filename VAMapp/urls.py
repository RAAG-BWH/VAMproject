from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_view, name='main_view'),
    path('receiver/', views.receiver_view, name="receiver_view"),
    path('check_access/', views.check_access, name = 'check_access'),
    path('get_default/', views.get_default, name = 'get_default'),
    # path('get_sino/', views.get_sino, name = 'get_sino')
]
