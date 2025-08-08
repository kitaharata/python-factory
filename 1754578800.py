from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__, template_folder=".")

tasks = []
task_id_counter = 1


@app.route("/", methods=["GET", "POST"])
def index():
    global task_id_counter
    if request.method == "POST":
        task_content = request.form["content"]
        if task_content:
            tasks.append({"id": task_id_counter, "content": task_content, "completed": False})
            task_id_counter += 1
        return redirect(url_for("index"))
    return render_template("1754578830.html", tasks=tasks)


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    global tasks
    tasks = [task for task in tasks if task["id"] != task_id]
    return redirect(url_for("index"))


@app.route("/update/<int:task_id>", methods=["POST"])
def update_task(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = not task["completed"]
            break
    return redirect(url_for("index"))


if __name__ == "__main__":
    from waitress import serve

    serve(app, host="localhost", port=5000)
