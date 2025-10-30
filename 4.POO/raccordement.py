# raccordement.py
import pandas as pd
from batiment import Batiment
from infrastructure import Infrastructure

class Raccordement:
    def __init__(self, chemin_csv):
        # Chargement du CSV
        self.df = pd.read_csv(chemin_csv)
        self.batiments = {}   # dictionnaire id_batiment → Batiment
        self.infras = {}      # dictionnaire id_infra → Infrastructure

        # Étapes principales
        self._nettoyer_donnees()
        self._creer_objets()

    def _nettoyer_donnees(self):
        """Standardise les données : colonnes et types."""
        self.df.columns = self.df.columns.str.strip().str.lower()
        self.df['infra_type'] = self.df['infra_type'].str.strip().str.lower()
        self.df['infra_type'] = self.df['infra_type'].replace({
            'a_remplacer': 'À remplacer',
            'remplacer': 'À remplacer',
            'infra_intacte': 'Intacte',
            'intacte': 'Intacte'
        })

    def _creer_objets(self):
        """Crée les objets Bâtiment et Infrastructure et les relie."""
        for _, row in self.df.iterrows():
            # --- Infrastructure ---
            infra_id = row['infra_id']
            if infra_id not in self.infras:
                self.infras[infra_id] = Infrastructure(
                    infra_id,
                    row['type_infra'],
                    row['infra_type'],
                    row['longueur'],
                    row.get('nb_maisons', 1)  # nb_maisons si présent dans le CSV
)
            infra = self.infras[infra_id]

            # --- Bâtiment ---
            bat_id = row['id_batiment']
            if bat_id not in self.batiments:
                self.batiments[bat_id] = Batiment(
                    id_batiment=bat_id,
                    nb_maisons=row.get('nb_maisons', 1),
                    type_batiment=row['type_batiment']
                )
            bat = self.batiments[bat_id]

            # --- Lier bâtiment ↔ infrastructure ---
            bat.ajouter_infrastructure(infra)
            infra.ajouter_batiment(bat)

 