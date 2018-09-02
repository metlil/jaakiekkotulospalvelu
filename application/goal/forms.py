from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField, HiddenField


class GoalForm(FlaskForm):
    scorer_id = SelectField("Player", coerce=int)
    game_id = SelectField("Game", coerce=int)
    time = StringField("Time")
    team_id = HiddenField("Team id")

    delete = SubmitField("Delete")

    class Meta():
        csrf = False
