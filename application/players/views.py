from flask import render_template, request, redirect, url_for

from application import app, db
from application.players.models import Player
from application.players.forms import PlayerForm

@app.route("/players/new/")
def players_form():
    return render_template("players/new.html", form = PlayerForm())


@app.route("/players/", methods=["POST"])
def players_create():
    form = PlayerForm(request.form)

    p = Player(form.firstname.data, form.lastname.data, form.number.data)


    db.session().add(p)
    db.session().commit()

    return redirect(url_for("players_index"))

@app.route("/players/", methods=["GET"])
def players_index():
    return render_template("players/list.html", players = Player.query.all())