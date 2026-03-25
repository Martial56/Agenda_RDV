from django.contrib import admin
from .models import Patient, RendezVous

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['numero_unique', 'sexe', 'age', 'type_client', 'date_mise_sous_arv']
    search_fields = ['numero_unique', 'contact_telephone']
    list_filter = ['sexe', 'type_client']

@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ['patient', 'date_rdv', 'motif_rdv', 'est_venu', 'date_prochain_rdv']
    list_filter = ['date_rdv', 'est_venu', 'motif_rdv']
    search_fields = ['patient__numero_unique']
