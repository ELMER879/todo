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
    name TEXT,
    done INTEGER DEFAULT 0
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


# ------------------ RUN APP ------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
