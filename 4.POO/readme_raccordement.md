# Planificateur de Raccordement Post-Sinistre

##  Vue d'ensemble

Système de planification automatisé pour prioriser et organiser le raccordement des bâtiments après un sinistre, en optimisant les coûts, les délais et les priorités opérationnelles.

### Objectif

Produire un plan de raccordement réaliste tenant compte de :
- L'état des infrastructures (intactes / à remplacer)
- Les coûts matériels et main d'œuvre
- La durée d'intervention (heures-homme)
- Les priorités métiers (hôpital > école > habitation)
- Les contraintes opérationnelles (effectifs, budget, autonomie générateur)

##  Structure du projet

```
.
├── infra.py                    # Modèle Infrastructure
├── batiment.py                 # Modèle Bâtiment
├── raccordement.py             # Chargement CSV et liaisons
├── plan_raccordement.py        # Logique de planification
├── main.py                     # Script principal
└── donnees_infrastructures_complet.csv
```

### Fichiers principaux

#### `infra.py` — Classe Infrastructure
Gère les propriétés et calculs d'une infrastructure :
- **Attributs** : `infra_id`, `type_infra` (aérien/semi-aérien/fourreau), `infra_type` (intacte/à remplacer), `longueur`, `nb_maisons`
- **Calculs automatiques** :
  - `prix` : coût matériel (longueur × prix/m)
  - `duree` : heures-homme nécessaires
  - `worker_cost` : coût salarial total
- **Méthodes** :
  - `elapsed_time_with_workers(n)` : durée réelle avec n ouvriers
  - `required_workers_for_target_elapsed(target_h)` : nombre d'ouvriers pour atteindre une durée cible

#### `batiment.py` — Classe Bâtiment
Agrège les métriques pour un bâtiment :
- **Métriques calculées** via `calc_metrics()` :
  - `difficulte` : longueur/nb_maisons (favorise la mutualisation)
  - `cout_total` : somme des coûts matériels
  - `duree_totale` : heures-homme totales
  - `duree_min_elapsed` : temps minimal avec effectif maximum
  - `worker_cost_total` : coût salarial total
  - `nb_infras_a_remplacer` : nombre d'infrastructures à réparer

#### `raccordement.py`
Charge le CSV, standardise les données et crée les instances d'objets (Infrastructure, Bâtiment).

#### `plan_raccordement.py`
Cœur de la planification :
- **Phase 0** : Hôpital prioritaire (contrainte d'autonomie générateur)
- **Phases 1-4** : Découpage budgétaire (40%, 20%, 20%, 20%)
- Tri par score combiné (priorité métier + métriques opérationnelles)
- Génération de warnings si contraintes non respectées

#### `main.py`
Orchestration : charge les données, planifie les phases, génère le CSV de sortie.

## Utilisation

### Prérequis
```bash
python 3.8+
pandas
```

### Installation
```bash
# Créer et activer l'environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

# Installer les dépendances
pip install pandas
```

### Exécution
```bash
python main.py
```

### Entrée requise

**Fichier** : `donnees_infrastructures_complet.csv`

**Colonnes** :
- `id_batiment` : Identifiant du bâtiment
- `infra_id` : Identifiant de l'infrastructure
- `infra_type` : État (Intacte / À remplacer)
- `longueur` : Longueur en mètres
- `type_batiment` : Type (habitation / école / hôpital)
- `type_infra` : Type technique (aérien / semi-aérien / fourreau)
- `nb_maisons` : Nombre de prises desservies

**Exemple** :
```csv
id_batiment,infra_id,infra_type,longueur,type_batiment,type_infra,nb_maisons
E000001,P000308,Intacte,39.14,habitation,fourreau,3
E000085,P005500,À remplacer,125.50,hôpital,aérien,1
```

##  Sortie

**Fichier** : `BOMBOCLAAAT.csv` (configurable)

### Colonnes du plan

| Colonne | Description |
|---------|-------------|
| `phase` | Numéro de phase (0 = hôpital, 1-4 = phases budgétaires) |
| `id_batiment` | Premier bâtiment du groupe (compatibilité) |
| `id_batiments` | Liste de tous les bâtiments de la phase |
| `nb_batiments` | Nombre de bâtiments traités |
| `nb_infras_reparees` | Nombre d'infrastructures à réparer |
| `cout_total` | Coût matériel total (€) |
| `duree_totale_heures_homme` | Heures-homme nécessaires |
| `duree_min_elapsed_h` | Durée réelle minimale (avec max d'ouvriers) |
| `worker_cost_euros` | Coût salarial total (€) |
| `liste_infras_reparees` | Liste des IDs d'infrastructures |
| `warning` | Messages d'alerte (contraintes critiques) |

### Exemple de ligne
```csv
0,E000085,['E000085'],1,3,18483.26,77.92,9.35,2921.87,"['P005500','P007447','P007990']",""
```

**Interprétation** :
- Phase 0 (hôpital prioritaire)
- Coût matériel : 18 483 €
- 77,92 heures-homme nécessaires
- Réalisable en 9,35 heures avec 4 ouvriers par infra
- Coût salarial : 2 922 €

##  Paramètres configurables

### Tarifs et durées (dans `infra.py`)
```python
PRIX_PAR_M = {
    'aérien': 50,
    'semi-aérien': 75,
    'fourreau': 100
}

DUREE_PAR_M = {
    'aérien': 0.5,      # heures-homme par mètre
    'semi-aérien': 0.75,
    'fourreau': 1.0
}

WORKER_PAY_PER_8H = 300  # €/jour
MAX_WORKERS_PER_INFRA = 4
```

### Budget (dans `plan_raccordement.py`)
```python
BUDGET_TOTAL = 500000  # Budget total disponible
PHASE_BUDGETS = [0.40, 0.20, 0.20, 0.20]  # Répartition phases 1-4
generator_autonomy_h = 24  # Autonomie générateur (heures)
safety_margin = 0.8  # Marge de sécurité (80%)
```

### Priorités métiers
```python
PRIORITES = {
    'hôpital': 10,
    'école': 5,
    'habitation': 1
}
```

##  Logique de planification

### Phase 0 : Hôpital
- Priorité absolue (impératif de vie)
- Contrainte : réparation avant épuisement générateur
- Warning si `duree_min_elapsed > autonomie × safety_margin`

### Phases 1-4 : Découpage budgétaire
1. Calcul du coût total restant
2. Répartition : 40% → 20% → 20% → 20%
3. Pour chaque phase :
   - Tri des bâtiments par **score combiné**
   - Inclusion jusqu'à atteindre l'objectif de coût
   - Regroupement en une ligne de phase

### Score combiné
```
score = α × priorité + β × (1/difficulté) + γ × (1/coût) + δ × (1/durée)
```
Permet d'équilibrer priorité métier, facilité technique et efficacité économique.

##  Modèle de calcul

### Coût matériel
```
prix = longueur × PRIX_PAR_M[type_infra]
```

### Durée (heures-homme)
```
duree = longueur × DUREE_PAR_M[type_infra]
```

### Coût salarial
```
worker_cost = (heures_homme / 8) × WORKER_PAY_PER_8H
```
**Important** : Indépendant du nombre d'ouvriers (paiement à l'heure)

### Durée réelle (elapsed)
```
elapsed = heures_homme / min(nb_ouvriers, MAX_WORKERS_PER_INFRA)
```

### Durée minimale d'un bâtiment
```
duree_min_elapsed = max(elapsed_time_with_workers(MAX_WORKERS) pour chaque infra)
```
On prend le **maximum** car toutes les infras doivent être terminées.

##  Hypothèses et limites

### Hypothèses actuelles
-  Coûts et durées **linéaires** en longueur
-  **Parallélisation parfaite** entre infrastructures
-  Coût salarial **constant** (pas d'heures sup)
-  Infrastructure réparée = bénéfice **immédiat** pour tous les bâtiments
-  **Un seul hôpital** géré (phase 0)

### Limites identifiées
-  Pas de modélisation des **déplacements** entre sites
-  Pas de **non-linéarités** (mobilisation, primes)
-  Pas de **dépendances** entre infrastructures
-  Pas d'**ordonnancement fin** (planning horaire)
-  Pas de gestion **multi-hôpitaux**

##  Améliorations proposées

### Court terme
- [ ] Ajouter logs détaillés et assertions
- [ ] Créer des tests unitaires
- [ ] Exporter un rapport synthétique (Markdown/PDF)
- [ ] Valider la cohérence des agrégats

### Moyen terme
- [ ] Intégrer temps de déplacement/logistique
- [ ] Gérer plusieurs hôpitaux
- [ ] Modéliser coûts non-linéaires (mobilisation)
- [ ] Ajouter contraintes de dépendances

### Long terme
- [ ] Ordonnancement multi-journées (planning horaire)
- [ ] Solver d'optimisation (ILP/MIP)
- [ ] Interface graphique de visualisation
- [ ] API REST pour intégration SI

##  Tests et validation

### Vérifications recommandées
```python
# Cohérence des coûts
total_cost_batiments = sum(b.cout_total for b in batiments)
total_prix_infras = sum(i.prix for i in infrastructures if i.a_reparer)
assert abs(total_cost_batiments - total_prix_infras) < 0.01

# Couverture des bâtiments
batiments_planifies = set(id for phase in phases for id in phase['id_batiments'])
batiments_a_reparer = set(b.id for b in batiments if not b.est_raccordable())
assert batiments_planifies == batiments_a_reparer
```

### Scénarios de test
1. **Budget limité** : BUDGET_TOTAL = 50000 → vérifier phases partielles
2. **Effectif réduit** : MAX_WORKERS_PER_INFRA = 2 → durées allongées
3. **Autonomie courte** : generator_autonomy_h = 12 → warning hôpital
4. **Multi-hôpitaux** : ajouter 2+ hôpitaux → identifier limitation

##  Support

Pour toute question ou amélioration, consulter la documentation technique complète dans le code source.

---

**Version** : 1.0  
**Dernière mise à jour** : 2025  
**Licence** : 