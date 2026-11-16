# 🌤️ Weatheryy

A simple weather web app that was built using Python Flask. Enter a city and get the current weather, a 7-day forecast, an hourly forecast and more. This application was created as a group project for the "Python Programming Language" course at the University of Latvia. You can test the website by clicking [this link](https://falafel.eu.pythonanywhere.com/).

## 📀 Video

[Weatheryy-demo.webm](https://github.com/user-attachments/assets/255e4abd-fcfb-474f-898c-a90919d388db)

## 📦 Technologies used
### Backend:
- `Python 3`
- `Flask`
- `requests`
- `Open-Meteo API`
### Frontend:
- `Jinja2 Templates`
- `CSS`
- `JavaScript`
### Development tools:
- `VS Code`
- `Git + GitHub`
### Deploy:
- `PythonAnywhere`

## ☄️ Features

Here's what you can do with Weatheryy:
- **Search any city:** Type a city name and the app finds it and shows the weather for it.
- **Current weather:** Temperature, "feels like", weather description, and the local date and time in the searched city.
- **7-day forecast:** Daily weather icon, minimum and maximum temperature and chance of rain.
- **Detailed metrics:** Humidity, wind speed, pressure, UV index, visibility, dew point and cloud cover.
- **Hourly forecast:** The next 24 hours, with day and night icons.
- **Sun card:** Sunrise, sunset, how long until the next one and how long the sun stays up.
- **Switch units:** Show temperatures in °C or °F.
- **Switch theme:** Choose between the green and the pink theme. Your choice is remembered in a cookie.
- **Friendly errors:** Separate pages for "city not found", "service unavailable" and "page not found".
- **Responsive layout:** The dashboard adapts to desktop and phone screens.

## 🚀 Getting started

You need Python 3.10 or newer.

```bash
# 1. Create a virtual environment (once)
python -m venv venv

# 2. Activate it
venv\Scripts\activate # for Windows
source venv/bin/activate # for macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server with auto-reload
flask run --debug
```

Then open http://127.0.0.1:5000 in your browser.

## 🗂️ Project structure

```
app.py              Flask: routes (/ and /weather), error handler, theme cookie
weather.py          Data module: Open-Meteo requests, data formatting, error handling
templates/
  base.html         Shared page layout
  _search.html      Search form (included in other templates)
  index.html        Home page
  weather.html      Weather page (grid of cards)
  error.html        Error page: city not found / service unavailable / 404
  cards/            One template per card (current, 7-day, metrics, hourly, sun)
static/style.css    Styling
```

## 🔎 How it works

1. The user enters a city, and the browser opens `/weather?city=Riga&unit=c`.
2. `app.py` reads and validates the parameters and calls `get_weather(city, unit)` from `weather.py`.
3. `weather.py` makes two requests to Open-Meteo: geocoding (city name --> coordinates), then the forecast for those coordinates.
4. The raw response is turned into one clean dictionary (`current`, `daily`, `hourly`). If anything goes wrong, the dictionary contains an error code instead, so the function never crashes.
5. Flask passes the dictionary to Jinja2 templates, which render the cards.

## 👥 Team of developers

- Illia Chupryna
- Klints Legranžs
- Evelina Sadurska
- Elza Sīle

## 📜 What We Learned

During this project, we picked up some important skills and got a better understanding of:

### ⛈️ Working with external APIs
Learned how to read API documentation, build requests with parameters, and handle responses with `requests`.

### 🧪 Flask & Jinja2
Leaned how routing, `request.args`, redirects, error handlers and context processors work in Flask.

### 🕒 Time zones
Using `timezone=auto` and `utc_offset_seconds` from the API local time, sunrise and sunset were calculated correctly.

### 🌳 Teamwork with Git
Worked with a protected `main` branch, one Issue per task, one branch per Issue and Pull Requests.

## 💡 How this project can be improved?
- Let the user choose between several cities with the same name (currently the first match is used) and add autocomplete to the search bar.
- Cache API responses for a few minutes to make pages load faster and reduce the number of requests.
- Add weather for the user's current location using the browser's geolocation.
- Add a chart for the hourly temperature.
- Add more languages for the interface.
- Save unit preferences in cookie, as was implemented with theme changer
