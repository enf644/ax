"""Ax workflow apps builder.

Usage:
  ax [--host=<host>] [--port=<port>]
  ax --version

Options:
  -h --help       Show this screen.
  --version       Show version.
  --host=<host>   Host addres to run ax web application (default: 127.0.0.1).
  --port=<port>   Port of ax web application (default: 8080).

"""

import os
import sys
from pathlib import Path
from sanic import Sanic
from sanic_cors import CORS
from loguru import logger
from docopt import docopt

# Add folder with main.py to sys.path.
root_path = Path(__file__).parent.resolve()
if root_path not in sys.path:
    sys.path.insert(0, str(root_path))

# pylint: disable=wrong-import-position
import backend.logger as ax_logger
import backend.misc as ax_misc
import backend.cache as ax_cache
import backend.model as ax_model
import backend.schema as ax_schema
import backend.pubsub as ax_pubsub
import backend.scheduler as ax_scheduler
import backend.migration as ax_migration
import backend.routes as ax_routes
import backend.dialects as ax_dialects

# pylint: enable=wrong-import-position


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


# class AxGraphQLView(GraphQLView):
#     """ Extends GraphQLView to output GQL errors"""
#     @staticmethod
#     def format_error(error):
#         logger.error(error)
#         return GraphQLView.format_error(error)


def init_ax():
    """Initiate all modules of Ax"""

    # Load settings from app.yaml to os.environ
    ax_misc.load_configuration()
    # Misc functions used throw all application. Nothing specific.
    ax_misc.init_misc(
        timezone_name=str(os.environ.get('AX_TIMEZONE') or 'UTC'),
        tmp_absolute_path=os.environ.get('AX_TMP_ABSOLUTE_PATH') or None,
        uploads_absolute_path=os.environ.get(
            'AX_UPLOADS_ABSOLUTE_PATH') or None
    )
    # Logger (loguru) used in all modules - console + file + sentry
    ax_logger.init_logger(
        logs_filename=os.environ.get('AX_LOGS_FILENAME') or None,
        logs_absolute_path=os.environ.get('AX_LOGS_ABSOLUTE_PATH') or None,
        logs_level=os.environ.get('AX_LOGS_LEVEL') or 'ERROR'
    )

    # for item, value in os.environ.items():
    #     logger.info('ENV: {}: {}'.format(item, value))

    # Initiate SqlAlchemy. Made with separate function for alembic.
    # It initiates database connection on migration.
    init_model()
    # Init cache module (aiocache). It is not yet used.
    ax_cache.init_cache(
        mode=str(os.environ.get('AX_CACHE_MODE') or 'default'),
        redis_endpoint=str(os.environ.get('AX_REDIS_ENDPOINT') or '127.0.0.1'),
        redis_port=int(os.environ.get('AX_REDIS_ENDPOINT') or 6379),
        redis_timeout=int(os.environ.get('AX_REDIS_ENDPOINT') or 1),
    )
    # Initiate pub-sub module. Used for web-socket subscriptions.
    # Notification on workflow action
    ax_pubsub.init_pubsub()
    # Check if database schema needs update
    ax_migration.init_migration()
    # Initiate gql schema.  Depends on cache and pubsub
    ax_schema.init_schema()

    # cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
    CORS(app, automatic_options=True)  # TODO limit CORS to api folder

    app.static('/uploads', str(ax_misc.path('uploads')))
    app.static('/static', str(ax_misc.path('dist/static')))
    app.static('/stats', str(ax_misc.path('dist/stats.html')))
    app.static('/test_webpack', str(ax_misc.path('dist/test.html')))

    @app.listener('before_server_start')
    async def initialize_scheduler(_app, _loop):  # pylint: disable=unused-variable
        """Initiate scheduler. It used for cron-like jobs"""
        ax_scheduler.init_scheduler()

    @app.listener('before_server_start')
    def save_loop(_app, _loop):  # pylint: disable=unused-variable
        """Initiate graphene graphql server"""
        ax_routes.loop = _loop
        ax_routes.app = _app
        ax_routes.init_graphql_view()
        # _app.add_route(ax_routes.graphql_view, '/api/graphql')

    # Initiate all sanic server routes
    ax_routes.init_routes(sanic_app=app)
    # Initiate SQL dialects module. Different SQL queries for differents DBs
    ax_dialects.init_dialects(os.environ.get('AX_DB_DIALECT') or 'sqlite')


ax_logo = """

                                           .
                                          .(
       ..                                 /(#
       ...           --- AX ---          ,/((////.
       ...,,                             ***(/////,
     ****,,,*/                          (****((///*
      ****///////                   ./(((#***/((/*,,,.
      ,/**////////((((/,      ,(((((((((/((**,.,..
        # (///((((((((((((#((((((((((////* ..
          # (((((((((((((##((((((((((((///,
             .#(((((((  ##(((((((((((((///
                       # (###/      /(///
                      # (//,
                      # (#            (//

"""


def main():
    """Main function"""
    # try:
    #     import googleclouddebugger
    #     googleclouddebugger.enable()
    # except ImportError:
    #     pass

    arguments = docopt(__doc__)

    host = str(os.environ.get('AX_HOST') or '127.0.0.1')
    port = int(os.environ.get('AX_PORT') or 8080)
    debug = bool(os.environ.get('AX_SANIC_DEBUG') or False)
    access_log = bool(os.environ.get('AX_SANIC_ACCESS_LOG') or False)

    if arguments['--host']:
        host = arguments['--host']

    if arguments['--port']:
        port = int(arguments['--port'])

    print(ax_logo)
    logger.info('Running Ax on {host}:{port}', host=host, port=port)
    app.run(host=host, port=port, debug=debug, access_log=access_log)


app = Sanic()
init_ax()

if __name__ == "__main__":
    main()
