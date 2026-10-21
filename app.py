import os
from dotenv import load_dotenv
from flask import Flask
from flask import render_template

load_dotenv()
SUPER_SECRET_KEY = os.getenv("KEY")

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('template.html')

@app.route("/test")
def test():
    # testing .env, we'll prob use Open-Meteo and won't need API Keys
    return f'{SUPER_SECRET_KEY} KEY'

    # if you are running with "python app.py", otherwise run via "flask run --debug" (--app app can be ommited here)
if __name__ == '__main__':
    app.run(debug=True)