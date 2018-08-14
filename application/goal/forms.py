from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField

class GoalForm(FlaskForm):
    player_id = SelectField("Player", coerce=int)
    game_id = SelectField("Game", coerce=int)
    time = StringField("Time")

    delete = SubmitField("Delete")

    class Meta():
        csrf = False
