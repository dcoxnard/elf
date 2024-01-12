from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, URL, ValidationError, \
    Optional


def validate_new_passwords_match(form, field):
    if field.data != form.new_password.data:
        # This validator needs to therefore be bound to password2
        raise ValidationError("Passwords must match.")


def strip_text(field):
    if isinstance(field, str):
        return field.strip()


class LoginForm(FlaskForm):

    username = StringField("Username",
                           validators=[InputRequired(), Email()],
                           filters=[strip_text])
    password = PasswordField("Password", validators=[InputRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class WishesForm(FlaskForm):

    wish1 = StringField("Wish #1", validators=[InputRequired()])
    link1 = StringField("Add Link (Optional)", validators=[Optional(), URL()])

    wish2 = StringField("Wish #2", validators=[Optional()])
    link2 = StringField("Add Link (Optional)", validators=[Optional(), URL()])

    wish3 = StringField("Wish #3", validators=[Optional()])
    link3 = StringField("Add Link (Optional)", validators=[Optional(), URL()])

    submit = SubmitField("Submit")


# User resets PW, knowing their current PW
# This is required for each user the first time they log in
# for a new round
class SetOwnPasswordForm(FlaskForm):

    previous_password = PasswordField("Previous Password",
                                      validators=[InputRequired()],
                                      filters=[strip_text])
    new_password = PasswordField("New Password",
                                 validators=[InputRequired()],
                                 filters=[strip_text])
    new_password2 = PasswordField("Confirm New Password",
                                  validators=[InputRequired(), validate_new_passwords_match],
                                  filters=[strip_text])
    submit = SubmitField("Set Password")


# User does not know password
class AccountRecoveryRequestForm(FlaskForm):

    email = StringField("Your Email Address",
                        validators=[InputRequired(), Email()],
                        filters=[strip_text])
    submit = SubmitField("Send Email")


# User resets PW, after authenticating via email link
class AccountRecoveryForm(FlaskForm):

    new_password = PasswordField("New Password",
                                 validators=[InputRequired()],
                                 filters=[strip_text])
    new_password2 = PasswordField("Confirm New Password",
                                  validators=[InputRequired(), validate_new_passwords_match],
                                  filters=[strip_text])
    submit = SubmitField("Set Password")


class MakePairsForm(FlaskForm):
    make_pairs = SubmitField("Make Pairs")


class ExportForm(FlaskForm):
    export = SubmitField("Export data as .csv")


class KickoffForm(FlaskForm):
    send_kickoff = SubmitField("Send Kickoff Email to All Users")


class ReminderForm(FlaskForm):
    send_reminder = SubmitField("Send Reminder Email\nto any Users with no Wishes")
