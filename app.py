"""Main flask application script
Contains GraphQL imports and main views
"""

import os
import flask
from flask_cors import CORS
from flask_graphql import GraphQLView
import backend.model as ax_model
import backend.schema as ax_schema
import backend.misc as ax_misc


app = flask.Flask(__name__, static_folder="./dist/static",
                  template_folder="./dist")


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
    ret_str = 'Ajax object_id=' + object_id
    return ret_str


@app.route('/install')
def install():
    """Initial install view"""
    ax_model.Base.metadata.create_all(ax_model.engine)
    return 'Done'


if __name__ == "__main__":
    main()
    debug = True
    if 'AX_MODE' in os.environ:
        if os.environ['AX_MODE'] == 'BROWSER_DEBUG':
            debug = True
        if os.environ['AX_MODE'] == 'VSCODE':
            debug = False

    app.run(
        host='127.0.0.1',
        port=8080,
        debug=debug
    )