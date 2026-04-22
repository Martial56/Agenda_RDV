from django.db import models
from django.contrib.auth.models import User

# ─── CONSTANTES DE SÉPARATION DES POPULATIONS ────────────────────────────────
# PTME : enfants (0-19 ans) + Femme enceinte (3) + Femme allaitante (4)
PTME_TYPES = ['3', '4']          # types_client réservés PTME (quel que soit l'âge)
PTME_AGE_MAX = 19                # âge max pour les enfants PTME

GROUP_PTME = 'Agenda PTME'
GROUP_ADULTE = 'Agenda Adulte'


def get_patients_queryset(user):
    """Retourne le queryset de patients filtré selon le groupe de l'utilisateur."""
    from django.db.models import Q
    qs = Patient.objects.all()
    if user.groups.filter(name=GROUP_PTME).exists():
        # PTME : enfants 0-19 ans OU femme enceinte/allaitante
        return qs.filter(
            Q(age__lte=PTME_AGE_MAX) | Q(type_client__in=PTME_TYPES)
        )
    elif user.groups.filter(name=GROUP_ADULTE).exists():
        # Adulte : > 19 ans ET pas femme enceinte/allaitante
        return qs.filter(age__gt=PTME_AGE_MAX).exclude(type_client__in=PTME_TYPES)
    # Staff / superuser : tout voir
    return qs


def get_rdv_queryset(user):
    """Retourne le queryset de RDV filtré selon le groupe de l'utilisateur."""
    from django.db.models import Q
    qs = RendezVous.objects.all()
    if user.groups.filter(name=GROUP_PTME).exists():
        return qs.filter(
            Q(patient__age__lte=PTME_AGE_MAX) | Q(patient__type_client__in=PTME_TYPES)
        )
    elif user.groups.filter(name=GROUP_ADULTE).exists():
        return qs.filter(patient__age__gt=PTME_AGE_MAX).exclude(
            patient__type_client__in=PTME_TYPES
        )
    return qs

SEXE_CHOICES = [('M', 'Masculin'), ('F', 'Féminin')]

TYPE_CLIENT_CHOICES = [
    ('1', 'Client sous TARV'),
    ('2', 'Enfant exposé'),
    ('3', 'Femme enceinte'),
    ('4', 'Femme allaitante'),
    ('5', 'Population clés'),
]

POPULATION_CLES_CHOICES = [
    ('TS', 'Travailleur(se) de sexe'),
    ('HSH', 'Hommes ayant des rapports sexuels avec hommes'),
    ('UD', 'Usagers de drogues'),
    ('PC', 'Populations Carcérales'),
]

MOTIF_RDV_CHOICES = [
    ('1', 'Bilan initial'),
    ('2', 'Bilan de suivi'),
    ('3', 'Charge virale'),
    ('4', 'Renouvellement ordonnance'),
    ('5', 'Visite de suivi'),
    ('6', 'PCR'),
    ('7', 'Statut définitif enfant exposé'),
    ('8', 'CO/ETP'),
    ('9', 'Autre'),
]

RESULTAT_RELANCE_CHOICES = [
    ('1', 'RDV confirmé'),
    ('2', 'Injoignable'),
    ('3', 'RDV reprogrammé (préciser la date)'),
    ('4', 'Refus du RDV'),
    ('5', 'Client décédé'),
    ('6', 'Pas de réponse au SMS'),
    ('7', 'Suivi dans un autre centre'),
    ('8', 'Ne répond pas aux appels'),
    ('9', 'Pas de relance effectuée'),
    ('10', 'Autre'),
]

MOYEN_RELANCE_CHOICES = [
    ('1', 'Appel téléphonique'),
    ('2', 'VAD'),
    ('3', 'SMS'),
    ('4', 'Autre'),
]

# Deux types de relance distincts
TYPE_RELANCE_CHOICES = [
    ('preventive', 'Relance préventive (J-2 avant RDV)'),
    ('absence',    'Relance absence (RDV manqué depuis 1 semaine)'),
]

class Patient(models.Model):
    numero_unique = models.CharField(max_length=50, unique=True, verbose_name="N° Unique d'identification")
    code_etablissement = models.CharField(max_length=20, verbose_name="Code établissement")
    numero_site = models.CharField(max_length=20, blank=True, verbose_name="N° Site")
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES, verbose_name="Sexe")
    age = models.PositiveIntegerField(verbose_name="Âge")
    age_en_mois = models.BooleanField(default=False, verbose_name="Âge en mois (< 2 ans)")
    type_client = models.CharField(max_length=1, choices=TYPE_CLIENT_CHOICES, verbose_name="Type de client")
    population_cles = models.CharField(max_length=10, choices=POPULATION_CLES_CHOICES, blank=True, verbose_name="Population clés")
    date_mise_sous_arv = models.DateField(verbose_name="Date de mise sous ARV")
    contact_telephone = models.CharField(max_length=20, verbose_name="Contact téléphonique")
    residence_adresse = models.CharField(max_length=255, verbose_name="Résidence/Adresse géographique")
    cree_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='patients_crees')
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Patient"
        verbose_name_plural = "Patients"

    def __str__(self):
        return f"{self.numero_unique} - {self.get_sexe_display()} - {self.age} ans"

    @property
    def age_display(self):
        if self.age_en_mois:
            return f"{self.age} mois"
        return f"{self.age} ans"
    
    def get_type_client_display(self):
        if not self.type_client:
            return ""
        choix_dict = dict(TYPE_CLIENT_CHOICES)
        
        codes = self.type_client.split(',')
        labels = [choix_dict.get(code.strip(), code.strip()) for code in codes]

        return ", ".join(labels)


class RendezVous(models.Model):
    numero_ordre = models.PositiveIntegerField(verbose_name="N° d'ordre (Colonne A)")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='rendez_vous')
    date_rdv = models.DateField(verbose_name="Date du RDV")
    date_derniere_visite = models.DateField(verbose_name="Date de la dernière visite")
    #motif_rdv = models.CharField(max_length=1, choices=MOTIF_RDV_CHOICES, verbose_name="Motif du RDV")
    motif_rdv = models.CharField(max_length=255, blank=True)
    motif_rdv_autre = models.CharField(max_length=200, blank=True, verbose_name="Motif autre (préciser)")

    # Colonne K — Relance préventive (J-2 avant RDV)
    date_relance_preventive = models.DateField(null=True, blank=True, verbose_name="Date relance préventive (J-2)")
    moyen_relance_preventive = models.CharField(max_length=1, choices=MOYEN_RELANCE_CHOICES, blank=True, verbose_name="Moyen relance préventive")
    resultat_relance_preventive = models.CharField(max_length=2, choices=RESULTAT_RELANCE_CHOICES, blank=True, verbose_name="Résultat relance préventive")

    # Colonne L — Relance absence (RDV manqué depuis 1 semaine)
    date_relance_absence = models.DateField(null=True, blank=True, verbose_name="Date relance absence (J+7)")
    moyen_relance_absence = models.CharField(max_length=1, choices=MOYEN_RELANCE_CHOICES, blank=True, verbose_name="Moyen relance absence")
    resultat_relance_absence = models.CharField(max_length=2, choices=RESULTAT_RELANCE_CHOICES, blank=True, verbose_name="Résultat relance absence")
    date_rdv_reprogramme = models.DateField(null=True, blank=True, verbose_name="Date RDV reprogrammé")

    # Colonne M et N — Présence au RDV
    est_venu = models.BooleanField(null=True, verbose_name="Patient venu au RDV")
    date_prochain_rdv = models.DateField(null=True, blank=True, verbose_name="Date prochain RDV")
    motif_prochain_rdv = models.CharField(max_length=200, blank=True, verbose_name="Motif du prochain RDV")
    motif_non_venue = models.CharField(max_length=200, blank=True, verbose_name="Motif de non-venue")

    cree_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='rdv_crees')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        ordering = ['date_rdv', 'numero_ordre']

    def __str__(self):
        return f"RDV {self.patient.numero_unique} - {self.date_rdv}"

    @property
    def statut(self):
        if self.est_venu is None:
            return 'en_attente'
        elif self.est_venu:
            return 'honore'
        else:
            return 'manque'

    @property
    def necessite_relance_preventive(self):
        """J-2 avant le RDV, pas encore relancé préventivement"""
        from datetime import date
        today = date.today()
        j_moins_2 = self.date_rdv
        from datetime import timedelta
        debut = self.date_rdv - timedelta(days=2)
        return (
            today >= debut and
            today < self.date_rdv and
            self.est_venu is None and
            not self.date_relance_preventive
        )

    @property
    def necessite_relance_absence(self):
        """RDV manqué depuis au moins 7 jours, pas encore relancé pour absence"""
        from datetime import date, timedelta
        today = date.today()
        return (
            self.est_venu == False and
            today >= self.date_rdv + timedelta(days=7) and
            not self.date_relance_absence
        )
    
    def get_motifs_labels(self):
        if not self.motif_rdv:
            return ""

        choix_dict = dict(MOTIF_RDV_CHOICES)

        codes = self.motif_rdv.split(',')
        labels = [choix_dict.get(code.strip(), code.strip()) for code in codes]

        return ", ".join(labels)
    
