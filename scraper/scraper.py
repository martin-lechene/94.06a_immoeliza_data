from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import random
import browser_cookie3


class Immoweb_Scraper:
    """
    A class for scraping data from the Immoweb website.
    """

    def __init__(self, numpages) -> None:
        """
        Initialize the Immoweb_Scraper object.
        
        Args:
        - numpages (int): Number of pages to scrape.
        """
        self.base_urls_list = []
        self.immoweb_urls_list = []
        self.element_list = ["Construction year","Bedrooms","Living area","Kitchen type","Furnished","Terrace surface",
                "Surface of the plot","Garden surface","Number of frontages","Swimming pool","Building condition",
                "Energy class","Tenement building","Flood zone type","Double glazing","Heating type","Bathrooms",
                "Elevator","Accessible for disabled people","Outdoor parking spaces","Covered parking spaces","Shower rooms"]
        self.data_set = []
        self.numpages = numpages
        self.session = requests.Session()
        
        # Load cookies from Chrome browser
        self._load_browser_cookies()
        
        # Set realistic headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8,nl;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1',
            'Referer': 'https://www.immoweb.be/',
        })
        
        # Visit homepage first to get cookies and establish session
        self._establish_session()
    
    def _load_browser_cookies(self):
        """
        Load cookies from Chrome browser to make requests look more authentic.
        """
        try:
            # Try to load cookies from Chrome
            chrome_cookies = browser_cookie3.chrome(domain_name='immoweb.be')
            cookie_dict = {}
            for cookie in chrome_cookies:
                cookie_dict[cookie.name] = cookie.value
                self.session.cookies.set(cookie.name, cookie.value, domain=cookie.domain)
            
            if cookie_dict:
                print(f"Loaded {len(cookie_dict)} cookies from Chrome browser")
            else:
                print("No Chrome cookies found for immoweb.be, using session cookies")
        except Exception as e:
            print(f"Could not load Chrome cookies: {e}")
            print("Continuing with session cookies only")
    
    def _establish_session(self):
        """
        Visit the homepage to establish a session and get initial cookies.
        """
        try:
            print("Establishing session with Immoweb...")
            response = self.session.get('https://www.immoweb.be', timeout=15, allow_redirects=True)
            if response.status_code == 200:
                print("Session established successfully")
                # Wait a bit to simulate human behavior
                time.sleep(random.uniform(2, 4))
            else:
                print(f"Warning: Homepage returned status {response.status_code}")
        except Exception as e:
            print(f"Warning: Could not establish session: {e}")
            print("Continuing anyway...")

    def get_base_urls(self):
        """
        Get the list of base URLs after applying the filter.
        
        Returns:
        - list: List of base URLs.
        """
        for i in range(1, self.numpages):
            base_url_house = f"https://www.immoweb.be/en/search/house/for-sale?countries=BE&isALifeAnnuitySale=false&page={i}&orderBy=relevance"
            base_url_apartment = f"https://www.immoweb.be/en/search/apartment/for-sale?countries=BE&isALifeAnnuitySale=false&page={i}&orderBy=relevance"
            self.base_urls_list.append(base_url_house)
            self.base_urls_list.append(base_url_apartment)
        print(f'Number of Base URLs generated: {len(self.base_urls_list)}')
        return list(set(self.base_urls_list))

    def get_immoweb_url(self, url):
        """
        Gets the list of Immoweb URLs from each page of base URLs.

        Args:
        - url (str): Base URL to scrape.

        Returns:
        - list: List of Immoweb URLs.
        """
        # Add random delay to appear more human-like (longer delay for first requests)
        time.sleep(random.uniform(2, 5))
        
        max_retries = 3
        url_content = None
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=15, allow_redirects=True)
                
                # Check if we got blocked
                if response.status_code == 403:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5 + random.uniform(2, 5)
                        print(f"Got 403 for {url}, waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"Error accessing {url}: 403 Forbidden (blocked after {max_retries} attempts)")
                        return []
                
                response.raise_for_status()
                url_content = response.content
                break
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3 + random.uniform(1, 3)
                    print(f"Error accessing {url} (attempt {attempt + 1}/{max_retries}): {e}, retrying in {wait_time:.1f}s")
                    time.sleep(wait_time)
                else:
                    print(f"Error accessing {url}: {e} (failed after {max_retries} attempts)")
                    return []
        
        # If we couldn't get the content, return empty list
        if url_content is None:
            return []

        lst = []
        soup = BeautifulSoup(url_content, "lxml")
        
        # Try multiple selectors to find property links
        selectors = [
            ("a", {"class": "card__title-link"}),
            ("a", {"class": "card-title-link"}),
            ("a", {"class": "search-result__title-link"}),
            ("a", {"class": "property-link"}),
            ("a", {"class": lambda x: x and "card" in x.lower() and "link" in x.lower()}),
        ]
        
        # First, try finding links by href pattern (most reliable method)
        for tag in soup.find_all("a", href=True):
            href = tag.get("href", "")
            if not href:
                continue
                
            # Normalize href
            if href.startswith("/"):
                href = f"https://www.immoweb.be{href}"
            elif not href.startswith("http"):
                continue
                
            # Check if it's a property URL
            if ("www.immoweb.be" in href or "immoweb.be" in href) and \
               ("/property/" in href or "/en/classified/" in href or "/fr/classified/" in href or "/nl/classified/" in href) and \
               "new-real-estate-project" not in href:
                lst.append(href)
        
        # Try the specific class selectors
        for tag_name, attrs in selectors:
            try:
                for tag in soup.find_all(tag_name, attrs=attrs):
                    immoweb_url = tag.get("href")
                    if immoweb_url:
                        if immoweb_url.startswith("/"):
                            immoweb_url = f"https://www.immoweb.be{immoweb_url}"
                        if ("www.immoweb.be" in immoweb_url or "immoweb.be" in immoweb_url) and \
                           "new-real-estate-project" not in immoweb_url:
                            lst.append(immoweb_url)
            except Exception as e:
                # Skip if selector fails
                continue

        # Ensure only unique URLs are returned
        unique_urls = list(set(lst))
        if unique_urls:
            print(f"Found {len(unique_urls)} URLs from {url}")
        else:
            print(f"Warning: No URLs found from {url}. The page structure may have changed.")
        return unique_urls

    def get_immoweb_urls_thread(self):
        self.base_urls_list = self.get_base_urls()
        # Use sequential requests instead of threading to avoid being blocked
        # Immoweb seems to block concurrent requests
        print('Generating urls (sequential mode to avoid blocking)')
        for url in self.base_urls_list:
            result = self.get_immoweb_url(url)
            if result:
                print(f"Found {len(result)} URLs from page")
            self.immoweb_urls_list.extend(result)
        print(f"Total URLs collected: {len(self.immoweb_urls_list)}")
        return self.immoweb_urls_list

    def create_soup_thread(self):
        print('Creating Soups')
        self.c=0
        self.soups = []
        self.immoweb_urls_list = self.get_immoweb_urls_thread()
        
        if not self.immoweb_urls_list:
            print("No URLs to process. Skipping soup creation.")
            return []
        
        # Use sequential requests instead of threading to avoid being blocked
        print('Creating soups (sequential mode to avoid blocking)')
        for url in self.immoweb_urls_list:
            soup = self.create_soup(url, self.session)
            if soup is not None:
                self.soups.append(soup)
        print(f"Created {len(self.soups)} soup objects out of {len(self.immoweb_urls_list)} URLs")
        return self.soups
    
    def create_soup(self, url, session):
        self.c += 1
        print(f'{self.c} Soup objects created')
        # Add random delay to appear more human-like
        time.sleep(random.uniform(0.5, 2))
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = session.get(url, timeout=15, allow_redirects=True)
                
                # Check if we got blocked
                if response.status_code == 403:
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 5 + random.uniform(2, 5)
                        print(f"Got 403 for {url}, waiting {wait_time:.1f}s before retry {attempt + 1}/{max_retries}")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"Error accessing {url}: 403 Forbidden (blocked after {max_retries} attempts)")
                        return None
                
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "lxml")
                return soup
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 3 + random.uniform(1, 3)
                    print(f"Error accessing {url} (attempt {attempt + 1}/{max_retries}): {e}, retrying in {wait_time:.1f}s")
                    time.sleep(wait_time)
                else:
                    print(f"Error accessing {url}: {e} (failed after {max_retries} attempts)")
                    return None

    def scrape_table_dataset(self):
        """
        Scrape data from Immoweb URLs.
        
        Returns:
        - list: List of dictionaries containing scraped data.
        """
        self.soups = self.create_soup_thread()
        # Filter out None soups and corresponding URLs
        valid_pairs = [(url, soup) for url, soup in zip(self.immoweb_urls_list, self.soups) if soup is not None]
        if not valid_pairs:
            print("No valid soups to process")
            return self.data_set
        
        # Use sequential processing to avoid being blocked
        print('Scraping in progress (sequential mode)')
        for url, soup in valid_pairs:
            result = self.process_url(url, soup)
            if result and result not in self.data_set:  # Check for duplicates before appending
                self.data_set.append(result)
        print(f"Scraped {len(self.data_set)} properties")
        return self.data_set

    def process_url(self, each_url, soup):
        """
        Process each URL to scrape data.
        
        Args:
        - each_url (str): URL to scrape.
        - soup: BeautifulSoup object for the URL.
        
        Returns:
        - dict: Dictionary containing scraped data.
        """
        if soup is None:
            return None
        data_dict = {}
        data_dict["url"] = each_url
        data_dict["Property ID"], data_dict["Locality name"], data_dict["Postal code"], data_dict[
            "Subtype of property"] = each_url.split('/')[-1], each_url.split('/')[-3], each_url.split('/')[-2], \
                                    each_url.split('/')[-5]
        print(each_url)
        try:
            for tag in soup.find("div", attrs={"id": "classified-description-content-text"}).find_all("p"):
                if any(keyword in tag.text.lower() for keyword in ["open haard", "cheminée", "feu ouvert", "open fire"]):
                    data_dict["Open Fire"] = 1
                else:
                    data_dict["Open Fire"] = 0
        except:
            data_dict["Open Fire"] = 0
        
        try:    
            price_tag = soup.find("p", attrs={"class": "classified__price"})
            if price_tag and price_tag.text.startswith("€"):
                data_dict["Price"] = price_tag.text.split(' ')[0][1:].replace(',', '')  # Drop commas from price
            else:
                data_dict["Price"] = 0
        except: 
            data_dict["Price"] = 0
        
        for tag in soup.find_all("tr"):
            for tag1 in tag.find_all("th", attrs={"class": "classified-table__header"}):
                if tag1.string is not None:
                    for element in self.element_list:
                        if element == tag1.string.strip():
                            tag_text = str(tag.td).strip().replace("\n", "").replace(" ", "")
                            start_loc = tag_text.find('>')
                            end_loc = tag_text.find('<', tag_text.find('<') + 1)
                            data_dict[element] = tag_text[start_loc + 1:end_loc]
        return data_dict

    def update_dataset(self):
        """
        Missing information on webpage is populated as 0
        Example : If the information regarding swimming pool is not on webpage then
        in the dataset Swimming pull will be updated to 0
        """
        for each_dict in self.data_set:
            dict_elem = []
            for each_element in each_dict:
                dict_elem.append(each_element)
            for each_value in self.element_list:
                if each_value not in dict_elem:
                    each_dict[each_value] = None
        return self.data_set

    def Raw_DataFrame(self):
        """ 
        Convert the data_set list of dict into a DataFrame 
        """
        self.data_set_df = pd.DataFrame(self.data_set)
        return self.data_set_df

    def to_csv_raw(self):
        """ 
        Convert the data_set DataFrame into CSV 
        """
        if len(self.data_set) == 0:
            print('Warning: No data to save. Creating empty CSV file.')
            # Create empty DataFrame with expected columns
            empty_df = pd.DataFrame(columns=["url", "Property ID", "Locality name", "Postal code", "Subtype of property", "Open Fire", "Price"] + self.element_list)
            empty_df.to_csv('data/raw_data/data_set_RAW.csv', index=False)
        else:
            self.data_set_df.to_csv('data/raw_data/data_set_RAW.csv', index=False)
        print('A .csv file called "data_set_RAW.csv" has been generated. ')


    def Clean_DataFrame(self):
        """
        Allow to convert the data_set list of dict in a DataFrame
        Allow to clean the DataFrame (inner aggregation, conversion, renaming )

        """
        import os
        csv_path = "data/raw_data/data_set_RAW.csv"
        
        # Check if file exists and is not empty
        if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
            print("Warning: No data to clean. The raw data file is empty or does not exist.")
            self.data_set_df = pd.DataFrame()
            return self.data_set_df
        
        try:
            self.data_set_df = pd.read_csv(csv_path, delimiter=',')
            
            # Check if DataFrame is empty
            if len(self.data_set_df) == 0:
                print("Warning: The raw data file is empty. Nothing to clean.")
                return self.data_set_df
                
            print(self.data_set_df.head())
            print(f"Number of rows before cleaning: {len(self.data_set_df)}")
        except pd.errors.EmptyDataError:
            print("Warning: The raw data file is empty. Nothing to clean.")
            self.data_set_df = pd.DataFrame()
            return self.data_set_df
        
        # Check if DataFrame is empty after reading
        if len(self.data_set_df) == 0:
            print("Warning: No data to clean. The DataFrame is empty.")
            return self.data_set_df
        
        #drop duplicate based of property id
        if 'Property ID' in self.data_set_df.columns:
            self.data_set_df = self.data_set_df.drop_duplicates(subset=['Property ID'])
        else:
            print("Warning: 'Property ID' column not found. Skipping duplicate removal.")
      
     

        # suppress wrong postal code
        if 'Postal code' in self.data_set_df.columns:
            condition_to_delete = self.data_set_df['Postal code'].astype(str).str.len() < 5
            #condition_to_delete = ((self.data_set_df['Postal code'].str.contains('%')) | (len(self.data_set_df['Postal code']) > 4))
            #condition_to_delete = (self.data_set_df['Postal code'].astype(str).str.isdigit()) | (self.data_set_df['Postal code'].astype(str).str.len() > 4)

            self.data_set_df = self.data_set_df[~condition_to_delete]  # Keep rows where postal code length >= 5
            self.data_set_df = self.data_set_df.reset_index(drop=True)
        else:
            print("Warning: 'Postal code' column not found. Skipping postal code filtering.")
      
        

        # replacements of ugly pattern
        if 'Locality name' in self.data_set_df.columns:
            patterns_to_search = [re.escape('?'), '%C3%8B','%28','%29', '%27','%20', '%C3%A8', '%C3%8A', '%C3%AA', '%C3%88', '%C3%89', '%C3%A9', '%C3%A0', '%C3%A2', '%C3%82', '%C3%80','%C3%BB']
            replacements = [' ', 'e','','',' ', ' ', 'e', 'e','e', 'e','e', 'e', 'a', 'a', 'a','a', 'u', ]
            for pattern, replacement in zip(patterns_to_search, replacements):
                condition_to_replace = self.data_set_df['Locality name'].str.contains(pattern, na=False)
                self.data_set_df.loc[condition_to_replace, 'Locality name'] = self.data_set_df.loc[condition_to_replace, 'Locality name'].str.replace(pattern, replacement)
        else:
            print("Warning: 'Locality name' column not found. Skipping pattern replacement.")
     



        #to convert the Price in a number format 
        self.data_set_df["Price"] = self.data_set_df["Price"].astype(str).str.replace(",", "")

        
        
        #to ensure that numeric to be column are containing numeric data
        col_to_conv = [
            "Property ID",
            "Postal code",
            "Open Fire",
            "Price",
            "Construction year",
            "Number of frontages",
            "Covered parking spaces",
            "Outdoor parking spaces",
            "Living area",
            "Bedrooms",
            "Bathrooms",
            "Surface of the plot",
            "Garden surface",
            "Terrace surface",
            "Shower rooms",
        ]
        for col in col_to_conv:
            if col in self.data_set_df.columns:
                
                self.data_set_df[col] = pd.to_numeric(self.data_set_df[col], downcast='integer', errors='coerce')
        

        #appartment or house classification creation
        self.data_set_df["Type of property"] = self.data_set_df[
            "Subtype of property"
        ].apply(
            lambda x: None
            if pd.isnull(x)
            else (
                "Apartment"
                if x
                in [
                    "apartment",
                    "loft",
                    "penthouse",
                    "duplex",
                    "ground-floor",
                    "flat-studio",
                    "service-flat",
                    "kot",
                    "triplex",
                ]
                else "House"
            )
        )


        #New columns creation (arithmetic or spatial aggregation)
        self.data_set_df["Parking tot nb"] = (self.data_set_df["Covered parking spaces"].fillna(0) + self.data_set_df["Outdoor parking spaces"].fillna(0))
        self.data_set_df["Bathrooms total nb"] = (self.data_set_df["Bathrooms"].fillna(0) + self.data_set_df["Shower rooms"].fillna(0))

        def province(dfval):
            if pd.isna(dfval):
                return None
            postal_codes = [range(1000,1300), range(1300, 1500), range(1500,1990), range(3000,3500), range(2000,3000), range(3500,4000), range(4000,5000), range(5000,6000), range(6000,6600), range(7000,8000), range(6600,7000), range(8000,9000), range(9000,10000)]
            provinces = ['Brussels Hoofdstedelijk Gewest', 'Waals-Brabant', 'Vlaams-Brabant', 'Vlaams-Brabant', 'Antwerpen', 'Limburg', 'Luik', 'Namen','Henegouwen', 'Henegouwen','Luxemburg', 'West-Vlaanderen', 'Oost-Vlaanderen']
            for pc_range, prov in zip(postal_codes, provinces):
                if dfval in pc_range:
                    return prov
            return None
        self.data_set_df['province'] = self.data_set_df['Postal code'].apply(lambda x: province(x))


        def region(dfval):
            if pd.isna(dfval):
                return None
            if dfval in range(1300,1500) or dfval in range(4000,7000):
                return 'Wallonia'
            elif dfval in range(1000,1300):
                return 'Brussels'
            else:
                return 'Flanders'
        self.data_set_df['region'] = self.data_set_df['Postal code'].apply(lambda x: region(x))

        
        #quali>quanti transformatiion : to create boolean output for all columns where it is possibile 
        #through direct converion (yes/no -0/1) or through aggregation 
            

        self.data_set_df["New Construction boolean"] = self.data_set_df[
            "Construction year"
        ].apply(lambda x: None if pd.isnull(x) else (0 if x < 2021 else 1))

        self.data_set_df["Tenement building boolean"] = self.data_set_df[
            "Tenement building"
        ].apply(lambda x: None if pd.isnull(x) else (1 if x.lower() == "yes" else 0))

        self.data_set_df["Building condition boolean"] = self.data_set_df[
            "Building condition"
        ].apply(
            lambda x: None
            if pd.isnull(x)
            else (1 if x in ["Asnew", "Good", "Justrenovated"] else 0)
        )

        self.data_set_df["Flood safe boolean"] = self.data_set_df[
            "Flood zone type"
        ].apply(lambda x: None if pd.isnull(x) else (1 if x == "Nonfloodzone" else 0))

        self.data_set_df["Furnished boolean"] = self.data_set_df[
            "Furnished"
        ].apply(lambda x: None if pd.isnull(x) else (1 if x.lower() == "yes" else 0))

      
        self.data_set_df["Kitchen equipped boolean"] = self.data_set_df[
            "Kitchen type"
        ].apply(
            lambda x: None
            if pd.isnull(x)
            else (0 if x in ["Notinstalled", "USAuninstalled"] else 1)
        )

        self.data_set_df["Energy class boolean"] = self.data_set_df[
            "Energy class"
        ].apply(
            lambda x: None
            if pd.isnull(x) or x =='Notspecified'
            else (1 if x in ["A", "A+","A++", "B"] else 0)
        )
        self.data_set_df["Terrace boolean"] = self.data_set_df["Terrace surface"].apply(
            lambda x: 0 if pd.isnull(x) else (1 if x > 0 else 0)
        )

        self.data_set_df["Swimming pool boolean"] = self.data_set_df[
            "Swimming pool"
        ].apply(lambda x: None if pd.isnull(x) else (1 if x.lower() == "yes" else 0))

        self.data_set_df["Garden boolean"] = self.data_set_df["Garden surface"].apply(
            lambda x: 0 if pd.isnull(x) else (1 if x > 0 else 0)
        )
        
        self.data_set_df["Parking boolean"] = self.data_set_df["Parking tot nb"].apply(
            lambda x: None if pd.isnull(x) else (1 if x > 0 else 0)
        )
        
        self.data_set_df["Bathrooms total nb boolean"] = self.data_set_df["Bathrooms total nb"].apply(
            lambda x: None if pd.isnull(x) else (1 if x > 1 else 0)
        )

        self.data_set_df["Elevator boolean"] = self.data_set_df["Elevator"].apply(
            lambda x: None if pd.isnull(x) else (1 if x.lower() == "yes" else 0)
        )

        self.data_set_df["Accessible for disabled people boolean"] = self.data_set_df[
            "Accessible for disabled people"
        ].apply(lambda x: None if pd.isnull(x) else (1 if x.lower() == "yes" else 0))

        self.data_set_df["Double glazing boolean"] = self.data_set_df[
            "Double glazing"
        ].apply(lambda x: None if pd.isnull(x) else (1 if x.lower() == "yes" else 0))


         #text reformating in a more readable way 

        replace_dict1 = {
            "Asnew": "As new",
            "Justrenovated": "Just renovated",
            "Tobedoneup": "To be done",
            "Torenovate": "To renovate",
            "Torestore" : "To restore"
        }
        replace_dict2 = {
            "Hyperequipped": "Hyper equipped",
            "Semiequipped": "Semi equipped",
            "USAhyperequipped": "USA hyper equipped",
            "Notinstalled": "Not installed",
            "USAinstalled": "USA installed",
            "USAsemiequipped": "USA semi-equipped",
            "USAuninstalled" : "USA uninstalled"
        }
        replace_dict3 = {"Fueloil": "Fuel oil"}

        replace_dict4 = {
            "Nonfloodzone": "Non flood zone",
            "Circumscribedzone": "Circumscribed zone",
            "Possiblecircumscribedwatersidezone": "Possible circumscribed waterside zone",
            "Possiblefloodzone": "Possible flood zone",
            "Recognizedfloodzone": "Recognized flood zone",
            "Propertypartiallyorcompletelylocatedinacircumscribedandrecognizedfloodzone": "Property partially or completely located in a circumscribed and recognized flood zone",
            "Propertypartiallyorcompletelylocatedinacircumscribedfloodzone" : "Property partially or completely located in a circumscribed flood zone",
            "Propertypartiallyorcompletelylocatedinapossiblefloodzoneandlocatedinacircumscribedwatersidezone" : "Property partially or completely located in a possible flood zone and located in a circumscribed waterside zone", 
    }

        replace_dict5 = {"Notspecified": "Not specified"}

        self.data_set_df["Building condition"] = self.data_set_df[
            "Building condition"
        ].replace(replace_dict1)

        self.data_set_df["Kitchen type"] = self.data_set_df["Kitchen type"].replace(
            replace_dict2
        )
        self.data_set_df["Heating type"] = self.data_set_df["Heating type"].replace(
            replace_dict3
        )
        self.data_set_df["Flood zone type"] = self.data_set_df["Flood zone type"].replace(
            replace_dict4
        )
        self.data_set_df["Energy class"] = self.data_set_df["Energy class"].replace(
            replace_dict5
        )
        

        # column renaming for clarity

        self.data_set_df = self.data_set_df.rename(
            columns={
                "url": "URL",
                "Price": "Price (euro)",
                "Surface of the plot": "Plot surface (sqm)",
                "Open Fire": "Open fire",
                "Locality name": "Locality",
                "Subtype of property": "Subtype",
                "Living area": "Living surface (sqm)",
                "Bedrooms": "Nb of Bedrooms",
                "Terrace surface": "Terrace surface (sqm)",
                "Garden surface": "Garden surface (sqm)",
            }
        )
  
         #Column final Reordering

        new_col_order = [
            "Locality",
            "province",
            "region",
            "Postal code",
            "Type of property",
            "Subtype",
            "Price (euro)",
            "Construction year",
            "New Construction boolean",
            "Building condition boolean",
            "Building condition",
            "Energy class boolean",
            "Energy class",
            "Heating type",
            "Double glazing boolean",
            "Double glazing",
            "Elevator boolean",
            "Elevator",
            "Accessible for disabled people boolean",
            "Accessible for disabled people",
            "Living surface (sqm)",
            "Furnished boolean",
            "Furnished",
            "Nb of Bedrooms",
            "Bathrooms total nb boolean",
            "Bathrooms total nb",
            "Bathrooms",
            "Shower rooms",
            "Kitchen equipped boolean",
            "Kitchen type",
            "Open fire",
            "Number of frontages",
            "Swimming pool boolean",
            "Swimming pool",
            "Plot surface (sqm)",
            "Terrace boolean",
            "Terrace surface (sqm)",
            "Garden boolean",
            "Garden surface (sqm)",
            "Parking boolean",
            "Parking tot nb",
            "Covered parking spaces",
            "Outdoor parking spaces",
            "Flood safe boolean",
            "Flood zone type",
            "Tenement building boolean",
            "Tenement building",
            "URL",
            "Property ID",
        ]
        self.data_set_df = self.data_set_df[new_col_order]

        self.data_set_df = self.data_set_df.round(0)

        # Drop outliers

        Q75 = self.data_set_df['Price (euro)'].quantile(0.75)
        Q25 = self.data_set_df['Price (euro)'].quantile(0.25)
        iqr = Q75- Q25
        upper = Q75 + (1.5 * iqr)
        lower = Q25 - (1.5 * iqr)

        self.data_set_df = self.data_set_df[(self.data_set_df['Price (euro)'] > lower) & (self.data_set_df['Price (euro)'] < upper)]

        Q75 = self.data_set_df['Plot surface (sqm)'].quantile(0.75)
        Q25 = self.data_set_df['Plot surface (sqm)'].quantile(0.25)
        iqr = Q75- Q25
        upper = Q75 + (1.5 * iqr)
        lower = Q25 - (1.5 * iqr)

        self.data_set_df = self.data_set_df[(self.data_set_df['Plot surface (sqm)'] > lower) & (self.data_set_df['Plot surface (sqm)'] < upper)]
        self.data_set_df['Locality'] = self.data_set_df['Locality'].str.capitalize()
        self.data_set_df['Price (sqm)'] = self.data_set_df['Price (euro)'] / self.data_set_df['Living surface (sqm)']

        print(self.data_set_df.head(10))
        print("DataFrame is cleaned!")
        return self.data_set_df 


    def to_csv_clean(self):
         
        #Convert the data_set DataFrame into CSV 
        
        if len(self.data_set_df) == 0:
            print('Warning: No cleaned data to save. Creating empty CSV file.')
            # Create empty DataFrame
            empty_df = pd.DataFrame()
            empty_df.to_csv('data/clean_data/data_set_CLEAN.csv', index=False)
        else:
            self.data_set_df.to_csv('data/clean_data/data_set_CLEAN.csv', index=False)
        print('A .csv file called "data_set_CLEAN.csv" has been generated. ')
