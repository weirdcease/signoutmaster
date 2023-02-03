from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from datetime import datetime

import tools

con = sqlite3.connect(tools.inst("signout.db"), check_same_thread=False)
cur = con.cursor()

signout = Blueprint("signout", __name__)

ALLOWED_USERNAME = "abcdefghijklmnopqrstuvwxyz1234567890_-"

def now(): return int(datetime.timestamp(datetime.now()))

def check_user():
    if ("user_id" not in session) or (not session["user_id"]):
        return False
    
    user = cur.execute(
        "SELECT username FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    if not user:
        session.clear()
        return False

    return True

def no_user():
    flash("error:You must be signed in!")
    return redirect(url_for("signout.login"))

# if not check_user(): return no_user()

@signout.app_template_filter("split")
def my_split(text: str, splitter: str):
    return text.split(splitter)

@signout.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, post-check=0, pre-check=0"
    return response

@signout.route("/")
def home():
    return render_template("home.html")

@signout.route("/register")
def register():
    return render_template("register.html")

@signout.route("/register/handler", methods=["POST"])
def register_handler():
    username = request.form.get("username")
    password = request.form.get("password")

    try:
        cur.execute(
            "INSERT INTO users (username, password_hash, config) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), "{}")
        )
    except sqlite3.IntegrityError:
        return "already exists"
    else:
        con.commit()
    
    flash("success:Account {username} successfully created. You can now login.")
    return redirect(url_for("signout.login"))

@signout.route("/login")
def login():
    return render_template("login.html")

@signout.route("/login/handler", methods=["POST"])
def login_handler():
    username = request.form.get("username")
    password = request.form.get("password")

    user = cur.execute(
        "SELECT id, password_hash FROM users WHERE username = ?", (username,)
    ).fetchone()

    if user:
        if check_password_hash(user[1], password):
            session.clear()
            session["user_id"] = user[0]
            flash(f"success:Successfully signed in as {username}!")
            return redirect(url_for("signout.panel"))

        else:
            flash("error:Incorrect password!")

    else:
        flash("error:That account doesn't exist!")

    return redirect(url_for("signout.login"))

@signout.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("signout.home"))

@signout.route("/panel")
def panel():
    if not check_user(): return no_user()

    username = cur.execute(
        "SELECT username FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()[0]

    return render_template("panel.html", username=username)

@signout.route("/panel/settings")
def settings():
    if not check_user(): return no_user()

    return render_template("settings.html")

@signout.route("/panel/settings/apply")
def apply_settings():
    if not check_user(): return no_user()
    # ...
    flash("success:Applied changes!")
    return redirect(url_for("signout.settings"))

@signout.route("/panel/monitor")
def monitor():
    if not check_user(): return no_user()

    return "monitoring page"

@signout.route("/panel/student")
def student():
    if not check_user(): return no_user()

    return "student panel"

@signout.route("/panel/sign", methods=["POST"])
def sign():
    if not check_user(): return no_user()

    return "signing out or in"

@signout.route("/share/<public_id>")
def student_public(public_id):
    return "student panel public share link"