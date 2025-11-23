"""
Interactive Scraper with Selenium - Allows user to interact with browser
and create scraping workflows
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
from bs4 import BeautifulSoup
import pandas as pd

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None


class InteractiveImmowebScraper:
    """
    Interactive scraper that opens a browser the user can interact with.
    Allows creating workflows by selecting elements on the page.
    """
    
    def __init__(self):
        """Initialize the interactive scraper with a real browser."""
        self.driver = None
        self.workflow = {
            'base_urls': [],
            'property_selectors': [],
            'detail_selectors': {},
            'extracted_data': []
        }
        self.setup_driver()
    
    def setup_driver(self):
        """Setup Chrome driver with options to keep session."""
        print("Setting up Chrome browser...")
        chrome_options = Options()
        
        # Keep browser open and use real user profile
        chrome_options.add_experimental_option("detach", True)
        chrome_options.add_experimental_option("useAutomationExtension", False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Use your Chrome profile to keep cookies and session
        user_data_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "User Data")
        profile_dir = "Default"
        
        # Check if Chrome is running
        chrome_running = False
        if PSUTIL_AVAILABLE:
            try:
                chrome_running = any("chrome" in p.name().lower() for p in psutil.process_iter(['name']))
            except:
                pass
        
        if chrome_running:
            print("[WARNING] Chrome is already running!")
            print("Please close Chrome completely before continuing.")
            print("Or we can use a separate profile...")
            choice = input("Use separate profile? (y/n): ").strip().lower()
            if choice == 'y':
                profile_dir = "Profile 1"
            else:
                input("Close Chrome and press Enter to continue...")
        
        if os.path.exists(user_data_dir):
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            chrome_options.add_argument(f"--profile-directory={profile_dir}")
            print(f"[OK] Using Chrome profile: {profile_dir}")
        
        # Other options to make it look like a real browser
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        
        # Remove automation flags
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("\n" + "="*60)
            print("[OK] Browser opened successfully!")
            print("="*60)
            print("\nYou can now:")
            print("- Navigate freely in the browser")
            print("- Use it like a normal Chrome browser")
            print("- Your session and cookies are preserved")
            print("\nThe browser will stay open even after the script ends.")
            print("="*60 + "\n")
        except Exception as e:
            print(f"[ERROR] Failed to open browser: {e}")
            print("\nTrying alternative method...")
            # Try without user profile
            chrome_options = Options()
            chrome_options.add_experimental_option("detach", True)
            chrome_options.add_argument("--start-maximized")
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("[OK] Browser opened (without user profile)")
            except:
                raise
    
    def navigate_to(self, url):
        """Navigate to a URL."""
        print(f"Navigating to: {url}")
        self.driver.get(url)
        time.sleep(2)
        print("[OK] Page loaded")
    
    def wait_for_user(self, message="Press Enter in the terminal when you're ready to continue..."):
        """Wait for user input in terminal."""
        input(f"\n{message}")
    
    def select_elements_interactive(self):
        """
        Interactive element selection mode.
        User can click on elements in the browser and they will be added to selectors.
        """
        print("\n" + "="*60)
        print("INTERACTIVE ELEMENT SELECTOR")
        print("="*60)
        print("\nInstructions:")
        print("1. The browser is now open and you can navigate manually")
        print("2. When you see an element you want to scrape, note its:")
        print("   - Text content")
        print("   - CSS class or ID")
        print("   - XPath (right-click > Inspect > Copy XPath)")
        print("3. Come back here to add selectors")
        print("\nOptions:")
        print("1. Add property link selector")
        print("2. Add detail page selector")
        print("3. View current workflow")
        print("4. Test selectors on current page")
        print("5. Start scraping with current workflow")
        print("6. Save workflow")
        print("7. Load workflow")
        print("0. Exit")
        
        while True:
            choice = input("\nYour choice: ").strip()
            
            if choice == "1":
                self.add_property_selector()
            elif choice == "2":
                self.add_detail_selector()
            elif choice == "3":
                self.view_workflow()
            elif choice == "4":
                self.test_selectors()
            elif choice == "5":
                self.start_scraping()
            elif choice == "6":
                self.save_workflow()
            elif choice == "7":
                self.load_workflow()
            elif choice == "0":
                break
            else:
                print("Invalid choice. Please try again.")
    
    def add_property_selector(self):
        """Add a selector for property links."""
        print("\n--- Add Property Link Selector ---")
        print("Selectors can be:")
        print("- CSS selector (e.g., 'a.property-link')")
        print("- XPath (e.g., '//a[@class='property-link']')")
        print("- Class name (e.g., '.card__title-link')")
        
        selector_type = input("Selector type (css/xpath/class/id): ").strip().lower()
        selector_value = input("Selector value: ").strip()
        attribute = input("Attribute to extract (href/text/class, default: href): ").strip() or "href"
        
        self.workflow['property_selectors'].append({
            'type': selector_type,
            'value': selector_value,
            'attribute': attribute
        })
        print(f"[OK] Added property selector: {selector_type}='{selector_value}'")
    
    def add_detail_selector(self):
        """Add a selector for detail page elements."""
        print("\n--- Add Detail Page Selector ---")
        field_name = input("Field name (e.g., 'price', 'bedrooms'): ").strip()
        selector_type = input("Selector type (css/xpath/class/id): ").strip().lower()
        selector_value = input("Selector value: ").strip()
        attribute = input("Attribute to extract (text/class/id, default: text): ").strip() or "text"
        
        self.workflow['detail_selectors'][field_name] = {
            'type': selector_type,
            'value': selector_value,
            'attribute': attribute
        }
        print(f"[OK] Added detail selector for '{field_name}'")
    
    def view_workflow(self):
        """Display current workflow."""
        print("\n" + "="*60)
        print("CURRENT WORKFLOW")
        print("="*60)
        print(f"\nBase URLs: {len(self.workflow['base_urls'])}")
        for url in self.workflow['base_urls']:
            print(f"  - {url}")
        
        print(f"\nProperty Selectors: {len(self.workflow['property_selectors'])}")
        for i, sel in enumerate(self.workflow['property_selectors'], 1):
            print(f"  {i}. {sel['type']}='{sel['value']}' -> {sel['attribute']}")
        
        print(f"\nDetail Selectors: {len(self.workflow['detail_selectors'])}")
        for field, sel in self.workflow['detail_selectors'].items():
            print(f"  - {field}: {sel['type']}='{sel['value']}' -> {sel['attribute']}")
        print("="*60)
    
    def test_selectors(self):
        """Test selectors on the current page."""
        print("\n--- Testing Selectors on Current Page ---")
        current_url = self.driver.current_url
        print(f"Current URL: {current_url}")
        
        # Test property selectors
        if self.workflow['property_selectors']:
            print("\nTesting Property Selectors:")
            for i, sel in enumerate(self.workflow['property_selectors'], 1):
                try:
                    elements = self.find_elements(sel['type'], sel['value'])
                    print(f"  {i}. Found {len(elements)} elements")
                    if elements:
                        value = self.extract_attribute(elements[0], sel['attribute'])
                        print(f"     First value: {value[:100] if value else 'None'}")
                except Exception as e:
                    print(f"  {i}. Error: {e}")
        
        # Test detail selectors
        if self.workflow['detail_selectors']:
            print("\nTesting Detail Selectors:")
            for field, sel in self.workflow['detail_selectors'].items():
                try:
                    elements = self.find_elements(sel['type'], sel['value'])
                    if elements:
                        value = self.extract_attribute(elements[0], sel['attribute'])
                        print(f"  {field}: {value[:100] if value else 'None'}")
                    else:
                        print(f"  {field}: Not found")
                except Exception as e:
                    print(f"  {field}: Error - {e}")
    
    def find_elements(self, selector_type, selector_value):
        """Find elements using different selector types."""
        if selector_type == 'css':
            return self.driver.find_elements(By.CSS_SELECTOR, selector_value)
        elif selector_type == 'xpath':
            return self.driver.find_elements(By.XPATH, selector_value)
        elif selector_type == 'class':
            return self.driver.find_elements(By.CLASS_NAME, selector_value)
        elif selector_type == 'id':
            return self.driver.find_elements(By.ID, selector_value)
        else:
            raise ValueError(f"Unknown selector type: {selector_type}")
    
    def extract_attribute(self, element, attribute):
        """Extract attribute from element."""
        if attribute == 'text':
            return element.text
        elif attribute == 'href':
            return element.get_attribute('href')
        else:
            return element.get_attribute(attribute)
    
    def start_scraping(self):
        """Start scraping with the current workflow."""
        if not self.workflow['property_selectors']:
            print("[ERROR] No property selectors defined!")
            return
        
        print("\n" + "="*60)
        print("STARTING SCRAPING")
        print("="*60)
        
        # Get base URLs
        if not self.workflow['base_urls']:
            print("\nNo base URLs in workflow. Using current page as starting point.")
            self.workflow['base_urls'] = [self.driver.current_url]
        
        all_properties = []
        
        for base_url in self.workflow['base_urls']:
            print(f"\nProcessing: {base_url}")
            self.driver.get(base_url)
            time.sleep(2)
            
            # Find all property links
            property_urls = set()
            for sel in self.workflow['property_selectors']:
                try:
                    elements = self.find_elements(sel['type'], sel['value'])
                    for elem in elements:
                        url = self.extract_attribute(elem, sel['attribute'])
                        if url and 'immoweb.be' in url:
                            if url.startswith('/'):
                                url = f"https://www.immoweb.be{url}"
                            property_urls.add(url)
                except Exception as e:
                    print(f"  Error with selector {sel['value']}: {e}")
            
            print(f"  Found {len(property_urls)} property URLs")
            
            # Scrape each property
            for i, prop_url in enumerate(property_urls, 1):
                print(f"\n  [{i}/{len(property_urls)}] Scraping: {prop_url}")
                try:
                    self.driver.get(prop_url)
                    time.sleep(1)
                    
                    property_data = {'url': prop_url}
                    for field, sel in self.workflow['detail_selectors'].items():
                        try:
                            elements = self.find_elements(sel['type'], sel['value'])
                            if elements:
                                value = self.extract_attribute(elements[0], sel['attribute'])
                                property_data[field] = value
                            else:
                                property_data[field] = None
                        except:
                            property_data[field] = None
                    
                    all_properties.append(property_data)
                    print(f"    Extracted: {list(property_data.keys())}")
                    
                except Exception as e:
                    print(f"    Error: {e}")
        
        self.workflow['extracted_data'] = all_properties
        print(f"\n[OK] Scraping complete! Extracted {len(all_properties)} properties.")
        
        # Save results
        self.save_results()
    
    def save_workflow(self):
        """Save workflow to JSON file."""
        filename = input("Workflow filename (default: workflow.json): ").strip() or "workflow.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.workflow, f, indent=2, ensure_ascii=False)
        print(f"[OK] Workflow saved to {filename}")
    
    def load_workflow(self):
        """Load workflow from JSON file."""
        filename = input("Workflow filename (default: workflow.json): ").strip() or "workflow.json"
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                self.workflow = json.load(f)
            print(f"[OK] Workflow loaded from {filename}")
            self.view_workflow()
        except FileNotFoundError:
            print(f"[ERROR] File {filename} not found")
        except Exception as e:
            print(f"[ERROR] Failed to load workflow: {e}")
    
    def save_results(self):
        """Save extracted data to JSON and CSV."""
        import pandas as pd
        
        if not self.workflow['extracted_data']:
            print("[WARNING] No data to save")
            return
        
        # Save as JSON
        json_file = "scraped_data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.workflow['extracted_data'], f, indent=2, ensure_ascii=False)
        print(f"[OK] Data saved to {json_file}")
        
        # Save as CSV
        try:
            df = pd.DataFrame(self.workflow['extracted_data'])
            csv_file = "scraped_data.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"[OK] Data saved to {csv_file}")
        except Exception as e:
            print(f"[WARNING] Failed to save CSV: {e}")
    
    def close(self):
        """Close the browser."""
        if self.driver:
            print("\nClosing browser...")
            self.driver.quit()
            print("[OK] Browser closed")


def main():
    """Main function to run interactive scraper."""
    print("="*60)
    print("INTERACTIVE IMMOWEB SCRAPER")
    print("="*60)
    print("\nThis tool opens a REAL Chrome browser that you can use normally.")
    print("You can navigate, click, search - do everything you want!")
    print("\nThe browser will:")
    print("- Use your Chrome profile (your bookmarks, history, cookies)")
    print("- Stay open even after the script ends")
    print("- Work exactly like normal Chrome")
    print("\nPress Enter to open the browser or Ctrl+C to cancel...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\nCancelled.")
        return
    
    scraper = InteractiveImmowebScraper()
    
    try:
        # Navigate to Immoweb
        print("\nOpening Immoweb in the browser...")
        scraper.navigate_to("https://www.immoweb.be")
        
        print("\n" + "="*60)
        print("BROWSER IS NOW OPEN - YOU CAN USE IT NORMALLY!")
        print("="*60)
        print("\nThe Chrome window is open. You can:")
        print("- Navigate anywhere you want")
        print("- Search for properties")
        print("- Click on links")
        print("- Do everything you normally do in Chrome")
        print("\nWhen you're ready to create a scraping workflow,")
        print("come back here and use the menu below.")
        print("\n" + "="*60)
        
        # Give user time to see the browser
        time.sleep(2)
        
        # Start interactive mode
        scraper.select_elements_interactive()
        
    except KeyboardInterrupt:
        print("\n\nScript interrupted. Browser will stay open.")
        print("You can continue using it normally.")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        print("\nBrowser will stay open. You can continue using it.")
    finally:
        # Don't close the browser - let user close it manually
        print("\n" + "="*60)
        print("Script finished. Browser will stay open.")
        print("Close it manually when you're done.")
        print("="*60)
        # scraper.close()  # Commented out - let browser stay open


if __name__ == "__main__":
    main()

