from flask import Flask, render_template, request, jsonify
import os
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "")
# Railway provides postgres:// but psycopg2 requires postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS guesses (
                    id SERIAL,
                    name TEXT PRIMARY KEY,
                    guess TEXT NOT NULL
                )
            """)
    conn.close()


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

    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO guesses (name, guess) VALUES (%s, %s)
                ON CONFLICT (name) DO UPDATE SET guess = EXCLUDED.guess
            """, (name, guess))
    conn.close()
    return jsonify({"ok": True})


@app.route("/api/guesses")
def get_guesses():
    conn = get_conn()
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT name, guess FROM guesses ORDER BY id")
        rows = cur.fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/reset", methods=["POST"])
def reset():
    conn = get_conn()
    with conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM guesses")
    conn.close()
    return jsonify({"ok": True})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5050)

# Create table on startup (safe to run every time — IF NOT EXISTS)
if DATABASE_URL:
    init_db()
