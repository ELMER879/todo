# Import the tools we need from Flask
# Flask → creates the web app
# render_template → shows HTML files
# request → gets data from forms
# redirect → refreshes or moves to another page
from flask import Flask, render_template, request, redirect

# Create the Flask application
# __name__ tells Flask where this file is located
app = Flask(__name__)

with get_db() as db:
    db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT
        )
    """)



# sqlite storage snippet
import sqlite3

def get_db():
    return sqlite3.connect("tasks.db")


# ------------------ MAIN PAGE ROUTE ------------------
# This route runs when someone visits "/"
# It allows both viewing the page (GET)
# and submitting the form (POST)
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


# ------------------ DELETE TASK ROUTE ------------------
# This route runs when clicking "Delete"
# <int:index> is the task number to delete
@app.route("/delete/<int:index>")
def delete_task(index):
    db = get_db()
    db.execute("DELETE FROM tasks WHERE id = ?", (index,))
    db.commit()
    return redirect("/")


    # Make sure the index exists in the list
    if 0 <= index < len(tasks):
        db = get_db()
db.execute("DELETE FROM tasks WHERE id = ?", (index,))
db.commit()


# ------------------ RUN THE APP ------------------
# This part runs the app when you start it
# Render (hosting service) provides the PORT number
if __name__ == "__main__":
    import os

    # Get the port from Render, or use 5000 if running locally
    port = int(os.environ.get("PORT", 5000))

    # Start the Flask app
    # 0.0.0.0 allows the app to be accessed from the network
    app.run(host="0.0.0.0", port=port)
