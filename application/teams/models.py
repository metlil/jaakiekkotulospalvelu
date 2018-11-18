import datetime

from sqlalchemy.sql import text

from application import db


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

    name = db.Column(db.String(144), nullable=False)
    city = db.Column(db.String(144), nullable=False)

    memberships = db.relationship("Membership", back_populates='team', lazy=True)

    def __init__(self, name, city):
        self.name = name
        self.city = city

    @staticmethod
    def find_current_players(team_id):
        today = datetime.date.today().isoformat()
        stmt = text(
            "SELECT"
            "  Player.lastname,"
            "  Player.firstname,"
            "  Player.number "
            "FROM"
            "  Player"
            "  INNER JOIN Membership"
            "    ON Player.id = Membership.player_id "
            "WHERE"
            "  Membership.team_id = :team_id"
            "  AND ("
            "    ("
            "      Membership.membership_start < :today AND Membership.membership_end IS NULL"
            "    )"
            "    OR ("
            "      :today BETWEEN Membership.membership_start AND Membership.membership_end"
            "    )"
            "  ) "
            "ORDER BY Player.lastname"
        ).params(team_id=team_id,today=today)

        res = db.engine.execute(stmt)
        response = []
        for row in res:
            response.append({"lastname": row[0], "firstname": row[1], "number": row[2]})

        return response
