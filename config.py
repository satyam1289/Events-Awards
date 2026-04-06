"""
Configuration and Constants for Sector-Based Event Scraper
"""

import os
from dotenv import load_dotenv
load_dotenv()

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Logging paths
LOG_FILE = os.path.join(LOGS_DIR, 'assistant.log')

# Data storage paths
EVENTS_FILE = os.path.join(DATA_DIR, 'events.json')

# Scraping configuration
REQUEST_TIMEOUT = 45
MAX_ARTICLES_PER_SEARCH = 20
MAX_PAGES_PER_SECTOR = 7
DELAY_BETWEEN_REQUESTS = 2  # seconds

# Proxy configuration (set to None to disable)
PROXY = None

# User agent for requests
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Event indicators
EVENT_INDICATORS = [
    'summit', 'conference', 'expo', 'exposition', 'forum', 'conclave', 
    'festival', 'meet', 'meeting', 'seminar', 'symposium', 'workshop', 
    'event', 'inaugural', 'launch', 'launches', 'hackathon', 'bootcamp', 
    'megathon', 'edition', 'annual', 'masterclass', 'retreat', 'panel', 
    'roundtable', 'mixer', 'webinar', 'gathering', 'showcase', 'celebration', 
    'fair', 'convention', 'bazaar', 'exhibition', 'keynote', 'plenary',
    'demo day', 'roadshow', 'trade fair', 'tech expo', 'conclave', 'symposium',
    'colloquium', 'summit', 'gala', 'pitch day', 'accelerator', 'incubator',
    'unveiling', 'premier', 'screening', 'reception', 'banquet', 'pageant',
    'vernissage', 'carnival', 'fiesta', 'soiree', 'party', 'ball', 'promenade',
    'rally', 'recital', 'concert', 'gig', 'show', 'spectacle', 'extravaganza',
    'opening ceremony', 'networking meet', 'pandal', 'mela', 'utsav', 'milan'
]

# Award indicators
AWARD_INDICATORS = [
    'awards', 'award', 'ceremony', 'gala', 'prize', 'recognition', 
    'accolade', 'honour', 'nomination', 'nominations', 'nominate', 
    'trophy', 'winner', 'winners', 'finalist', 'finalists', 'shortlist',
    'felicitation', 'jury', 'hall of fame', 'excellence awards', 
    'leadership awards', 'industry awards', 'achievement awards'
]

# Action/Intent modifiers
INTENT_KEYWORDS = [
    'nominations open', 'register now', 'last date to apply', 
    'delegate registration', 'stall booking', 'exhibit now',
    'call for speakers', 'early bird discount', 'agenda announced'
]

# Noise filtering (negative words to exclude)
NEGATIVE_KEYWORDS = [
    'internal meeting', 'private event', 'closed door', 'invitation only', 
    'already concluded', 'past event', 'review 2025', 'recap 2025', 
    'internal award', 'employee award', 'scholarship awarded',
    'grant awarded', 'won the award', 'congratulates', 'winner list',
    'announced winners', 'held on', 'took place', 'was organized'
]

# Influential Event Organizers & Media Houses
ORGANIZERS = [
    'Economic Times', 'The Economic Times', 'ET Edge', 'ETHR World', 'ET News',
    'Nasscom', 'NASSCOM', 'CII', 'FICCI', 'ASSOCHAM', 'Zinnov', 'YourStory', 'Techsparks',
    'Your story', 'Business World', 'BW Business World', 'BW People', 'Financial Express',
    'Valiant and Company', 'EE Times Europe', 'Power Energy News', 'Scribe Minds and Media',
    'Ministry of Housing and Urban Affairs', 'New Delhi Print Media', 'Banking Frontiers',
    'Banking and Finance Post', 'Elets Technomedia', 'eletsonline', 'EXITO', 'Financial Times',
    'PDA Ventures', 'World Leadership Congress', 'Dun And Bradstreet', 'Constellar',
    'Moneycontrol', 'Mosaic Digital', 'Be to Be Infomedia', 'Point to business Service',
    'Quantic India', 'People Matters', 'Ambition Box', 'Fast Company', 'HRAI',
    'The Human Resource Association India', 'UBS Forums', 'Great place to work', 
    'VCCircle', 'Inc42', 'MediaNama', 'Indian Retailer', 'Eventfaqs', 'Adgully', 
    'Afaqs', 'Campaign India', 'Exchange4media', 'MediaNews4U', 'Everything Experiential',
    'StartupTalky', 'Trak.in', 'CXO Today', 'Express Computer', 'Dataquest', 'TechGraph',
    'Entrepreneur India', 'Forbes India', 'Fortune India', 'Business Standard',
    'Mint', 'CNBC TV18', 'Zee Business', 'NDTV Profit'
]

# Sector definitions with keywords
SECTORS = {
    'BFSI': [
        'bfsi', 'banking', 'financial services', 'insurance', 'digital banking', 
        'neobank', 'lending', 'credit', 'wealth management', 'stock market', 
        'equity', 'mutual fund', 'capital market', 'investment'
    ],
    'Fintech': [
        'fintech', 'payments', 'digital payments', 'upi', 'neobank', 
        'payment gateway', 'pos', 'remittance', 'wallets'
    ],
    'Technology': [
        'technology', 'software', 'cloud computing', 'it services', 'saas', 
        'cybersecurity', 'digital transformation', 'big data', 'blockchain', 
        'iot', 'robotics', 'automation', 'fintech', 'edtech', 'healthtech',
        'paas', 'iaas', 'app development', 'mobile app', 'augmented reality', 
        'virtual reality', 'vr', 'ar', 'quantum computing', 'semiconductor'
    ],
    'Healthcare': [
        'healthcare', 'medical', 'pharma', 'pharmaceutical', 'hospital',
        'biotech', 'biotechnology', 'health tech', 'medtech', 'telemedicine',
        'healthtech', 'wellness', 'clinical', 'drug discovery', 'vaccine',
        'diagnostics', 'medical devices', 'life sciences', 'genomics'
    ],
    'Startups': [
        'startup', 'entrepreneur', 'venture capital', 'vc', 'angel investor',
        'seed funding', 'fundraising', 'ecommerce', 'fintech', 'saas',
        'incubator', 'accelerator', 'seed fund', 'series a', 'series b',
        'funding', 'unicorn', 'founders meet', 'startup ecosystem'
    ],
    'Retail': [
        'retail', 'fmcg', 'supply chain', 'logistics', 'omnichannel', 'wholesale',
        'b2b retail', 'quick commerce', 'qcommerce'
    ],
    'eCommerce': [
        'ecommerce', 'e-commerce', 'marketplace', 'online store', 'cart',
        'digital commerce', 'web store', 'shopping platform'
    ],
    'D2C': [
        'd2c', 'direct to consumer', 'd2c brands', 'd2c summit'
    ],
    'B2C': [
        'b2c', 'b2c startups', 'b2c retail', 'consumer business'
    ],
    'Marketing': [
        'marketing', 'advertising', 'branding', 'media', 'communication',
        'public relations', 'pr', 'brand', 'campaign', 'influencer'
    ],
    'MarTech': [
        'martech', 'customer experience', 'cx', 'digital marketing', 
        'social media', 'content marketing', 'seo', 'marketing automation'
    ],
    'Human Resources': [
        'hr', 'human resources', 'talent management', 'talent acquisition', 
        'recruitment', 'hr technology', 'workplace culture', 'future of work'
    ],
    'Automotive': [
        'automotive', 'connected cars', 'vehicle safety', 'driverless', 
        'car show', 'mobility expo', 'auto show'
    ],
    'EV': [
        'ev', 'electric vehicle', 'charging station', 'li-ion', 'battery',
        'electric mobility', 'low carbon transport'
    ],
    'AV': [
        'av', 'autonomous vehicle', 'driverless', 'self-driving', 'lidar', 'adas'
    ],
    'Road transport': [
        'road transport', 'road safety', 'highways', 'trucking', 'expressway', 'toll'
    ],
    'Commercial vehicle': [
        'commercial vehicle', 'cv', 'heavy vehicles', 'fleet management', 'cv awards'
    ],
    'Transport': [
        'transportation', 'transport', 'logistics', 'rail', 'air transport'
    ],
    'Government': [
        'policy', 'government', 'ministry', 'public sector', 'governance',
        'regulatory', 'smart city', 'digital india', 'public infrastructure'
    ],
    'Education': [
        'education', 'edtech', 'learning', 'higher education', 'k-12',
        'skills', 'training', 'university', 'college', 'e-learning'
    ],
    'Sustainability': [
        'sustainability', 'esg', 'green energy', 'renewable', 'climate change',
        'circular economy', 'net zero', 'environment', 'social impact'
    ],
    'Entertainment': [
        'entertainment', 'media', 'gaming', 'ott', 'streaming', 'film',
        'music', 'events', 'content creation', 'creative industry'
    ],
    'Real Estate': [
        'real estate', 'proptech', 'construction', 'infrastructure',
        'smart buildings', 'commercial real estate', 'residential'
    ],
    'Agriculture': [
        'agriculture', 'agtech', 'farming', 'food security', 'agri business',
        'supply chain', 'processing', 'precision farming'
    ],
    'Artificial Intelligence': [
        'ai', 'artificial intelligence', 'genai', 'generative ai', 
        'machine learning', 'deep learning', 'nlp', 'computer vision', 
        'ai ethics', 'large language models', 'llm'
    ],
    'Regional & Cities': [
        'regional', 'local', 'city', 'urban', 'state', 'district',
        'metropolitan', 'municipal', 'town'
    ]
}

# City priority for discovery
CITIES = [
    'Mumbai', 'Delhi', 'Bangalore', 'Bengaluru', 'Hyderabad', 
    'Chennai', 'Pune', 'Ahmedabad', 'Kolkata', 'Gurgaon', 
    'Noida', 'Jaipur', 'Lucknow', 'Indore', 'Chandigarh',
    'Surat', 'Nagpur', 'Visakhapatnam', 'Bhopal', 'Patna', 
    'Ludhiana', 'Kochi', 'Coimbatore', 'Vadodara', 'Guwahati',
    'Amritsar', 'Bhubaneswar', 'Madurai', 'Raipur', 'Rajkot', 
    'Varanasi', 'Srinagar', 'Aurangabad', 'Ranchi', 'Jodhpur', 
    'Gwalior', 'Vijayawada', 'Jalandhar', 'Tiruchirappalli', 'Kanpur', 
    'Dehradun', 'Mysuru', 'Meerut', 'Solapur', 'Nashik', 
    'Hubballi-Dharwad', 'Bareilly', 'Moradabad', 'Aligarh', 'Jabalpur', 
    'Tiruppur', 'Salem', 'Warangal', 'Guntur', 'Bijapur', 
    'Belgaum', 'Mangalore', 'Kozhikode', 'Thiruvananthapuram', 'Gaya', 
    'Bhagalpur', 'Muzaffarpur', 'Darbhanga', 'Ajmer', 'Udaipur', 
    'Kota', 'Jaisalmer', 'Bikaner', 'Jhansi', 'Agra', 
    'Mathura', 'Haridwar', 'Rishikesh', 'Rohtak', 'Panipat', 
    'Karnal', 'Shimla', 'Manali', 'Gangtok', 'Shillong', 
    'Imphal', 'Agartala', 'Aizawl', 'Kohima', 'Itanagar', 
    'Port Blair', 'Silvassa', 'Daman', 'Diu', 'Kavaratti', 
    'Pondicherry', 'Puducherry', 'Ghaziabad', 'Faridabad', 'Navi Mumbai', 
    'Kalyan', 'Dombivli', 'Vasai-Virar', 'Mira-Bhayandar', 'Thane'
]

# Region priority for discovery
REGIONS = [
    'India', 'National', 'Pan-India', 'North India', 'South India', 
    'West India', 'East India', 'Maharashtra', 'Karnataka', 
    'Tamil Nadu', 'Telangana', 'Uttar Pradesh', 'Gujarat'
]

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# High signal domains to boost during extraction
DEEP_FETCH_ALLOWLIST = [
    'economic-times', 'financialexpress', 'business-standard', 'hindustantimes',
    'timesofindia', 'moneycontrol', 'livemint', 'nasscom', 'cii.in', 'ficci.in'
]

# PLATINUM: Literal event platforms (Auto-verify)
PLATINUM_DOMAINS = [
    '10times.com', 'meraevents.com', 'townscript.com', 'allevents.in', 
    'eventbrite.com', 'meetup.com', 'explara.com', 'bookmyshow.com',
    'konfhub.com'
]

# Blocklist of domains to ignore
URL_BLOCKLIST_DOMAINS = [
    'youtube.com', 'facebook.com', 'twitter.com', 'linkedin.com', 'instagram.com',
    'pinterest.com', 'tiktok.com', 'wikipedia.org', 'amazon.com', 'flipkart.com',
    'glassdoor.co.in', 'ambitionbox.com', 'justdial.com'
]

# Negative Intent (News that uses event words but isn't an event)
NEGATIVE_INTENT_SIGNALS = [
    'market research', 'stock price', 'hiring', 'recruitment', 'job opening',
    'how to', 'best practices', 'top 10', 'case study', 'whitepaper',
    'news update', 'quarterly results', 'stock analysis', 'pvt ltd', 'salary',
    'speaker request', 'call for entry', 'call for presentation', 'rules and regulations',
    'entry criteria', 'deadlines', 'frequently asked questions', 'about summit'
]

# Confidence thresholds
MIN_STORAGE_CONFIDENCE = 50  # Workable threshold
MAX_DAILY_QUERIES = 2500 # Serper Free-ish tier limit

# Deduplication thresholds
FUZZY_MATCH_THRESHOLD = 0.85

# --- NEW CONFIGURATIONS FROM UPGRADE ---

# New field defaults
NOMINATION_DEADLINE_PATTERNS_ENABLED = True
DEEP_FETCH_TOP_N = 5  # Only deep-fetch top 5 results per run

# Free sources toggle
ENABLE_FREE_SOURCES = True
ENABLE_RSS_FEEDS = True  
ENABLE_GOOGLE_NEWS_RSS = True

# Telegram alerts toggle
ENABLE_TELEGRAM_ALERTS = True

# Daily Serper budget (hard cap)
MAX_SERPER_CALLS_PER_DAY = 80
MAX_SERPER_CALLS_PER_MONTH = 2400  # Full capacity usage

# Cache settings
QUERY_CACHE_TTL_HOURS = 48

# Archive settings
AUTO_ARCHIVE_CONCLUDED = True

# Status values
STATUS_UPCOMING = "UPCOMING"
STATUS_NOMINATIONS_OPEN = "NOMINATIONS_OPEN"
STATUS_CONCLUDED = "CONCLUDED"
STATUS_UNVERIFIED = "UNVERIFIED"
STATUS_STALE = "STALE"

# New event type — add "roundtable" and "conclave" as first class types
EVENT_TYPES = ["awards", "conference", "summit", "expo", "workshop", 
               "hackathon", "webinar", "roundtable", "conclave", "festival"]

# Update NEGATIVE_INTENT_SIGNALS — add these:
NEGATIVE_INTENT_SIGNALS.extend([
    "apply for job", "job opening", "vacancy", "hiring now",
    "salary", "work from home job", "freelance project",
    "course enrolment", "online course", "certification program",
    "scholarship", "grant application", "research paper submission",
])

# Add sector-specific award body domains for auto-boost
SECTOR_AWARD_BODIES = {
    "BFSI": ["bankingfrontiers.com", "ibanet.org"],
    "Technology": ["nasscom.in", "dataquest.in", "expresscomputer.in"],
    "Startups": ["inc42.com", "yourstory.com", "startupindia.gov.in"],
    "Healthcare": ["ahpi.in", "cii.in"],
    "Marketing": ["exchange4media.com", "adgully.com", "afaqs.com"],
    "Human Resources": ["peoplematters.in", "hrai.in"],
}

