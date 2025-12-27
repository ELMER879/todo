from flask import Flask, render_template, request, redirect
import sqlite3
import os
from flask import session


# ------------------ DATABASE FUNCTION ------------------
# This MUST be defined before it is used
def get_db():
    return sqlite3.connect("tasks.db")

# ------------------ FLASK APP ------------------
app = Flask(__name__)


app.secret_key = "super-secret-key"


# ------------------ CREATE TABLE (RUNS ON START) ------------------
with get_db() as db:
    # Users table
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Tasks table (linked to users)
    db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            done INTEGER DEFAULT 0,
            user_id INTEGER
        )
    """)


# ------------------ MAIN PAGE ------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]
    db = get_db()

    if request.method == "POST":
        task = request.form.get("task")
        if task:
            db.execute(
                "INSERT INTO tasks (name, user_id) VALUES (?, ?)",
                (task, user_id)
            )
            db.commit()
        return redirect("/")

    tasks = db.execute(
        "SELECT * FROM tasks WHERE user_id = ?",
        (user_id,)
    ).fetchall()

    return render_template("index.html", tasks=tasks)




@app.route("/toggle/<int:task_id>")
def toggle_task(task_id):
    db = get_db()

    # Switch done from 0 → 1 or 1 → 0
    db.execute("""
        UPDATE tasks
        SET done = CASE WHEN done = 0 THEN 1 ELSE 0 END
        WHERE id = ?
    """, (task_id,))

    db.commit()
    return redirect("/")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            db.commit()
            return redirect("/login")
        except:
            return "Username already exists"

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()

        if user:
            session["user_id"] = user[0]
            return redirect("/")
        else:
            return "Invalid login"

    return render_template("login.html")



@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    db.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"])
    )
    db.commit()
    return redirect("/")


@app.route("/toggle/<int:task_id>")
def toggle_task(task_id):
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()
    db.execute("""
        UPDATE tasks
        SET done = CASE WHEN done = 0 THEN 1 ELSE 0 END
        WHERE id = ? AND user_id = ?
    """, (task_id, session["user_id"]))
    db.commit()

    return redirect("/")




# ------------------ RUN APP ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
