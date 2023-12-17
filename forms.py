from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, URL, ValidationError, \
    Optional


def validate_password(form, field):
    if field.data != form.new_password2.data:
        raise ValidationError("Passwords must match")


class LoginForm(FlaskForm):

    username = StringField("Username", validators=[Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class WishesForm(FlaskForm):

    wish1 = StringField("Wish #1", validators=[InputRequired()])
    link1 = StringField("Add Link (Optional)", validators=[Optional(), URL()])

    wish2 = StringField("Wish #2", validators=[InputRequired()])
    link2 = StringField("Add Link (Optional)", validators=[Optional(), URL()])

    wish3 = StringField("Wish #3", validators=[InputRequired()])
    link3 = StringField("Add Link (Optional)", validators=[Optional(), URL()])

    submit = SubmitField("Submit")


# User resets PW, knowing their current PW
# This is required for each user the first time they log in
# for a new round
class SetOwnPasswordForm(FlaskForm):

    previous_password = StringField("Previous Password", validators=[InputRequired()])
    new_password = StringField("New Password", validators=[InputRequired(), validate_password])
    new_password2 = StringField("Confirm New Password", validators=[InputRequired()])
    submit = SubmitField("Submit")


# User does not know password
class AccountRecoveryRequestForm(FlaskForm):

    email = StringField("Your Email Address", validators=[Email()])
    submit = SubmitField("Submit")


# User resets PW, after authenticating via email link
class AccountRecoveryForm(FlaskForm):

    new_password = StringField("New Password", validators=[InputRequired(), validate_password])
    new_password2 = StringField("Confirm New Password", validators=[InputRequired()])
    submit = SubmitField("Submit")
