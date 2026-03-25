from django.db import models
from django.contrib.auth.models import User

class SyntheseHebdomadaire(models.Model):
    semaine_debut = models.DateField(verbose_name="Début de semaine")
    semaine_fin = models.DateField(verbose_name="Fin de semaine")
    total_rdv_prevus = models.PositiveIntegerField(default=0)
    total_venus = models.PositiveIntegerField(default=0)
    total_absents = models.PositiveIntegerField(default=0)
    total_relances = models.PositiveIntegerField(default=0)
    notes = models.TextField(blank=True)
    cree_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Synthèse Hebdomadaire"
        unique_together = ['semaine_debut', 'semaine_fin']
        ordering = ['-semaine_debut']

    def __str__(self):
        return f"Synthèse semaine du {self.semaine_debut.strftime('%d/%m/%Y')}"

    @property
    def taux_presence(self):
        if self.total_rdv_prevus == 0:
            return 0
        return round((self.total_venus / self.total_rdv_prevus) * 100, 1)

class SyntheseMensuelle(models.Model):
    mois = models.PositiveIntegerField(verbose_name="Mois")
    annee = models.PositiveIntegerField(verbose_name="Année")
    total_rdv_prevus = models.PositiveIntegerField(default=0)
    total_venus = models.PositiveIntegerField(default=0)
    total_absents = models.PositiveIntegerField(default=0)
    total_perdus_de_vue = models.PositiveIntegerField(default=0, verbose_name="Perdus de vue")
    notes = models.TextField(blank=True)
    cree_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Synthèse Mensuelle"
        unique_together = ['mois', 'annee']
        ordering = ['-annee', '-mois']

    def __str__(self):
        from calendar import month_name
        mois_fr = ['', 'Janvier','Février','Mars','Avril','Mai','Juin','Juillet','Août','Septembre','Octobre','Novembre','Décembre']
        return f"Synthèse {mois_fr[self.mois]} {self.annee}"

    @property
    def taux_presence(self):
        if self.total_rdv_prevus == 0:
            return 0
        return round((self.total_venus / self.total_rdv_prevus) * 100, 1)
