from application import db


class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

    player_id = db.Column(db.Integer, db.ForeignKey('player.id'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'), nullable=False)
    membership_start = db.Column(db.DateTime)
    membership_end = db.Column(db.DateTime)

    def __init__(self, player_id, team_id, membership_start, membership_end):
        self.player_id = player_id
        self.team_id = team_id
        self.membership_start = membership_start
        self.membership_end = membership_end

    def __init__(self, dict):
        for key in dict:
            setattr(self, key, dict[key])

    def __str__(self):
        return f'Membership({self.player_id}, {self.team_id}, {self.membership_start}, {self.membership_end})'

    def __repr__(self):
        return f'Membership({self.player_id}, {self.team_id}, {self.membership_start}, {self.membership_end})'
