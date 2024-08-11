from flask import Flask

app = Flask(__name__)
app.config.from_object('app.config.Config')
from app.routes.api_routes import *