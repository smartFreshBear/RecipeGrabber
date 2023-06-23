from datetime import timedelta

TIMEOUT_TOLERANCE = 3

EXPIRATION_TIME = timedelta(minutes=30)


def in_timeout_blacklist(url, caching_manager):
    return caching_manager.exists_in_cache(key=url) and \
        int(caching_manager.get_from_cache(key=url)) >= TIMEOUT_TOLERANCE


def increase_timeout_count(url, caching_manager):
    caching_manager.cache_url(key=url, time=EXPIRATION_TIME, value=int(caching_manager.get_from_cache(key=url) or 0) + 1)
