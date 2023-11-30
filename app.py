# Import the Flask class
import secrets

from flask import Flask, render_template
from flask_login import LoginManager

from forms import LoginForm

app = Flask(__name__)
app.secret_key = secrets.token_hex()
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    raise NotImplementedError  # return User.get(user_id)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
