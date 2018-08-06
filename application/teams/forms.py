from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField


class TeamForm(FlaskForm):
    name = StringField("Name")
    city = StringField("City")

    delete = SubmitField("Delete")

    class Meta():
        csrf = False
