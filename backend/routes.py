"""All routes of ax-core and ax-admin"""

import os
from sanic import response
from loguru import logger
from graphql_ws.websockets_lib import WsLibSubscriptionServer
import backend.cache as ax_cache
import backend.schema as ax_schema


def init_routes(app):
    """Innitiate all Ax routes"""
    try:
        subscription_server = WsLibSubscriptionServer(ax_schema.schema)

        @app.route('/draw_ax')
        async def draw_ax(request):  # pylint: disable=unused-variable
            """Outputs bundle.js with right headers"""
            del request
            return await response.file(
                './dist/static/js/ax-bundle.js',
                headers={
                    'Content-Type': 'application/javascript; charset=utf-8'
                }
            )

        @app.websocket('/api/subscriptions', subprotocols=['graphql-ws'])
        async def subscriptions(request, web_socket):  # pylint: disable=unused-variable
            """Web socket route for graphql subscriptions"""
            del request
            await subscription_server.handle(web_socket)
            return web_socket

        @app.route('/<path:path>')
        def index(request, path):  # pylint: disable=unused-variable
            """Catch all requests"""
            del request, path
            return response.html(open('./dist/index.html').read())

        @app.route("/install")
        async def install(request):  # pylint: disable=unused-variable
            """Initial install view"""
            del request

        @app.route('/api/hello')
        async def hello(request):  # pylint: disable=unused-variable
            """Test function"""
            object_id = request.raw_args['object_id']
            ret_str = 'Ajax object_id = ' + object_id
            return response.text(ret_str)

        @app.route('/api/set')
        async def cache_set(request):  # pylint: disable=unused-variable
            """Test function"""
            del request
            obj = ['one', 'two', 'three']
            await ax_cache.cache.set('user_list', obj)
            return response.text('Cache SET' + str(obj))

        @app.route('/api/get')
        async def cache_get(request):  # pylint: disable=unused-variable
            """Test function"""
            del request
            obj = await ax_cache.cache.get('user_list')
            ret_str = 'READ cache == ' + \
                str(obj[0].username + ' - ' + os.environ['AX_VERSION'])
            return response.text(ret_str)
    except Exception:
        logger.exception('Error initiating routes.')
        raise
