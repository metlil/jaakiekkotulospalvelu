import datetime

from flask import request, redirect, url_for
from flask_login import login_required

from application import app, db, get_render_page_function
from application.game.forms import GameForm
from application.game.game_status import GameStatus
from application.game.models import Game
from application.goal.forms import GoalForm
from application.goal.models import Goal
from application.goal.views import parse_time_from_view
from application.lineup.forms import GameLineupForm
from application.lineup.models import LineupEntry
from application.memberships.models import Membership
from application.teams.models import Team

lineup_min = 3
lineup_max = 3
render_page = get_render_page_function('games')


@app.route("/games/", methods=["GET"])
def games_index():
    return render_page("games/list.html", games=Game.query.order_by(Game.time).all())


@app.route("/games/new/")
@login_required
def games_form():
    form = GameForm()
    teams = Team.query.order_by('name')
    form.home_id.choices = [(team.id, team.name) for team in teams]
    form.guest_id.choices = [(team.id, team.name) for team in teams]
    return render_page("games/new.html", form=form)


@app.route("/games/", methods=["POST"])
@login_required
def games_create():
    form = GameForm(request.form)

    g = Game(form.home_id.data, form.guest_id.data, form.time.data, Team.query.get(form.home_id.data).city,
             GameStatus.SCHEDULED)
    db.session().add(g)
    db.session().commit()

    return redirect(url_for("game_page", game_id=g.id))


@app.route("/games/<game_id>/", methods=["GET", "POST"])
def game_page(game_id):
    if request.method == 'POST':
        if 'update_game' in set(request.form):
            return games_save_modified_data(game_id)
        if 'confirm_game' in set(request.form):
            return confirm_game(game_id)
        if 'confirm_lineup' in set(request.form):
            return save_modified_game_lineup(game_id)
        if 'add_goal' in set(request.form):
            return goals_create(game_id)
        # if 'finish_game' in set(request.form):
        #     return finish_game(game_id)
    else:
        return games_show_update_form(game_id)


@app.route("/games/<game_id>/delete", methods=["POST"])
def game_delete(game_id):
    game = Game.query.get(game_id)
    db.session().delete(game)
    db.session().commit()
    return redirect(url_for("games_index"))


@app.route("/games/<game_id>/finish", methods=["POST"])
def finish_game(game_id):
    game = Game.query.get(game_id)
    # copy_form_data_to_game(game, request.form)
    game.status = GameStatus.FINISHED
    db.session().commit()

    return redirect(url_for("game_page", game_id=game_id))


def games_save_modified_data(game_id):
    game = Game.query.get(game_id)
    copy_form_data_to_game(game, request.form)
    db.session().commit()

    return redirect(url_for("game_page", game_id=game_id))


def copy_form_data_to_game(game, request_form):
    form = GameForm(request_form)
    game.home_id = form.home_id.data
    game.guest_id = form.guest_id.data
    game.time = form.time.data
    game.place = Team.query.get(form.home_id.data).city


def games_show_update_form(game_id, error=''):
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
        game_lineup_form = GameLineupForm()
        populate_lineup_form(home_lineup_entries, home_memberships, game_lineup_form.home_lineup, game.time,
                             game.status)
        populate_lineup_form(guest_lineup_entries, guest_memberships, game_lineup_form.guest_lineup, game.time,
                             game.status)
        home_goals_form = GoalForm()
        home_goals_form.team_id.data = game.home_id
        home_goals_form.scorer_id.choices = [format_lineup_entry_for_dropdown(lineup_entry) for lineup_entry in
                                             home_lineup_entries]
        guest_goals_form = GoalForm()
        guest_goals_form.team_id.data = game.guest_id
        guest_goals_form.scorer_id.choices = [format_lineup_entry_for_dropdown(lineup_entry) for lineup_entry in
                                              guest_lineup_entries]
        return render_page(
            "games/update.html",
            form=form,
            game_id=game_id,
            game=game,
            game_lineup_form=game_lineup_form,
            home_team_goals=Goal.team_goals(game.home_id, game_id),
            guest_team_goals=Goal.team_goals(game.guest_id, game_id),
            home_goals_form=home_goals_form,
            guest_goals_form=guest_goals_form,
            error=error,
            home_team_players=Game.team_lineup(game_id, game.home_id),
            guest_team_players=Game.team_lineup(game_id, game.guest_id)
        )

    return render_page("games/update.html", form=form, game_id=game_id, game=game, error=error)


def populate_lineup_form(lineup_entries, memberships, lineup_form, start_time, game_status):
    # TODO check membership validity period
    for lineup_entry in lineup_entries:
        if len(lineup_form.lineup_entries) == lineup_max:
            break
        lineup_form.lineup_entries.append_entry()
        lineup_entry_form = lineup_form.lineup_entries[-1]
        lineup_entry_form.membership_id.data = lineup_entry.membership_id
    # default
    while len(lineup_form.lineup_entries) < lineup_max:
        lineup_form.lineup_entries.append_entry()
        lineup_entry_form = lineup_form.lineup_entries[-1]
        selected_entry_ids = set([y.membership_id.data for y in lineup_form.lineup_entries])
        not_selected_entries = [x.id for x in memberships if
                                x.id not in selected_entry_ids and is_member_during_game(x, start_time)]
        if len(not_selected_entries) > 0:
            lineup_entry_form.membership_id.data = not_selected_entries[0]
    for lineup_entry_form in lineup_form.lineup_entries.entries:
        lineup_entry_form.membership_id.choices = [(-1, '')]
        lineup_entry_form.membership_id.choices.extend(
            [format_membership_for_dropdown(y) for y in memberships if is_member_during_game(y, start_time)]
        )
        if game_status == GameStatus.ONGOING or game_status == GameStatus.FINISHED:
            lineup_entry_form.membership_id.render_kw = {'disabled': True}


def format_membership_for_dropdown(membership: Membership):
    return (membership.id, membership.player.firstname + " " + membership.player.lastname)


def format_lineup_entry_for_dropdown(lineup_entry: LineupEntry):
    return (lineup_entry.id, lineup_entry.membership.player.firstname + " " + lineup_entry.membership.player.lastname)


def confirm_game(game_id):
    game = Game.query.get(game_id)
    copy_form_data_to_game(game, request.form)
    game.status = GameStatus.STARTING
    db.session().commit()

    return redirect(url_for("game_page", game_id=game_id))


def validate_game_lineup_form(game_lineup_form):
    def lineup_valid(lineup):
        return len(lineup) == len(set(lineup)) and lineup_min <= len(lineup) <= lineup_max

    home_membership_ids = [x.membership_id.data for x in game_lineup_form.home_lineup.lineup_entries.entries]
    guest_membership_ids = [x.membership_id.data for x in game_lineup_form.guest_lineup.lineup_entries.entries]
    # Remove empty values
    home_membership_ids = [x for x in home_membership_ids if x != -1]
    guest_membership_ids = [x for x in guest_membership_ids if x != -1]
    # Should be unique
    return lineup_valid(home_membership_ids) and lineup_valid(guest_membership_ids)


def save_modified_game_lineup(game_id):
    game_lineup_form = GameLineupForm(request.form)
    valid = validate_game_lineup_form(game_lineup_form)
    if not valid:
        return games_show_update_form(game_id, error='Lineup is not valid. Lineup contains atleast '
                                                     + str(lineup_min) + ' and atmost ' + str(lineup_max) + ' entries.')
    game = Game.query.get(game_id)
    form_membership_ids = []
    form_membership_ids.extend([x.membership_id.data for x in game_lineup_form.home_lineup.lineup_entries.entries])
    form_membership_ids.extend([x.membership_id.data for x in game_lineup_form.guest_lineup.lineup_entries.entries])
    # Remove empty values
    form_membership_ids = set([x for x in form_membership_ids if x != -1])

    new_lineup = []
    deleted_lineup = []
    for lineup_entry in game.lineup:
        if lineup_entry.membership_id in form_membership_ids:
            new_lineup.append(lineup_entry)
        else:
            deleted_lineup.append(lineup_entry)
    new_membership_ids = set([x.membership_id for x in new_lineup])
    new_lineup.extend([LineupEntry(game_id, x) for x in form_membership_ids if x not in new_membership_ids])
    game.lineup = new_lineup
    for deleted_lineup_entry in deleted_lineup:
        db.session().delete(deleted_lineup_entry)
    game.status = GameStatus.ONGOING
    db.session().commit()
    return games_show_update_form(game_id)


def is_member_during_game(x: Membership, game_start: datetime):
    if game_start.date() < x.membership_start:
        return False
    if x.membership_end is None:
        return True
    return game_start.date() < x.membership_end


# maalilogiikkaa
def goals_create(game_id):
    form = GoalForm(request.form)
    try:
        start_time = parse_time_from_view(form.time.data)
    except Exception as e:
        return games_show_update_form(game_id, error=str(e))
    goal = Goal(form.scorer_id.data, game_id, start_time, form.team_id.data)
    db.session().add(goal)
    db.session().commit()

    return redirect(url_for("game_page", game_id=game_id))
