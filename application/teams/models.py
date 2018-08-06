from application import db


class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(),
                              onupdate=db.func.current_timestamp())

    name = db.Column(db.String(144), nullable=False)
    city = db.Column(db.String(144), nullable=False)

    players = db.relationship("Player", backref='team', lazy=True)

    def __init__(self, name, city):
        self.name = name
        self.city = city
