import os

from flask import Flask
from cli import ovveride_star_cmd

app = Flask(__name__)


@app.route("/")
def hello_world():
    print("Hello World")
    ovveride_star_cmd()
    return 'Success'


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)