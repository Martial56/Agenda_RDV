from django import forms
from .models import SyntheseHebdomadaire, SyntheseMensuelle

class SyntheseHebdoForm(forms.ModelForm):
    class Meta:
        model = SyntheseHebdomadaire
        exclude = ['cree_par', 'date_creation']
        widgets = {
            'semaine_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'semaine_fin': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class SyntheseMensuelleForm(forms.ModelForm):
    class Meta:
        model = SyntheseMensuelle
        exclude = ['cree_par', 'date_creation']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
