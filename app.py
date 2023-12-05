# Import the Flask class
import secrets
from urllib.parse import urlsplit

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, current_user, login_user, logout_user, \
    login_required

from forms import LoginForm
from round import Round

app = Flask(__name__)
app.secret_key = secrets.token_hex()
login_manager = LoginManager(app)
login_manager.login_view = 'login'


current_round = Round()


@login_manager.user_loader
def load_user(user_email):
    return current_round.get_user(user_email)


@app.route("/")
def hello_world():
    return 'Hello, World!'


@app.route("/index")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    # TODO: I don't like this fxn structure, seems to implicitly
    # branch on GET vs POST.  But not 100% sure.  Need to experiment

    if current_user.is_authenticated:
        return redirect(url_for("index"))  # TODO: Create a template for index
    form = LoginForm()

    if form.validate_on_submit():
        user_email = form.username.data
        password_data = form.password.data
        remember = form.remember_me.data

        user = current_round.get_user(user_email)
        if not user.check_password(password_data):
            flash("Invalid username or password!")
            return redirect(url_for("login"))

        login_user(user, remember=remember)
        # TODO: Look into https://flask-login.readthedocs.io/en/latest/#configuring-your-application
        # see also explanation at https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
        next_page = request.args.get("next")
        if next_page is None or urlsplit(next_page).netloc != "":
            return redirect(url_for("index"))
        return redirect(next_page)

    return render_template("login.html", title='Sign In', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


# Run the application
if __name__ == "__main__":
    app.run(debug=True)
