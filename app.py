# Import the Flask class
import secrets

from flask import Flask
from flask_login import LoginManager


app = Flask(__name__)
app.secret_key = secrets.token_hex()
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    raise NotImplementedError  # return User.get(user_id)


@app.route('/')
def hello_world():
    return 'Hello, World!'


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
