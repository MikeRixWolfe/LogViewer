from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import current_user, login_required

from app import app, db, login
from app.models import Message, Phonebook


bp = Blueprint('logs', __name__, url_prefix='/logviewer')


@bp.route('/', defaults={'name': None}, methods=['GET'])
@bp.route('/<name>', methods=['GET'])
@login_required
def index(name):
    if name:
        messages = db.session.query(Message, Phonebook) \
            .outerjoin(Phonebook, Phonebook.Number==Message.From) \
            .filter(Message.AccountSid==app.config['TWILIO_ACCOUNT_SIDS_CSV']) \
            .filter(Message.To==app.config['PHONE_NUMBER']) \
            .filter(Message.MediaUrl!=None) \
            .filter(Phonebook.Name==name) \
            .order_by(Message.DateReceived.desc()) \
            .all()
    else:
        messages = db.session.query(Message, Phonebook) \
            .outerjoin(Phonebook, Phonebook.Number==Message.From) \
            .filter(Message.AccountSid==app.config['TWILIO_ACCOUNT_SIDS_CSV']) \
            .filter(Message.To==app.config['PHONE_NUMBER']) \
            .filter(Message.MediaUrl!=None) \
            .filter(Phonebook.Name!=None) \
            .order_by(Message.DateReceived.desc()) \
            .all()

    phonebook = db.session.query(Phonebook) \
        .outerjoin(Message, Phonebook.Number==Message.From) \
        .filter(Message.AccountSid==app.config['TWILIO_ACCOUNT_SIDS_CSV']) \
        .filter(Message.To==app.config['PHONE_NUMBER']) \
        .filter(Message.MediaUrl!=None) \
        .filter(Phonebook.Name!=None) \
        .order_by(Phonebook.Name.asc()) \
        .distinct(Phonebook.Name)

    return render_template('index.html', msgs=messages, pb=phonebook)


@bp.route('/image/<sid>', methods=['GET'])
@login_required
def image(sid):
    messages = db.session.query(Message, Phonebook) \
        .outerjoin(Phonebook, Phonebook.Number==Message.From) \
        .filter(Message.AccountSid==app.config['TWILIO_ACCOUNT_SIDS_CSV']) \
        .filter(Message.To==app.config['PHONE_NUMBER']) \
        .filter(Message.MediaUrl!=None) \
        .filter(Phonebook.Name!=None) \
        .filter(Message.MessageSid==sid) \
        .all()

    phonebook = db.session.query(Phonebook) \
        .outerjoin(Message, Phonebook.Number==Message.From) \
        .filter(Message.AccountSid==app.config['TWILIO_ACCOUNT_SIDS_CSV']) \
        .filter(Message.To==app.config['PHONE_NUMBER']) \
        .filter(Message.MediaUrl!=None) \
        .filter(Phonebook.Name!=None) \
        .order_by(Phonebook.Name.asc()) \
        .distinct(Phonebook.Name)

    return render_template('image.html', msgs=messages, pb=phonebook)

