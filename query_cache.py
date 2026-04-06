import json, hashlib, os, time

CACHE_FILE = "data/query_cache.json"
CACHE_TTL_HOURS = 48  # Don't re-run the same query for 48 hours

def get_cache_key(query):
    return hashlib.md5(query.strip().lower().encode()).hexdigest()

def is_cached(query):
    key = get_cache_key(query)
    if not os.path.exists(CACHE_FILE):
        return False
    try:
        with open(CACHE_FILE) as f:
            cache = json.load(f)
        entry = cache.get(key)
        if entry:
            age_hours = (time.time() - entry["timestamp"]) / 3600
            if age_hours < CACHE_TTL_HOURS:
                return True
    except:
        pass
    return False

def save_to_cache(query, results):
    key = get_cache_key(query)
    cache = {}
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE) as f:
                cache = json.load(f)
        except:
            pass
    cache[key] = {"timestamp": time.time(), "result_count": len(results)}
    # Prune cache entries older than 7 days
    now = time.time()
    cache = {k: v for k, v in cache.items() if (now - v["timestamp"]) < 7 * 24 * 3600}
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)
