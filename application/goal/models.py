from application import db


class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

    player_id = db.Column(db.Integer, db.ForeignKey('player.id'),
                          nullable=False)
    player = db.relationship('Player', foreign_keys=[player_id])
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = db.relationship('Game', foreign_keys=[game_id])
    time = db.Column(db.Time)

    def __init__(self, player_id, game_id, time):
        self.player_id = player_id
        self.game_id = game_id
        self.time = time
