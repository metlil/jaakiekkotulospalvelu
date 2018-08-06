from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField

class PlayerForm(FlaskForm):
    firstname = StringField("Firstname")
    lastname = StringField("Lastname")
    number = IntegerField("Number")

    delete = SubmitField("Delete")

    class Meta:
        csrf = False