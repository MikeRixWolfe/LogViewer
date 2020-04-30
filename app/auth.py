from flask import render_template, flash, redirect, request, url_for, Blueprint
from flask_login import current_user, login_required, login_user, logout_user

from app import app, db, login
from app.models import User
from app.forms import LoginForm, SignupForm


bp = Blueprint('auth', __name__, url_prefix='/logviewer')


@login.user_loader
def load_user(username):
    return User.query.get(username)


@bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('logs.search'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(Username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        flash('You have successfully logged in!', 'success')
        return redirect(request.args.get("next") or url_for('logs.search'))

    #if form.errors:
    #    if isinstance(form.errors, dict):
    #        flash(form.errors.values(), 'danger')

    return render_template('login.html', form=form)


@bp.route('/signup', methods=['GET','POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('logs.search'))

    form = SignupForm()
    if form.validate_on_submit():
        if form.signup_code.data != app.config['SIGNUP_CODE']:
            flash('Incorrect signup code.', 'warning')
            return redirect(url_for('auth.signup'))

        user = User(form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html', title='Sign Up', form=form)


@bp.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
