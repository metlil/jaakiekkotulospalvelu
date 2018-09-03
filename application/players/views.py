from flask import request, redirect, url_for
from flask_login import login_required

from application import app, db, get_render_page_function
from application.memberships.models import Membership
from application.players.forms import PlayerForm
from application.players.models import Player
from application.teams.models import Team

render_page = get_render_page_function('players')


@app.route("/players/new/")
@login_required
def players_form():
    return render_page("players/new.html", form=PlayerForm())


@app.route("/players/", methods=["POST"])
@login_required
def players_create():
    if 'add_membership' in set(request.form):
        form = create_player_form_with_appended_membership(request.form)
        return render_page("players/new.html", form=form)
    form = PlayerForm(request.form)

    p = Player(form.firstname.data, form.lastname.data, form.number.data)
    for membership_data in form.memberships.data:
        p.memberships.append(Membership(membership_data))
    db.session().add(p)
    db.session().commit()
    return redirect(url_for("player_page", player_id=p.id))


@app.route("/players/", methods=["GET"])
def players_index():
    return render_page("players/list.html", players=Player.query.all())


@app.route("/players/<player_id>/", methods=["GET", "POST"])
def player_page(player_id):
    if request.method == 'POST':
        if 'add_membership' in set(request.form):
            # Add membership button was pressed
            form = create_player_form_with_appended_membership(request.form)
            return render_page("players/update.html", form=form, player_id=player_id)
        # Update player information button was pressed
        return players_save_modified_data(player_id)
    else:
        return players_show_update_form(player_id)


@app.route("/players/<player_id>/delete", methods=["POST"])
def player_delete(player_id):
    player = Player.query.get(player_id)
    for membership in player.memberships:
        db.session().delete(membership)
    db.session().delete(player)
    db.session().commit()
    return redirect(url_for("players_index"))


def players_show_update_form(player_id):
    player = Player.query.get(player_id)
    form = PlayerForm()
    form.firstname.data = player.firstname
    form.lastname.data = player.lastname
    form.number.data = player.number

    teams = Team.query.order_by('name')
    for membership in sorted(player.memberships, key=lambda Membership: Membership.membership_start):
        form.memberships.append_entry()
        membership_form = form.memberships[-1]
        membership_form.membership_id.data = membership.id
        membership_form.team_id.data = membership.team_id
        membership_form.team_id.choices = [(team.id, team.name) for team in teams]
        membership_form.player_id.data = player_id
        membership_form.membership_start.data = membership.membership_start
        membership_form.membership_end.data = membership.membership_end
    return render_page("players/update.html", form=form, player_id=player_id)


def players_save_modified_data(player_id):
    form = PlayerForm(request.form)

    p = Player.query.get(player_id)
    p.firstname = form.firstname.data
    p.lastname = form.lastname.data
    p.number = form.number.data

    for membership_data in form.memberships.data:
        if membership_data['membership_id'] == '':
            p.memberships.append(Membership(membership_data))
        else:
            found_memberships = [m for m in p.memberships if m.id == int(membership_data['membership_id'])]
            # Should be exactly one found membership
            assert len(found_memberships) == 1
            found_membership = found_memberships[0]
            found_membership.membership_start = membership_data['membership_start']
            found_membership.membership_end = membership_data['membership_end']
            found_membership.team_id = membership_data['team_id']

    db.session().commit()

    return redirect(url_for("player_page", player_id=player_id))


def create_player_form_with_appended_membership(request_form):
    form = PlayerForm(request_form)
    form.memberships.append_entry()
    teams = Team.query.order_by('name')
    for entry in form.memberships.entries:
        entry.team_id.choices = [(team.id, team.name) for team in teams]
    return form
