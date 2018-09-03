from application import db
from application.game.game_status import GameStatus


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

    home_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    home_team = db.relationship('Team', foreign_keys=[home_id])
    guest_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    guest_team = db.relationship('Team', foreign_keys=[guest_id])

    time = db.Column(db.DateTime, nullable=False)
    place = db.Column(db.String, nullable=False)
    status = db.Column(db.Enum(GameStatus), nullable=False)
    lineup = db.relationship("LineupEntry", back_populates='game', lazy=True)
    goals = db.relationship("Goal", back_populates='game', lazy=True)

    def __init__(self, home_id, guest_id, time, place, status: GameStatus):
        self.home_id = home_id
        self.guest_id = guest_id
        self.time = time
        self.place = place
        self.status = status
