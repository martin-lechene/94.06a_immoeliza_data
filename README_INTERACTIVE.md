# Interactive Immoweb Scraper

## Description

Ce scraper interactif ouvre un navigateur Chrome réel que vous pouvez contrôler manuellement. Vous pouvez naviguer sur Immoweb, sélectionner les éléments à scraper, créer un workflow personnalisé et utiliser votre vraie session de navigateur.

## Installation

Les dépendances sont déjà installées. Assurez-vous d'avoir Chrome installé sur votre système.

## Utilisation

### Lancer le scraper interactif

```bash
python interactive_main.py
```

### Étapes d'utilisation

1. **Le navigateur s'ouvre automatiquement**
   - Chrome s'ouvre avec votre profil utilisateur
   - Votre session et cookies sont préservés
   - Vous pouvez naviguer normalement

2. **Navigation manuelle**
   - Naviguez vers une page de recherche Immoweb
   - Par exemple: https://www.immoweb.be/en/search/house/for-sale
   - Appuyez sur Entrée dans le terminal quand vous êtes prêt

3. **Menu interactif**
   - **Option 1**: Ajouter un sélecteur de liens de propriétés
     - Permet de définir comment trouver les liens vers les pages de détails
     - Exemple: `css` selector avec valeur `a.card__title-link`
   
   - **Option 2**: Ajouter un sélecteur de page de détails
     - Permet de définir quels éléments extraire de chaque page de propriété
     - Exemple: prix, nombre de chambres, surface, etc.
   
   - **Option 3**: Voir le workflow actuel
     - Affiche tous les sélecteurs configurés
   
   - **Option 4**: Tester les sélecteurs
     - Teste les sélecteurs sur la page actuelle
     - Utile pour vérifier que tout fonctionne
   
   - **Option 5**: Démarrer le scraping
     - Lance le scraping avec le workflow configuré
     - Utilise votre vraie session de navigateur
   
   - **Option 6**: Sauvegarder le workflow
     - Sauvegarde votre configuration dans un fichier JSON
     - Permet de réutiliser le workflow plus tard
   
   - **Option 7**: Charger un workflow
     - Charge un workflow sauvegardé précédemment

## Types de sélecteurs

### CSS Selector
Exemple: `a.card__title-link` ou `.property-link`

### XPath
Exemple: `//a[@class='card__title-link']` ou `//div[@id='price']`

### Class Name
Exemple: `card__title-link` (sans le point)

### ID
Exemple: `property-price` (sans le #)

## Attributs à extraire

- **href**: Pour les liens
- **text**: Pour le texte visible
- **class**: Pour la classe CSS
- **id**: Pour l'ID
- Ou tout autre attribut HTML

## Exemple de workflow

1. Ouvrir le scraper interactif
2. Naviguer vers une page de recherche
3. Ajouter un sélecteur de propriété:
   - Type: `css`
   - Valeur: `a.card__title-link`
   - Attribut: `href`
4. Naviguer vers une page de détails
5. Ajouter des sélecteurs de détails:
   - Prix: `css` -> `.classified__price` -> `text`
   - Chambres: `css` -> `[data-label="Bedrooms"]` -> `text`
   - Surface: `css` -> `[data-label="Living area"]` -> `text`
6. Tester les sélecteurs
7. Sauvegarder le workflow
8. Démarrer le scraping

## Résultats

Les données extraites sont sauvegardées dans:
- `scraped_data.json`: Format JSON
- `scraped_data.csv`: Format CSV (si pandas est disponible)

## Avantages

✅ **Vraie session de navigateur**: Utilise votre profil Chrome avec vos cookies
✅ **Pas de blocage**: Le navigateur est réel, pas détecté comme bot
✅ **Workflow personnalisable**: Créez vos propres sélecteurs
✅ **Test interactif**: Testez vos sélecteurs avant de scraper
✅ **Sauvegarde/Chargement**: Réutilisez vos workflows

## Notes

- Le navigateur reste ouvert même après la fin du script (option `detach`)
- Vous pouvez fermer le navigateur manuellement quand vous avez terminé
- Les workflows sont sauvegardés en JSON et peuvent être modifiés manuellement

