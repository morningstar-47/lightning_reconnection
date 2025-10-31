"""Configuration et constantes globales du projet.

Ce module centralise les constantes (prix, durées, gains salariaux,
capacités de ressources, priorités, budgets, etc.) afin que les autres
modules puissent les importer.
"""

# Prix par mètre (euros) par type d'infrastructure
PRIX_PAR_M = {
    "aerien": 500,
    "semi-aerien": 750,
    "fourreau": 900,
}

# Durée (heures-homme) par mètre par type d'infrastructure
DUREE_PAR_M = {
    "aerien": 2,
    "semi-aerien": 4,
    "fourreau": 5,
}

# Configuration ouvriers / contraintes
# paiement: montant (euros) pour 8 heures de travail
WORKER_PAY_PER_8H = 300
# nombre max d'ouvriers simultanés par infrastructure
MAX_WORKERS_PER_INFRA = 4

# Priorité selon le type de bâtiment (plus petit = plus prioritaire)
PRIORITE_TYPE_BAT = {
    "hôpital": 1,
    "hopital": 1,
    "école": 2,
    "ecole": 2,
    "habitation": 3,
}

# Configuration des phases et budget
NB_EMPLOYES_PAR_PHASE = 4
HEURES_PAR_EMPLOYE = 8
BUDGET_TOTAL = 0 # pour les futurs calculs
PHASE_BUDGETS = [0.4, 0.2, 0.2, 0.2]

# Contraintes spécifiques
MAX_HEURES_HOPITAL = 16

# Nombre maximal de phases
MAX_PHASES = len(PHASE_BUDGETS)
