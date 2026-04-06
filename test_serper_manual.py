import http.client
import json
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("SERPER_API_KEY")

print(f"API Key: {api_key}")

conn = http.client.HTTPSConnection("google.serper.dev")
payload = json.dumps({
  "q": "upcoming technology awards 2026 India",
  "gl": "in"
})
headers = {
  'X-API-KEY': api_key.strip(),
  'Content-Type': 'application/json'
}
conn.request("POST", "/search", payload, headers)
res = conn.getresponse()
data = res.read().decode("utf-8")
print(data)
