from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class Message(db.Model):
    __tablename__ = 'Message'

    MessageSid = db.Column(db.String, primary_key=True)
    AccountSid = db.Column(db.String)
    ApiVersion = db.Column(db.String)
    Body = db.Column(db.String)
    From = db.Column(db.String)
    To = db.Column(db.String)
    MediaUrl = db.Column(db.String, nullable=True)
    DateReceived = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, MessageSid, AccountSid, ApiVersion,
                 Body, From, To, MediaUrl):
        self.MessageSid = MessageSid
        self.AccountSid = AccountSid
        self.ApiVersion = ApiVersion
        self.Body = Body
        self.From = From
        self.To = To
        self.MediaUrl = MediaUrl


class Phonebook(db.Model):
    __tablename__ = 'Phonebook'

    Name = db.Column(db.String, primary_key=True)
    Number = db.Column(db.String)

    def __init__(self, name, number):
        self.Name = name
        self.Number = number


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

