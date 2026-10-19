from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('history/', views.history, name='history'),
    path('analysis/<int:pk>/', views.analysis_detail, name='analysis_detail'),
    path('analysis/<int:pk>/rename/', views.rename_analysis, name='rename_analysis'),
    path('analysis/<int:pk>/delete/', views.delete_analysis, name='delete_analysis'),
    path('favorites/', views.favorites, name='favorites'),
    path('favorites/toggle/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites/<int:pk>/remove/', views.remove_favorite, name='remove_favorite'),
]