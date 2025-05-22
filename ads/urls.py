from django.urls import path

from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.list_ads, name='list_ads'),
    path('ads/<int:pk>/', views.ad_detail, name='ad_detail'),
    path('ads/create/', views.create_ad, name='create_ad'),
]
