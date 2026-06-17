from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)

# On Railway, set DATA_DIR=/data (persistent volume). Locally, uses current directory.
DATA_DIR = os.environ.get("DATA_DIR", ".")
DATA_FILE = os.path.join(DATA_DIR, "guesses.json")
os.makedirs(DATA_DIR, exist_ok=True)


def load_guesses():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_guesses(guesses):
    with open(DATA_FILE, "w") as f:
        json.dump(guesses, f, indent=2)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/guess", methods=["POST"])
def add_guess():
    data = request.get_json()
    name = (data.get("name") or "").strip()
    guess = data.get("guess") or ""
    if not name or guess not in ("boy", "girl"):
        return jsonify({"error": "Invalid input"}), 400

    guesses = load_guesses()
    idx = next((i for i, g in enumerate(guesses) if g["name"].lower() == name.lower()), -1)
    entry = {"name": name, "guess": guess}
    if idx >= 0:
        guesses[idx] = entry
    else:
        guesses.append(entry)
    save_guesses(guesses)
    return jsonify({"ok": True})


@app.route("/api/guesses")
def get_guesses():
    return jsonify(load_guesses())


@app.route("/api/reset", methods=["POST"])
def reset():
    save_guesses([])
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5050)
