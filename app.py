import os
import csv
from io import StringIO
from urllib.parse import urlsplit

from flask import Flask, render_template, redirect, url_for, flash, request, \
    Response
from flask_login import LoginManager, current_user, login_user, logout_user, \
    login_required

from forms import LoginForm, WishesForm, SetOwnPasswordForm, \
    AccountRecoveryRequestForm, AccountRecoveryForm
from round import Round
from app_token import secret_key, validate_token

app = Flask(__name__)

app.secret_key = secret_key

login_manager = LoginManager(app)
login_manager.login_view = "login"


# TODO: This should live in a session
current_round = Round()
if not current_round.has_users():
    initialize_file = os.environ["APP_INITIALIZE_FILE"]
    with open(initialize_file, "r") as f_obj:
        reader = csv.reader(f_obj)
        rows = [row for row in reader]
    header, users = rows[0], rows[1:]
    current_round.register_users(users)


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
    if not current_user.user_has_set_own_password:
        return redirect(url_for("login"))

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

    return render_template("wishes.html", form=form, user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    # TODO: I don't like this fxn structure, seems to implicitly
    # branch on GET vs POST.  But not 100% sure.  Need to experiment
    if current_user.is_authenticated and current_user.user_has_set_own_password:
        return redirect(url_for("wishes"))
    elif current_user.is_authenticated:
        return redirect(url_for("account_recovery"))

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

        # Force first-time redirect to set own PW
        if not user.user_has_set_own_password:
            return redirect(url_for("account_recovery"))

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

        email = form.email.data
        current_round.send_recovery_email(email)

        # TODO: Implement this template
        render_template("account_recovery_direction.html")

    return render_template("account_recovery_request.html", form=form, user=current_user)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


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


@app.route("/account_recovery", methods=["GET", "POST"])
@login_required
def account_recovery():
    form = AccountRecoveryForm()

    # Collect form info, validate, set PW, and move on to santa
    if form.validate_on_submit():
        password1 = form.new_password.data
        password2 = form.new_password2.data
        current_round.set_user_password(current_user.email, password1)
        return redirect(url_for("santa"))

    return render_template("account_recovery.html", form=form, user=current_user)


@app.route("/santa")
@login_required
def santa():
    if not current_user.user_has_set_own_password:
        return redirect(url_for("login"))

    # You need to submit your wishes before you can see whom you're paired with
    if current_user.n_wishes() == 0:
        return redirect(url_for("wishes"))

    return render_template("santa.html", user=current_user)


@app.route("/round_status")
@login_required
def round_status():
    if not current_user.is_admin:
        return redirect(url_for("login"))

    status_data = current_round.status()
    return render_template("round_status.html", status_data=status_data)


@app.route("/pairs")
@login_required
def pairs():
    if not current_user.is_admin:
        return redirect(url_for("login"))

    current_round.make_pairs()
    return redirect(url_for("round_status"))


@app.route("/kickoff")
@login_required
def kickoff():
    if not current_user.is_admin:
        return redirect(url_for("login"))

    current_round.send_all_kickoff_email()
    return redirect(url_for("round_status"))


@app.route("/export")
@login_required
def export():
    if not current_user.is_admin:
        return redirect(url_for("login"))

    export_data = current_user.export_for_next_round()
    lines = StringIO()
    writer = csv.writer(lines)
    writer.writerows(export_data)
    csv_string = lines.getvalue()
    return Response(
        csv_string,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=export.csv"}
    )


# Run the application
if __name__ == "__main__":
    app.run(debug=True)
