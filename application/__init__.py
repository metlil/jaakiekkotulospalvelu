# flask- sovellus

from flask import Flask, render_template

app = Flask(__name__)

# tietokanta
from flask_sqlalchemy import SQLAlchemy

import os

if os.environ.get("HEROKU"):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///jaakiekkotulospalvelu.db"
    # Pyydetään SQLAlchemyä tulostamaan kaikki SQL-kyselyt
    app.config["SQLALCHEMY_ECHO"] = True

# Luodaan db-olio, jota käytetään tietokannan käsittelyyn
db = SQLAlchemy(app)


def get_render_page_function(state):
    def render_page(template, **kwargs):
        kwargs['state'] = state
        return render_template(template, **kwargs)

    return render_page


# oman sovelluksen toiminnalisuudet
from application import views

from application.teams import models
from application.teams import views

from application.players import models
from application.players import views

from application.memberships import models

from application.lineup import models

from application.auth import models
from application.auth import views

from application.game import models
from application.game import views

from application.goal import models

# kirjautuminen
from application.auth.models import User
from os import urandom

app.config["SECRET_KEY"] = urandom(32)

from flask_login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "auth_login"
login_manager.login_message = "Please login to use this functionality."


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# Luodaan lopulta tarvittavat tietokantataulut
try:
    db.create_all()
except:
    pass

import argparse
from application.test_data import import_test_data


@app.before_first_request
def before_first_request():
    # Should be after start up
    parser = argparse.ArgumentParser()
    parser.add_argument('--import-data', action='store_true')
    args = parser.parse_args()
    if args.import_data:
        import_test_data()
