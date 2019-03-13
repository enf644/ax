"""Ax workflow apps builder.

Usage:
  ax run [--host=<host>] [--port=<port>]
  ax --version
  ax (-h | --help)

Options:
  -h --help       Show this screen.
  --version       Show version.
  --host=<host>   Host addres to run ax web application (default: 127.0.0.1).
  --port=<port>   Port of ax web application (default: 8080).

"""
import os
from sanic_graphql import GraphQLView
from sanic import Sanic
from sanic_cors import CORS
from loguru import logger
from docopt import docopt
from graphql.execution.executors.asyncio import AsyncioExecutor

import backend.logger as ax_logger
import backend.misc as ax_misc
import backend.cache as ax_cache
import backend.model as ax_model
import backend.schema as ax_schema
import backend.pubsub as ax_pubsub
import backend.scheduler as ax_scheduler
import backend.migration as ax_migration
import backend.routes as ax_routes


def init_model():
    """Initiate model. Used in alembic scripts"""
    ax_model.init_model(
        dialect=str(os.environ.get('AX_DB_DIALECT') or 'sqlite'),
        host=str(os.environ.get('AX_DB_HOST') or '127.0.0.1'),
        port=str(os.environ.get('AX_DB_PORT') or '5432'),
        login=str(os.environ.get('AX_DB_LOGIN') or ''),
        password=str(os.environ.get('AX_DB_PASSWORD') or ''),
        database=str(os.environ.get('AX_DB_DATABASE') or 'ax'),
        sqlite_filename=str(os.environ.get(
            'AX_DB_SQLITE_FILENAME') or 'ax_sqlite.db'),
        sqlite_absolute_path=os.environ.get(
            'AX_DB_SQLITE_ABSOLUTE_PATH') or None
    )


def init_ax():
    """Initiate all modules of Ax"""
    ax_misc.load_configuration()  # Load settings from app.yaml to os.environ
    ax_misc.init_misc(
        timezone_name=str(os.environ.get('AX_TIMEZONE') or 'UTC')
    )
    ax_logger.init_logger(
        logs_filename=os.environ.get('AX_LOGS_FILENAME') or None,
        logs_absolute_path=os.environ.get('AX_LOGS_ABSOLUTE_PATH') or None,
        logs_level=os.environ.get('AX_LOGS_LEVEL') or 'ERROR'
    )  # Initiate logger - console + file + sentry
    init_model()
    ax_cache.init_cache(
        mode=str(os.environ.get('AX_CACHE_MODE') or 'default'),
        redis_endpoint=str(os.environ.get('AX_REDIS_ENDPOINT') or '127.0.0.1'),
        redis_port=int(os.environ.get('AX_REDIS_ENDPOINT') or 6379),
        redis_timeout=int(os.environ.get('AX_REDIS_ENDPOINT') or 1),
    )  # Initiate aiocache
    ax_pubsub.init_pubsub()  # Initiate pubsub.
    ax_schema.init_schema()  # Initiate gql schema.  Depends on cache and pubsub
    ax_migration.init_migration()  # Check if database schema needs update

    app = Sanic()

    # cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app, automatic_options=True)  # TODO limit CORS to api folder

    app.static('/static', str(ax_misc.path('dist/static')))
    app.static('/stats', str(ax_misc.path('dist/stats.html')))
    app.static('/test_webpack', str(ax_misc.path('dist/test.html')))

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


def main():
    """Main function"""
    arguments = docopt(__doc__, version='Ax v0.0.1')

    if arguments['run']:
        sanic_app = init_ax()

        host = str(os.environ.get('AX_HOST') or '127.0.0.1')
        port = int(os.environ.get('AX_PORT') or 8080)
        debug = bool(os.environ.get('AX_SANIC_DEBUG') or False)
        access_log = bool(os.environ.get('AX_SANIC_ACCESS_LOG') or False)

        if arguments['--host']:
            host = arguments['--host']

        if arguments['--port']:
            port = int(arguments['--port'])

        logger.debug(ax_model.engine.table_names())
        logger.info('Running Ax on {host}:{port}', host=host, port=port)
        sanic_app.run(host=host, port=port, debug=debug, access_log=access_log)


if __name__ == "__main__":
    main()
