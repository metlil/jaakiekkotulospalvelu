from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, FieldList, FormField

from application.memberships.forms import MembershipForm


class PlayerForm(FlaskForm):
    firstname = StringField("Firstname")
    lastname = StringField("Lastname")
    number = IntegerField("Number")
    memberships = FieldList(FormField(MembershipForm))

    delete = SubmitField("Delete")

    class Meta:
        csrf = False
