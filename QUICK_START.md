# Quick Start Guide - Interactive Immoweb Scraper

## 🚀 Quick Start

### 1. Launch the interactive scraper

```bash
python interactive_main.py
```

### 2. Browser opens

- Chrome opens automatically with your profile
- You are logged in with your Immoweb session
- Navigate normally in the browser

### 3. Create your workflow

#### Step 1: Navigate to a search page
- In the browser, go to an Immoweb results page
- Example: https://www.immoweb.be/en/search/house/for-sale
- Return to the terminal and press Enter

#### Step 2: Add a property selector
In the menu, choose **Option 1**:
- **Type**: `css`
- **Value**: `a.card__title-link` (or find the right selector by inspecting the page)
- **Attribute**: `href`

#### Step 3: Navigate to a detail page
- In the browser, click on a property to see its detail page
- Inspect the elements you want to extract (right-click > Inspect)

#### Step 4: Add detail selectors
In the menu, choose **Option 2** multiple times for each field:

**Example for price:**
- **Field name**: `price`
- **Type**: `css`
- **Value**: `.classified__price` (or the selector you find)
- **Attribute**: `text`

**Example for bedrooms:**
- **Field name**: `bedrooms`
- **Type**: `css`
- **Value**: `[data-label="Bedrooms"]` (or another selector)
- **Attribute**: `text`

#### Step 5: Test
- Choose **Option 4** to test your selectors
- Verify that the values are correct

#### Step 6: Save
- Choose **Option 6** to save your workflow
- Name it (e.g., `workflow.json`)

#### Step 7: Scrape
- Go back to the search page in the browser
- Choose **Option 5** to start scraping
- The scraper will use your real session!

## 💡 Tips

### Finding the right selectors

1. **Open developer tools** (F12)
2. **Use the selection tool** (Ctrl+Shift+C)
3. **Click on the element** you want to scrape
4. **In the inspector**, right-click on the HTML element
5. **Copy**:
   - "Copy > Copy selector" for CSS
   - "Copy > Copy XPath" for XPath

### Common selector examples

**Property links:**
- CSS: `a.card__title-link`
- XPath: `//a[contains(@class, 'card__title-link')]`

**Price:**
- CSS: `.classified__price`
- XPath: `//p[@class='classified__price']`

**Feature table:**
- CSS: `tr th.classified-table__header`
- XPath: `//tr//th[@class='classified-table__header']`

## 📁 Generated files

- `workflow.json`: Your saved workflow
- `data/scraped_data.json`: Extracted data (JSON)
- `data/scraped_data.csv`: Extracted data (CSV)

## ⚠️ Important

- **Close Chrome completely** before launching the scraper
- The browser stays open after scraping (this is normal)
- You can close the browser manually when you're done

## 🔄 Reuse a workflow

1. Launch the scraper
2. Choose **Option 7** to load a workflow
3. Enter the filename (e.g., `workflow.json`)
4. Your workflow is loaded!

