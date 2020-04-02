from datetime import datetime
from flask import abort, render_template, Blueprint, Markup
from flask_login import login_required
from re import compile, sub, IGNORECASE

from app import app, db
from app.models import Log
from app.util import color_hash


bp = Blueprint('logs', __name__, url_prefix='/logviewer')

url_re = compile(r'(https?:\/\/(?:www\.)?([^: \/]+\.[^: \/]+)(?::\d+)?\/?[^\" ]*)', IGNORECASE)


@bp.route('/search', methods=['GET'])
@login_required
def search():
    try:
        return render_template('search.html')
    except Exception as ex:
        abort(400, ex)


@bp.route('/', defaults={'chan': None, 'date': None, 'time': None}, methods=['GET'])
@bp.route('/<chan>', defaults={'date': None, 'time': None}, methods=['GET'])
@bp.route('/<chan>/<date>', defaults={'time': None}, methods=['GET'])
@bp.route('/<chan>/<date>/<time>', methods=['GET'])
@login_required
def index(chan, date, time):
    formats = {
        #'PRIVMSG': u'{time} < {nick}> {msg}',
        'PRIVMSG': u'{time} < <span style="color: {color}">{nick}</span>> {msg}',
        'ACTION': u'{time} {msg}',
        'PART': u'{time} -!- {nick} [{user}] has left {chan} [{msg}]',
        'JOIN': u'{time} -!- {nick} [{user}] has joined {chan}',
        'MODE': u'{time} -!- mode/{chan} [{msg}] by {nick}',
        'KICK': u'{time} -!- {nick} was kicked from {chan} by {msg}',
        'TOPIC': u'{time} -!- {nick} changed the topic of {chan} to: {msg}',
        'QUIT': u'{time} -!- {nick} has quit IRC [{msg}]',
        'NICK': u'{time} -!- {nick} [{user}] is now known as {msg}',
    }

    if not chan or not date:
        return render_template('index.html', logs=[], ts=None)

    try:
        if date: datetime.strptime(date, "%Y-%m-%d")
        if time: datetime.strptime(time, "%H:%M:%S")

        logs = db.session.query(Log) \
            .filter(db.text("logfts MATCH 'chan:\"#{}\" AND time:\"{}\"'".format(chan, date))) \
            .all()

        for line in logs:
            line.time = line.time[11:]
            line.msg = str(Markup.escape(line.msg.encode('ascii', 'ignore')))
            line.msg = url_re.sub(r'<a href="\1">\1</a>', line.msg)

        logs = [Markup(formats[line.action].format(color=color_hash(line.nick),
            **line.to_dict())) for line in logs if line.action not in ['PING', 'NOTICE']]

        return render_template('index.html', logs=logs, ts=time)
    except Exception as ex:
        abort(400, ex)

