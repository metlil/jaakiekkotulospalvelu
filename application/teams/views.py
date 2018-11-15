from flask import redirect, request, url_for
from flask_login import current_user

from application import app, db, get_render_page_function, login_required
from application.teams.forms import TeamForm
from application.teams.models import Team

render_page = get_render_page_function('teams')


@app.route("/teams/", methods=["GET"])
def teams_index():
    return render_page("teams/list.html", teams=Team.query.all())


@app.route("/teams/new/")
@login_required(role="ADMIN")
def teams_form():
    return render_page("teams/new.html", form=TeamForm())


@app.route("/teams/", methods=["POST"])
@login_required(role="ADMIN")
def teams_create():
    form = TeamForm(request.form)

    t = Team(form.name.data, form.city.data)

    db.session().add(t)
    db.session().commit()

    return redirect(url_for("team_page", team_id=t.id))


@app.route("/teams/<team_id>/", methods=["GET", "POST"])
def team_page(team_id):
    if request.method == 'POST':
        return teams_save_modified_data(team_id)
    else:
        return teams_update_form(team_id)


@app.route("/teams/<team_id>/delete", methods=["POST"])
def team_delete(team_id):
    team = Team.query.get(team_id)
    db.session().delete(team)
    db.session().commit()
    return redirect(url_for("teams_index"))


def teams_update_form(team_id):
    team = Team.query.get(team_id)
    form = TeamForm()
    form.name.data = team.name
    form.city.data = team.city
    return render_page("teams/update.html",
                       form=form,
                       team=team,
                       team_id=team_id,
                       current_members=Team.find_current_players(team_id))


def teams_save_modified_data(team_id):
    form = TeamForm(request.form)
    t = Team(form.name.data, form.city.data)
    t2 = Team.query.get(team_id)
    t2.name = t.name
    t2.city = t.city
    db.session().commit()

    return redirect(url_for("team_page", team_id=team_id))
