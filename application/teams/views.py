from flask import redirect, render_template, request, url_for
from flask_login import login_required

from application import app, db
from application.teams.forms import TeamForm
from application.teams.models import Team


@app.route("/teams/", methods=["GET"])
def teams_index():
    return render_template("teams/list.html", teams=Team.query.all())


@app.route("/teams/new/")
@login_required
def teams_form():
    return render_template("teams/new.html", form=TeamForm())


@app.route("/teams/", methods=["POST"])
@login_required
def teams_create():
    form = TeamForm(request.form)

    t = Team(form.name.data, form.city.data)

    db.session().add(t)
    db.session().commit()

    return redirect(url_for("teams_index"))


def teams_update_form(team_id):
    team = Team.query.get(team_id)
    form = TeamForm()
    form.name.data = team.name
    form.city.data = team.city
    return render_template("teams/update.html", form=form, team_id=team_id)


def teams_modify(team_id):
    form = TeamForm(request.form)
    t = Team(form.name.data, form.city.data)
    t2 = Team.query.get(team_id)
    t2.name = t.name
    t2.city = t.city
    db.session().commit()

    return redirect(url_for("teams_index"))


@app.route("/teams/<team_id>/", methods=["GET", "POST"])
@login_required
def team_page(team_id):
    if request.method == 'POST':
        return teams_modify(team_id)
    else:
        return teams_update_form(team_id)


@app.route("/teams/<team_id>/delete", methods=["POST"])
def team_delete(team_id):
    team = Team.query.get(team_id)
    db.session().delete(team)
    db.session().commit()
    return redirect(url_for("teams_index"))
