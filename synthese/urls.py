from django.urls import path
from . import views

urlpatterns = [
    path('', views.synthese_list, name='synthese_list'),
    path('hebdo/generer/', views.generer_hebdo, name='generer_hebdo'),
    path('hebdo/<int:pk>/', views.synthese_hebdo_detail, name='synthese_hebdo_detail'),
    path('mensuelle/<int:pk>/', views.synthese_mensuelle_detail, name='synthese_mensuelle_detail'),
    path('mensuelle/generer/', views.generer_mensuelle, name='generer_mensuelle'),
]
