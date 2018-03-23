from flask import redirect, render_template, request, url_for

from application import app, db
from application.teams.models import Team


@app.route("/teams/", methods=["GET"])
def teams_index():
    return render_template("teams/list.html", teams=Team.query.all())


@app.route("/teams/new/")
def teams_form():
    return render_template("teams/new.html")


def teams_update_form(team_id):
    return render_template("teams/update.html", team=Team.query.get(team_id))


def teams_modify(team_id):
    form = request.form
    t = Team(form.get("name"), form.get("city"))
    t2 = Team.query.get(team_id)
    t2.name = t.name
    t2.city = t.city
    db.session().commit()

    return redirect(url_for("teams_index"))


@app.route("/teams/<team_id>/", methods=["GET", "POST"])
def team_page(team_id):
    if request.method == 'POST':
        return teams_modify(team_id)
    else:
        return teams_update_form(team_id)


@app.route("/teams/", methods=["POST"])
def teams_create():
    form = request.form
    t = Team(form.get("name"), form.get("city"))

    db.session().add(t)
    db.session().commit()

    return redirect(url_for("teams_index"))
