from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__, static_url_path='/logviewer/static')
app.config.from_pyfile('app.cfg')
app.url_map.strict_slashes = False

db = SQLAlchemy(app)

login = LoginManager(app)
#login.init_app(app)
login.login_view = 'auth.login'
login.login_message_category = 'info'

from app import auth, errors, views
app.register_blueprint(auth.bp)
app.register_blueprint(views.bp)

