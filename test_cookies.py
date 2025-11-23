import browser_cookie3
import requests
from bs4 import BeautifulSoup

print("Testing browser cookie loading...")

# Test loading cookies
try:
    print("\n1. Testing Chrome cookies...")
    chrome_cookies = browser_cookie3.chrome(domain_name='immoweb.be')
    cookie_list = list(chrome_cookies)
    print(f"   Found {len(cookie_list)} cookies from Chrome")
    if cookie_list:
        for cookie in cookie_list[:5]:  # Show first 5
            print(f"   - {cookie.name}: {cookie.value[:50]}...")
except Exception as e:
    print(f"   Error: {e}")

try:
    print("\n2. Testing Edge cookies...")
    edge_cookies = browser_cookie3.edge(domain_name='immoweb.be')
    cookie_list = list(edge_cookies)
    print(f"   Found {len(cookie_list)} cookies from Edge")
except Exception as e:
    print(f"   Error: {e}")

# Test making a request with cookies
print("\n3. Testing request with session...")
session = requests.Session()
try:
    chrome_cookies = browser_cookie3.chrome(domain_name='immoweb.be')
    for cookie in chrome_cookies:
        session.cookies.set(cookie.name, cookie.value, domain=cookie.domain)
    print(f"   Loaded {len(session.cookies)} cookies into session")
except Exception as e:
    print(f"   Error loading cookies: {e}")

# Test actual request
print("\n4. Testing actual request to Immoweb...")
try:
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    })
    response = session.get('https://www.immoweb.be/en/search/house/for-sale?countries=BE&page=1', timeout=10)
    print(f"   Status code: {response.status_code}")
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        links = soup.find_all('a', href=True)
        immoweb_links = [l.get('href') for l in links if 'immoweb.be' in l.get('href', '') and '/property/' in l.get('href', '')]
        print(f"   Found {len(immoweb_links)} property links")
    elif response.status_code == 403:
        print("   ❌ Got 403 Forbidden - still being blocked")
    else:
        print(f"   ⚠ Unexpected status: {response.status_code}")
except Exception as e:
    print(f"   Error: {e}")

