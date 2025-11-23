# Guide Rapide - Scraper Interactif Immoweb

## 🚀 Démarrage Rapide

### 1. Lancer le scraper interactif

```bash
python interactive_main.py
```

### 2. Le navigateur s'ouvre

- Chrome s'ouvre automatiquement avec votre profil
- Vous êtes connecté avec votre session Immoweb
- Naviguez normalement dans le navigateur

### 3. Créer votre workflow

#### Étape 1: Naviguer vers une page de recherche
- Dans le navigateur, allez sur une page de résultats Immoweb
- Exemple: https://www.immoweb.be/en/search/house/for-sale
- Revenez au terminal et appuyez sur Entrée

#### Étape 2: Ajouter un sélecteur de propriétés
Dans le menu, choisissez **Option 1**:
- **Type**: `css`
- **Valeur**: `a.card__title-link` (ou trouvez le bon sélecteur en inspectant la page)
- **Attribut**: `href`

#### Étape 3: Naviguer vers une page de détails
- Dans le navigateur, cliquez sur une propriété pour voir sa page de détails
- Inspectez les éléments que vous voulez extraire (clic droit > Inspecter)

#### Étape 4: Ajouter des sélecteurs de détails
Dans le menu, choisissez **Option 2** plusieurs fois pour chaque champ:

**Exemple pour le prix:**
- **Nom du champ**: `price`
- **Type**: `css`
- **Valeur**: `.classified__price` (ou le sélecteur que vous trouvez)
- **Attribut**: `text`

**Exemple pour les chambres:**
- **Nom du champ**: `bedrooms`
- **Type**: `css`
- **Valeur**: `[data-label="Bedrooms"]` (ou autre sélecteur)
- **Attribut**: `text`

#### Étape 5: Tester
- Choisissez **Option 4** pour tester vos sélecteurs
- Vérifiez que les valeurs sont correctes

#### Étape 6: Sauvegarder
- Choisissez **Option 6** pour sauvegarder votre workflow
- Nommez-le (ex: `workflow.json`)

#### Étape 7: Scraper
- Retournez sur la page de recherche dans le navigateur
- Choisissez **Option 5** pour démarrer le scraping
- Le scraper utilisera votre vraie session!

## 💡 Astuces

### Trouver les bons sélecteurs

1. **Ouvrez les outils de développement** (F12)
2. **Utilisez l'outil de sélection** (Ctrl+Shift+C)
3. **Cliquez sur l'élément** que vous voulez scraper
4. **Dans l'inspecteur**, faites clic droit sur l'élément HTML
5. **Copiez**:
   - "Copy > Copy selector" pour CSS
   - "Copy > Copy XPath" pour XPath

### Exemples de sélecteurs courants

**Liens de propriétés:**
- CSS: `a.card__title-link`
- XPath: `//a[contains(@class, 'card__title-link')]`

**Prix:**
- CSS: `.classified__price`
- XPath: `//p[@class='classified__price']`

**Tableau de caractéristiques:**
- CSS: `tr th.classified-table__header`
- XPath: `//tr//th[@class='classified-table__header']`

## 📁 Fichiers générés

- `workflow.json`: Votre workflow sauvegardé
- `data/scraped_data.json`: Données extraites (JSON)
- `data/scraped_data.csv`: Données extraites (CSV)

## ⚠️ Important

- **Fermez Chrome complètement** avant de lancer le scraper
- Le navigateur reste ouvert après le scraping (c'est normal)
- Vous pouvez fermer le navigateur manuellement quand vous avez terminé

## 🔄 Réutiliser un workflow

1. Lancez le scraper
2. Choisissez **Option 7** pour charger un workflow
3. Entrez le nom du fichier (ex: `workflow.json`)
4. Votre workflow est chargé!

