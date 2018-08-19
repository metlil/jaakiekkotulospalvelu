from flask import render_template, request, redirect, url_for

from application import app, db
from application.game.forms import GameForm
from application.game.game_status import GameStatus
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

    g = Game(form.home_id.data, form.guest_id.data, form.time.data, Team.query.get(form.home_id.data).city, GameStatus.SCHEDULED)
    db.session().add(g)
    db.session().commit()

    return redirect(url_for("games_index"))


def games_save_modified_data(game_id):
    game = Game.query.get(game_id)
    copy_form_data_to_game(game, request.form)
    db.session().commit()

    return redirect(url_for("games_index"))


def copy_form_data_to_game(game, request_form):
    form = GameForm(request_form)
    game.home_id = form.home_id.data
    game.guest_id = form.guest_id.data
    game.time = form.time.data
    game.place = Team.query.get(form.home_id.data).city


def games_show_update_form(game_id):
    game = Game.query.get(game_id)
    form = GameForm()
    teams = Team.query.order_by('name')
    form.home_id.choices = [(team.id, team.name) for team in teams]
    form.guest_id.choices = [(team.id, team.name) for team in teams]
    form.home_id.data = game.home_id
    form.guest_id.data = game.guest_id
    form.time.data = game.time
    if game.status == GameStatus.STARTING:
        form.time.render_kw={'disabled': True}
        form.home_id.render_kw={'disabled': True}
        form.guest_id.render_kw={'disabled': True}

    return render_template("games/update.html", form=form, game_id=game_id, game_status=game.status.value)


def confirm_game(game_id):
    game = Game.query.get(game_id)
    copy_form_data_to_game(game, request.form)
    game.status = GameStatus.STARTING
    db.session().commit()

    return redirect(url_for("game_page", game_id=game_id))


@app.route("/games/<game_id>/", methods=["GET", "POST"])
def game_page(game_id):
    if request.method == 'POST':
        if 'update_game' in set(request.form):
            return games_save_modified_data(game_id)
        if 'confirm_game' in set(request.form):
            return confirm_game(game_id)
        #myy
    else:
        return games_show_update_form(game_id)

@app.route("/games/<game_id>/delete", methods=["POST"])
def game_delete(game_id):
    game = Game.query.get(game_id)
    db.session().delete(game)
    db.session().commit()
    return redirect(url_for("games_index"))
