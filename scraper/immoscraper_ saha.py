from time import perf_counter
import json
import asyncio
from bs4 import BeautifulSoup
import aiohttp
import pandas as pd



class ImmoCrawler():
    """
    A web scraper class for collecting real estate data from Immoweb.
    """
    def __init__(self) -> None:
        """
        Initializes the ImmoCrawler class.
        """
        self.base_url = "https://www.immoweb.be/en/search/house-and-apartment/for-sale/"
        self.links = []
        self.property_data = {}
        self.property_key = 0
        self.links_counter = 0
        self.regions = ["west-flanders", "east-flanders", "antwerp", "brussels", "walloon-brabant", "limburg", "liege", "luxembourg", "namur", "hainaut", "flemish-brabant"]
        self.provinces = ["West Flanders", "East Flanders", "Antwerp", "Brussels", "Walloon Brabant", "Limburg", "Liege", "Luxembourg", "Namur", "Hainaut", "Flemish Brabant"]
        self.filters_url = "/province?countries=BE&isALifeAnnuitySale=false&orderBy=postal_code&page="
        self.unique_links = set()
        self.page_counter = 0  # Initialize page_counter here


    async def load_json_async(self, json_str):
        """
        Asynchronously loads JSON data from a string.

        Parameters
        ----------
        json_str : str
            JSON string to be loaded asynchronously.

        Returns
        -------
        dict
            Parsed JSON data.
        """
        return await asyncio.to_thread(json.loads, json_str)


    async def crawl_page(self, session, region, page, semaphore):
        """
        Asynchronously crawls a page to extract property links and data.

        Parameters
        ----------
        session : aiohttp.ClientSession
            The aiohttp session for making asynchronous requests.
        region : str
            The region to crawl.
        page : int
            The page number to crawl.
        semaphore : asyncio.Semaphore
            Semaphore for controlling the number of concurrent requests.

        Returns
        -------
        None
        """
        async with semaphore:
        

                try:
                    # Asynchronously fetch the HTML content of the page
                    async with session.get(f"{self.base_url}{region}{self.filters_url}{page}") as response:
                        response.raise_for_status()
                        html = await response.text()
                        r = BeautifulSoup(html, "html.parser")
                        properties = r.find_all("a", attrs={"class": "card__title-link"})
                        self.page_counter = len(properties) * page
                        print(f"\033[95mProvince: {region} -------> Page: {page}\033[0m")

                        # Iterate over each property link on the page
                        for property in properties: 
                                href = property.get("href")
                                
                                # Check if it is the new project of real estate 
                                if "new-real-estate-project-apartments" in href or "new-real-estate-project-houses" in href:
                                    # Extract links from sub-properties 
                                    async with session.get(f"{href}") as response:
                                        html = await response.text()
                                        r = BeautifulSoup(html, "html.parser")
                                        sub_properties = r.find_all("a", attrs={"class":"classified__list-item-link"})

                                        for sub_property in sub_properties:
                                            sub_href = sub_property.get("href")
                                            if sub_href not in self.unique_links:
                                                self.links_counter += 1
                                                self.links.append(sub_href)
                                                self.unique_links.add(sub_href)
                                                self.property_key += 1
                                                print(f"Grabbing Links & Extracting Data: {self.property_key}")
                                                await self.get_data(session, sub_href, region)

                                elif href not in self.unique_links:
                                    self.links_counter += 1
                                    self.unique_links.add(href)
                                    self.links.append(href)
                                    self.property_key += 1
                                    print(f"Grabbing Links & Extracting Data: {self.property_key}")
                                    await self.get_data(session, href, region)

                        
                except Exception as error:
                    print(f"Error in thread for page {page}: {error}")


    async def get_data(self, session, url, region):
        """
        Asynchronously fetches and extracts property data from a given URL.

        Parameters
        ----------
        session : aiohttp.ClientSession
            The aiohttp session for making asynchronous requests.
        url : str
            The URL of the property.
        region : str
            The region associated with the property.

        Returns
        -------
        dict or None
            Extracted property data if the property is in Belgium; otherwise, None.
        """
        try:
            async with session.get(url) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                scripts = soup.find_all("script", attrs={"type": "text/javascript"})
                
                classified_script = None
                # Find the script containing window.classified
                for script in scripts:
                    if "window.classified" in script.get_text():
                        classified_script = script
                        break
                    
                
                if classified_script is None:
                    print(f"Error: 'classified_script' not found in {url}")
                    return None
                # Extract the text content of the script tag
                script_content = classified_script.get_text()
            
                # Use string manipulation to extract the window.classified object
                json_str = script_content[script_content.find('{'):script_content.rfind('}') + 1]
                if json_str is not None:
                # Load the JSON data
                    try:
                        
                        data = await self.load_json_async(json_str)

                        
                        
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                        raise ValueError("Invalid JSON string") from e
                else:
                    print("JSON_STR IS NONE")

                def multi_get(dict_obj, *attrs, default=None):
                    result = dict_obj
                    for attr in attrs:
                        if not result or attr not in result:
                            return default
                        result = result[attr]
                    return result
                
                
                if multi_get(data,'property','location', 'country') == "Belgium": 

                        # Extract relevant property data
                     self.property_data[self.property_key] = {
                            "link": url,
                            "id": data.get('id',None),
                            "locality": multi_get(data,'property','location','district'),
                            "country": multi_get(data,'property','location', 'country'),
                            "construction_year": multi_get(data,'property','building','constructionYear'),
                            "Number_of_frontages": multi_get(data,'property','building','facadeCount'),
                            "province": multi_get(data,'property','location', 'province'),
                            "zip_code":multi_get(data,'property','location','postalCode'),
                            "price": multi_get(data,'transaction','sale','price'),
                            "property_type": multi_get(data,'property','type'),
                            "subproperty_type": multi_get(data,'property','subtype'),
                            "bedroom_count": multi_get(data,'property','bedroomCount'),
                            "total_area_m2": multi_get(data,'property','netHabitableSurface'),
                            "equipped_kitchen": multi_get(data,'property','kitchen','type') ,
                            "furnished": 1 if multi_get(data,'transaction','sale','isFurnished') else 0,
                            "open_fire": 1 if multi_get(data, 'property', 'fireplaceExists') else 0,
                            "terrace_sqm": multi_get(data,'property','terraceSurface') if data['property']['hasTerrace'] else 0,
                            "terrace": 1 if data['property']['hasTerrace'] else 0,
                            "garden_sqm": multi_get(data,'property','gardenSurface') if data['property']['hasGarden'] else 0,
                            "garden": 1 if data['property']['hasGarden'] else 0,
                            'floodZoneType':1 if multi_get(data,'property','constructionPermit', 'floodZoneType')!= "NON_FLOOD_ZONE" else 0,
                            "surface_land": multi_get(data,'property','land','surface'),
                            "swimming_pool": 1 if multi_get(data,'property','hasSwimmingPool') else 0,
                            "state_building": multi_get(data,'property','building','condition'),
                            "epc": multi_get(data,'transaction','certificates','epcScore'),
                            "primaryEnergyConsumptionPerSqm": multi_get(data,'transaction','certificates','primaryEnergyConsumptionPerSqm'),
                            "heating_Type": multi_get(data,'property','energy', 'heatingType'),
                            "Double_Glazing": 1 if multi_get(data,'property','energy', 'hasDoubleGlazing') else 0,
                            "cadastral_income": multi_get(data,'transaction','sale','cadastralIncome'),
                            "latitude": multi_get(data,'property','location','latitude'),
                            "longitude":multi_get(data,'property','location','longitude'),
                            "public_sales":  multi_get(data,'flag','isPublicSale'), 
                            "notary_sales":  multi_get(data,'flag','isNotarySale'),
                            }
            
            
                return self.property_data[self.property_key]
                    
        except Exception as error:
            print(f"Error in gathering data from {url}: {error}") 

    async def get_properties(self, num_pages=333):
        """
        Asynchronously fetches and extracts property data from multiple pages.

        Parameters
        ----------
        num_pages : int, optional
            The number of pages to crawl, by default 333.

        Returns
        -------
        None
        """
        start_time = perf_counter()
        
        # Adjust the semaphore count based on server limits
        semaphore = asyncio.Semaphore(10)  
        async with aiohttp.ClientSession() as session:
                for region in self.regions:

                    tasks = [self.crawl_page(session, region, page, semaphore) for page in range(1, num_pages + 1)]
                    await asyncio.gather(*tasks)
                    print(f"finished with {region}")

        print(f"Took {perf_counter() - start_time}")
        
        

    
    def to_csv(self, name):
        """
        Convert the collected property data to a CSV file.

        Parameters
        ----------
        name : str
            The name of the CSV file (without extension).

        Returns
        -------
        None
        """

        df = pd.DataFrame.from_dict(self.property_data, orient="index")
        df.to_csv(name + '.csv')