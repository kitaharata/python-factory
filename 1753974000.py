import json
import os

TODO_FILE = "todo_list.json"


def load_tasks():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return []
    return []


def save_tasks(tasks):
    with open(TODO_FILE, "w") as file:
        json.dump(tasks, file, indent=4)


def add_task(tasks):
    task_description = input("Enter the task description: ")
    tasks.append({"description": task_description, "completed": False})
    save_tasks(tasks)
    print("Task added successfully.")


def view_tasks(tasks):
    if not tasks:
        print("No tasks in the list.")
        return
    print("\n--- To-Do List ---")
    for i, task in enumerate(tasks):
        status = "\u2713" if task["completed"] else " "
        print(f"{i + 1}. [{status}] {task['description']}")
    print("------------------\n")


def mark_task_complete(tasks):
    view_tasks(tasks)
    try:
        task_num = int(input("Enter the task number to mark as complete: "))
        if 1 <= task_num <= len(tasks):
            tasks[task_num - 1]["completed"] = True
            save_tasks(tasks)
            print("Task marked as complete.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def delete_task(tasks):
    view_tasks(tasks)
    try:
        task_num = int(input("Enter the task number to delete: "))
        if 1 <= task_num <= len(tasks):
            removed_task = tasks.pop(task_num - 1)
            save_tasks(tasks)
            print(f"Task '{removed_task['description']}' deleted.")
        else:
            print("Invalid task number.")
    except ValueError:
        print("Invalid input. Please enter a number.")


def main():
    tasks = load_tasks()
    while True:
        print("\nToDo App Menu:")
        print("1. Add a task")
        print("2. View all tasks")
        print("3. Mark a task as complete")
        print("4. Delete a task")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == "1":
            add_task(tasks)
        elif choice == "2":
            view_tasks(tasks)
        elif choice == "3":
            mark_task_complete(tasks)
        elif choice == "4":
            delete_task(tasks)
        elif choice == "5":
            print("Exiting ToDo App. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()
