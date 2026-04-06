
import requests
from bs4 import BeautifulSoup
# Try Google Basic Version (no JS required)
url = "https://www.google.com/search?q=AI+summit+India+2026&gbv=1"
headers = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

print(f"Status Code: {response.status_code}")
print(f"H3 count: {len(soup.find_all('h3'))}")

for h3 in soup.find_all('h3'):
    print(f"Found H3: {h3.get_text()}")
    parent_a = h3.find_parent('a')
    if parent_a:
        print(f"  Link: {parent_a['href']}")
