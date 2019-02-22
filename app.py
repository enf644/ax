import gevent.monkey
gevent.monkey.patch_all()

from geventwebsocket.handler import WebSocketHandler
from gevent import pywsgi
import werkzeug.serving
import backend.misc as ax_misc
import backend.schema as ax_schema
import backend.model as ax_model
from graphql_ws.gevent import GeventSubscriptionServer
from flask_sockets import Sockets
from flask_graphql import GraphQLView
from flask_cors import CORS
import flask
import sys
import os


"""Main flask application script
Contains GraphQL imports and main views
"""

app = flask.Flask(__name__, static_folder="./dist/static",
                  template_folder="./dist")
sockets = Sockets(app)
subscription_server = GeventSubscriptionServer(ax_schema.schema)
app.app_protocol = lambda environ_path_info: 'graphql-ws'


def main():
    """Main function"""

    CORS(app, resources={r"/api/*": {"origins": "*"}}
         )  # Apply CORS to enable cross-domain requests

    ax_misc.load_configuration(app.root_path)  # Load config from app.yaml

    view_func = GraphQLView.as_view(
        'graphql',
        schema=ax_schema.schema,
        graphiql=True,
        context={'session': ax_model.db_session}
    )
    app.add_url_rule('/graphql', view_func=view_func)  # Initiate GraphQL View


@sockets.route('/api/subscriptions')
def gql_socket(ws):
    subscription_server.handle(ws)
    return []


@sockets.route('/api/echo')
def echo_socket(ws):
    while True:
        message = ws.receive()
        ws.send(message[::-1])


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    """Main view - index.html"""
    print(path)
    return flask.render_template("index.html")


@app.route('/api/hello')
def show_users():
    """Test function"""
    object_id = flask.request.args.get('object_id')
    ret_str = 'Ajax object_id = ' + object_id
    return ret_str


@app.route('/install')
def install():
    """Initial install view"""
    ax_model.Base.metadata.create_all(ax_model.engine)
    return 'Done'


# @werkzeug.serving.run_with_reloader
def runServer():
    app.debug = False
    server = pywsgi.WSGIServer(
        ('127.0.0.1', 8080), app, handler_class=WebSocketHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
    runServer()

    # app.run(
    #     host='127.0.0.1',
    #     port=8080,
    #     debug=True
    # )
