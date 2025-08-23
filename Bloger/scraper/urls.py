from django.urls import path
from . import views

app_name = 'scraper'

urlpatterns = [
    path('', views.index, name='index'),
    path('detail/<int:pk>/', views.detail, name='detail'),
    path('download/<int:pk>/', views.download_json, name='download_json'),
    path('api/scrape/', views.api_scrape, name='api_scrape'),
]