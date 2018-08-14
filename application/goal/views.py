from datetime import time

from flask import render_template, request, redirect, url_for

from application import app, db
from application.game.models import Game
from application.goal.forms import GoalForm
from application.goal.models import Goal
from application.players.models import Player


@app.route("/goals/", methods=["GET"])
def goals_index():
    return render_template("goals/list.html", goals=Goal.query.all())


@app.route("/goals/new/")
def goals_form():
    form = populate_goal_form(GoalForm())
    return render_template("goals/new.html", form=form)


@app.route("/goals/", methods=["POST"])
def goals_create():
    form = GoalForm(request.form)
    try:
        start_time = parse_time_from_view(form.time.data)
    except Exception as e:
        form = populate_goal_form(form)
        return render_template("goals/new.html", form=form, error=str(e))
    goal = Goal(form.player_id.data, form.game_id.data, start_time)
    db.session().add(goal)
    db.session().commit()

    return redirect(url_for("goals_index"))


def goals_save_modified_data(goal_id):
    form = GoalForm(request.form)
    goal = Goal.query.get(goal_id)

    goal.player_id = form.player_id.data
    goal.game_id = form.game_id.data
    try:
        goal.time = parse_time_from_view(form.time.data)
    except Exception as e:
        form = populate_goal_form(form)
        return render_template("goals/update.html", form=form, goal_id=goal_id, error=str(e))
    db.session().commit()

    return redirect(url_for("goals_index"))


def goals_show_update_form(goal_id):
    goal = Goal.query.get(goal_id)
    form = populate_goal_form(GoalForm())
    form.player_id.data = goal.player_id
    form.game_id.data = goal.game_id
    form.time.data = format_time_for_view(goal.time)

    return render_template("goals/update.html", form=form, goal_id=goal_id)


@app.route("/goals/<goal_id>/", methods=["GET", "POST"])
def goal_page(goal_id):
    if request.method == 'POST':
        return goals_save_modified_data(goal_id)
    else:
        return goals_show_update_form(goal_id)


@app.route("/goals/<goal_id>/delete", methods=["POST"])
def goal_delete(goal_id):
    goal = Goal.query.get(goal_id)
    db.session().delete(goal)
    db.session().commit()
    return redirect(url_for("goals_index"))


def parse_time_from_view(view_time):
    if ":" not in view_time:
        raise ValueError("Could not find value separator")
    times = view_time.split(":", 1)
    try:
        seconds = int(times[1])
    except ValueError:
        raise ValueError("Seconds was expected to be an integer")
    try:
        minutes = int(times[0])
    except ValueError:
        raise ValueError("Minutes was expected to be an integer")
    if seconds < 0 or 60 <= seconds:
        raise ValueError("Seconds was expected to be between 0 and 59")
    if minutes < 0:
        raise ValueError("Minutes was expected to non negative")
    return time(hour=int(minutes / 60), minute=minutes % 60, second=seconds)


def format_time_for_view(game_time: time):
    minutes = 60 * game_time.hour + game_time.minute
    return str(minutes) + ":" + str(game_time.second)


def populate_goal_form(form):
    players = Player.query.order_by('lastname')
    games = Game.query.all()
    form.player_id.choices = [(player.id, player.lastname) for player in players]
    form.game_id.choices = [(game.id, game.id) for game in games]
    return form
