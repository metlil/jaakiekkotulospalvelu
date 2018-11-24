from flask import request, redirect, url_for
from flask_login import current_user

from application import app, db, login_required
from application.usergame.models import UserGame


@app.route("/usergames/<game_id>/add", methods=["POST"])
@login_required(role="ANY")
def add_user_game(game_id):
    user_game = UserGame(current_user.id, game_id)
    db.session().add(user_game)
    db.session().commit()
    return redirect(request.referrer or url_for("index"))


@app.route("/usergames/<game_id>/remove", methods=["POST"])
@login_required(role="ANY")
def remove_user_game(game_id):
    user_games = UserGame.query.filter(UserGame.user_id == current_user.id, UserGame.game_id == game_id).all()
    for user_game in user_games:
        db.session().delete(user_game)
    db.session().commit()
    return redirect(request.referrer or url_for("index"))
