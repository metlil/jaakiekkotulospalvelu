from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, TimeField

class GoalForm(FlaskForm):
    player_id = SelectField("Player", coerce=int)
    game_id = SelectField("Game", coerce=int)
    time = TimeField("Time")

    delete = SubmitField("Delete")

    class Meta():
        csrf = False
