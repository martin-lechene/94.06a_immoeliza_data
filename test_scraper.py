from scraper.scraper import Immoweb_Scraper
import time

def test_scraper():
    print("Testing Immoweb Scraper with 1 page...")
    numpages = 1
    
    start = time.time()
    immoscrap = Immoweb_Scraper(numpages + 1)
    
    print("\n=== Step 1: Scraping table dataset ===")
    immoscrap.scrape_table_dataset()
    
    print(f"\n=== Step 2: Data collected: {len(immoscrap.data_set)} properties ===")
    
    if len(immoscrap.data_set) > 0:
        print("\n=== Step 3: Updating dataset ===")
        immoscrap.update_dataset()
        
        print("\n=== Step 4: Creating raw DataFrame ===")
        immoscrap.Raw_DataFrame()
        
        print("\n=== Step 5: Saving raw CSV ===")
        immoscrap.to_csv_raw()
        
        print("\n=== Step 6: Cleaning DataFrame ===")
        immoscrap.Clean_DataFrame()
        
        print("\n=== Step 7: Saving clean CSV ===")
        immoscrap.to_csv_clean()
        
        end = time.time()
        print(f"\n=== SUCCESS ===")
        print(f"Time Taken: {end - start:.2f}s")
        print(f"Scraped {len(immoscrap.data_set_df)} rows from {immoscrap.numpages} pages")
    else:
        print("\n=== WARNING: No data collected ===")
        print("The scraper ran but didn't collect any data.")
        print("This could be due to:")
        print("1. All pages returned 403 errors")
        print("2. The HTML structure of Immoweb has changed")
        print("3. Network issues")
    
    return len(immoscrap.data_set) > 0

if __name__ == "__main__":
    success = test_scraper()
    exit(0 if success else 1)

