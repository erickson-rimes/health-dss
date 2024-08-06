import dash
import dash_bootstrap_components as dbc
import pandas as pd

from flask import Flask, redirect, request, url_for, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_dance.consumer import OAuth2ConsumerBlueprint
from keycloak import KeycloakOpenID
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin, SQLAlchemyStorage
import os

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Create the Flask server
server = Flask(__name__)
server.secret_key = os.urandom(24)  # Use a strong, random secret key

# Configure server-side sessions
server.config["SESSION_TYPE"] = "filesystem"
server.config["SESSION_PERMANENT"] = False
server.config["SESSION_USE_SIGNER"] = True
server.config["SESSION_KEY_PREFIX"] = "myapp_"
Session(server)

# Setup SQLAlchemy
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
db = SQLAlchemy(server)

class OAuth(OAuthConsumerMixin, db.Model):
    pass

# Create tables within application context
with server.app_context():
    db.create_all()

# Keycloak Configuration
KEYCLOAK_SERVER_URL = 'http://localhost:8051/'
REALM_NAME = 'CRISH'
CLIENT_ID = 'crish-web-app'
CLIENT_SECRET = 'Xx4lBaLqDrCXF4h1XKT1PzQ6A1YOhSS5'  # Replace with the actual client secret

keycloak_openid = KeycloakOpenID(server_url=KEYCLOAK_SERVER_URL,
                                 client_id=CLIENT_ID,
                                 realm_name=REALM_NAME,
                                 client_secret_key=CLIENT_SECRET)

# OAuth2 Blueprint
blueprint = OAuth2ConsumerBlueprint(
    "crish-app",
    __name__,
    base_url=f'{KEYCLOAK_SERVER_URL}realms/{REALM_NAME}/protocol/openid-connect',
    token_url=f'{KEYCLOAK_SERVER_URL}realms/{REALM_NAME}/protocol/openid-connect/token',
    authorization_url=f'{KEYCLOAK_SERVER_URL}realms/{REALM_NAME}/protocol/openid-connect/auth',
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_to="/",  # Redirect to the home page after login
    storage=SQLAlchemyStorage(OAuth, db.session, user=None),
)

server.register_blueprint(blueprint, url_prefix="/login")

# Check if user is authenticated
def is_authenticated():
    return blueprint.session.authorized

def is_token_valid():
    if is_authenticated():
        token = blueprint.session.token["access_token"]
        try:
            keycloak_openid.userinfo(token)
            return True
        except Exception:
            return False
    return False

@server.before_request
def before_request():
    if is_authenticated() and request.path.startswith("/logout"):
        session.clear()
        return redirect(url_for('crish-app.login'))
    elif (not is_authenticated() or not is_token_valid()) and not request.path.startswith("/login"):
        blueprint.session.token = None  # Clear the token
        return redirect(url_for('crish-app.login'))

# @server.route('/logout')
# def logout():
#     session.clear()
#     return redirect(url_for('crish-app.login'))

my_app = dash.Dash(
    __name__,
    server=server,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.MATERIA, dbc.icons.FONT_AWESOME],
)
my_app.title = "Health DSS"
# server = my_app.server

# import the dataset
url = "../data/train.json"
df = pd.read_json(url)