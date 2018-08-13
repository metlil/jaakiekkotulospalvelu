from flask import render_template, request, redirect, url_for
from application import app, db
from application.goal.forms import GoalForm
from application.goal.models import Goal
from application.players.models import Player
from application.game.models import Game

@app.route("/goals/", methods=["GET"])
def goals_index():
    return render_template("goals/list.html", goals=Goal.query.all())

@app.route("/goals/new/")
def goals_form():
    form = GoalForm()
    players = Player.query.order_by('lastname')
    games = Game.query.all()
    form.player_id.choices =[(player.id, player.lastname) for player in players]
    form.game_id.choices = [(game.id, game.id) for game in games]
    return render_template("goals/new.html", form=form)

@app.route("/goals/", methods=["POST"])
def goals_create():
    form = GoalForm(request.form)

    goal = Goal(form.player_id.data, form.game_id.data, form.time.data)
    db.session().add(goal)
    db.session().commit()

    return redirect(url_for("goals_index"))


def goals_save_modified_data(goal_id):
    form = GoalForm(request.form)
    goal = Goal.query.get(goal_id)

    goal.player_id = form.player_id.data
    goal.game_id = form.game_id.data
    goal.time = form.time.data

    db.session().commit()

    return redirect(url_for("goals_index"))

def goals_show_update_form(goal_id):
    goal = Goal.query.get(goal_id)
    form = GoalForm()
    players = Player.query.order_by('lastname')
    games = Game.query.all()
    form.player_id.choices = [(player.id, player.lastname) for player in players]
    form.game_id.choices = [(game.id, game.id) for game in games]
    form.player_id.data = goal.player_id
    form.game_id.data = goal.game_id
    form.time.data = goal.time

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
