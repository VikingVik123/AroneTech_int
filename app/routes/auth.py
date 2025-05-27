from flask import Blueprint, request, jsonify, flash, redirect, url_for, render_template
from flask_login import login_user, logout_user, current_user, login_required
from app.models.users import User
from app.databases.db import db


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def index():
    """Render the home page."""
    return ("Welcome to the Basic Flask App!")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Register a new user."""
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        if not username or not email or not password:
            flash("All fields are required.")
            return redirect(url_for("auth.register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful! Please log in.")
        return redirect(url_for("auth.login"))
    return render_template('register.html')


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Log in a user."""
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        if not email or not password:
            flash("Email and password are required.")
            return redirect(url_for("auth.login"))
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!")
            return redirect(url_for("auth.dashboard"))
        else:
            flash("Invalid email or password.")
            return redirect(url_for("auth.login"))
    return render_template('login.html')


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=current_user.username)