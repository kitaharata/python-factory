import json
import os
from datetime import datetime

import click

TASK_FILE = "task_list.json"
DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
INPUT_DATE_FORMATS = [
    DATE_FORMAT,
    "%Y%m%dT%H%M%SZ",
    "%Y%m%d%H%M%S",
]


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


@cli.command(name="d")
def delete_cmd():
    """Delete a task."""
    tasks = load_tasks()
    delete_task(tasks)


@cli.command(name="h")
def help_cmd():
    """Show this message and exit."""
    with click.Context(cli) as ctx:
        click.echo(cli.get_help(ctx))


if __name__ == "__main__":
    cli()
