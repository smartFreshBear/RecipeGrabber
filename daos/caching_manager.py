from utils.logger import create_logger_instance

import redis

caching_manager_logger = create_logger_instance('Caching_Manager')


class CachingManager:
    def __init__(self):
        self.redis = redis.Redis(host='redis-10060.c135.eu-central-1-1.ec2.cloud.redislabs.com', port=10060,
                                 username='default', password='CWqOy4UlreQiOgo8lenpSc6ZMnCvTA8x', decode_responses=True)

    def cache_url(self, key, value=None, name=None, time=None):
        if name is None:
            if self.redis.setex(key, time=time, value=value):
                caching_manager_logger.info(
                    "Successfully cached url:\n{}".format(key)
                )
            else:
                caching_manager_logger.error(
                    "failed caching url:\n{}".format(key)
                )
        else:
            if self.redis.hset(name=name, key=key, value=value):
                caching_manager_logger.info(
                    "cached data from url:\n{}".format(key)
                )
            else:
                caching_manager_logger.error(
                    "failed caching data from url:\n{}".format(key)
                )

    def exists_in_cache(self, key, name=None):
        return self.redis.exists(key) if name is None else self.redis.hexists(name=name, key=key)

    def get_from_cache(self, key, name=None):
        return self.redis.get(key) if name is None else self.redis.hget(name=name, key=key)
