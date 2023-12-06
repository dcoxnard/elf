from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, URL


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class WishesForm(FlaskForm):
    wish1 = StringField("Wish #1", validators=[InputRequired()])
    link1 = StringField("Add Link (Optional)", validators=URL())

    wish2 = StringField("Wish #2", validators=[InputRequired()])
    link2 = StringField("Add Link (Optional)", validators=URL())

    wish3 = StringField("Wish #3", validators=[InputRequired()])
    link3 = StringField("Add Link (Optional)", validators=URL())

    submit = SubmitField("Submit")
