from flask import Flask, session
from flask.ext.session import Session
from config import Config

app = Flask(__name__)
# app.config.from_object(Config)
sess = Session()
app.secret_key = 'You Will Never Guess'
# bootstrap = Bootstrap(app)

from app import routes
