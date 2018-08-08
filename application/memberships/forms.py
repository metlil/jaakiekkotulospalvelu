from flask_wtf import FlaskForm
from wtforms import SelectField, DateField, HiddenField


class MembershipForm(FlaskForm):
    player_id = SelectField("Player", coerce=int)
    team_id = SelectField("Team", coerce=int)
    membership_start = DateField("Membership start")
    membership_end = DateField("Membership end")
    # With this we will know which membership this is
    membership_id = HiddenField("Membership id")

    class Meta:
        csrf = False
