from application import db


class LineupEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)
    game = db.relationship('Game', back_populates='lineup')

    membership_id = db.Column(db.Integer, db.ForeignKey('membership.id'), nullable=False)
    membership = db.relationship('Membership', foreign_keys=[membership_id])

    def __init__(self, game_id, membership_id):
        self.game_id = game_id
        self.membership_id = membership_id
