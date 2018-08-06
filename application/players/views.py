from flask import render_template, request, redirect, url_for

from application import app, db
from application.players.forms import PlayerForm
from application.players.models import Player
from application.teams.models import Team


@app.route("/players/new/")
def players_form():
    form = PlayerForm()
    form.team_id.choices = [(team.id, team.name) for team in Team.query.order_by('name')]
    return render_template("players/new.html", form=form)


@app.route("/players/", methods=["POST"])
def players_create():
    form = PlayerForm(request.form)

    p = Player(form.firstname.data, form.lastname.data, form.number.data)
    p.team_id = form.team_id.data
    db.session().add(p)
    db.session().commit()

    return redirect(url_for("players_index"))


@app.route("/players/", methods=["GET"])
def players_index():
    return render_template("players/list.html", players=Player.query.all())


@app.route("/players/<player_id>/", methods=["GET", "POST"])
def player_page(player_id):
    if request.method == 'POST':
        return players_modify(player_id)
    else:
        return players_update_form(player_id)


@app.route("/players/<player_id>/delete", methods=["POST"])
def player_delete(player_id):
    player = Player.query.get(player_id)
    db.session().delete(player)
    db.session().commit()
    return redirect(url_for("players_index"))


def players_update_form(player_id):
    player = Player.query.get(player_id)
    form = PlayerForm()
    form.firstname.data = player.firstname
    form.lastname.data = player.lastname
    form.number.data = player.number
    form.team_id.data = player.team_id
    form.team_id.choices = [(team.id, team.name) for team in Team.query.order_by('name')]
    return render_template("players/update.html", form=form, player_id=player_id)


def players_modify(player_id):
    form = PlayerForm(request.form)

    p = Player(form.firstname.data, form.lastname.data, form.number.data)
    p2 = Player.query.get(player_id)
    p2.firstname = p.firstname
    p2.lastname = p.lastname
    p2.number = p.number
    p2.team_id = form.team_id.data

    db.session().commit()

    return redirect(url_for("players_index"))
