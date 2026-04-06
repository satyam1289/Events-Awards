
try:
    import bs4
    import requests
    import lxml
    import newspaper
    import nltk
    import flask
    import flask_cors
    import dateutil
    import fake_useragent
    import googlenewsdecoder
    import feedparser
    import dateparser
    print("All basic imports passed.")
except ImportError as e:
    print(f"Missing dependency: {e}")
