"""Runneble script"""
import os

from sanic_graphql import GraphQLView
from sanic import Sanic, response
from sanic.response import json
from sanic_cors import CORS

from graphql_ws.websockets_lib import WsLibSubscriptionServer
from graphql.execution.executors.asyncio import AsyncioExecutor

# from aiocache import caches, SimpleMemoryCache, RedisCache
# from aiocache.serializers import JsonSerializer

import backend.misc as ax_misc
ax_misc.load_configuration()  # Load config from app.yaml


from backend.cache import cache, init_cache
# init_cache()

from backend.schema import ax_schema
import backend.model as ax_model


# init_schema()


app = Sanic()
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
CORS(app, automatic_options=True)

app.static('/static', './dist/static')
app.static('/stats', './dist/stats.html')
app.static('/test_webpack', './dist/test.html')


@app.listener('before_server_start')
def init_graphql(_app, loop):
    """Initiate graphql"""

    graphql_view = GraphQLView.as_view(schema=ax_schema,
                                       graphiql=False,
                                       executor=AsyncioExecutor(loop=loop))
    _app.add_route(graphql_view, '/api/graphql')


subscription_server = WsLibSubscriptionServer(ax_schema)


@app.route('/draw_ax')
async def draw_ax(request):
    """Outputs bundle.js with right headers"""
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
    return response.html(open('./dist/index.html').read())


@app.route("/install")
async def install(request):
    """Initial install view"""
    del request
    ax_model.Base.metadata.create_all(ax_model.engine)
    return json({"status": "Install Done"})


@app.route('/api/hello')
async def hello(request):
    """Test function"""
    object_id = request.raw_args['object_id']
    ret_str = 'Ajax object_id = ' + object_id
    return response.text(ret_str)


@app.route('/api/set')
async def cache_set(request):
    """Test function"""
    obj = ['one', 'two', 'three']
    await cache.set('user_list', obj)
    return response.text('Cache SET' + str(obj))


@app.route('/api/get')
async def cache_get(request):
    """Test function"""
    del request
    obj = await cache.get('user_list')
    ret_str = 'READ cache == ' + \
        str(obj[0].username + ' - ' + os.environ['AX_VERSION'])
    return response.text(ret_str)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
