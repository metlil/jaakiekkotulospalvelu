from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, FieldList, FormField


class MembershipForm(FlaskForm):
    player_id = SelectField("Player", coerce=int)
    team_id = SelectField("Team", coerce=int)
    membership_start = DateField("Membership start")
    membership_end = DateField("Membership end")

    class Meta:
        csrf = False
