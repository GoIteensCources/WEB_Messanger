from flask import Flask, abort, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from app import app
from models import User
from settings import DatabaseConfig, Session


@app.route("/")
def index():
    return render_template("base.html")

@app.route("/account/admin/")
@login_required
def admin_panel():
    # Перевіряти роль користувача перед відображенням сторінки
    if not current_user.is_admin:
        abort(403)
    return "Ласкаво просимо до адмін-панелі!"


@app.route("/account")
@login_required
def account():
    return render_template("account.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        hashed = generate_password_hash(password)

        user = User.get_by_username(username)
        if user:
            flash("Користувач з таким ім'ям вже існує. Спробуйте інше ім'я.")
            return redirect(url_for("register"))
        else:
            new_user = User(username=username, password=hashed, email=email)

            with Session() as session_db:
                session_db.add(new_user)
                session_db.commit()

            flash("Реєстрація успішна, увійдіть у свій акаунт.")
            return redirect(url_for("login"))

    return render_template("auth/register.html", title="Реєстрація")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.get_by_username(username)

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Вхід успішний!")
            return redirect(url_for("index"))
        else:
            flash("Невірне ім'я користувача або пароль.")
            return redirect(url_for("login"))
    return render_template("auth/login.html", title="Вхід")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))
