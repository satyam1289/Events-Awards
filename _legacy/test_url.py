
import requests
import re

url = "https://news.google.com/rss/articles/CBMiigFBVV95cUxNSDBhREVyUE1wM0paLUdoa3cxUWVpZUJoUm43LVFFRW5WU3ZTbHlUX0V4LVdENjlOT2x2NUpTb3RpNmJpSXE3d2JrMzhnSHlmREJSTXExcEFDekJrSnBFb0pwZEdpVHZLMTcxOUFpZ0Z3eU9hQldyM2o5WWJONjd1QkhxQ2xJb05OaWc?oc=5"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

try:
    # Google News sometimes gives the URL in the meta tags if it blocks the redirect
    r = requests.get(url, headers=headers, timeout=10)
    print(f"Final URL via requests: {r.url}")
    
    if "google.com" in r.url:
        # Look for the real URL in the HTML
        # Sometimes it's in a <c-wiz> or a data attribute
        match = re.search(r'data-url="(https?://[^"]+)"', r.text)
        if match:
            print(f"Found URL in data-url: {match.group(1)}")
        
        # Or look for any external links
        matches = re.findall(r'href="(https?://(?!.*google\.com)[^"]+)"', r.text)
        if matches:
            print(f"Other external links: {matches[:3]}")
except Exception as e:
    print(f"Error: {e}")
