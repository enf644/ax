import sys
sys.path.append('backend')
sys.path.append('backend/graphql')

import os
import flask
from flask_cors import CORS
import six
from flask_graphql import GraphQLView
import axy_model
import axy_graphql
import axy_misc

app = flask.Flask(__name__,
            static_folder = "./dist/static",
            template_folder = "./dist")
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
axy_misc.load_configuration(app.root_path)

view_func = GraphQLView.as_view(
                'graphql', 
                schema=axy_graphql.schema, 
                graphiql=True, 
                context={'session': axy_model.db_session}
            )
app.add_url_rule('/graphql', view_func=view_func)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return flask.render_template("index.html")

@app.route('/api/hello')
def show_users():
    object_id =  flask.request.args.get('object_id')
    str = 'Ajax object_id=' + object_id

    print(os.environ['AXY_VERSION'])
    return str
    
@app.route('/install')
def install():
    axy_model.Base.metadata.create_all(axy_model.engine)
    return 'Done'
    
if __name__ == "__main__":
    app.run(
        host = os.getenv('IP', '0.0.0.0'), 
        port = int(os.getenv('PORT', 8080)), 
        debug = True
    )