from config import MAX_WORKERS_PER_INFRA, WORKER_PAY_PER_8H


class Batiment:
    def __init__(self, id_batiment, nb_maisons, type_batiment):
        self.id = id_batiment
        self.nb_maisons = int(nb_maisons)
        self.type_batiment = (type_batiment or "").strip()
        self.infras = []  # liste des infrastructures

        # attributs calculés
        self.difficulte = 0.0
        self.cout_total = 0.0
        # duree_totale est le total des heures-homme nécessaires (somme des durees)
        self.duree_totale = 0.0
        # duree minimale écoulée pour réparer le bâtiment si on maximise les ouvriers
        self.duree_min_elapsed = 0.0
        self.nb_infras_a_remplacer = 0
        self.liste_infras_a_remplacer = []
        # coût total des ouvriers pour réparer ce bâtiment
        self.worker_cost_total = 0.0

    def ajouter_infrastructure(self, infra):
        if infra not in self.infras:
            self.infras.append(infra)

    def est_raccordable(self):
        # Retourne True si aucune des infrastructures ne nécessite réparation
        return all(not getattr(infra, 'a_reparer', False) for infra in self.infras)

    def calc_metrics(self):
        """Calcule et stocke les métriques utilisées pour la priorisation.

        - difficulte : somme(longueur / nb_maisons) pour infras à réparer
        - cout_total : somme(prix) pour infras à réparer (coût matériel)
        - duree_totale : somme(duree) => heures-homme totales nécessaires
        - duree_min_elapsed : temps minimal (heures) si on met MAX_WORKERS_PER_INFRA par infra
        - nb_infras_a_remplacer, liste_infras_a_remplacer
        - worker_cost_total : coût salaires des ouvriers (euros)
        """
        a_reparer = [i for i in self.infras if getattr(i, 'a_reparer', False)]

        # difficulté (approx) : longueur / nb_maisons desservies
        self.difficulte = sum(i.longueur / max(1, i.nb_maisons) for i in a_reparer)

        # coût matériel
        self.cout_total = sum(i.prix for i in a_reparer)

        # heures-homme totales (somme des besoins)
        self.duree_totale = sum(i.duree for i in a_reparer)

        # temps minimal écoulé si on affecte au maximum d'ouvriers par infra
        if a_reparer:
            self.duree_min_elapsed = max(i.elapsed_time_with_workers(MAX_WORKERS_PER_INFRA) for i in a_reparer)
        else:
            self.duree_min_elapsed = 0.0

        self.nb_infras_a_remplacer = len(a_reparer)
        self.liste_infras_a_remplacer = [i.infra_id for i in a_reparer]

        # coût total des ouvriers (salaire) pour réparer ce bâtiment (heures-homme /8 * 300)
        # note: same worker cost independent of parallelization
        self.worker_cost_total = sum(i.worker_cost for i in a_reparer)

    def is_hopital(self) -> bool:
        t = (self.type_batiment or "").strip().lower()
        return 'hopital' in t or 'hôpital' in t
