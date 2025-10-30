# Données d'Exemple

Ces données ont été générées automatiquement pour tester les scripts d'analyse.

## Contenu

- **buildings.shp**: 50 bâtiments
- **network.shp**: 52 segments de réseau électrique
- **substations.shp**: 3 postes de transformation
- **buildings.csv**: Données tabulaires des bâtiments
- **costs.csv**: Coûts de raccordement estimés

## Statistiques

### Bâtiments
- Total: 50
- Connectés: 14
- Déconnectés: 36
- Population totale: 4619

### Types de bâtiments
building_type
residential    33
school          8
commercial      8
hospital        1

### Priorités
priority
high      24
medium    20
low        6

### Réseau
- Segments: 52
- Segments actifs: 45
- Segments endommagés: 7
- Longueur totale: 1667.35 unités

## Utilisation

Pour analyser ces données, exécutez:

```bash
python scripts/main.py --data-path data
```
