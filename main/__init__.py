from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
pjdir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(pjdir, 'app.db')
app.config['SCHEDULER_API_ENABLED'] = True
db = SQLAlchemy(app)
from main import view
