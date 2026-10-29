from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from . import db
from .models import User
from .security import hash_password, verify_password

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password1")

        user = User.query.filter_by(email=email).first()
        if user:
            valid, needs_rehash = verify_password(user.password, password)
            if valid:
                if needs_rehash:  # upgrade a legacy hash now that we have the plaintext
                    user.password = hash_password(password)
                    db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for("views.configureDashboard"))
            flash("Incorrect Password, try again", category="error")
        else:
            flash("Email does not exist.", category="error")

    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/signup", methods=["GET", "POST"])
def sig_up():
    if request.method == "POST":
        email = request.form.get("email") or ""
        password1 = request.form.get("password1") or ""
        password2 = request.form.get("password2") or ""
        first_name = request.form.get("fullname") or ""
        user_type = request.form.get("radio")

        if User.query.filter_by(email=email).first():
            flash("This Email already exists", category="error")
        elif len(first_name) < 3:
            flash("User name must be greater than 2 characters", category="error")
        elif len(email) < 8:
            flash("Please user a valid email address", category="error")
        elif password1 != password2:
            flash("passwords don't match.", category="error")
        elif not password1:
            flash("Please choose a password.", category="error")
        else:
            new_user = User(
                email=email,
                first_name=first_name,
                password=hash_password(password1),
                type=user_type,
            )
            db.session.add(new_user)
            db.session.commit()
            flash("Your account was successfully created.", category="success")
            return redirect(url_for("auth.login"))

    return render_template("signup.html", user=current_user)
