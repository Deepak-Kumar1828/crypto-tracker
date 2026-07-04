from flask import Flask, render_template, request, redirect
import requests
import sqlite3

def init_db():
    conn = sqlite3.connect("watchlist.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
             coin_name TEXT UNIQUE
       )         
    """)

app = Flask(__name__)

def get_crypto_prices(coins):
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": ",".join(coins), "vs_currencies": "usd"}
    response = requests.get(url, params=params)
    data = response.json()
    return data

@app.route("/")
def home():
    conn = sqlite3.connect("watchlist.db")
    cursor = conn.cursor()
    cursor.execute("SELECT coin_name FROM watchlist")
    coins = [row[0] for row in cursor.fetchall()]
    conn.close()

    if coins:
        prices = get_crypto_prices(coins)
    else:
        prices = {}
    return render_template("index.html", prices=prices)

@app.route("/add", methods=["POST"])
def add_coin():
    coin = request.form.get("coin").lower()
    conn = sqlite3.connect("watchlist.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO watchlist (coin_name) VALUES (?)", (coin,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()
    return redirect("/")

@app.route("/remove/<coin>")
def remove_coin(coin):
    conn = sqlite3.connect("watchlist.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM watchlist WHERE coin_name = ?", (coin,))
    conn.commit()
    conn.close()
    return redirect("/")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

