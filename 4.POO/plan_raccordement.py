# plan_raccordement.py
from infrastructure import MAX_WORKERS_PER_INFRA

def score_combine(bat, alpha=0.4, beta=0.3, gamma=0.2, delta=0.1,
                  max_priorite=4, max_difficulte=None, max_cout=None, max_duree=None):
    """Calcule le score combiné d’un bâtiment pour priorisation."""
    priorite_norm = getattr(bat, 'priorite', 1) / max_priorite
    difficulte_norm = bat.difficulte / (max_difficulte + 1e-6)
    cout_norm = bat.cout_total / (max_cout + 1e-6)
    duree_norm = bat.duree_totale / (max_duree + 1e-6)
    
    return alpha*priorite_norm + beta*difficulte_norm + gamma*cout_norm + delta*duree_norm


def planifier_phases(batiments, generator_autonomy_h=20.0, safety_margin=0.2):
    """Planifie 5 phases en respectant les contraintes :

    - phase 0 : réparer l'hôpital (si présent)
    - phase 1 : ~40% du coût total
    - phases 2,3,4 : ~20% chacune

    Vérifie la contrainte d'autonomie du générateur de l'hôpital :
    on essaie d'utiliser le maximum d'ouvriers par infra (4) ; si le temps minimal
    nécessaire dépasse autonomy*(1 - safety_margin), on ajoute un champ "warning"
    dans la phase de l'hôpital.
    """
    phases = []
    infras_reparees = set()

    # Nettoyage liste: ne garder que ceux avec travaux
    to_fix = [b for b in batiments if getattr(b, 'nb_infras_a_remplacer', 0) > 0]
    if not to_fix:
        return phases

    # Totaux pour découpage par coût
    total_cost = sum(b.cout_total for b in to_fix)
    if total_cost <= 0:
        # fallback: plan par bâtiment
        return []

    # repères pour phases en %
    phase_targets = [0.40, 0.20, 0.20, 0.20]

    # 1) Phase 0 : hôpital(s)
    hopitaux = [b for b in to_fix if getattr(b, 'is_hopital', lambda: False)()]
    if hopitaux:
        # on prend le premier hopital (ouon pourrait en gérer plusieurs)
        hop = hopitaux[0]
        infras_phase = [i for i in getattr(hop, 'liste_infras_a_remplacer', []) if i not in infras_reparees]

        # vérifier contrainte générateur
        autonomy_threshold = generator_autonomy_h * (1.0 - safety_margin)
        warning = None
        if hop.duree_min_elapsed > autonomy_threshold:
            warning = (
                f"Attention: même avec {MAX_WORKERS_PER_INFRA} ouvriers/infra,\n"
                f"le temps minimal pour l'hôpital ({hop.duree_min_elapsed:.1f} h) > seuil ({autonomy_threshold:.1f} h)."
            )

        phases.append({
            "phase": 0,
            "id_batiment": hop.id,
            "id_batiments": [hop.id],
            "nb_batiments": 1,
            "nb_infras_reparees": len(infras_phase),
            "cout_total": hop.cout_total,
            "duree_totale_heures_homme": hop.duree_totale,
            "duree_min_elapsed_h": hop.duree_min_elapsed,
            "worker_cost_euros": hop.worker_cost_total,
            "liste_infras_reparees": infras_phase,
            "warning": warning
        })
        
        

        infras_reparees.update(infras_phase)
        # retirer hop du to_fix
        to_fix = [b for b in to_fix if b.id != hop.id]

    # 2) Phases 1..4 : découpage par coût
    remaining = sorted(to_fix, key=lambda b: -b.cout_total)  # tri décroissant par coût

    start_idx = 1
    cost_consumed = 0.0
    for pct in phase_targets:
        target = total_cost * pct
        phase_included = []
        cum = 0.0
        # On ajoute bâtiments (triés par score interne) tant que cum < target
        # utiliser score pour ordre interne
        # préparer scores (plus petit = prioritaire selon score_combine implémentation)
        max_difficulte = max((b.difficulte for b in remaining), default=1.0)
        max_cout = max((b.cout_total for b in remaining), default=1.0)
        max_duree = max((b.duree_totale for b in remaining), default=1.0)

        scored = sorted(
            [(b, score_combine(b, max_difficulte=max_difficulte, max_cout=max_cout, max_duree=max_duree)) for b in remaining],
            key=lambda x: x[1]
        )

        # ajouter en respectant l'ordre de score
        for b, _s in scored:
            if b in [x[0] for x in scored] and b not in [p[0] for p in phase_included]:
                if cum >= target and phase_included:
                    break
                phase_included.append((b, b.liste_infras_a_remplacer))
                cum += b.cout_total

        # créer entrée de phase pour chaque bâtiment sélectionné (on combine en une ligne)
        ids = [b.id for b, _ in phase_included]
        cout_phase = sum(b.cout_total for b, _ in phase_included)
        duree_homme_phase = sum(b.duree_totale for b, _ in phase_included)
        worker_cost_phase = sum(b.worker_cost_total for b, _ in phase_included)

        phases.append({
            "phase": start_idx,
            # id_batiment kept for backward-compatibility: first building in the group (or empty)
            "id_batiment": ids[0] if ids else "",
            "id_batiments": ids,
            "nb_batiments": len(ids),
            "nb_infras_reparees": sum(len(infra_list) for b, infra_list in phase_included),
            "cout_total": cout_phase,
            "duree_totale_heures_homme": duree_homme_phase,
            # duree minimale écoulée (max des minima des bâtiments inclus)
            "duree_min_elapsed_h": max((b.duree_min_elapsed for b, _ in phase_included), default=0.0),
            "worker_cost_euros": worker_cost_phase,
            "liste_infras_reparees": [infra for b, infra_list in phase_included for infra in infra_list],
            "warning": None
        })

        # marquer infras réparées
        for b, infra_list in phase_included:
            infras_reparees.update(infra_list)

        # retirer bâtiments sélectionnés
        remaining = [b for b in remaining if b.id not in ids]
        start_idx += 1

    return phases
