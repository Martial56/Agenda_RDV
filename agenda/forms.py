from django import forms
from .models import Patient, RendezVous
from django.utils import timezone


MOTIF_RDV_CHOICES = [
    ('1', 'Bilan initial'),
    ('2', 'Bilan de suivi'),
    ('3', 'Charge virale'),
    ('4', 'Renouvellement ordonnance'),
    ('5', 'Visite de suivi'),
    ('6', 'PCR'),
    ('7', 'Statut définitif enfant exposé'),
    ('8', 'CO/nETP'),
    ('9', 'Autre'),
]
class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ['cree_par', 'date_creation']
        widgets = {
            'numero_unique':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 09817/01/26:XXXX'}),
            'code_etablissement': forms.TextInput(attrs={'class': 'form-control', 'value': 'CMS WALE', 'readonly': 'readonly'}),
            'numero_site':        forms.TextInput(attrs={'class': 'form-control', 'value': '09817', 'readonly': 'readonly'}),
            'sexe':               forms.Select(attrs={'class': 'form-select'}),
            'age':                forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'age_en_mois':        forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'type_client':        forms.Select(attrs={'class': 'form-select'}),
            'population_cles':    forms.Select(attrs={'class': 'form-select'}),
            'date_mise_sous_arv': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contact_telephone':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+225 XX XX XX XX XX'}),
            'residence_adresse':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Commune, Quartier, Village'}),
        }


# Formulaire AVEC choix du patient (depuis la sidebar)
'''class RendezVousAvecPatientForm(forms.ModelForm):
    'motif_rdv'= forms.MultipleChoiceField(
                choices=MOTIF_RDV_CHOICES,
                widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
                required=False
            ),
    class Meta:
        model = RendezVous
        fields = ['patient', 'date_rdv', 'date_derniere_visite', 'motif_rdv', 'motif_rdv_autre']
        widgets = {
            'patient':            forms.Select(attrs={'class': 'form-select select2'}),
            'date_rdv':           forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_derniere_visite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            #'motif_rdv':          forms.Select(attrs={'class': 'form-select'}),
            'motif_rdv_autre':    forms.TextInput(attrs={'class': 'form-control'}),
        }'''
class RendezVousAvecPatientForm(forms.ModelForm):
    motif_rdv = forms.MultipleChoiceField(
    choices=MOTIF_RDV_CHOICES,
    widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
    required=False
    )

    class Meta:
        model = RendezVous
        fields = ['patient', 'date_rdv', 'date_derniere_visite', 'motif_rdv', 'motif_rdv_autre']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select select2'}),
            'date_rdv': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_derniere_visite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'motif_rdv_autre': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_motif_rdv(self):
        data = self.cleaned_data.get('motif_rdv')
        return ','.join(data) if data else ''


# Formulaire SANS champ patient (depuis la fiche patient — patient fixé dans la vue)
'''class RendezVousSansPatientForm(forms.ModelForm):
    'motif_rdv'= forms.MultipleChoiceField(
                choices=MOTIF_RDV_CHOICES,
                widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
                required=False
            ),
    class Meta:
        model = RendezVous
        fields = ['date_rdv', 'date_derniere_visite', 'motif_rdv', 'motif_rdv_autre']
        widgets = {
            'date_rdv':           forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_derniere_visite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            #'motif_rdv':          forms.Select(attrs={'class': 'form-select'}),
            'motif_rdv_autre':    forms.TextInput(attrs={'class': 'form-control'}),
        }'''
class RendezVousSansPatientForm(forms.ModelForm):
    motif_rdv = forms.MultipleChoiceField(
        choices=MOTIF_RDV_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )

    class Meta:
        model = RendezVous
        fields = ['date_rdv', 'date_derniere_visite', 'motif_rdv', 'motif_rdv_autre']
        widgets = {
            'date_rdv': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_derniere_visite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'motif_rdv_autre': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_motif_rdv(self):
        data = self.cleaned_data.get('motif_rdv')
        return ','.join(data) if data else ''


class RelancePreventiveForm(forms.ModelForm):
    """Relance J-2 : appel de confirmation 2 jours avant le RDV."""
    class Meta:
        model = RendezVous
        fields = ['date_relance_preventive', 'moyen_relance_preventive',
                  'resultat_relance_preventive', 'date_rdv_reprogramme']
        widgets = {
            'date_relance_preventive':    forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'moyen_relance_preventive':   forms.Select(attrs={'class': 'form-select'}),
            'resultat_relance_preventive': forms.Select(attrs={'class': 'form-select'}),
            'date_rdv_reprogramme':       forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class RelanceAbsenceForm(forms.ModelForm):
    """Relance J+7 : patient absent depuis au moins 1 semaine."""
    class Meta:
        model = RendezVous
        fields = ['date_relance_absence', 'moyen_relance_absence',
                  'resultat_relance_absence', 'date_rdv_reprogramme']
        widgets = {
            'date_relance_absence':    forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'moyen_relance_absence':   forms.Select(attrs={'class': 'form-select'}),
            'resultat_relance_absence': forms.Select(attrs={'class': 'form-select'}),
            'date_rdv_reprogramme':    forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class PresenceForm(forms.ModelForm):
    motif_prochain_rdv = forms.MultipleChoiceField(
        choices=MOTIF_RDV_CHOICES,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )
    class Meta:
        model = RendezVous
        fields = ['est_venu', 'date_prochain_rdv','motif_prochain_rdv', 'motif_non_venue'] #'date_derniere_visite', 'motif_rdv', 
        widgets = {
            'est_venu': forms.Select(
                attrs={'class': 'form-select'},
                choices=[('', '-- Sélectionner --'), ('True', 'Oui — Venu'), ('False', 'Non — Absent')]
            ),
            #'date_derniere_visite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_prochain_rdv': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            #'motif_rdv':  forms.Select(attrs={'class': 'form-select'}),
            'motif_non_venue':   forms.TextInput(attrs={'class': 'form-control'}),
        }
    def clean_motif_rdv(self):
        data = self.cleaned_data.get('motif_rdv')
        return ','.join(data) if data else ''


class DateFilterForm(forms.Form):
    date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        label="Date du RDV",
        initial=timezone.now().date,
    )
