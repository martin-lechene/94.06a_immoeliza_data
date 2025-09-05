from bs4 import BeautifulSoup
import requests

urls = [
    "https://www.immoweb.be/en/classified/house/for-sale/woluwe-saint-pierre/1150/11112019",
    "https://www.immoweb.be/en/classified/house/for-sale/oupeye/4682/11094364",
]

soup2 = (
    """<div class="flag-list__item flag-list__item--main"><!----> <span class="flag-list__text">Under option</span></div>""",
)

soups = []
for url in urls:
    r = requests.get(url)
    print(url, r.status_code)
    soups.append(BeautifulSoup(r.content, "lxml"))

titles = []
for soup in soups:
    # Get title
    elems = soup.find_all("span", attrs={"class": "flag-list__text"})
    for elem in elems:
        title_text = elem.get_text(strip=True)
        titles.append(title_text)

ele = BeautifulSoup(soup2, "lxml")
text = ele.find("span", class_="flag-list__text")
