import os
import csv
from io import StringIO
from urllib.parse import urlsplit

from flask import Flask, render_template, redirect, url_for, flash, request, \
    Response
from flask_login import LoginManager, current_user, login_user, logout_user, \
    login_required

from forms import LoginForm, WishesForm, SetOwnPasswordForm, \
    AccountRecoveryRequestForm, AccountRecoveryForm, MakePairsForm, ExportForm, \
    KickoffForm, ReminderForm
from round import Round
from app_token import secret_key, validate_token
import elf_logger

app = Flask(__name__)

app.secret_key = secret_key

login_manager = LoginManager(app)
login_manager.login_view = "login"

logger = elf_logger.logger

# TODO: This should live in a session
current_round = Round()
if not current_round.has_users():
    initialize_file = os.environ["APP_INITIALIZE_FILE"]
    logger.info(f"Registering users from {initialize_file}")
    with open(initialize_file, "r") as f_obj:
        reader = csv.reader(f_obj)
        rows = [row for row in reader]
    header, users = rows[0], rows[1:]
    n_registered = current_round.register_users(users)
    logger.info(f"Registered {n_registered} users")


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
        n_wishes = current_round.record_wishes(current_user.email, wishes, links)
        logger.info(f"Recorded {n_wishes} for user: {current_user.email}")
        return redirect(url_for("santa"))

    return render_template("wishes.html", form=form, user=current_user,
                           active_tab="wishes")


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
            logger.info(f"Invalid credentials passed.  Username: {user_email}")
            return redirect(url_for("login", credential_error=True))

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

    error = request.args.get("credential_error", False)
    return render_template("login.html", title='Sign In', form=form,
                           error=error)


@app.route("/set_own_password", methods=["GET", "POST"])
@login_required
def set_own_password():
    form = SetOwnPasswordForm()
    if form.validate_on_submit():
        password = form.new_password.data
        current_round.set_user_password(current_user.email, password)
        logger.info(f"Password successfully reset for {current_user.email}")
        return redirect(url_for("santa"))

    return render_template("set_own_password.html", form=form,
                           user=current_user, active_tab="set_own_password")


# https://www.freecodecamp.org/news/setup-email-verification-in-flask-app/
@app.route("/account_recovery_request", methods=["GET", "POST"])
def account_recovery_request():
    form = AccountRecoveryRequestForm()
    if form.validate_on_submit():

        email = form.email.data
        current_round.send_recovery_email(email)
        logger.info(f"Account recovery email sent to {email}")

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
        logger.info(f"Password successfully set for {current_user.email}")
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

    return render_template("santa.html", user=current_user, active_tab="santa")


@app.route("/round_status", methods=["GET", "POST"])
@login_required
def round_status():
    if not current_user.is_admin:
        return redirect(url_for("login"))

    if not current_user.user_has_set_own_password:
        return redirect(url_for("login"))

    status_data = current_round.status()
    communications = current_round.communications()
    n_pairs_set = sum([data["recipient_set"] for data in status_data.values()])
    n_users = len(status_data)
    if n_pairs_set != n_users and n_pairs_set != 0:
        msg = f"Invalid round state found: {n_pairs_set} pairs set but {n_users} users total"
        logger.warning(msg)
        pairs_set = False
    elif n_pairs_set == 0:
        pairs_set = False
    else:  # i.e. n_paris_set == n_users
        pairs_set = True

    pairs_form = MakePairsForm()
    export_form = ExportForm()
    kickoff_form = KickoffForm()
    reminder_form = ReminderForm()

    return render_template("round_status.html", status_data=status_data,
                           communications=communications, pairs_set=pairs_set,
                           pairs_form=pairs_form, export_form=export_form,
                           kickoff_form=kickoff_form, reminder_form=reminder_form,
                           user=current_user, active_tab="admin")


@app.route("/pairs")
@login_required
def pairs():
    if not current_user.is_admin:
        return redirect(url_for("login"))

    n_pairs = current_round.make_pairs()
    logger.info(f"Updated pairings for {n_pairs} users")
    return redirect(url_for("round_status"))


@app.route("/kickoff")
@login_required
def kickoff():
    if not current_user.is_admin:
        return redirect(url_for("login"))

    sent_emails = current_round.send_all_kickoff_email()
    for email in sent_emails:
        logger.info(f"Sent kickoff email to {email}")
    return redirect(url_for("round_status"))


@app.route("/reminder")
@login_required
def reminder():
    if not current_user.is_admin:
        return redirect(url_for("login"))

    sent_emails = current_round.send_all_reminder_email()
    for email in sent_emails:
        logger.info(f"Sent reminder email to {email}")
    return redirect(url_for("round_status"))


@app.route("/export")
@login_required
def export():
    if not current_user.is_admin:
        return redirect(url_for("login"))

    export_data = current_round.export_for_next_round()
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
