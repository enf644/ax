"""Runneble script"""
import os
from sanic_graphql import GraphQLView
from sanic import Sanic, response
# from sanic.response import json
from sanic_cors import CORS
from loguru import logger

from graphql_ws.websockets_lib import WsLibSubscriptionServer
from graphql.execution.executors.asyncio import AsyncioExecutor

import backend.logger as ax_logger
import backend.misc as ax_misc
import backend.cache as ax_cache
import backend.schema as ax_schema
# import backend.model as ax_model
import backend.pubsub as ax_pubsub
import backend.scheduler as ax_scheduler
import backend.migration as ax_migration

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
async def initialize_ax(_app, _loop):
    """Initiate scheduler"""
    ax_scheduler.init_scheduler()


@app.listener('before_server_start')
async def initialize_scheduler(_app, _loop):
    """Initiate scheduler"""
    ax_scheduler.init_scheduler()


@app.listener('before_server_start')
def init_graphql(_app, loop):
    """Initiate graphql"""

    graphql_view = GraphQLView.as_view(schema=ax_schema.schema,
                                       graphiql=False,
                                       executor=AsyncioExecutor(loop=loop))
    _app.add_route(graphql_view, '/api/graphql')


subscription_server = WsLibSubscriptionServer(ax_schema.schema)


@app.route('/draw_ax')
async def draw_ax(request):
    """Outputs bundle.js with right headers"""
    del request
    return await response.file(
        './dist/static/js/ax-bundle.js',
        headers={'Content-Type': 'application/javascript; charset=utf-8'}
    )


@app.websocket('/api/subscriptions', subprotocols=['graphql-ws'])
async def subscriptions(request, web_socket):
    """Web socket route for graphql subscriptions"""
    del request
    await subscription_server.handle(web_socket)
    return web_socket


@app.route('/<path:path>')
def index(request, path):
    """Catch all requests"""
    del request, path
    return response.html(open('./dist/index.html').read())


@app.route("/install")
async def install(request):
    """Initial install view"""
    del request


@app.route('/api/hello')
async def hello(request):
    """Test function"""
    object_id = request.raw_args['object_id']
    ret_str = 'Ajax object_id = ' + object_id
    return response.text(ret_str)


@app.route('/api/set')
async def cache_set(request):
    """Test function"""
    del request
    obj = ['one', 'two', 'three']
    await ax_cache.cache.set('user_list', obj)
    return response.text('Cache SET' + str(obj))


@app.route('/api/get')
async def cache_get(request):
    """Test function"""
    del request
    obj = await ax_cache.cache.get('user_list')
    ret_str = 'READ cache == ' + \
        str(obj[0].username + ' - ' + os.environ['AX_VERSION'])
    return response.text(ret_str)


if __name__ == "__main__":
    logger.info('Ax. Ready to run.')
    # TODO Take debug and access logs from app.yaml
    app.run(host="127.0.0.1", port=8080, debug=True, access_log=False)
