# Import the tools we need from Flask
# Flask → creates the web app
# render_template → shows HTML files
# request → gets data from forms
# redirect → refreshes or moves to another page
from flask import Flask, render_template, request, redirect

# Create the Flask application
# __name__ tells Flask where this file is located
app = Flask(__name__)

# This list will store all the tasks the user adds
# Example: ["Buy milk", "Study Python"]
tasks = []

# ------------------ MAIN PAGE ROUTE ------------------
# This route runs when someone visits "/"
# It allows both viewing the page (GET)
# and submitting the form (POST)
@app.route("/", methods=["GET", "POST"])
def index():

    # Check if the user submitted the form
    if request.method == "POST":

        # Get the text entered in the input field named "task"
        task = request.form.get("task")

        # Make sure the input is not empty
        if task:
            # Add the task to the tasks list
            tasks.append(task)

        # Refresh the page so the new task appears
        return redirect("/")

    # Show the HTML page and send the tasks list to it
    return render_template("index.html", tasks=tasks)

# ------------------ DELETE TASK ROUTE ------------------
# This route runs when clicking "Delete"
# <int:index> is the task number to delete
@app.route("/delete/<int:index>")
def delete_task(index):

    # Make sure the index exists in the list
    if 0 <= index < len(tasks):
        # Remove the task from the list
        tasks.pop(index)

    # Go back to the main page
    return redirect("/")

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
