import os
import sys
from aiocache import caches, SimpleMemoryCache, RedisCache
from aiocache.serializers import JsonSerializer

this = sys.modules[__name__]
this.cache = None


def init_cache(
        mode: str = 'default',
        redis_endpoint: str = '127.0.0.1',
        redis_port: int = 6379,
        redis_timeout: int = 1) -> bool:
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

        caches.set_config(redis_config)
        this.cache = caches.get('redis')
    else:
        ram_config = {
            'default': {
                'cache': "aiocache.SimpleMemoryCache",
                'serializer': {
                    'class': "aiocache.serializers.PickleSerializer"
                }
            }
        }

        caches.set_config(ram_config)
        this.cache = caches.get('default')

    return True
