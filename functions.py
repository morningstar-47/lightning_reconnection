Notes:
- 4 employés par infra
- 1 employé 8h 250$
- max des infras pas la somme
- 3 ou 4 phases
- budget: 40 35 25 ou 40 20 20 20
- générateur hôpital, que 20h d'autonomie restantes

############################################################################################################
class Infrastructure:
    def __init__(self, infra_id, type_infra, infra_type, longueur, nb_maisons):
        self.infra_id = infra_id
        self.type_infra = type_infra
        self.infra_type = infra_type
        self.longueur = longueur
        self.nb_maisons = nb_maisons
        
        # Tarifs et durées par type
        prix_par_m = {"aerien": 500, "semi-aerien": 750, "fourreau": 900}
        temps_par_m = {"aerien": 2, "semi-aerien": 4, "fourreau": 5}
        
        self.prix_m = prix_par_m.get(type_infra, 0)
        self.duree_h_m = temps_par_m.get(type_infra, 0)
        
        # Calcul automatique du coût et de la durée
        self.prix = self.longueur * self.prix_m
        self.duree = self.longueur * self.duree_h_m
        
        # Est-ce qu’il faut réparer ?
        self.a_reparer = "remplacer" in self.infra_type.lower()

class Batiment:
    def __init__(self, id_batiment, type_batiment, nb_maisons, infrastructures):
        self.id_batiment = id_batiment
        self.type_batiment = type_batiment
        self.nb_maisons = nb_maisons
        self.infrastructures = infrastructures  # liste d'objets Infrastructure
        
        # Calcul des métriques
        self.difficulte, self.cout_total, self.duree_totale, self.nb_infras_a_remplacer, self.liste_infras_a_remplacer = self.calc_metrics()
        
        # Priorité selon type
        priorite = {"hôpital": 1, "ecole": 2, "habitation": 3}
        self.priorite = priorite.get(type_batiment, 4)
    
    def calc_metrics(self):
        a_reparer = [i for i in self.infrastructures if i.a_reparer]
        difficulte = sum(i.longueur / (i.nb_maisons + 1e-6) for i in a_reparer)
        cout_total = sum(i.prix for i in a_reparer)
        duree_totale = sum(i.duree for i in a_reparer)
        nb_infras = len(a_reparer)
        liste_infras = [i.infra_id for i in a_reparer]
        return difficulte, cout_total, duree_totale, nb_infras, liste_infras
############################################################################################################
def score_combine(bat, alpha=0.4, beta=0.3, gamma=0.2, delta=0.1,
                  max_priorite=4, max_difficulte=None, max_cout=None, max_duree=None):
    # Normalisation
    priorite_norm = bat.priorite / max_priorite
    difficulte_norm = bat.difficulte / (max_difficulte + 1e-6)
    cout_norm = bat.cout_total / (max_cout + 1e-6)
    duree_norm = bat.duree_totale / (max_duree + 1e-6)
    
    # Score combiné (plus petit = plus prioritaire)
    return alpha*priorite_norm + beta*difficulte_norm + gamma*cout_norm + delta*duree_norm
################################################################################################################
def planifier_phases(batiments):
    phases = []
    infras_reparees = set()
    phase_num = 1
    
    # Pré-calcul des max pour normalisation
    max_difficulte = max(b.difficulte for b in batiments)
    max_cout = max(b.cout_total for b in batiments)
    max_duree = max(b.duree_totale for b in batiments)
    
    to_fix = [b for b in batiments if b.nb_infras_a_remplacer > 0]
    
    while to_fix:
        # Calcul scores
        scores = [(b, score_combine(b, max_difficulte=max_difficulte, max_cout=max_cout, max_duree=max_duree)) 
                  for b in to_fix]
        scores.sort(key=lambda x: x[1])  # tri par score
        
        # Bâtiment à réparer cette phase
        bat = scores[0][0]
        infras_phase = [i for i in bat.liste_infras_a_remplacer if i not in infras_reparees]
        
        if not infras_phase:
            to_fix.remove(bat)
            continue
        
        infras_reparees.update(infras_phase)
        
        # Stats de la phase
        phases.append({
            "phase": phase_num,
            "id_batiment": bat.id_batiment,
            "nb_infras_reparees": len(infras_phase),
            "cout_total": bat.cout_total,
            "duree_totale": bat.duree_totale,
            "liste_infras_reparees": infras_phase
        })
        
        # Recalcul métriques des autres bâtiments
        for b in to_fix:
            nouvelles_infras = [i for i in b.liste_infras_a_remplacer if i not in infras_reparees]
            a_reparer = [infra for infra in b.infrastructures if infra.infra_id in nouvelles_infras]
            b.difficulte = sum(i.longueur / (i.nb_maisons + 1e-6) for i in a_reparer)
            b.cout_total = sum(i.prix for i in a_reparer)
            b.duree_totale = sum(i.duree for i in a_reparer)
            b.nb_infras_a_remplacer = len(a_reparer)
            b.liste_infras_a_remplacer = [i.infra_id for i in a_reparer]
        
        # Retirer bâtiments finis
        to_fix = [b for b in to_fix if b.nb_infras_a_remplacer > 0]
        phase_num += 1
        
    return phases
    ####################################################################################################
    priorite = {"hôpital": 1, "ecole": 2, "habitation": 3}
