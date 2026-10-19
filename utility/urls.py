from django.urls import path
from . import views

app_name = 'utility'

urlpatterns = [
    path('upload/', views.upload, name='upload'),
    path('result/', views.result, name='result'),
    path('analyse/', views.analyse_api, name='analyse_api'),
    path('transform-image/', views.transform_image_api, name='transform_image_api'),
]