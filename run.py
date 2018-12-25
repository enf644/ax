import flask
import flask_cors
import os
import sys

sys.path.append('backend')
import axy_misc

app = flask.Flask(__name__,
            static_folder = "./dist/static",
            template_folder = "./dist")
cors = flask_cors.CORS(app, resources={r"/api/*": {"origins": "*"}})
axy_misc.load_configuration(app.root_path)


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
    
if __name__ == "__main__":
    app.run(
        host = os.getenv('IP', '0.0.0.0'), 
        port = int(os.getenv('PORT', 8080)), 
        debug = True
    )