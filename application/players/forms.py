from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField

class PlayerForm(FlaskForm):
    firstname = StringField("Firstname")
    lastname = StringField("Lastname")
    number = IntegerField("Number")

    class Meta:
        csrf = False