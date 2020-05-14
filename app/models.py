from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

class SerializableModel(object):
    def to_dict(self):
        value = {}
        for column in self.__table__.columns:
            attribute = getattr(self, column.name)
            if isinstance(attribute, datetime):
                attribute = str(attribute)
            value[column.name] = attribute
        return value


class Log(db.Model, SerializableModel):
    __tablename__ = 'logfts'

    time = db.Column(db.Text)
    server = db.Column(db.Text)
    chan = db.Column(db.Text)
    nick = db.Column(db.Text, primary_key=True)
    user = db.Column(db.Text)
    action = db.Column(db.Text)
    msg = db.Column(db.Text, primary_key=True)
    uts = db.Column(db.Text, primary_key=True)


class Quote(db.Model, SerializableModel):
    __tablename__ = 'quotefts'

    id = db.Column(db.Text, primary_key=True)
    msg = db.Column(db.Text)
    nick = db.Column(db.Text)
    active = db.Column(db.Text)
    uts = db.Column(db.Text)


class User(UserMixin, db.Model):
    __tablename__ = 'User'

    Username = db.Column(db.String, primary_key=True)
    Password = db.Column(db.String)
    Authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, username):
        self.Username = username

    def set_password(self, password):
        self.Password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.Password, password)

    def get_id(self):
        return self.Username

