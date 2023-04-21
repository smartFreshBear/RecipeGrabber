from datetime import timedelta

import redis

TIMEOUT_TOLERANCE = 3
EXPIRATION_TIME = timedelta(minutes=30)
user_connection = redis.Redis(host='redis-10060.c135.eu-central-1-1.ec2.cloud.redislabs.com', port=10060,
                              username='default', password='CWqOy4UlreQiOgo8lenpSc6ZMnCvTA8x', decode_responses=True)


def in_timeout_blacklist(url):
    return user_connection.get(url) and int(user_connection.get(url)) >= TIMEOUT_TOLERANCE


def increase_timeout_count(url):
    user_connection.setex(url, EXPIRATION_TIME, int(user_connection.get(url) or 0) + 1)
