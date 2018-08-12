from flask import render_template, request, redirect, url_for

from application import app, db
from application.game.forms import GameForm
from application.game.models import Game
from application.teams.models import Team


@app.route("/games/", methods=["GET"])
def games_index():
    return render_template("games/list.html", games=Game.query.all())


@app.route("/games/new/")
def games_form():
    form = GameForm()
    teams = Team.query.order_by('name')
    form.home_id.choices = [(team.id, team.name) for team in teams]
    form.guest_id.choices = [(team.id, team.name) for team in teams]
    return render_template("games/new.html", form=form)


@app.route("/games/", methods=["POST"])
def games_create():
    form = GameForm(request.form)

    g = Game(form.home_id.data, form.guest_id.data, form.time.data, Team.query.get(form.home_id.data).city)
    db.session().add(g)
    db.session().commit()

    return redirect(url_for("games_index"))
