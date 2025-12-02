import os
import random
import string

from flask import Flask
import psycopg2

app = Flask(__name__)


def get_db_connection():
    # Read the connection string from an env var called DATABASE_URL
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")

    # psycopg2 can take the full URL directly
    return psycopg2.connect(db_url)


def get_random_string(length: int = 10) -> str:
    """Generate a random alphanumeric string, length <= 30 (DB column limit)."""
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


@app.route("/")
def index():
    return "<h1>Python Railway App</h1><p>Go to <a href='/db'>/db</a></p>"


@app.route("/db")
def db():
    # This is your /db endpoint for the extra credit
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # 1. Ensure table exists
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS table_timestamp_and_random_string (
                tick timestamp,
                random_string varchar(30)
            )
            """
        )

        # 2. Insert a new row with timestamp + random string
        random_str = get_random_string()
        cur.execute(
            "INSERT INTO table_timestamp_and_random_string VALUES (now(), %s)",
            (random_str,),
        )
        conn.commit()

        # 3. Fetch all rows to display
        cur.execute(
            "SELECT tick, random_string "
            "FROM table_timestamp_and_random_string "
            "ORDER BY tick DESC"
        )
        rows = cur.fetchall()

        cur.close()
        conn.close()

        # 4. Render a very simple HTML page
        html = "<h1>Python /db – timestamps and random strings</h1>"
        html += "<p>Refresh this page to add more rows.</p>"
        html += "<ul>"
        for tick, rs in rows:
            html += f"<li>{tick} — {rs}</li>"
        html += "</ul>"

        return html

    except Exception as e:
        # Basic error text if something goes wrong
        return f"<h1>Error</h1><pre>{e}</pre>", 500


if __name__ == "__main__":
    # Local run: http://localhost:5000/db
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)

