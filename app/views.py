from datetime import datetime
from flask import abort, redirect, render_template, url_for, Blueprint, Markup
from flask_login import login_required
from re import compile, sub, IGNORECASE
from time import localtime, strftime

from app import app, db
from app.forms import SearchForm
from app.models import Log, Quote
from app.tokenize import build_query
from app.util import color_hash


bp = Blueprint('logs', __name__, url_prefix='/logviewer')

url_re = compile(r'(https?:\/\/(?:www\.)?([^: \/]+\.[^: \/]+)(?::\d+)?\/?[^\" ]*)', IGNORECASE)
irc_color_re = compile(r'(\x03(\d{1,2}(,\d{1,2})?)|[\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\x7f])')
formats = {
    'PRIVMSG': u'{time} < <span style="color: {color}">{nick}</span>> {msg}',
    'ACTION': u'{time} {msg}',
    'PART': u'{time} -!- {nick} [{user}] has left {chan} [{msg}]',
    'JOIN': u'{time} -!- {nick} [{user}] has joined {chan}',
    'MODE': u'{time} -!- mode/{chan} [{msg}] by {nick}',
    'KICK': u'{time} -!- {who} was kicked from {chan} by {nick} with reason {msg}',
    'TOPIC': u'{time} -!- {nick} changed the topic of {chan} to: {msg}',
    'QUIT': u'{time} -!- {nick} has quit IRC [{msg}]',
    'NICK': u'{time} -!- {nick} [{user}] is now known as {msg}',
}


@bp.route('/', methods=['GET'])
@bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    try:
        form = SearchForm()
        query = form.search.data
        logs = []

        if form.validate_on_submit():
            logs = db.session.query(Log) \
                .filter(db.text("logfts MATCH '{}'".format(build_query(form.search.data)))) \
                .order_by(db.desc(db.cast(Log.uts, db.Integer))).limit(50).all()

            logs = [line.to_dict() for line in logs]

            for line in logs:
                line['link'] = '/logviewer/{}/{}/{}'.format(line['chan'].strip('#'), *line['time'].split())
                line['time'] = line['time'][11:]

                line['msg'] = irc_color_re.sub('', line['msg'])
                line['msg'] = str(Markup.escape(line['msg'].encode('ascii', 'ignore')))
                line['msg'] = url_re.sub(r'<a href="\1">\1</a>', line['msg'])

                if line['action'] == 'KICK':
                    line['who'], line['msg'] = line['msg'].split(' ', 1)

                line['msg'] = Markup(formats[line['action']].format(color=color_hash(line['nick']), **line))

            logs = [line for line in logs if line['action'] not in ['PING', 'NOTICE']]

        return render_template('search.html', form=form, logs=logs, query=query)
    except Exception as ex:
        abort(400, ex)


@bp.route('/quotes', methods=['get'])
@login_required
def quotes():
    try:
        quotes = db.session.query(Quote).filter(Quote.active == '1').all()
        quotes = [quote.to_dict() for quote in quotes]

        for quote in quotes:
            quote['date'] = "{} {}".format(
                "Early" if int(strftime("%d", localtime(float(quote['uts'])))) < 15 else "Late",
                strftime("%b %Y", localtime(float(quote['uts']))))

        return render_template('quotes.html', quotes=quotes)
    except Exception as ex:
        abort(400, ex)


@bp.route('/<chan>/<date>', defaults={'time': None}, methods=['GET'])
@bp.route('/<chan>/<date>/<time>', methods=['GET'])
@login_required
def index(chan, date, time):
    try:
        chan = chan[:15]
        if date: datetime.strptime(date, "%Y-%m-%d")
        if time: datetime.strptime(time, "%H:%M:%S")

        logs = db.session.query(Log) \
            .filter(db.text("logfts MATCH 'chan:\"#{}\" AND time:\"{}\"'".format(chan, date))) \
            .all()

        logs = [line.to_dict() for line in logs]

        for line in logs:
            line['time'] = line['time'][11:]

            line['msg'] = irc_color_re.sub('', line['msg'])
            line['msg'] = str(Markup.escape(line['msg'].encode('ascii', 'ignore')))
            line['msg'] = url_re.sub(r'<a href="\1">\1</a>', line['msg'])

            if line['action'] == 'KICK':
                line['who'], line['msg'] = line['msg'].split(' ', 1)

        logs = [Markup(formats[line['action']].format(color=color_hash(line['nick']),
            **line)) for line in logs if line['action'] not in ['PING', 'NOTICE']]

        return render_template('index.html', logs=logs, ts=time)
    except Exception as ex:
        abort(400, ex)

