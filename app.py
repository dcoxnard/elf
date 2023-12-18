import secrets
from urllib.parse import urlsplit

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, current_user, login_user, logout_user, \
    login_required

from forms import LoginForm, WishesForm, SetOwnPasswordForm, \
    AccountRecoveryRequestForm, AccountRecoveryForm
from round import Round
from app_token import validate_token

app = Flask(__name__)
app.secret_key = secrets.token_hex()
login_manager = LoginManager(app)
login_manager.login_view = "login"


current_round = Round()


@login_manager.user_loader
def load_user(user_email):
    return current_round.get_user(user_email)


@app.route("/")
def root():
    if current_user.is_authenticated:
        redirect_ = redirect(url_for("santa"))
    else:
        redirect_ = redirect(url_for("login"))

    return redirect_


@app.route("/wishes", methods=["GET", "POST"])
@login_required
def wishes():
    if current_user.wishes:
        return redirect(url_for("santa"))

    form = WishesForm()

    if form.validate_on_submit():
        wishes = [
            form.wish1.data,
            form.wish2.data,
            form.wish3.data,
        ]
        links = [
            form.link1.data,
            form.link2.data,
            form.link3.data,
        ]
        current_round.record_wishes(current_user.email, wishes, links)
        return redirect(url_for("santa"))

    return render_template("wishes.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    # TODO: I don't like this fxn structure, seems to implicitly
    # branch on GET vs POST.  But not 100% sure.  Need to experiment
    if current_user.is_authenticated:
        return redirect(url_for("wishes"))
    form = LoginForm()

    if form.validate_on_submit():
        user_email = form.username.data.lower()
        password_data = form.password.data
        remember = form.remember_me.data

        user = current_round.get_user(user_email)
        if not user.check_password(password_data):
            flash("Invalid username or password!")
            return redirect(url_for("login"))

        login_user(user, remember=remember)
        # Look into https://flask-login.readthedocs.io/en/latest/#configuring-your-application
        # see also explanation at https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins
        next_page = request.args.get("next")
        if next_page is None or urlsplit(next_page).netloc != "":
            return redirect(url_for("wishes"))
        return redirect(next_page)

    return render_template("login.html", title='Sign In', form=form)


@app.route("/set_own_password", methods=["GET", "POST"])
@login_required
def set_own_password():
    form = SetOwnPasswordForm()
    if form.validate_on_submit():
        password = form.new_password.data
        current_round.set_user_password(current_user.email, password)
        return redirect(url_for("santa"))

    return render_template("set_own_password.html", form=form)


# https://www.freecodecamp.org/news/setup-email-verification-in-flask-app/
@app.route("/account_recovery_request", methods=["GET", "POST"])
def account_recovery_request():
    form = AccountRecoveryRequestForm()
    if form.validate_on_submit():
        # TODO: Send an email with a link to the recovery page
        # Redirect to a template that says to check your email
        redirect(url_for("account_recovery"))
        raise NotImplementedError

    return render_template("account_recovery_request.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("wishes"))


@app.route("/confirm_email/<token>")
def confirm_email(token):
    if current_user.is_authenticated:
        return redirect(url_for("santa"))

    email = validate_token(token)
    if email is False:
        return redirect(url_for("login"))
    else:
        user = current_round.get_user(email)
        login_user(user, remember=False)
        return redirect(url_for("account_recovery"))


@app.route("/account_recovery")
@login_required
def account_recovery():
    form = AccountRecoveryForm()
    return render_template("account_recovery.html", form=form)


@app.route("/santa")
@login_required
def santa():
    # You need to submit your wishes before you can see whom you're paired with
    if not current_user.wishes:
        return redirect(url_for("wishes"))

    recipient = current_user.recipient

    return render_template("santa.html", user=current_user, recipient=recipient)


# Run the application
if __name__ == "__main__":
    app.run(debug=True)
