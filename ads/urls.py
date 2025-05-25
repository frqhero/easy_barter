from django.urls import path

from . import views

app_name = 'ads'

urlpatterns = [
    path('', views.list_ads, name='list_ads'),
    path('ads/<int:pk>/', views.ad_detail, name='ad_detail'),
    path('ads/<int:pk>/delete/', views.delete_ad, name='delete_ad'),
    path('ads/create/', views.create_ad, name='create_ad'),
    path('ads/<int:pk>/edit/', views.update_ad, name='update_ad'),
    path('proposals/create/<int:ad_id>/', views.create_proposal, name='create_proposal'),
    path('proposals/', views.list_proposals, name='list_proposals'),
    path('proposals/<int:pk>/accept/', views.accept_proposal, name='accept_proposal'),

]
