from flask import render_template, redirect, url_for, flash, request, session, jsonify
from flask_login import current_user
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse

from finsibility import finsy, login
from finsibility.forms import LoginForm, RegistrationForm
from finsibility.models import User
import finsibility.helper as helper
import finsibility.constants as constants
import finsibility.applicationException as appEx

import os
import json


@finsy.route('/')
def index():
    finsy.logger.debug(os.environ['DATABASE_URL'])
    return render_template('index.html')

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@finsy.route('/login', methods=['GET', 'POST'])
def login():
    finsy.logger.debug("in render login")
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        finsy.logger.debug(f'next: {next_page}')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@finsy.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@finsy.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        helper.register(form)
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))

    return render_template('register.html', title='Register', form=form)

@finsy.route('/upload_positions')
@login_required
def upload_positions():
    return render_template('upload_positions.html')

@finsy.route("/upload_positions_file", methods=['GET', 'POST'])
@login_required
def upload_positions_file():

    try:
        if request.method == 'POST':
            file = request.files['file']
            if not file:
                raise appEx.FileNotChosenException()

            tables, titles, mkt_value, session_data = helper.verify_file(file)

            session_key = str(current_user.id) + '_positions'
            session[session_key] = session_data

            finsy.logger.debug(f"session data: {session_data}")
            finsy.logger.debug(f"session before: {session}")

            return render_template(
                'upload_positions.html',
                tables=tables,
                titles=titles, mkt_value=mkt_value)

    except appEx.ApplicationException as ex:
        flash(ex.msg)
        finsy.logger.critical(ex.msg)
        return render_template('upload_positions.html')
    except Exception as ex:
        flash(constants.UNKNOWN_EXCEPTION)
        #finsy.logger.critical(constants.UNKNOWN_EXCEPTION)
        finsy.logger.critical(ex)
        return render_template('upload_positions.html')

@finsy.route("/save_positions", methods=['GET', 'POST'])
@login_required
def save_positions():
    session_key = str(current_user.id) + '_positions'
    session_data = session.pop(session_key, default=None)

    finsy.logger.debug(f"session data after: {session_data}")
    finsy.logger.debug(f"session after: {session}")

    if session_data:
        positions = session_data['positions']
        file_date = session_data['file_date']

        finsy.logger.debug(f'positions: {positions}')
        finsy.logger.debug(f'file_date: {file_date}')

        try:
            helper.save_data_to_positions(current_user, file_date, 'TD Ameritrade', positions)
            flash('file succesfully saved!')
            return render_template('upload_positions.html')

        except Exception as ex:
            flash('The file could not be saved')
            return render_template('upload_positions.html')
    else:
        flash('The file could not be saved')
        return render_template('upload_positions.html')


@finsy.route("/review_positions", methods=['GET', 'POST'])
@login_required
def review_positions():

    date_value = None

    if request.method == "POST":
        date_value = request.json['date_value']

    try:
        tables = helper.review_positions(date_value)
    except appEx.DataFetchException as ex:
        flash("Positions could not be fetched for this account")
        return render_template('review_positions.html')

    if date_value:
        return jsonify({'tables': tables})
    else:
        return render_template('review_positions.html', tables=tables)

