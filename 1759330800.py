import json
import os
import tkinter as tk
from datetime import datetime, timezone
from tkinter import messagebox

import click
from flask import Flask, redirect, render_template, request, url_for

TASK_FILE = "task_list.json"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
INPUT_DATE_FORMATS = [
    DATE_FORMAT,
    "%Y%m%dT%H%M%SZ",
    "%Y%m%d%H%M%S",
]

app = Flask(__name__, template_folder=".")


def load_tasks():
    """Loads tasks from the JSON file."""
    if not os.path.exists(TASK_FILE):
        return []
    try:
        with open(TASK_FILE, "r", encoding="utf-8") as f:
            tasks = json.load(f)
            return tasks
    except (IOError, json.JSONDecodeError):
        return []


def save_tasks(tasks):
    """Save tasks to the JSON file, sorted by due date."""
    try:
        sorted_tasks = sorted(tasks, key=lambda x: datetime.fromisoformat(x["due_date"]))
    except (KeyError, ValueError, TypeError):
        click.echo("Warning: Could not sort tasks by due date before saving due to data error.", err=True)
        sorted_tasks = tasks
    try:
        with open(TASK_FILE, "w", encoding="utf-8") as f:
            json.dump(sorted_tasks, f, indent=4, ensure_ascii=False)
    except IOError as e:
        click.echo(f"Error saving tasks: {e}", err=True)


def add_task(tasks, due, description):
    """Add a new task to the list."""
    due_date = None
    for fmt in INPUT_DATE_FORMATS:
        try:
            due_date = datetime.strptime(due, fmt)
            break
        except ValueError:
            pass
    if due_date is None:
        click.echo("Invalid date format. Please follow the specified format.", err=True)
        return False
    new_task = {"description": description, "done": False, "due_date": due_date.isoformat()}
    tasks.append(new_task)
    return True


def prepare_display_data(tasks):
    """Prepare tasks data for display, sorted by due date."""
    display_tasks = []
    for i, task in enumerate(tasks):
        try:
            due_dt = datetime.fromisoformat(task["due_date"])
            display_tasks.append(
                {"original_index": i, "description": task["description"], "due_dt": due_dt, "done": task["done"]}
            )
        except ValueError:
            continue
    display_tasks.sort(key=lambda x: x["due_dt"])
    return display_tasks


def output_tasks(display_tasks):
    """Display the list of tasks and return the index map for interactive selection (index_map, count)."""
    if not display_tasks:
        click.echo("No tasks available.")
        return {}, 0
    index_map = {}
    for i, task in enumerate(display_tasks):
        formatted_date = task["due_dt"].strftime(DATE_FORMAT)
        done_marker = "*" if task["done"] else ""
        sequence_number = f"{i + 1:08d}"
        click.echo(f"{sequence_number} {formatted_date} {done_marker}".strip())
        click.echo(task["description"])
        if i < len(display_tasks) - 1:
            click.echo("")
        index_map[i + 1] = task["original_index"]
    return index_map, len(display_tasks)


def list_tasks(tasks):
    """List all tasks, sorted by due date."""
    display_tasks = prepare_display_data(tasks)
    output_tasks(display_tasks)


def mark_task_by_original_index(tasks, original_index):
    """Marks a task as done by its original index in the unsorted tasks list."""
    if 0 <= original_index < len(tasks):
        tasks[original_index]["done"] = True
        save_tasks(tasks)
        return True
    return False


def unmark_task_by_original_index(tasks, original_index):
    """Marks a task as not done (pending) by its original index in the unsorted tasks list."""
    if 0 <= original_index < len(tasks):
        tasks[original_index]["done"] = False
        save_tasks(tasks)
        return True
    return False


def delete_task_by_original_index(tasks, original_index):
    """Deletes a task by its original index in the unsorted tasks list."""
    if 0 <= original_index < len(tasks):
        tasks.pop(original_index)
        save_tasks(tasks)
        return True
    return False


def mark_done(tasks):
    """Mark a task as done by selecting its displayed number."""
    display_tasks = prepare_display_data(tasks)
    index_map, count = output_tasks(display_tasks)
    if count == 0:
        return
    while True:
        try:
            task_input = click.prompt("Enter the number of the task to mark as done (Enter 'c' to cancel)", type=str)
            if task_input.lower() == "c":
                return
            display_index = int(task_input)
            if display_index in index_map:
                original_index = index_map[display_index]
                tasks[original_index]["done"] = True
                save_tasks(tasks)
                click.echo(f"Task {display_index} marked as done.")
                break
            else:
                click.echo("Invalid number.")
        except ValueError:
            click.echo("Invalid input. Please enter a number.")


def unmark_done(tasks):
    """Mark a task as not done (pending) by selecting its displayed number."""
    display_tasks = prepare_display_data(tasks)
    index_map, count = output_tasks(display_tasks)
    if count == 0:
        return
    while True:
        try:
            task_input = click.prompt("Enter the number of the task to unmark (Enter 'c' to cancel)", type=str)
            if task_input.lower() == "c":
                return
            display_index = int(task_input)
            if display_index in index_map:
                original_index = index_map[display_index]
                tasks[original_index]["done"] = False
                save_tasks(tasks)
                click.echo(f"Task {display_index} unmarked.")
                break
            else:
                click.echo("Invalid number.")
        except ValueError:
            click.echo("Invalid input. Please enter a number.")


def delete_task(tasks):
    """Delete a task by selecting its displayed number."""
    display_tasks = prepare_display_data(tasks)
    index_map, count = output_tasks(display_tasks)
    if count == 0:
        return
    while True:
        try:
            task_input = click.prompt("Enter the number of the task to delete (Enter 'c' to cancel)", type=str)
            if task_input.lower() == "c":
                return
            display_index = int(task_input)
            if display_index in index_map:
                original_index_to_delete = index_map[display_index]
                tasks.pop(original_index_to_delete)
                save_tasks(tasks)
                click.echo(f"Task {display_index} deleted.")
                break
            else:
                click.echo("Invalid number.")
        except ValueError:
            click.echo("Invalid input. Please enter a number.")


class TaskApp(tk.Tk):
    """Main application class for the Task Scheduler GUI."""

    def __init__(self):
        """Initialize the main application window and components."""
        super().__init__()
        self.title("Task Scheduler")
        self.geometry("800x600")

        list_frame = tk.Frame(self)
        list_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind("<Double-1>", self.show_task_details)

        input_frame = tk.Frame(self)
        input_frame.pack(padx=10, pady=(0, 5), fill=tk.X)

        due_frame = tk.Frame(input_frame)
        due_frame.pack(fill=tk.X, pady=2)
        tk.Label(due_frame, text=f"Due Date (e.g., {INPUT_DATE_FORMATS[0]}):").pack(side=tk.LEFT)
        self.due_entry = tk.Entry(due_frame)
        current_utc_time_str = datetime.now(timezone.utc).strftime(DATE_FORMAT)
        self.due_entry.insert(0, current_utc_time_str)
        self.due_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        tk.Label(input_frame, text="Task Description:").pack(anchor=tk.W)
        self.desc_text = tk.Text(input_frame, height=4, width=1)
        self.desc_text.pack(fill=tk.X, pady=2)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        tk.Button(button_frame, text="Add Task", command=self.gui_add_task).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Mark Done", command=self.gui_mark_task).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Unmark", command=self.gui_unmark_task).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Delete", command=self.gui_delete_task).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Refresh", command=self.load_and_display_tasks).pack(side=tk.LEFT, padx=5)

        self.task_data = []
        self.load_and_display_tasks()

    def load_and_display_tasks(self):
        """Loads tasks from storage and updates the listbox display."""
        tasks = load_tasks()
        self.task_data = prepare_display_data(tasks)
        self.listbox.delete(0, tk.END)
        if not self.task_data:
            self.listbox.insert(tk.END, "No tasks available.")
            return
        for task in self.task_data:
            status = "[DONE] " if task["done"] else "[PEND] "
            due_str = task["due_dt"].strftime("%Y-%m-%d %H:%M:%S")
            display_line = f"{due_str} {status}: {task['description']}"
            self.listbox.insert(tk.END, display_line)
            if task["done"]:
                self.listbox.itemconfig(tk.END, {"fg": "gray"})

    def get_selected_task_display_index(self):
        """Returns the index of the currently selected task in the listbox."""
        selection = self.listbox.curselection()
        return selection[0] if selection else None

    def gui_add_task(self):
        """Handles adding a new task from GUI inputs."""
        description = self.desc_text.get("1.0", tk.END).strip()
        due_input = self.due_entry.get().strip()
        if not description:
            messagebox.showwarning("Input Error", "Task description cannot be empty.")
            return
        if not due_input:
            messagebox.showwarning("Input Error", "Due date cannot be empty.")
            return
        tasks = load_tasks()
        if add_task(tasks, due_input, description):
            save_tasks(tasks)
            self.desc_text.delete("1.0", tk.END)
            self.due_entry.delete(0, tk.END)
        else:
            messagebox.showerror(
                "Error", "Invalid date format. Please ensure the due date follows the specified format."
            )
        self.load_and_display_tasks()

    def gui_mark_task(self):
        """Handles marking the selected task as done."""
        display_index = self.get_selected_task_display_index()
        if display_index is None:
            messagebox.showwarning("Warning", "Please select a task first.")
            return
        if not (0 <= display_index < len(self.task_data)):
            messagebox.showerror("Error", "Invalid task selection.")
            return
        original_index = self.task_data[display_index]["original_index"]
        tasks = load_tasks()
        mark_task_by_original_index(tasks, original_index)
        self.load_and_display_tasks()

    def gui_unmark_task(self):
        """Handles marking the selected task as pending/not done."""
        display_index = self.get_selected_task_display_index()
        if display_index is None:
            messagebox.showwarning("Warning", "Please select a task first.")
            return
        if not (0 <= display_index < len(self.task_data)):
            messagebox.showerror("Error", "Invalid task selection.")
            return
        original_index = self.task_data[display_index]["original_index"]
        tasks = load_tasks()
        unmark_task_by_original_index(tasks, original_index)
        self.load_and_display_tasks()

    def gui_delete_task(self):
        """Handles deleting the selected task."""
        display_index = self.get_selected_task_display_index()
        if display_index is None:
            messagebox.showwarning("Warning", "Please select a task first.")
            return
        if not (0 <= display_index < len(self.task_data)):
            messagebox.showerror("Error", "Invalid task selection.")
            return
        task_info = self.task_data[display_index]
        if not messagebox.askyesno(
            "Confirm Delete", f"Are you sure you want to delete task:\n{task_info['description']}?"
        ):
            return
        original_index = task_info["original_index"]
        tasks = load_tasks()
        delete_task_by_original_index(tasks, original_index)
        self.load_and_display_tasks()

    def show_task_details(self, event):
        """Shows detailed information for the double-clicked task."""
        display_index = self.get_selected_task_display_index()
        if display_index is not None and 0 <= display_index < len(self.task_data):
            task = self.task_data[display_index]
            status = "Done" if task["done"] else "Pending"
            due_str = task["due_dt"].strftime(DATE_FORMAT)
            details = f"Description: {task['description']}\nDue Date: {due_str}\nStatus: {status}"
            messagebox.showinfo("Task Details", details)


def run_gui():
    """Starts the Tkinter GUI application."""
    app = TaskApp()
    app.mainloop()


@app.route("/", methods=["GET", "POST"])
def index():
    """Handles task display and addition via the web interface."""
    if request.method == "POST":
        due_input = request.form.get("due")
        description = request.form.get("description")

        if description and due_input:
            tasks = load_tasks()
            if add_task(tasks, due_input, description):
                save_tasks(tasks)
                return redirect(url_for("index"))

    tasks = load_tasks()
    display_tasks = prepare_display_data(tasks)

    web_tasks = []
    for i, task in enumerate(display_tasks):
        web_tasks.append(
            {
                "id": i + 1,
                "description": task["description"],
                "due_date": task["due_dt"].strftime("%Y-%m-%d %H:%M:%S"),
                "done": task["done"],
                "original_index": task["original_index"],
            }
        )

    now_utc_str = datetime.now(timezone.utc).strftime(DATE_FORMAT)

    return render_template(
        "1759330830.html", tasks=web_tasks, date_format_hint=INPUT_DATE_FORMATS[0], default_due=now_utc_str
    )


@app.route("/<int:original_index>/<action>")
def perform_action(original_index, action):
    """Performs actions (mark, unmark, delete) on a task."""
    tasks = load_tasks()

    if action == "mark":
        mark_task_by_original_index(tasks, original_index)
    elif action == "unmark":
        unmark_task_by_original_index(tasks, original_index)
    elif action == "delete":
        delete_task_by_original_index(tasks, original_index)

    return redirect(url_for("index"))


def run_web():
    """Starts the Flask web application."""
    from waitress import serve

    click.echo("Starting Flask web UI on http://127.0.0.1:8080/")
    serve(app, host="127.0.0.1", port=8080)


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli():
    """Task scheduler CLI"""
    pass


@click.argument("description")
@click.argument("due")
@cli.command(name="a")
def add_cmd(due, description):
    """Add a new task. DUE is the due date, DESCRIPTION is the task description."""
    tasks = load_tasks()
    if add_task(tasks, due, description):
        save_tasks(tasks)
        click.echo("Task added.")


@cli.command(name="l")
def list_cmd():
    """Display the task list."""
    tasks = load_tasks()
    list_tasks(tasks)


@cli.command(name="m")
def mark_cmd():
    """Mark a task as done."""
    tasks = load_tasks()
    mark_done(tasks)


@cli.command(name="u")
def unmark_cmd():
    """Mark a task as pending/not done."""
    tasks = load_tasks()
    unmark_done(tasks)


@cli.command(name="d")
def delete_cmd():
    """Delete a task."""
    tasks = load_tasks()
    delete_task(tasks)


@cli.command(name="t")
def tk_cmd():
    """Launch the Task Scheduler GUI (Tkinter)."""
    run_gui()


@cli.command(name="w")
def web_cmd():
    """Launch the Task Scheduler Web UI (Flask)."""
    run_web()


@cli.command(name="h")
def help_cmd():
    """Show this message and exit."""
    with click.Context(cli) as ctx:
        click.echo(cli.get_help(ctx))


if __name__ == "__main__":
    cli()
