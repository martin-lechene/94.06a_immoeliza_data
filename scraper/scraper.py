from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
import pandas as pd


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
        self.element_list = [
            "Construction year",
            "Bedrooms",
            "Living area",
            "Kitchen type",
            "Furnished",
            "Terrace surface",
            "Surface of the plot",
            "Garden surface",
            "Number of frontages",
            "Swimming pool",
            "Building condition",
            "Energy class",
            "Tenement building",
            "Flood zone type",
            "Double glazing",
            "Heating type",
            "Bathrooms",
            "Elevator",
            "Accessible for disabled people",
            "Outdoor parking spaces",
            "Covered parking spaces",
            "Shower rooms",
        ]
        self.data_set = []
        self.numpages = numpages
        self.session = requests.Session()

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
        print(f"Number of Base URLs generated: {len(self.base_urls_list)}")
        return self.base_urls_list

    def get_immoweb_urls(self, session):
        """
        Gets the list of Immoweb URLs from each page of base URLs.

        Args:
        - session (requests.Session): Session object for making HTTP requests.

        Returns:
        - list: List of Immoweb URLs.
        """
        self.session = session
        self.base_urls_list = self.get_base_urls()
        for each_url in self.base_urls_list:
            url_content = session.get(each_url).content
            soup = BeautifulSoup(url_content, "lxml")
            for tag in soup.find_all("a", attrs={"class": "card__title-link"}):
                immoweb_url = tag.get("href")
                if (
                    "www.immoweb.be" in immoweb_url
                    and "new-real-estate-project" not in immoweb_url
                ):
                    self.immoweb_urls_list.append(immoweb_url)
        self.immoweb_urls_list = list(dict.fromkeys(self.immoweb_urls_list))
        print(f"Number of Immoweb URLs generated: {len(self.immoweb_urls_list)}")
        return self.immoweb_urls_list

    def scrape_table_dataset(self):
        """
        Scrape data from Immoweb URLs.

        Returns:
        - list: List of dictionaries containing scraped data.
        """
        with requests.Session() as self.session:
            self.immoweb_urls_list = self.get_immoweb_urls(self.session)
            with ThreadPoolExecutor(max_workers=18) as executor:
                print("Scraping in progress")
                results = executor.map(self.process_url, self.immoweb_urls_list)
                for result in results:
                    self.data_set.append(result)
            return self.data_set

    def process_url(self, each_url):
        """
        Process each URL to scrape data.

        Args:
        - each_url (str): URL to scrape.

        Returns:
        - dict: Dictionary containing scraped data.
        """
        data_dict = {}
        data_dict["url"] = each_url
        (
            data_dict["Property ID"],
            data_dict["Locality name"],
            data_dict["Postal code"],
            data_dict["Subtype of property"],
        ) = (
            each_url.split("/")[-1],
            each_url.split("/")[-3],
            each_url.split("/")[-2],
            each_url.split("/")[-5],
        )
        print(each_url)
        # Scraping logic
        with requests.Session() as self.session:
            url_content = self.session.get(each_url).content
        soup = BeautifulSoup(url_content, "lxml")
        try:
            for tag in soup.find(
                "div", attrs={"id": "classified-description-content-text"}
            ).find_all("p"):
                if any(
                    keyword in tag.text.lower()
                    for keyword in ["open haard", "cheminée", "feu ouvert", "open fire"]
                ):
                    data_dict["Open Fire"] = 1
                else:
                    data_dict["Open Fire"] = 0
        except:
            data_dict["Open Fire"] = None
            # print("AttributeError: 'NoneType' object has no attribute 'find'")
        try:
            for tag in soup.find("p", attrs={"class": "classified__price"}):
                if tag.text.startswith("€"):
                    data_dict["Price"] = tag.text.split(" ")[0][1:]
        except:
            data_dict["Price"] = None
            # print("AttributeError: 'NoneType' object has no attribute 'find'")

        for tag in soup.find_all("tr"):
            for tag1 in tag.find_all("th", attrs={"class": "classified-table__header"}):
                if tag1.string is not None:
                    for element in self.element_list:
                        if element == tag1.string.strip():
                            tag_text = (
                                str(tag.td).strip().replace("\n", "").replace(" ", "")
                            )
                            start_loc = tag_text.find(">")
                            end_loc = tag_text.find("<", tag_text.find("<") + 1)
                            data_dict[element] = tag_text[start_loc + 1 : end_loc]
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
        self.data_set_df.to_csv("data/raw_data/data_set_RAW.csv", index=False)
        print('A .csv file called "data_set_RAW.csv" has been generated. ')

    def Clean_DataFrame(self):
        """
        Allow to convert the data_set list of dict in a DataFrame
        Allow to clean the DataFrame (inner aggregation, conversion, renaming )

        """
        self.data_set_df = self.Raw_DataFrame()
        self.data_set_df["Price"] = self.data_set_df["Price"].str.replace(",", "")
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
            "Open Fire",
            "Shower rooms",
        ]
        for col in col_to_conv:
            if col in self.data_set_df.columns:
                self.data_set_df[col] = pd.to_numeric(self.data_set_df[col])

        self.data_set_df["New Construction boolean"] = self.data_set_df[
            "Construction year"
        ].apply(lambda x: None if pd.isnull(x) else (0 if x < 2021 else 1))

        self.data_set_df["Tenement building boolean"] = self.data_set_df[
            "Subtype of property"
        ].apply(
            lambda x: None
            if x == pd.isnull(x)
            else (1 if x in ["mixed-use-building", "apartment-block"] else 0)
        )
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
                ]
                else "House"
            )
        )

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

        self.data_set_df["Furnished boolean"] = self.data_set_df["Furnished"].apply(
            lambda x: None if pd.isnull(x) else (1 if x.lower == "yes" else 0)
        )

        self.data_set_df["Kitchen equipped boolean"] = self.data_set_df[
            "Kitchen type"
        ].apply(
            lambda x: None
            if pd.isnull(x)
            else (0 if x in ["Notinstalled", "USAuninstalled"] else 1)
        )

        self.data_set_df["Terrace boolean"] = self.data_set_df["Terrace surface"].apply(
            lambda x: 0 if pd.isnull(x) else (1 if x > 0 else 0)
        )

        self.data_set_df["Swimming pool boolean"] = self.data_set_df[
            "Swimming pool"
        ].apply(lambda x: 0 if pd.isnull(x) else (1 if x.lower() == "yes" else 0))

        self.data_set_df["Garden boolean"] = self.data_set_df["Garden surface"].apply(
            lambda x: 0 if pd.isnull(x) else (1 if x > 0 else 0)
        )

        self.data_set_df["Parking tot nb"] = self.data_set_df[
            "Covered parking spaces"
        ].fillna(0) + self.data_set_df["Outdoor parking spaces"].fillna(0)

        self.data_set_df["Parking boolean"] = self.data_set_df["Parking tot nb"].apply(
            lambda x: None if pd.isnull(x) else (1 if x > 0 else 0)
        )

        self.data_set_df["Bathrooms total nb"] = self.data_set_df["Bathrooms"].fillna(
            0
        ) + self.data_set_df["Shower rooms"].fillna(0)

        self.data_set_df["Bathrooms total nb boolean"] = self.data_set_df[
            "Bathrooms total nb"
        ].apply(lambda x: None if pd.isnull(x) else (1 if x > 1 else 0))

        self.data_set_df["Elevator boolean"] = self.data_set_df["Elevator"].apply(
            lambda x: None if pd.isnull(x) else (1 if x.lower() == "yes" else 0)
        )

        self.data_set_df["Accessible for disabled people boolean"] = self.data_set_df[
            "Accessible for disabled people"
        ].apply(lambda x: None if pd.isnull(x) else (1 if x.lower() == "yes" else 0))

        self.data_set_df["Double glazing boolean"] = self.data_set_df[
            "Double glazing"
        ].apply(lambda x: None if pd.isnull(x) else (1 if x.lower() == "yes" else 0))

        replace_dict1 = {
            "Asnew": "As new",
            "Justrenovated": "Just renovated",
            "Tobedoneup": "To be done",
            "Torenovate": "To renovate",
        }
        replace_dict2 = {
            "Hyperequipped": "Hyper equipped",
            "Semiequipped": "Semi equipped",
            "USAhyperequipped": "USA hyper equipped",
            "USAinstalled": "USA installed",
            "USAsemiequipped": "USA semi-equipped",
            "Notinstalled": "Not installed",
        }
        replace_dict3 = {"Fueloil": " Fuel oil"}

        replace_dict4 = {
            "Nonfloodzone": "Non flood zone",
            "Possiblecircumscribedwatersidezone": "Possible circumscribed waterside zone",
            "Possiblefloodzone": "Possible flood zone",
            "Recognizedfloodzone": "Recognized flood zone",
            "Propertypartiallyorcompletelylocatedinacircumscribedandrecognizedfloodzone": "Property partially or completely located in a circumscribed and recognized flood zone",
        }
        self.data_set_df["Building condition"] = self.data_set_df[
            "Building condition"
        ].replace(replace_dict1)

        self.data_set_df["Kitchen type"] = self.data_set_df["Kitchen type"].replace(
            replace_dict2
        )
        self.data_set_df["Heating type"] = self.data_set_df["Heating type"].replace(
            replace_dict3
        )
        self.data_set_df["Flood zone type"] = self.data_set_df[
            "Flood zone type"
        ].replace(replace_dict4)
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
        new_col_order = [
            "Locality",
            "Postal code",
            "Type of property",
            "Subtype",
            "Price (euro)",
            "Construction year",
            "New Construction boolean",
            "Building condition boolean",
            "Building condition",
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
            "Tenement building",
            "URL",
            "Property ID",
        ]
        self.data_set_df = self.data_set_df[new_col_order]
        print(self.data_set_df.head(10))
        print("DataFrame is cleaned!")
        return self.data_set_df

    def to_csv_clean(self):
        """
        Convert the data_set DataFrame into CSV
        """
        self.data_set_df.to_csv("data/clean_data/data_set_CLEAN.csv", index=False)
        print('A .csv file called "data_set_CLEAN.csv" has been generated. ')
