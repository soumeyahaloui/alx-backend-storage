# web.py

import requests
from functools import wraps
import redis
import time

# Initialize Redis connection
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def cache_decorator(func):
    @wraps(func)
    def wrapper(url):
        # Construct cache and count keys
        cache_key = f"cache:{url}"
        count_key = f"count:{url}"

        # Check if the URL is already cached
        if r.exists(cache_key):
            # Increment the count
            r.incr(count_key)
            return r.get(cache_key)
        
        # If not cached, fetch the content using the decorated function
        content = func(url)
        
        # Cache the content with an expiration time of 10 seconds
        r.setex(cache_key, 10, content)
        
        # Increment the count, initializing it if it doesn't exist
        r.incr(count_key)
        
        return content
    return wrapper

@cache_decorator
def get_page(url: str) -> str:
    """Fetches the HTML content of the given URL."""
    response = requests.get(url)
    return response.text

# Example usage
if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk/delay/3000/url/http://www.google.com"
    print(get_page(url))
    # Subsequent calls within 10 seconds should hit the cache
    print(get_page(url))

