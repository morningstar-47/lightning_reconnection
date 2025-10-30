# plan_raccordement.py

# Priorité selon le type de bâtiment
PRIORITE_TYPE_BAT = {
    "hôpital": 1,
    "école": 2,
    "habitation": 3
}

def score_combine(bat, alpha=0.4, beta=0.3, gamma=0.2, delta=0.1,
                  max_priorite=4, max_difficulte=None, max_cout=None, max_duree=None):
    """Calcule le score combiné d’un bâtiment pour priorisation."""
    priorite_norm = getattr(bat, 'priorite', 1) / max_priorite
    difficulte_norm = bat.difficulte / (max_difficulte + 1e-6)
    cout_norm = bat.cout_total / (max_cout + 1e-6)
    duree_norm = bat.duree_totale / (max_duree + 1e-6)
    
    return alpha*priorite_norm + beta*difficulte_norm + gamma*cout_norm + delta*duree_norm


def planifier_phases(batiments):
    """Planifie les phases de réparation des bâtiments en fonction du score combiné."""
    phases = []
    infras_reparees = set()
    phase_num = 1
    
    # Attribuer la priorité selon le type de bâtiment
    for b in batiments:
        b.priorite = PRIORITE_TYPE_BAT.get(getattr(b, 'type_batiment', 'habitation').lower(), 4)
    
    # Max pour normalisation
    max_difficulte = max(b.difficulte for b in batiments)
    max_cout = max(b.cout_total for b in batiments)
    max_duree = max(b.duree_totale for b in batiments)
    
    # Liste des bâtiments à traiter
    to_fix = [b for b in batiments if getattr(b, 'nb_infras_a_remplacer', 0) > 0]
    
    while to_fix:
        # Calcul des scores
        scores = [(b, score_combine(b, max_difficulte=max_difficulte, 
                                    max_cout=max_cout, max_duree=max_duree)) 
                  for b in to_fix]
        scores.sort(key=lambda x: x[1])  # tri par score (plus petit = plus prioritaire)
        
        # Bâtiment le plus prioritaire
        bat = scores[0][0]
        infras_phase = [i for i in getattr(bat, 'liste_infras_a_remplacer', []) if i not in infras_reparees]
        
        if not infras_phase:
            to_fix.remove(bat)
            continue
        
        infras_reparees.update(infras_phase)
        
        # Stats de la phase
        phases.append({
            "phase": phase_num,
            "id_batiment": bat.id,
            "nb_infras_reparees": len(infras_phase),
            "cout_total": bat.cout_total,
            "duree_totale": bat.duree_totale,
            "liste_infras_reparees": infras_phase
        })
        
        # Recalcul métriques des autres bâtiments
        for b in to_fix:
            nouvelles_infras = [i for i in getattr(b, 'liste_infras_a_remplacer', []) if i not in infras_reparees]
            a_reparer = [infra for infra in getattr(b, 'infras', []) if infra.infra_id in nouvelles_infras]
            b.difficulte = sum(i.longueur / (i.nb_maisons + 1e-6) for i in a_reparer)
            b.cout_total = sum(i.prix for i in a_reparer)
            b.duree_totale = sum(i.duree for i in a_reparer)
            b.nb_infras_a_remplacer = len(a_reparer)
            b.liste_infras_a_remplacer = [i.infra_id for i in a_reparer]
        
        # Retirer bâtiments finis
        to_fix = [b for b in to_fix if b.nb_infras_a_remplacer > 0]
        phase_num += 1
        
    return phases
