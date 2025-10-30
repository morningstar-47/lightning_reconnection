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

    def ajouter_batiment(self, batiment):
        """Ajoute un bâtiment desservi par cette infrastructure."""
        if batiment not in self.batiments:
            self.batiments.append(batiment)

    def __repr__(self):
        return (f"Infra({self.infra_id}, type={self.type_infra}, "
                f"longueur={self.longueur}, nb_maisons={self.nb_maisons}, "
                f"a_reparer={self.a_reparer})")
