"""Runneble script"""

from sanic_graphql import GraphQLView
from sanic import Sanic, response
from sanic.response import json
from sanic_cors import CORS

from graphql_ws.websockets_lib import WsLibSubscriptionServer
from graphql.execution.executors.asyncio import AsyncioExecutor

import backend.misc as ax_misc
from backend.schema import ax_schema
import backend.model as ax_model

app = Sanic()
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
CORS(app, automatic_options=True)
app.static('/static', './dist/static')


@app.listener('before_server_start')
def init_graphql(_app, loop):
    """Initiate graphql"""

    graphql_view = GraphQLView.as_view(schema=ax_schema,
                                       graphiql=False,
                                       executor=AsyncioExecutor(loop=loop))
    _app.add_route(graphql_view, '/api/graphql')


subscription_server = WsLibSubscriptionServer(ax_schema)


@app.websocket('/api/subscriptions', subprotocols=['graphql-ws'])
async def subscriptions(request, web_socket):
    """Web socket route for graphql subscriptions"""
    del request
    await subscription_server.handle(web_socket)
    return web_socket


@app.route('/<path:path>')
def index(request, path):
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


if __name__ == "__main__":
    ax_misc.load_configuration()  # Load config from app.yaml
    app.run(host="127.0.0.1", port=8080, debug=True)
