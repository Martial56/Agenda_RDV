from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User, Group
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


# ─── Inline pour afficher/modifier les groupes d'un utilisateur ───────────────

class GroupInline(admin.TabularInline):
    model = User.groups.through
    extra = 1
    verbose_name = "Groupe (Agenda)"
    verbose_name_plural = "Groupes (Agenda PTME / Agenda Adulte)"


class UserAgendaAdmin(BaseUserAdmin):
    inlines = [GroupInline]
    list_display = ['username', 'first_name', 'last_name', 'email', 'get_agenda_group', 'is_staff']
    list_filter = ['groups', 'is_staff', 'is_active']

    def get_agenda_group(self, obj):
        groupes = obj.groups.filter(name__in=['Agenda PTME', 'Agenda Adulte'])
        return ', '.join(g.name for g in groupes) if groupes.exists() else '— (tous)'
    get_agenda_group.short_description = 'Agenda'


# Désenregistrer l'admin User par défaut, réenregistrer avec le nôtre
admin.site.unregister(User)
admin.site.register(User, UserAgendaAdmin)
