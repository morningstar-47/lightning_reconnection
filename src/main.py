from raccordement import Raccordement
from plan_raccordement import planifier_phases
import pandas as pd

chemin_csv = 'donnees_infrastructures_complet.csv'
raccordement = Raccordement(chemin_csv)

# Calcul des métriques pour chaque bâtiment
for bat in raccordement.batiments.values():
    bat.calc_metrics()

# Planifier les phases
phases = planifier_phases(list(raccordement.batiments.values()))

# Conversion en DataFrame
df_phases = pd.DataFrame(phases)

# Sauvegarde CSV
df_phases.to_csv("BOMBOCLAAAT.csv", index=False, encoding="utf-8")
print("Fichier 'BOMBOCLAAAT.csv' créé avec succès !")
