from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
from agenda.models import RendezVous
from .models import SyntheseHebdomadaire, SyntheseMensuelle
from .forms import SyntheseHebdoForm, SyntheseMensuelleForm

@login_required
#'''def synthese_list(request):
#    hebdo = SyntheseHebdomadaire.objects.all()[:10]
 #   mensuel = SyntheseMensuelle.objects.all()[:12]
  #  return render(request, 'synthese/synthese_list.html', {
   #     'hebdo_list': hebdo, 'mensuel_list': mensuel
    #})'''
    
def synthese_list(request):
    jour = date.today()

    hebdo = SyntheseHebdomadaire.objects.all()[:10]
    mensuel = SyntheseMensuelle.objects.all()[:12]

    # 🔥 absents récents (ex: 7 derniers jours)
    debut = jour - timedelta(days=7)

    rdv_absents = RendezVous.objects.filter(
        date_rdv__range=[debut, jour],
        est_venu=False
    ).select_related('patient').order_by('date_rdv')

    return render(request, 'synthese/synthese_list.html', {
        'hebdo_list': hebdo,
        'mensuel_list': mensuel,
        'rdv_absents': rdv_absents
})

@login_required
def generer_hebdo(request):
    """Génère automatiquement une synthèse hebdomadaire"""
    today = date.today()
    debut = today - timedelta(days=today.weekday())
    fin = debut + timedelta(days=6)
    
    rdv_semaine = RendezVous.objects.filter(date_rdv__range=[debut, fin])
    
    synthese, created = SyntheseHebdomadaire.objects.get_or_create(
        semaine_debut=debut,
        semaine_fin=fin,
        defaults={'cree_par': request.user}
    )
    synthese.total_rdv_prevus = rdv_semaine.count()
    synthese.total_venus = rdv_semaine.filter(est_venu=True).count()
    synthese.total_absents = rdv_semaine.filter(est_venu=False).count()
    #synthese.total_relances = rdv_semaine.filter(date_relance__isnull=False).count()
    synthese.total_relances = rdv_semaine.filter(date_relance_absence__isnull=False).count()
    synthese.save()
    
    messages.success(request, f"Synthèse hebdomadaire générée : {synthese}")
    return redirect('synthese_list')

@login_required
def generer_mensuelle(request):
    today = date.today()
    rdv_mois = RendezVous.objects.filter(
        date_rdv__month=today.month, date_rdv__year=today.year
    )
    synthese, created = SyntheseMensuelle.objects.get_or_create(
        mois=today.month, annee=today.year,
        defaults={'cree_par': request.user}
    )
    synthese.total_rdv_prevus = rdv_mois.count()
    synthese.total_venus = rdv_mois.filter(est_venu=True).count()
    synthese.total_absents = rdv_mois.filter(est_venu=False).count()
    synthese.total_perdus_de_vue = rdv_mois.filter(
        est_venu=False, date_relance_absence__isnull=True
    ).count()
    synthese.save()
    messages.success(request, f"Synthèse mensuelle générée.")
    return redirect('synthese_list')

@login_required
def synthese_hebdo_detail(request, pk):
    synthese = get_object_or_404(SyntheseHebdomadaire, pk=pk)
    rdv_absents = RendezVous.objects.filter(
        date_rdv__range=[synthese.semaine_debut, synthese.semaine_fin],
        est_venu=False
    ).select_related('patient')
    return render(request, 'synthese/hebdo_detail.html', {
        'synthese': synthese, 'rdv_absents': rdv_absents
    })

@login_required
def synthese_mensuelle_detail(request, pk):
    synthese = get_object_or_404(SyntheseMensuelle, pk=pk)

    rdv_absents = RendezVous.objects.filter(
        date_rdv__month=synthese.mois,
        date_rdv__year=synthese.annee,
        est_venu=False
    ).select_related('patient')

    return render(request, 'synthese/mensuel_detail.html', {
        'synthese': synthese,
        'rdv_absents': rdv_absents
    })