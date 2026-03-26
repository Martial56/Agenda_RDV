from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('agenda/', views.agenda_jour, name='agenda_jour'),
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/nouveau/', views.patient_create, name='patient_create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:pk>/modifier/', views.patient_edit, name='patient_edit'),
    path('patients/<int:patient_id>/rdv/', views.rdv_create_for_patient, name='rdv_create_for_patient'),
    path('rdv/nouveau/', views.rdv_create, name='rdv_create'),
    path('rdv/<int:pk>/relance-preventive/', views.rdv_relance_preventive, name='rdv_relance_preventive'),
    path('rdv/<int:pk>/relance-absence/', views.rdv_relance_absence, name='rdv_relance_absence'),
    path('rdv/<int:pk>/presence/', views.rdv_presence, name='rdv_presence'),
    path('relances/', views.a_relancer_list, name='a_relancer_list'),
    path('relances_pdv/<int:pk>/pdv/', views.pdv_relance, name='pdv_a_relancer'),
    path('pdv/', views.pdv_list, name='pdv_list'),
    path('api/stats/', views.api_stats, name='api_stats'),
]
