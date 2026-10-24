from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

    # if you are running with "python app.py"; otherwise run via "flask run --debug" (--app app can be ommited here) to enter debug mode
if __name__ == '__main__':
    app.run(debug=True)