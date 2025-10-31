# infra.py

# Constantes globales pour prix et durée par type d'infrastructure
PRIX_PAR_M = {
    "aerien": 500,
    "semi-aerien": 750,
    "fourreau": 900
}

DUREE_PAR_M = {
    "aerien": 2,
    "semi-aerien": 4,
    "fourreau": 5
}

# Configuration ouvriers / contraintes
# paiement: 300 euros pour 8h de travail
WORKER_PAY_PER_8H = 300
# nombre max d'ouvriers simultanés par infrastructure (téléportation => pas de travel-time)
MAX_WORKERS_PER_INFRA = 4


class Infrastructure:
    def __init__(self, infra_id, type_infra, infra_type, longueur, nb_maisons):
        """
        :param infra_id: identifiant de l'infrastructure
        :param type_infra: 'aerien', 'semi-aerien', 'fourreau'
        :param infra_type: 'intacte' ou 'à remplacer'
        :param longueur: longueur de l'infrastructure (m)
        :param nb_maisons: nombre de maisons desservies
        """
        self.infra_id = infra_id
        self.type_infra = type_infra.strip().lower()      # aérien, semi-aérien, fourreau
        self.infra_type = infra_type.strip().lower()      # intacte ou à remplacer
        self.longueur = float(longueur)
        self.nb_maisons = int(nb_maisons)
        self.batiments = []  # bâtiments desservis

        # Calcul automatique du coût et de la durée
        self.prix_m = PRIX_PAR_M.get(self.type_infra, 0)
        self.duree_h_m = DUREE_PAR_M.get(self.type_infra, 0)
        self.prix = self.longueur * self.prix_m
        self.duree = self.longueur * self.duree_h_m

        # Est-ce qu’il faut réparer ?
        self.a_reparer = "remplacer" in self.infra_type.lower()

        # Coûts liés aux ouvriers (basés sur nombre d'heures-homme)
        # self.duree représente le nombre total d'heures-homme nécessaires
        # si on met n ouvriers simultanément, l"elapsed" time = self.duree / n
        # Le coût des ouvriers (salaire) total est indépendant du n (heures-homme fixes)
        self.worker_hours = self.duree
        # coût total des ouvriers pour cette infra (en euros)
        self.worker_cost = (self.worker_hours / 8.0) * WORKER_PAY_PER_8H

    def elapsed_time_with_workers(self, n_workers: int) -> float:
        """Retourne le temps écoulé (heures) si on affecte n_workers simultanément (min 1)."""
        n = max(1, min(int(n_workers), MAX_WORKERS_PER_INFRA))
        return self.duree / n

    def required_workers_for_target_elapsed(self, target_elapsed_h: float) -> int:
        """Combien d'ouvriers (<= MAX_WORKERS_PER_INFRA) pour réduire l'elapsed time
        en-dessous de target_elapsed_h. Retourne MAX_WORKERS_PER_INFRA si impossible.
        """
        if target_elapsed_h <= 0:
            return MAX_WORKERS_PER_INFRA
        needed = int((self.duree + target_elapsed_h - 1e-9) // target_elapsed_h)
        # ceil alternative: needed = math.ceil(self.duree / target_elapsed_h)
        needed = max(1, needed)
        return min(needed, MAX_WORKERS_PER_INFRA)

    def ajouter_batiment(self, batiment):
        """Ajoute un bâtiment desservi par cette infrastructure."""
        if batiment not in self.batiments:
            self.batiments.append(batiment)

    def __repr__(self):
        return (f"Infra({self.infra_id}, type={self.type_infra}, "
                f"longueur={self.longueur}, nb_maisons={self.nb_maisons}, "
                f"a_reparer={self.a_reparer})")
