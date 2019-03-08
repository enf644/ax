"""Pubsub module"""

import sys
import aiopubsub

this = sys.modules[__name__]
hub = None
publisher = None


def init_pubsub():
    """Initiate pubsub module, create default publisher"""
    this.hub = aiopubsub.Hub()
    this.publisher = aiopubsub.Publisher(
        this.hub, prefix=aiopubsub.Key())
