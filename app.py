# Import Flask tools needed to build a web app
from flask import Flask, render_template, request, redirect, session

# Import SQLite (lightweight database stored in a file)
import sqlite3

# Import OS tools (used for deployment ports like Render)
import os


# ------------------ DATABASE FUNCTION ------------------
# This function opens (or creates) the database file
# It returns a connection we can use to run SQL commands
def get_db():
    return sqlite3.connect("tasks.db")


# ------------------ FLASK APP ------------------
# Create the Flask application
app = Flask(__name__)

# Secret key is REQUIRED for login sessions
# It keeps user sessions secure
app.secret_key = "super-secret-key"


# ------------------ CREATE TABLES (RUNS ON APP START) ------------------
# This runs automatically when the app starts
with get_db() as db:

    # Create USERS table if it does not exist
    # This stores login accounts
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- unique user ID
            username TEXT UNIQUE,                  -- username (must be unique)
            password TEXT                          -- password (plain for now)
        )
    """)

    # Create TASKS table if it does not exist
    # Each task belongs to a user
    db.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- unique task ID
            name TEXT,                             -- task text
            done INTEGER DEFAULT 0,                -- 0 = not done, 1 = done
            user_id INTEGER                        -- which user owns the task
        )
    """)


# ------------------ MAIN PAGE (TO-DO LIST) ------------------
@app.route("/", methods=["GET", "POST"])
def index():

    # If user is NOT logged in, send them to login page
    if "user_id" not in session:
        return redirect("/login")

    # Get logged-in user's ID from session
    user_id = session["user_id"]

    # Open database connection
    db = get_db()

    # If form was submitted (Add Task button)
    if request.method == "POST":

        # Get the task text from the input field
        task = request.form.get("task")

        # Only save task if input is not empty
        if task:
            db.execute(
                "INSERT INTO tasks (name, user_id) VALUES (?, ?)",
                (task, user_id)
            )
            db.commit()  # Save changes to database

        # Reload page after adding task
        return redirect("/")

    # Get all tasks for THIS logged-in user
    tasks = db.execute(
        "SELECT * FROM tasks WHERE user_id = ?",
        (user_id,)
    ).fetchall()

    # Send tasks to HTML template
    return render_template("index.html", tasks=tasks)


# ------------------ SIGNUP PAGE ------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():

    # If signup form submitted
    if request.method == "POST":

        # Get username and password from form
        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()

        try:
            # Try to insert new user
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            db.commit()

            # Redirect to login page after success
            return redirect("/login")

        except:
            # Happens if username already exists
            return "Username already exists"

    # Show signup page
    return render_template("signup.html")


# ------------------ LOGIN PAGE ------------------
@app.route("/login", methods=["GET", "POST"])
def login():

    # If login form submitted
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        db = get_db()

        # Check if username and password match a user
        user = db.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()

        if user:
            # Save user ID in session (login success)
            session["user_id"] = user[0]
            return redirect("/")
        else:
            return "Invalid login"

    # Show login page
    return render_template("login.html")


# ------------------ LOGOUT ------------------
@app.route("/logout")
def logout():
    # Clear all session data (logs user out)
    session.clear()
    return redirect("/login")


# ------------------ DELETE TASK ------------------
@app.route("/delete/<int:task_id>")
def delete_task(task_id):

    # Block access if not logged in
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    # Delete ONLY the user's own task
    db.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"])
    )
    db.commit()

    return redirect("/")


# ------------------ TOGGLE TASK DONE / UNDONE ------------------
@app.route("/toggle/<int:task_id>")
def toggle_task(task_id):

    # Block access if not logged in
    if "user_id" not in session:
        return redirect("/login")

    db = get_db()

    # Flip done value:
    # 0 becomes 1, 1 becomes 0
    db.execute("""
        UPDATE tasks
        SET done = CASE WHEN done = 0 THEN 1 ELSE 0 END
        WHERE id = ? AND user_id = ?
    """, (task_id, session["user_id"]))

    db.commit()
    return redirect("/")


# ------------------ RUN APP ------------------
# This allows the app to run locally and on Render
if __name__ == "__main__":

    # Render provides a PORT automatically
    port = int(os.environ.get("PORT", 5000))

    # Run app and allow external access
    app.run(host="0.0.0.0", port=port)
