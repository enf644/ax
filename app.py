
from sanic_graphql import GraphQLView
from sanic import Sanic, response
from sanic.response import json

import backend.misc as ax_misc
from backend.schema import ax_schema
# import backend.model as ax_model

from graphql_ws.websockets_lib import WsLibSubscriptionServer
from graphql.execution.executors.asyncio import AsyncioExecutor

import sys
import os

"""Main flask application script
Contains GraphQL imports and main views
"""

app = Sanic()
app.static('/static', './dist/static')
app.static('/', './dist/index.html')


@app.listener('before_server_start')
def init_graphql(app, loop):
    app.add_route(GraphQLView.as_view(schema=ax_schema,
                                      graphiql=True,
                                      executor=AsyncioExecutor(loop=loop)),
                  '/graphql')

# app.add_route(GraphQLView.as_view(schema=ax_schema, graphiql=True), '/graphql')


subscription_server = WsLibSubscriptionServer(ax_schema)


@app.websocket('/api/subscriptions', subprotocols=['graphql-ws'])
async def subscriptions(request, ws):
    await subscription_server.handle(ws)
    return ws


# @sockets.route('/api/subscriptions')
# def gql_socket(ws):
#     subscription_server.handle(ws)
#     return []


# @sockets.route('/api/echo')
# def echo_socket(ws):
#     while True:
#         message = ws.receive()
#         ws.send(message[::-1])


# @app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def catch_all(path):
#     """Main view - index.html"""
#     print(path)
#     return flask.render_template("index.html")


# @app.route('/install')
# def install():
#     """Initial install view"""
#     ax_model.Base.metadata.create_all(ax_model.engine)
#     return 'Done'

@app.route("/hello")
async def test(request):
    return json({"hello": "world 22"})


@app.route('/api/hello')
async def hello(request):
    """Test function"""
    object_id = request.raw_args['object_id']
    ret_str = 'Ajax object_id = ' + object_id
    return response.text(ret_str)


if __name__ == "__main__":
    ax_misc.load_configuration()  # Load config from app.yaml
    app.run(host="127.0.0.1", port=8080, debug=True)
