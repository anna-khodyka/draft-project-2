# pylint: disable=E0402
"""
Blueprint login for Flask application Bot

"""

import sys
import os
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, flash, redirect, render_template, request, session, url_for


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))
if __package__ == "" or __package__ is None:
    import global_var
else:
    from . import global_var


login_bp = Blueprint("login", __name__, url_prefix="/login")


@login_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    GET - prepare login form
    POST - do the login
    """
    if request.method == "POST":
        return do_the_login(request)
    return render_template("login/log.html")


@login_bp.route("/register", methods=("GET", "POST"))
def register():
    """
    Register new user
    GET - prepare register form
    POST - registering user
    :return: redirect to login/register
    """
    if request.method == "POST":
        username = request.form["User_name"]
        login_ = request.form["Login"]
        password = request.form["Password"]
        error = None
        if not username:
            error = "Username is required."
        elif not username:
            error = "Login is required."
        elif not password:
            error = "Password is required."
        if error is None:
            res = global_var.users_db.insert_user(
                username, login_, generate_password_hash(password)
            )
            if not res:
                return redirect(url_for("login.login"))
            error = res
        flash(error)
    return render_template("login/register.html")


def do_the_login(request_):
    """
    Login user using werkzeug security
    :param request_:
    :return: redirect to bot form/login
    """
    login_ = request_.form["Login"]
    password = request_.form["Password"]
    user = global_var.users_db.get_user(login_)
    error = None
    if user is None:
        error = "Incorrect login"
    elif not check_password_hash(user.password, password):
        error = "Incorrect password."
    if error is None:
        session["user_id"] = str(user.user_id)
        session["user"] = user.user_name
        return redirect(url_for("init.bot"))
    flash(error)
    return render_template("login/log.html")


@login_bp.route("/logout", methods=("GET",))
def logout():
    """
    logout current user, session cleared except the state of db
    :return: redirect to login
    """
    session.clear()
    session["user"] = None
    session["db"] = "choosed"
    return redirect(url_for("login.login"))
