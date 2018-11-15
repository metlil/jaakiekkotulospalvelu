from flask import request, url_for, redirect, render_template
from flask.ext.login import login_user, logout_user

from application import app, db
from application.auth.forms import LoginForm
from application.auth.forms import RegistrationForm
from application.auth.models import User


@app.route("/auth/login", methods=["GET", "POST"])
def auth_login():
    if request.method == "GET":
        return render_template("auth/loginform.html", form=LoginForm())

    form = LoginForm(request.form)

    user = User.query.filter_by(username=form.username.data, password=form.password.data).first()
    if not user:
        return render_template("auth/loginform.html", form=form, error="No such username or password")

    login_user(user)
    return redirect(request.args.get("next") or url_for("index"))


@app.route("/auth/logout")
def auth_logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/auth/register", methods=["GET", "POST"])
def auth_register():
    if request.method == "GET":
        return render_template("auth/registrationform.html", form=RegistrationForm())

    form = RegistrationForm(request.form)

    user = User.query.filter_by(username=form.username.data).first()
    if user:
        return render_template("auth/registrationform.html", form=form, error="User already exists")

    if form.username.data == '':
        return render_template("auth/registrationform.html", form=form, error="Username empty")

    if form.password.data == '':
        return render_template("auth/registrationform.html", form=form, error="Password empty")

    user = User(form.name.data, form.username.data, form.password.data, "ADMIN")

    db.session().add(user)
    db.session().commit()

    login_user(user)
    return redirect(url_for("index"))
