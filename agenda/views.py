from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from datetime import date, timedelta
from .models import Patient, RendezVous
from .forms import (PatientForm, RendezVousAvecPatientForm, RendezVousSansPatientForm,
                    RelancePreventiveForm, RelanceAbsenceForm, PresenceForm, DateFilterForm)


def _prochain_numero(date_rdv):
    last = RendezVous.objects.filter(date_rdv=date_rdv).order_by('-numero_ordre').first()
    return (last.numero_ordre + 1) if last else 1


# ─── DASHBOARD ───────────────────────────────────────────────────────────────

@login_required
def dashboard(request):
    today = date.today()
    rdv_aujourd_hui = RendezVous.objects.filter(date_rdv=today).select_related('patient')
    rdv_absent = RendezVous.objects.filter(est_venu=False).select_related('patient')

    # Relances préventives J-2
    j2 = today + timedelta(days=2)
    relances_preventives = RendezVous.objects.filter(
        date_rdv=j2,
        est_venu__isnull=True,
        date_relance_preventive__isnull=True,
    ).select_related('patient')

    # Relances absence J+7
    max_date = today - timedelta(days=1)
    min_date = today - timedelta(days=7)
    relances_absence = RendezVous.objects.filter(
        date_rdv__range=(min_date, max_date),
        est_venu=False,
        date_relance_absence__isnull=True,
    ).select_related('patient')

    agenda_7j = [
        {'date': today + timedelta(days=i),
         'count': RendezVous.objects.filter(date_rdv=today + timedelta(days=i)).count()}
        for i in range(7)
    ]

    return render(request, 'agenda/dashboard.html', {
        'today': today,
        'rdv_aujourd_hui': rdv_aujourd_hui,
        'rdv_venus':    rdv_aujourd_hui.filter(est_venu=True).count(),
        #'rdv_absents':  rdv_aujourd_hui.filter(est_venu=False).count(), // nombre de RDV marqués absents aujourd'hui, sans compter les RDV des jours précédents
        'rdv_absents': rdv_absent.count(), #le nombre de RDV marqués absents, qui inclut aussi les RDV des jours précédents
        'rdv_en_attente': rdv_aujourd_hui.filter(est_venu__isnull=True).count(),
        'relances_preventives':    relances_preventives,
        'relances_absence':        relances_absence,
        'nb_relances_preventives': relances_preventives.count(),
        'nb_relances_absence':     relances_absence.count(),
        'total_patients': Patient.objects.count(),
        'rdv_ce_mois': RendezVous.objects.filter(
            date_rdv__month=today.month, date_rdv__year=today.year).count(),
        'agenda_7j': agenda_7j,
    })


# ─── AGENDA ──────────────────────────────────────────────────────────────────

@login_required
def agenda_jour(request):
    form = DateFilterForm(request.GET)
    selected_date = date.today()
    if form.is_valid() and form.cleaned_data.get('date'):
        selected_date = form.cleaned_data['date']

    rdv_list = RendezVous.objects.filter(
        date_rdv=selected_date).select_related('patient').order_by('numero_ordre')

    return render(request, 'agenda/agenda_jour.html', {
        'rdv_list': rdv_list,
        'selected_date': selected_date,
        'form': form,
        'prev_date': (selected_date - timedelta(days=1)).strftime('%Y-%m-%d'),
        'next_date': (selected_date + timedelta(days=1)).strftime('%Y-%m-%d'),
        'stats': {
            'total':      rdv_list.count(),
            'venus':      rdv_list.filter(est_venu=True).count(),
            'absents':    rdv_list.filter(est_venu=False).count(),
            'en_attente': rdv_list.filter(est_venu__isnull=True).count(),
        },
    })


# ─── PATIENTS ────────────────────────────────────────────────────────────────

@login_required
def patient_list(request):
    query = request.GET.get('q', '')
    patients = Patient.objects.all().order_by('-date_creation')
    if query:
        patients = patients.filter(
            Q(numero_unique__icontains=query) |
            Q(residence_adresse__icontains=query) |
            Q(contact_telephone__icontains=query)
        )
    return render(request, 'agenda/patient_list.html', {'patients': patients, 'query': query})


@login_required
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.cree_par = request.user
            patient.save()
            messages.success(request, f"Patient {patient.numero_unique} créé avec succès.")
            return redirect('rdv_create_for_patient', patient_id=patient.pk)
    else:
        form = PatientForm()
    return render(request, 'agenda/patient_form.html', {'form': form, 'title': 'Nouveau Patient'})


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    rdv_list = patient.rendez_vous.all().order_by('-date_rdv')
    prochain_rdv = patient.rendez_vous.filter(
        date_rdv__gte=date.today(), est_venu__isnull=True
    ).order_by('date_rdv').first()
    return render(request, 'agenda/patient_detail.html', {
        'patient': patient, 'rdv_list': rdv_list, 'prochain_rdv': prochain_rdv,
    })


@login_required
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, "Patient mis à jour.")
            return redirect('patient_detail', pk=pk)
    else:
        form = PatientForm(instance=patient)
    return render(request, 'agenda/patient_form.html', {
        'form': form, 'title': 'Modifier Patient', 'patient': patient})


# ─── RENDEZ-VOUS ─────────────────────────────────────────────────────────────

@login_required
def rdv_create(request):
    """Depuis la sidebar : l'utilisateur choisit le patient dans une liste déroulante."""
    if request.method == 'POST':
        form = RendezVousAvecPatientForm(request.POST)
        if form.is_valid():
            rdv = form.save(commit=False)
            rdv.cree_par = request.user
            rdv.numero_ordre = _prochain_numero(rdv.date_rdv)
            rdv.save()
            messages.success(request,
                f"RDV du {rdv.date_rdv.strftime('%d/%m/%Y')} enregistré pour {rdv.patient.numero_unique}.")
            return redirect('agenda_jour')
        # form invalide → réafficher avec erreurs (pas de redirect)
    else:
        initial = {}
        if request.GET.get('date'):
            initial['date_rdv'] = request.GET.get('date')
        form = RendezVousAvecPatientForm(initial=initial)

    return render(request, 'agenda/rdv_form.html', {
        'form': form,
        'title': 'Planifier un RDV',
        'patient': None,   # pas de patient pré-sélectionné
    })


@login_required
def rdv_create_for_patient(request, patient_id):
    """Depuis la fiche patient : patient déjà connu, formulaire sans champ patient."""
    patient = get_object_or_404(Patient, pk=patient_id)
    if request.method == 'POST':
        form = RendezVousSansPatientForm(request.POST)
        if form.is_valid():
            rdv = form.save(commit=False)
            rdv.patient = patient          # ← patient assigné ici, pas dans le formulaire
            rdv.cree_par = request.user
            rdv.numero_ordre = _prochain_numero(rdv.date_rdv)
            rdv.save()
            messages.success(request,
                f"RDV du {rdv.date_rdv.strftime('%d/%m/%Y')} ajouté à l'agenda.")
            return redirect('patient_detail', pk=patient_id)
        # form invalide → réafficher avec erreurs
    else:
        form = RendezVousSansPatientForm()

    return render(request, 'agenda/rdv_form.html', {
        'form': form,
        'title': 'Planifier un RDV',
        'patient': patient,   # affiché dans le bandeau info, pas dans le form
    })


# ─── RELANCES ────────────────────────────────────────────────────────────────

@login_required
def a_relancer_list(request):
    today = date.today()
    j2    = today + timedelta(days=2)
    max_date = today - timedelta(days=1)
    min_date = today - timedelta(days=7)

    preventives = RendezVous.objects.filter(
        date_rdv=j2,
        est_venu__isnull=True,
        date_relance_preventive__isnull=True,
    ).select_related('patient').order_by('date_rdv')

    absences = RendezVous.objects.filter(
        date_rdv__range=(min_date, max_date),
        est_venu=False,
        date_relance_absence__isnull=True,
    ).select_related('patient').order_by('date_rdv')

    return render(request, 'agenda/a_relancer.html', {
        'preventives': preventives,
        'absences':    absences,
        'today':       today,
        'j2':          j2,
        'seuil_absence_min': min_date,
        'seuil_absence_max': max_date,
    })


def _creer_rdv_reprogramme(rdv_origine, nouvelle_date, user):
    RendezVous.objects.create(
        patient=rdv_origine.patient,
        date_rdv=nouvelle_date,
        date_derniere_visite=rdv_origine.date_derniere_visite,
        motif_rdv=rdv_origine.motif_rdv,
        cree_par=user,
        numero_ordre=_prochain_numero(nouvelle_date),
    )


@login_required
def rdv_relance_preventive(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk)
    if request.method == 'POST':
        form = RelancePreventiveForm(request.POST, instance=rdv)
        if form.is_valid():
            saved = form.save()
            if saved.resultat_relance_preventive == '3' and saved.date_rdv_reprogramme:
                _creer_rdv_reprogramme(rdv, saved.date_rdv_reprogramme, request.user)
                messages.success(request,
                    f"Relance préventive enregistrée. RDV reprogrammé au "
                    f"{saved.date_rdv_reprogramme.strftime('%d/%m/%Y')}.")
            else:
                messages.success(request, "Relance préventive enregistrée.")
            return redirect('a_relancer_list')
    else:
        form = RelancePreventiveForm(instance=rdv,
                                      initial={'date_relance_preventive': date.today()})
    return render(request, 'agenda/relance_form.html', {
        'form': form, 'rdv': rdv, 'type_relance': 'preventive'})


@login_required
def rdv_relance_absence(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk)
    if request.method == 'POST':
        form = RelanceAbsenceForm(request.POST, instance=rdv)
        if form.is_valid():
            saved = form.save()
            if saved.resultat_relance_absence == '3' and saved.date_rdv_reprogramme:
                _creer_rdv_reprogramme(rdv, saved.date_rdv_reprogramme, request.user)
                messages.success(request,
                    f"Relance absence enregistrée. RDV reprogrammé au "
                    f"{saved.date_rdv_reprogramme.strftime('%d/%m/%Y')}.")
            else:
                messages.success(request, "Relance absence enregistrée.")
            return redirect('a_relancer_list')
    else:
        form = RelanceAbsenceForm(instance=rdv,
                                   initial={'date_relance_absence': date.today()})
    return render(request, 'agenda/relance_form.html', {
        'form': form, 'rdv': rdv, 'type_relance': 'absence'})


# ─── PRÉSENCE ────────────────────────────────────────────────────────────────

@login_required
def rdv_presence(request, pk):
    rdv = get_object_or_404(RendezVous, pk=pk)
    if request.method == 'POST':
        form = PresenceForm(request.POST, instance=rdv)
        if form.is_valid():
            saved = form.save()
            if saved.est_venu and saved.date_prochain_rdv:
                RendezVous.objects.create(
                    patient=rdv.patient,
                    date_rdv=saved.date_prochain_rdv,
                    date_derniere_visite=rdv.date_rdv,
                    motif_rdv='4',
                    cree_par=request.user,
                    numero_ordre=_prochain_numero(saved.date_prochain_rdv),
                )
                messages.success(request,
                    f"Présence enregistrée. Prochain RDV créé le "
                    f"{saved.date_prochain_rdv.strftime('%d/%m/%Y')}.")
            else:
                messages.success(request, "Absence enregistrée.")
            return redirect('agenda_jour')
    else:
        form = PresenceForm(instance=rdv)
    return render(request, 'agenda/presence_form.html', {'form': form, 'rdv': rdv})


# ─── API ─────────────────────────────────────────────────────────────────────

@login_required
def api_stats(request):
    today = date.today()
    stats = []
    for i in range(30, -1, -1):
        d = today - timedelta(days=i)
        rdv = RendezVous.objects.filter(date_rdv=d)
        stats.append({
            'date':    d.strftime('%d/%m'),
            'total':   rdv.count(),
            'venus':   rdv.filter(est_venu=True).count(),
            'absents': rdv.filter(est_venu=False).count(),
        })
    return JsonResponse({'stats': stats})
