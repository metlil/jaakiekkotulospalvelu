from flask_wtf import FlaskForm
from wtforms import SelectField, FieldList, FormField


class LineupEntryForm(FlaskForm):
    membership_id = SelectField("Player", coerce=int)

    class Meta:
        csrf = False


class LineupForm(FlaskForm):
    lineup_entries = FieldList(FormField(LineupEntryForm))

    class Meta:
        csrf = False


class GameLineupForm(FlaskForm):
    home_lineup = FormField(LineupForm)
    guest_lineup = FormField(LineupForm)

    class Meta:
        csrf = False
