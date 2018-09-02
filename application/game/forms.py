from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DateTimeField


class GameForm(FlaskForm):
    home_id = SelectField("Home", coerce=int)
    guest_id = SelectField("Guest", coerce=int)
    time = DateTimeField("Game Start")
    place = StringField("Place")

    finish = SubmitField("Finish")

    delete = SubmitField("Delete")

    class Meta():
        csrf = False
