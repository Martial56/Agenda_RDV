# ARV Agenda — Système de Suivi des Rendez-Vous ARV

Application Django pour la gestion des rendez-vous des patients sous traitement antirétroviral (ARV).

## 🚀 Installation et Démarrage

### 1. Prérequis
- Python 3.10+
- pip

### 2. Installation
```bash
# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Installer Django
pip install django

# Se placer dans le dossier
cd arv_agenda

# Créer la base de données
python manage.py migrate

# Créer un compte administrateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

### 3. Accès
- Application : http://127.0.0.1:8000
- Administration : http://127.0.0.1:8000/admin

---

## 📋 Fonctionnalités

### Agenda du Jour (Colonnes A à N)
Reproduit fidèlement la structure du registre papier :

| Colonne | Champ | Description |
|---------|-------|-------------|
| A | N° d'ordre | Numéro d'enregistrement automatique |
| B | N° Unique | Identifiant unique du patient |
| C | Sexe | M / F |
| D | Âge | En années ou mois |
| E | Type client | TARV, Enfant exposé, Femme enceinte... |
| F | Mise sous ARV | Date de début du traitement |
| G | Contact | Téléphone patient/soutien |
| H | Résidence | Adresse géographique |
| I | Dernière visite | Date de la dernière consultation |
| J | Motif RDV | Bilan, suivi, charge virale... |
| K | Relance | Date + moyen de relance |
| L | Résultat relance | RDV confirmé, injoignable... |
| M | Présence | Venu / Absent |
| N | Prochain RDV | Date + motif du prochain RDV |

### Workflow d'utilisation

#### 1. Nouveau patient
1. Aller dans **Patients > Nouveau Patient**
2. Remplir les infos (colonnes B à H)
3. Planifier le 1er RDV à la **date de fin de traitement**

#### 2. Enregistrement avec données existantes
1. Chercher le patient existant
2. Cliquer **+ RDV** pour planifier le prochain rendez-vous
3. Le système crée automatiquement l'entrée dans l'agenda à la date choisie

#### 3. Le jour du RDV
1. Ouvrir l'**Agenda du Jour**
2. Pour chaque patient venu : cliquer ✓ → noter la présence + prochain RDV
3. Le prochain RDV est **automatiquement créé** dans l'agenda

#### 4. Relances (Colonnes K & L)
1. Aller dans **À Relancer** pour voir les absents
2. Cliquer **📞 Relancer** → noter le moyen + résultat
3. Si RDV reprogrammé : saisir la nouvelle date

#### 5. Synthèses
- **Synthèse Hebdomadaire** : générée automatiquement (absents non programmés)
- **Synthèse Mensuelle** : agrège les synthèses hebdo du mois

---

## 🏗️ Structure du Projet

```
arv_agenda/
├── arv_agenda/          # Configuration Django
│   ├── settings.py
│   └── urls.py
├── agenda/              # App principale
│   ├── models.py        # Patient, RendezVous
│   ├── views.py         # Toutes les vues
│   ├── forms.py         # Formulaires
│   └── urls.py
├── synthese/            # App synthèses
│   ├── models.py        # SyntheseHebdo, SyntheseMensuelle
│   └── views.py
├── templates/           # Templates HTML
│   ├── base.html
│   ├── login.html
│   ├── agenda/
│   └── synthese/
├── static/
│   └── css/main.css
└── db.sqlite3           # Base de données SQLite
```

---

## 👤 Compte par défaut (démo)
- **Utilisateur** : admin
- **Mot de passe** : admin123

> ⚠️ Changer le mot de passe en production !
