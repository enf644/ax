"""All routes of ax-core and ax-admin"""

import os
import sys
import asyncio
from sanic import response
# from sanic.views import HTTPMethodView
from loguru import logger
from graphql_ws.websockets_lib import WsLibSubscriptionServer
from sanic_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor
import aiopubsub

import backend.cache as ax_cache
import backend.schema as ax_schema
# import backend.model as ax_model
# import backend.dialects as ax_dialects
import backend.misc as ax_misc
import backend.pubsub as ax_pubsub
# import sqlite3


this = sys.modules[__name__]

loop = None
app = None
graphql_view = None
dummy_view = None
test_schema = 'WTF'


class AxGraphQLView(GraphQLView):
    """ Extends GraphQLView to output GQL errors and schema updates"""

    def __init__(self, **kwargs):
        super().__init__(schema=ax_schema.schema,
                         graphiql=False,
                         executor=AsyncioExecutor(loop=this.loop))

    @staticmethod
    def format_error(error):
        logger.error(error)
        return GraphQLView.format_error(error)


# class DummyView(HTTPMethodView):
#     schema = None

#     def __init__(self, **kwargs):
#         for key, value in kwargs.items():
#             if hasattr(self, key):
#                 setattr(self, key, value)

#     def get(self, request, *args, **kwargs):
#         return response.text(f'I am get method with {self.schema}')


# class AxDummyView(DummyView):
#     updated_schema = None

    # async def set_schema(self, key, message):
    #     print(f"Hello from pubsub - {message}")
    #     self.updated_schema = message
    #     # super().schema = message
    #     super().__init__(schema=self.updated_schema)

    # def __init__(self, **kwargs):
        # subscriber = aiopubsub.Subscriber(ax_pubsub.hub, 'dummy_subscriber')
        # subscriber.add_async_listener(
        #     aiopubsub.Key('dummy_test'), self.set_schema)

        # self.updated_schema = this.test_schema + " with Ax!"
        # super().__init__(schema=self.updated_schema)


def init_graphql_view():  # pylint: disable=unused-variable
    """Initiate graphql"""
    this.graphql_view = AxGraphQLView.as_view()
    this.app.add_route(this.graphql_view, '/api/graphql')

    # dummy_view = AxDummyView.as_view(schema=this.test_schema)
    # this.app.add_route(dummy_view, '/api/help')


def init_routes(app):
    """Innitiate all Ax routes"""
    try:
        subscription_server = WsLibSubscriptionServer(ax_schema.schema)

        @app.route('/<path:path>')
        def index(request, path):  # pylint: disable=unused-variable
            """Catch all requests"""
            del request, path
            absolute_path = ax_misc.path('dist/index.html')
            return response.html(open(absolute_path).read())

        @app.route('/draw_ax')
        async def draw_ax(request):  # pylint: disable=unused-variable
            """Outputs bundle.js with right headers"""
            del request
            absolute_path = ax_misc.path('dist/static/js/ax-bundle.js')
            return await response.file(
                absolute_path,
                headers={
                    'Content-Type': 'application/javascript; charset=utf-8'
                }
            )

        @app.websocket('/api/subscriptions', subprotocols=['graphql-ws'])
        async def subscriptions(request, web_socket):  # pylint: disable=unused-variable
            """Web socket route for graphql subscriptions"""
            del request
            try:
                # TODO: Why socket error exception occurs without internet
                await subscription_server.handle(web_socket)
                return web_socket
            except asyncio.CancelledError:
                pass
                # logger.exception('Socket error')

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

        @app.route('/api/test')
        async def test(request):  # pylint: disable=unused-variable
            """Test function"""
            del request
            this.test_schema = 'IT WORKS'
            ax_pubsub.publisher.publish(
                aiopubsub.Key('dummy_test'), this.test_schema)
            return response.text(this.test_schema)

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
