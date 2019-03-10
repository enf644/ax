"""Module with aiocache instance. Works inMemory or with redis
"""

import sys
from aiocache import caches
from loguru import logger

this = sys.modules[__name__]
cache = None


def init_cache(
        mode: str = 'default',
        redis_endpoint: str = '127.0.0.1',
        redis_port: int = 6379,
        redis_timeout: int = 1) -> bool:
    """Initiate aiocache cache.

    Args:
        mode (str, optional): Defaults to 'default'. Set 'redis' for Redis.
        redis_endpoint (str, optional): Defaults to '127.0.0.1'. IP of Redis.
        redis_port (int, optional): Defaults to 6379. Port of Redies server.
        redis_timeout (int, optional): Defaults to 1. Redis timeout.

    Returns:
        bool: True if succesuful
    """

    if mode.lower == 'redis':
        redis_config = {
            'redis': {
                'cache': "aiocache.RedisCache",
                'endpoint': redis_endpoint,
                'port': redis_port,
                'timeout': redis_timeout,
                'serializer': {
                    'class': "aiocache.serializers.PickleSerializer"
                },
                'plugins': [
                    {'class': "aiocache.plugins.HitMissRatioPlugin"},
                    {'class': "aiocache.plugins.TimingPlugin"}
                ]
            }
        }
        # TODO check if Redis is up and running with given settings

        try:
            caches.set_config(redis_config)
            this.cache = caches.get('redis')
        except Exception:
            logger.exception('Error initiating aiocache with Redis.')
            raise
    else:
        ram_config = {
            'default': {
                'cache': "aiocache.SimpleMemoryCache",
                'serializer': {
                    'class': "aiocache.serializers.PickleSerializer"
                }
            }
        }

        try:
            caches.set_config(ram_config)
            this.cache = caches.get('default')
        except Exception:
            logger.exception(
                'Error initiating aiocache with SimpleMemoryCache. ')
            raise

    return True
