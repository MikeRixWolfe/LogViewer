from datetime import datetime
from flask import abort, render_template, request, Blueprint
from flask_login import login_required

from app import app, db
from app.forms import SearchForm
from app.models import Log, Quote
from app.tokenize import build_query
from app.util import format_line, format_quote


bp = Blueprint('logs', __name__, url_prefix='/logviewer')


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    try:
        form = SearchForm()
        query = form.search.data
        logs = []

        if form.validate_on_submit():
            logs = db.session.query(Log) \
                .filter(db.text("logfts MATCH '{}'".format(build_query(query.replace("'", "''").replace('"', '""'))))) \
                .order_by(db.desc(db.cast(Log.uts, db.Float))).limit(100).all()

            logs = [format_line(line.to_dict(), True) for line in logs
                if line.action not in ['PING', 'NOTICE']]

        return render_template('search.html', form=form, logs=logs, query=query)
    except Exception as ex:
        abort(400, ex)


@bp.route('/<chan>/<date>', defaults={'time': None}, methods=['GET'])
@bp.route('/<chan>/<date>/<time>', methods=['GET'])
@login_required
def index(chan, date, time):
    try:
        chan = chan[:15]

        logs = db.session.query(Log) \
            .filter(db.text("logfts MATCH '(chan:\"#{}\" OR chan:\"nick\" OR chan:\"quit\") AND time:\"{}\"'".format(chan, date))) \
            .all()

        logs = [format_line(line.to_dict()) for line in logs
            if line.action not in ['PING', 'NOTICE']]

        return render_template('index.html', logs=logs, ts=time)
    except Exception as ex:
        abort(400, ex)


@bp.route('/quotes', methods=['GET'])
@login_required
def quotes():
    try:
        page = request.args.get('page', None)
        if page == 'all':
            quotes = db.session.query(Quote).all()
        elif page == 'deleted':
            quotes = db.session.query(Quote).filter(Quote.active=='0').all()
        else:
            quotes = db.session.query(Quote).filter(Quote.active=='1').all()

        quotes = [format_quote(quote.to_dict()) for quote in quotes]

        return render_template('quotes.html', quotes=quotes)
    except Exception as ex:
        abort(400, ex)

