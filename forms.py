from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class WishesForm(FlaskForm):
    wish1 = StringField("Wish #1", validators=[DataRequired()])
    link1 = StringField("Add Link (Optional)")
    wish2 = StringField("Wish #2", validators=[DataRequired()])
    link2 = StringField("Add Link (Optional)")
    wish3 = StringField("Wish #3", validators=[DataRequired()])
    link3 = StringField("Add Link (Optional)")
    submit = SubmitField("Submit")
