from sqlalchemy import String, DateTime
from sqlalchemy import text

from application import db


class UserGame(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    user_id = db.Column(db.Integer, db.ForeignKey('account.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("game.id"), nullable=False)

    def __init__(self, user_id, game_id):
        self.user_id = user_id
        self.game_id = game_id

    @staticmethod
    def get_games_for_user(user_id):
        stmt = text(
            "SELECT"
            "  HomeTeam.name home_name,"
            "  GuestTeam.name guest_name,"
            "  Game.time,"
            "  Game.place,"
            "  Game.status,"
            "  Game.id "
            "FROM"
            "  ("
            "    SELECT"
            "      Game.home_id,"
            "      Game.guest_id,"
            "      Game.time,"
            "      Game.place,"
            "      Game.status,"
            "      Game.id "
            "    FROM"
            "      User_Game"
            "      INNER JOIN Game"
            "        ON User_Game.game_id = Game.id "
            "    WHERE"
            "      User_Game.user_id = :user_id"
            "  ) Game,"
            "  Team HomeTeam,"
            "  Team GuestTeam "
            "WHERE"
            "  Game.home_id = HomeTeam.id"
            "  AND Game.guest_id = GuestTeam.id "
            "ORDER BY Game.time"
        ).params(
            user_id=user_id
        ).columns(
            home_name=String, guest_name=String,
            place=String, status=String, time=DateTime)

        res = db.engine.execute(stmt)
        response = []
        for row in res:
            response.append({"home_name": row[0], "guest_name": row[1], "time": row[2],
                             "place": row[3], "status": row[4], "game_id":row[5]})

        return response
