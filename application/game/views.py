from flask import render_template, request, redirect, url_for

from application import app, db
from application.game.forms import GameForm
from application.game.game_status import GameStatus
from application.game.models import Game
from application.lineup.forms import LineupForm
from application.lineup.models import LineupEntry
from application.memberships.models import Membership
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

    g = Game(form.home_id.data, form.guest_id.data, form.time.data, Team.query.get(form.home_id.data).city,
             GameStatus.SCHEDULED)
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
    # kun on vahvistettu
    if game.status != GameStatus.SCHEDULED:
        form.time.render_kw = {'disabled': True}
        form.home_id.render_kw = {'disabled': True}
        form.guest_id.render_kw = {'disabled': True}
        home_memberships = Membership.query.filter(Membership.team_id == game.home_id).all()
        guest_memberships = Membership.query.filter(Membership.team_id == game.guest_id).all()
        lineup_entries = LineupEntry.query.filter(LineupEntry.game_id == game_id).all()
        home_lineup_entries = [x for x in lineup_entries if x.membership_id in set([y.id for y in home_memberships])]
        guest_lineup_entries = [x for x in lineup_entries if x.membership_id in set([y.id for y in guest_memberships])]
        home_lineup_form = populate_lineup_form(home_lineup_entries, home_memberships)
        guest_lineup_form = populate_lineup_form(guest_lineup_entries, guest_memberships)
        return render_template("games/update.html", form=form, game_id=game_id, game_status=game.status.value,
                               home_lineup_form=home_lineup_form, guest_lineup_form=guest_lineup_form)

    return render_template("games/update.html", form=form, game_id=game_id, game_status=game.status.value)


def populate_lineup_form(lineup_entries, memberships):
    # TODO check membership validity period
    lineup_min = 3
    lineup_max = 3
    lineup_form = LineupForm()
    for lineup_entry in lineup_entries:
        if len(lineup_form.lineup_entries) == lineup_max:
            break
        lineup_form.lineup_entries.append_entry()
        lineup_entry_form = lineup_form.lineup_entries[-1]
        lineup_entry_form.membership_id.data = lineup_entry.membership_id
        lineup_entry_form.membership_id.choices = [format_membership_for_dropdown(y) for y in memberships]
        lineup_entry_form.membership_id.choices.append((-1, ''))
    # default
    while len(lineup_form.lineup_entries) < lineup_max:
        lineup_form.lineup_entries.append_entry()
        lineup_entry_form = lineup_form.lineup_entries[-1]
        lineup_entry_form.membership_id.choices = [(-1, '')]
        lineup_entry_form.membership_id.choices.extend([format_membership_for_dropdown(y) for y in memberships])
        selected_entry_ids = set([y.membership_id.data for y in lineup_form.lineup_entries])
        not_selected_entries = [x.id for x in memberships if x.id not in selected_entry_ids]
        if len(not_selected_entries) > 0:
            lineup_entry_form.membership_id.data = not_selected_entries[0]
    return lineup_form


def format_membership_for_dropdown(membership: Membership):
    return (membership.id, membership.player.firstname + " " + membership.player.lastname)


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
        # myy
    else:
        return games_show_update_form(game_id)


@app.route("/games/<game_id>/delete", methods=["POST"])
def game_delete(game_id):
    game = Game.query.get(game_id)
    db.session().delete(game)
    db.session().commit()
    return redirect(url_for("games_index"))
