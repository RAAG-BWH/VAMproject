from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.myview, name='myview'),
    path('home/embryo.x3d', views.threeD, name='x3d'),
    path('voxel/', views.voxel, name = 'voxel')
]
