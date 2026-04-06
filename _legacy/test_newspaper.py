
import os
import sys

# Add current dir to path for polyfill
sys.path.insert(0, os.getcwd())

try:
    from newspaper import Article
    import requests
    
    url = "https://news.google.com/rss/articles/CBMiigFBVV95cUxNSDBhREVyUE1wM0paLUdoa3cxUWVpZUJoUm43LVFFRW5WU3ZTbHlUX0V4LVdENjlOT2x2NUpTb3RpNmJpSXE3d2JrMzhnSHlmREJSTXExcEFDekJrSnBFb0pwZEdpVHZLMTcxOUFpZ0Z3eU9hQldyM2o5WWJONjd1QkhxQ2xJb05OaWc?oc=5"
    
    print("Initializing Article...")
    article = Article(url)
    print("Downloading...")
    article.download()
    print(f"Final URL in newspaper: {article.url}")
    print("Parsing...")
    article.parse()
    print(f"Title: {article.title}")
    print(f"Content Sample: {article.text[:100]}...")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
