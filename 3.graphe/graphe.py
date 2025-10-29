import pandas as pd
import networkx as nx

# ==============================
# 1️ Charger le CSV nettoyé
# ==============================
df = pd.read_csv("donnees_infrastructures.csv")

# ==============================
# 2️ Créer le graphe
# ==============================
G = nx.Graph()

# Attribuer un coût à chaque arête
def cout(infra_type, longueur):
    # Intacte = faible coût, À remplacer = coût plus élevé
    if infra_type == 'Intacte':
        return longueur
    else:  # À remplacer
        return longueur * 3  # coefficient à ajuster selon criticité / coût

# Ajouter les arêtes (chaque infrastructure relie un bâtiment à son infra)
for _, row in df.iterrows():
    # Chaque ligne représente un bâtiment et son infra
    # On crée l'arête "bâtiment → infra" avec le coût
    G.add_edge(row['id_batiment'], row['infra_id'], weight=cout(row['infra_type'], row['longueur']))

print(f"Graphe créé : {G.number_of_nodes()} nœuds, {G.number_of_edges()} arêtes")

# ==============================
# 3️ Calcul de métrique de priorisation
# ==============================
# Pour chaque bâtiment, on peut calculer :
# score = nombre de maisons desservies / coût total des arêtes qui le relient

scores = {}
for bat in df['id_batiment'].unique():
    subset = df[df['id_batiment'] == bat]
    nb_maisons = subset['nb_maisons'].sum()
    cout_total = sum([cout(t,l) for t,l in zip(subset['infra_type'], subset['longueur'])])
    scores[bat] = nb_maisons / cout_total if cout_total > 0 else 0

# Trier les bâtiments par score décroissant
batiments_priorites = sorted(scores.items(), key=lambda x: x[1], reverse=True)

print("\nTop 10 bâtiments à raccorder (score le plus élevé = priorité) :")
for bat, score in batiments_priorites[:10]:
    print(f"{bat} → score : {score:.2f}")

# ==============================
# 4️ Optionnel : sauvegarder le tableau des scores
# ==============================
df_scores = pd.DataFrame(batiments_priorites, columns=['id_batiment', 'score_priorite'])
df_scores.to_csv("batiments_priorites.csv", index=False, encoding='utf-8')
print("\nFichier 'batiments_priorites.csv' créé.")
