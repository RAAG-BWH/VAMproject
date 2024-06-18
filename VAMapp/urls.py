from django.urls import path
from . import views

urlpatterns = [
    path('', views.myview, name='default_view'),
    path('home/embryo.x3d', views.threeD, name='x3d'),
    path('voxel/', views.voxel, name = 'voxel'),
    path('check_access/', views.check_access, name = 'check_access')
]
