# auth.py
from flask import Blueprint, request, redirect, url_for, session, flash, render_template
from werkzeug.security import generate_password_hash
from ..extensions import db
from ..models import User

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user is None or not user.verify_password(password):
            flash('Invalid email or password')
            return redirect(url_for('.login'))

        session['user_id']
