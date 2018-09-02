from datetime import time

from sqlalchemy import String, Integer, Time
from sqlalchemy.sql import text

from application import db


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    scorer_id = db.Column(db.Integer, db.ForeignKey('lineup_entry.id'), nullable=False)
    scorer = db.relationship('LineupEntry', foreign_keys=[scorer_id])
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = db.relationship('Game', foreign_keys=[game_id])
    time = db.Column(db.Time)

    def __init__(self, scorer_id, game_id, time, team_id):
        self.scorer_id = scorer_id
        self.game_id = game_id
        self.time = time
        self.team_id = team_id

    @staticmethod
    def team_goals(team_id, game_id):
        stmt = text(
            "SELECT"
            "  Player.lastname,"
            "  Player.firstname,"
            "  Player.number,"
            "  Goal.time "
            "FROM"
            "  Goal,"
            "  Lineup_Entry,"
            "  Membership,"
            "  Player "
            "WHERE"
            "  Goal.team_id = :team_id"
            "  AND Goal.game_id = :game_id"
            "  AND Goal.scorer_id=Lineup_Entry.id"
            "  AND Lineup_Entry.membership_id = Membership.id"
            "  AND Membership.player_id = Player.id "
            "ORDER BY Goal.time"
        ).params(
            team_id=team_id, game_id=game_id
        ).columns(
            lastname=String, firstname=String,
            number=Integer, time=Time)

        res = db.engine.execute(stmt)
        response = []
        for row in res:
            response.append(
                {"lastname": row[0], "firstname": row[1], "number": row[2], "time": format_time_for_view(row[3])})

        return response


def format_time_for_view(game_time: time):
    minutes = 60 * game_time.hour + game_time.minute
    return str(minutes) + ":" + str(game_time.second)
