from datetime import datetime
from flask import abort, render_template, Blueprint, Markup
from flask_login import login_required
from re import sub, IGNORECASE

from app import app, db
from app.models import Log


bp = Blueprint('logs', __name__, url_prefix='/logviewer')


@bp.route('/', defaults={'chan': None, 'date': None}, methods=['GET'])
@bp.route('/<chan>/<date>', methods=['GET'])
@login_required
def index(chan, date):
    formats = {
        'PRIVMSG': '{time} < {nick}> {msg}',
        'PART': '{time} -!- {nick} [{user}] has left {chan} [{msg}]',
        'JOIN': '{time} -!- {nick} [{user}] has joined {chan}',
        'MODE': '{time} -!- mode/{chan} [{msg}] by {nick}',
        'KICK': '{time} -!- {nick} was kicked from {chan} by {msg}',
        'TOPIC': '{time} -!- {nick} changed the topic of {chan} to: {msg}',
        'QUIT': '{time} -!- {nick} has quit IRC [{msg}]',
        'NICK': '{time} -!- {nick} [{user}] is now known as {msg}',
    }

    if chan == date:
        return render_template('index.html', logs=[])

    try:
        datetime.strptime(date, "%Y-%m-%d")  # input validation

        logs = db.session.query(Log) \
            .filter(db.text(f"logfts MATCH 'chan:\"{chan}\" AND time:\"{date}\"'")) \
            .all()

        for line in logs:
            line.time = line.time[11:]
            line.msg = str(Markup.escape(line.msg))
            line.msg = sub(r'(https?:\/\/(?:www\.)?([^: \/]+\.[^: \/]+)(?::\d+)?\/?\S*)',
                           r'<a href="\1">\1</a>', line.msg, flags=IGNORECASE)

        logs = [Markup(formats[line.action].format(**line.to_dict()))
                for line in logs if line.action not in ['PING', 'NOTICE']]

        return render_template('index.html', logs=logs)
    except Exception as ex:
        abort(400, ex)


