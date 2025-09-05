from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from .utils import get_soup, get_max_workers
import scrapy


def get_links_concurrently(base_url, pages=333):
    """
    Fetch property links from multiple pages concurrently using a thread pool.

    """
    url_list = []

    def fetch_links_from_page(page_number):
        """
        Fetch links from a single page by formatting the base_url with the page_number,
        parsing the page with BeautifulSoup, and extracting all links with a specific class.

        """
        page_url = base_url.format(page_number)
        soup = get_soup(page_url)
        links = [a.get("href") for a in soup.find_all(
            'a', attrs={"class": "card__title-link"})]
        return links

    with ThreadPoolExecutor(max_workers=get_max_workers()) as executor:
        # Submit all pages to be fetched concurrently
        future_to_page = {executor.submit(
            fetch_links_from_page, page): page for page in range(1, pages + 1)}

        for future in as_completed(future_to_page):
            page = future_to_page[future]
            try:
                page_links = future.result()
                url_list.extend(page_links)
                print(f"Extracted URLs from Page {page}")
            except Exception as exc:
                print(f"Page {page} generated an exception: {exc}")

    print(list(set(url_list)))
    return list(set(url_list))


def get_property_details(url):
    """
    Get details from a single property page by parsing JavaScript object notation within the webpage.

    Args:
        url (str): The URL of the property page to parse.

    Returns:
        dict: A dictionary containing the parsed details of the property.
    """
    soup = get_soup(url)
    script_tags = soup.find_all("script", attrs={"type": "text/javascript"})
    for script in script_tags:
        if "window.classified" in script.get_text():
            script_text = script.get_text()
            json_string = script_text.split('window.classified = ', 1)[
                1].rsplit(';', 1)[0]
            results = json.loads(json_string)
            return results


def fetch_details_concurrently(url_list):
    """
    Fetch property details for a list of URLs concurrently using a thread pool.

    Args:
        url_list (list): A list of URLs to fetch details from.

    Returns:
        list: A list of dictionaries, each containing the details of a property.
    """
    with ThreadPoolExecutor(max_workers=get_max_workers()) as executor:
        futures = {executor.submit(
            get_property_details, url): url for url in url_list}
        results = []
        for future in futures:
            try:
                data = future.result()
                results.append(data)
            except Exception as exc:
                print('%r generated an exception: %s' % (futures[future], exc))
    return results
