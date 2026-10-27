from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/weather")
def weather():
    city = request.args.get("city", "")
    if not city:
        # nothing was typed: go back to the home page
        return redirect(url_for("index"))
    return render_template("weather.html", city=city)

    # if you are running with "python app.py"; otherwise run via "flask run --debug" (--app app can be ommited here) to enter debug mode
if __name__ == '__main__':
    app.run(debug=True)