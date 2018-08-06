from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField

class PlayerForm(FlaskForm):
    firstname = StringField("Firstname")
    lastname = StringField("Lastname")
    number = IntegerField("Number")
    team_id = SelectField("Team", coerce=int)

    delete = SubmitField("Delete")

    class Meta:
        csrf = False