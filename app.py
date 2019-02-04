"""Main flask application script
Contains GraphQL imports and main views
"""

import os
import flask
from flask_cors import CORS
from flask_graphql import GraphQLView
import backend.axy_model as axy_model
import backend.axy_graphql as axy_graphql
import backend.axy_misc as axy_misc


app = flask.Flask(__name__, static_folder="./dist/static",
                  template_folder="./dist")


def main():
    """Main function"""
    CORS(app, resources={r"/api/*": {"origins": "*"}}
         )  # Apply CORS to enable cross-domain requests
    # Load configuration from app.yaml Horrible mistake
    axy_misc.load_configuration(app.root_path)
    view_func = GraphQLView.as_view(
        'graphql',
        schema=axy_graphql.schema,
        graphiql=True,
        context={'session': axy_model.db_session}
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

    print(os.environ['AXY_VERSION'])
    return ret_str


@app.route('/install')
def install():
    """Initial install view"""
    axy_model.Base.metadata.create_all(axy_model.engine)
    return 'Done'


if __name__ == "__main__":
    main()
    app.run(
        host='127.0.0.1',
        port=8080,
        debug=True
    )
