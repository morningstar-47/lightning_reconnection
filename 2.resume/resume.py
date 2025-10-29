import pandas as pd
import os

# ==============================
# 0️⃣ Créer le dossier de sortie s'il n'existe pas
# ==============================
os.makedirs("fichiers", exist_ok=True)

# ==============================
# 1️⃣ Charger et nettoyer les données
# ==============================
df = pd.read_csv("donnees_infrastructures.csv")

# Nettoyage minimal
df['infra_type'] = df['infra_type'].astype(str).str.strip()
print(df['infra_type'].unique())  # <- montre toutes les valeurs réelles

# Nettoyage des noms de colonnes
df.columns = df.columns.str.strip().str.lower()

# Normalisation des valeurs texte
df['infra_type'] = df['infra_type'].astype(str).str.strip().str.lower()

# Harmonisation : mettre les types d’infra en format uniforme
df['infra_type'] = df['infra_type'].replace({
    'a_remplacer': 'À remplacer',
    'a remplacer': 'À remplacer',
    'remplacer': 'À remplacer',
    'infra_a_remplacer': 'À remplacer',
    'intacte': 'Intacte',
    'infra_intacte': 'Intacte'
})

print("Données nettoyées.\n")
print("Répartition des types d'infrastructures :")
print(df['infra_type'].value_counts(), "\n")

# ==============================
# 2️⃣ Séparer en fichiers selon le type
# ==============================
infra_intactes = df[df['infra_type'] == 'Intacte']
infra_a_remplacer = df[df['infra_type'] == 'À remplacer']

infra_intactes.to_csv("fichiers/infra_intactes.csv", index=False, encoding='utf-8')
infra_a_remplacer.to_csv("fichiers/infra_a_remplacer.csv", index=False, encoding='utf-8')

print(f"{len(infra_intactes)} lignes 'Intactes'")
print(f"{len(infra_a_remplacer)} lignes 'À remplacer'\n")

# ==============================
# 3️⃣ Infrastructures par bâtiment
# ==============================
infras_par_batiment = (
    df.groupby('id_batiment')['infra_id']
      .apply(list)
      .reset_index()
)
infras_par_batiment.to_csv("fichiers/infras_par_batiment.csv", index=False, encoding='utf-8')
print("Fichier 'infras_par_batiment.csv' créé.\n")

# ==============================
# 4️⃣ Résumé par bâtiment
# ==============================
resume_par_batiment = (
    df.groupby('id_batiment')
      .agg(
          nb_infras=('infra_id', 'nunique'),
          total_longueur=('longueur', 'sum'),
          nb_intactes=('infra_type', lambda x: (x == 'Intacte').sum()),
          nb_a_remplacer=('infra_type', lambda x: (x == 'À remplacer').sum())
      )
      .reset_index()
)
resume_par_batiment.to_csv("fichiers/resume_par_batiment.csv", index=False, encoding='utf-8')
print("Fichier 'resume_par_batiment.csv' créé.\n")

# ==============================
# 5️⃣ Résumé par infrastructure
# ==============================
resume_par_infra = (
    df.groupby('infra_id')
      .agg(
          nb_batiments=('id_batiment', 'nunique'),
          longueur_moy=('longueur', 'mean'),
          type_dominant=('infra_type', lambda x: x.mode()[0] if not x.mode().empty else None)
      )
      .reset_index()
)
resume_par_infra.to_csv("fichiers/resume_par_infra.csv", index=False, encoding='utf-8')
print("Fichier 'resume_par_infra.csv' créé.\n")

# ==============================
# 6️⃣ Statistiques globales
# ==============================
with open("fichiers/statistiques_globales.txt", "w", encoding="utf-8") as f:
    f.write("=== Statistiques globales ===\n")
    f.write(f"Lignes totales : {len(df)}\n")
    f.write(f"Bâtiments uniques : {df['id_batiment'].nunique()}\n")
    f.write(f"Infrastructures uniques : {df['infra_id'].nunique()}\n")
    f.write(f"Intactes : {(df['infra_type'] == 'Intacte').sum()}\n")
    f.write(f"À remplacer : {(df['infra_type'] == 'À remplacer').sum()}\n")
    f.write(f"Longueur totale : {df['longueur'].sum():.2f} m\n")

print("Fichier 'statistiques_globales.txt' créé.\n")
print("Tous les fichiers ont été générés avec succès.")
