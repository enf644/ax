"""Runneble script"""
import os
from sanic_graphql import GraphQLView
from sanic import Sanic
# from sanic.response import json
from sanic_cors import CORS
from loguru import logger

from graphql.execution.executors.asyncio import AsyncioExecutor

import backend.logger as ax_logger
import backend.misc as ax_misc
import backend.cache as ax_cache
import backend.schema as ax_schema
# import backend.model as ax_model
import backend.pubsub as ax_pubsub
import backend.scheduler as ax_scheduler
import backend.migration as ax_migration
import backend.routes as ax_routes


def init_ax():
    """Initiate all modules of Ax"""
    ax_misc.load_configuration()  # Load settings from app.yaml to os.environ
    ax_logger.init_logger()  # Initiate logger - console + file + sentry
    ax_cache.init_cache(
        mode=os.environ.get('CACHE_MODE') or 'default',
        redis_endpoint=os.environ.get('REDIS_ENDPOINT') or None,
        redis_port=os.environ.get('REDIS_ENDPOINT') or None,
        redis_timeout=os.environ.get('REDIS_ENDPOINT') or None,
    )  # Initiate aiocache
    ax_pubsub.init_pubsub()  # Initiate pubsub.
    ax_schema.init_schema()  # Initiate gql schema.  Depends on cache and pubsub
    ax_migration.init_migration()  # Check if database schema needs update

    app = Sanic()

    # cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app, automatic_options=True)  # TODO limit CORS to api folder

    app.static('/static', './dist/static')
    app.static('/stats', './dist/stats.html')
    app.static('/test_webpack', './dist/test.html')

    @app.listener('before_server_start')
    async def initialize_scheduler(_app, _loop):  # pylint: disable=unused-variable
        """Initiate scheduler"""
        ax_scheduler.init_scheduler()

    @app.listener('before_server_start')
    def init_graphql(_app, _loop):  # pylint: disable=unused-variable
        """Initiate graphql"""
        graphql_view = GraphQLView.as_view(schema=ax_schema.schema,
                                           graphiql=False,
                                           executor=AsyncioExecutor(loop=_loop))
        _app.add_route(graphql_view, '/api/graphql')

    ax_routes.init_routes(app)

    return app


if __name__ == "__main__":
    sanic_app = init_ax()
    logger.info('Ax. Ready to run.')
    # TODO Take debug and access logs from app.yaml
    sanic_app.run(host="127.0.0.1", port=8080, debug=True, access_log=False)
