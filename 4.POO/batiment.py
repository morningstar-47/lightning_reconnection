class Batiment:
    def __init__(self, id_batiment, nb_maisons, type_batiment):
        self.id = id_batiment
        self.nb_maisons = int(nb_maisons)
        self.type_batiment = type_batiment
        self.infras = []  # liste des infrastructures

    def ajouter_infrastructure(self, infra):
        if infra not in self.infras:
            self.infras.append(infra)

    def est_raccordable(self):
        return all(infra.infra_type == 'intacte' for infra in self.infras)
    # sert à savoir si un bâtiment peut être raccordé immédiatement sans 
    # qu’aucune infrastructure desservant
    # ce bâtiment ne nécessite de réparation.
    def calc_metrics(self):
        a_reparer = [i for i in self.infras if i.infra_type != 'intacte']
        
        difficulte = sum(i.longueur / max(1, sum(b.nb_maisons for b in i.batiments))
                         for i in a_reparer)
        
        cout_total = sum(i.prix for i in a_reparer)
        duree_totale = sum(i.duree for i in a_reparer)
        nb_infras = len(a_reparer)
        liste_infras = [i.id for i in a_reparer]

        return difficulte, cout_total, duree_totale, nb_infras, liste_infras

    def calc_metrics(self):
        a_reparer = [i for i in self.infras if i.a_reparer]
        self.difficulte = sum(i.longueur / (i.nb_maisons + 1e-6) for i in a_reparer)
        self.cout_total = sum(i.prix for i in a_reparer)
        self.duree_totale = sum(i.duree for i in a_reparer)
        self.nb_infras_a_remplacer = len(a_reparer)
        self.liste_infras_a_remplacer = [i.infra_id for i in a_reparer]
