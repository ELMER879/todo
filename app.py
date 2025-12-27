from flask import Flask, render_template, request, redirect
import sqlite3
import os

# ------------------ DATABASE FUNCTION ------------------
# This MUST be defined before it is used
def get_db():
    return sqlite3.connect("tasks.db")

# ------------------ FLASK APP ------------------
app = Flask(__name__)

# ------------------ CREATE TABLE (RUNS ON START) ------------------
with get_db() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    """)

# ------------------ MAIN PAGE ------------------
@app.route("/", methods=["GET", "POST"])
def index():
    db = get_db()

    if request.method == "POST":
        task = request.form.get("task")
        if task:
            db.execute("INSERT INTO tasks (name) VALUES (?)", (task,))
            db.commit()
        return redirect("/")

    tasks = db.execute("SELECT * FROM tasks").fetchall()
    return render_template("index.html", tasks=tasks)

# ------------------ DELETE TASK ------------------
@app.route("/delete/<int:index>")
def delete_task(index):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", (index,))
    db.commit()
    return redirect("/")

# ------------------ RUN APP ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
