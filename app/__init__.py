from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config.from_object('app.config.Config')
from app.routes.api_routes import *