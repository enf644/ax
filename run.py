from flask import Flask, render_template, jsonify
from random import *
from flask_cors import CORS
import requests
import os

app = Flask(__name__,
            static_folder = "./dist/static",
            template_folder = "./dist")
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html")
    
if __name__ == "__main__":
    app.run(
        host = os.getenv('IP', '0.0.0.0'), 
        port = int(os.getenv('PORT', 8080)), 
        debug = True
    )