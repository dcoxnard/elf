# Import the Flask class
from flask import Flask

# Create an instance of the Flask class
app = Flask(__name__)


# Define a route and the associated function
@app.route('/')
def hello_world():
    return 'Hello, World!'


# Run the application
if __name__ == '__main__':
    app.run(debug=True)
