from datetime import datetime, timedelta
from pathlib import Path
import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

COLUMN_WIDTH = 4
LEFT_WIDTH = 25
BASE_DIR = Path(__file__).resolve().parent
SAVE_FILE = Path.cwd() / "projects.json"
ASSIGNEE_COLORS = [
    "bright_cyan",
    "bright_green",
    "bright_magenta",
    "bright_yellow",
    "bright_blue",
    "bright_red",
    "cyan",
    "green",
    "magenta",
    "yellow",
]


def show_header():
    banner = r"""
██████╗ ██╗   ██╗ ██████╗  █████╗ ███╗   ██╗████████╗████████╗
██╔══██╗╚██╗ ██╔╝██╔════╝ ██╔══██╗████╗  ██║╚══██╔══╝╚══██╔══╝
██████╔╝ ╚████╔╝ ██║  ███╗███████║██╔██╗ ██║   ██║      ██║
██╔═══╝   ╚██╔╝  ██║   ██║██╔══██║██║╚██╗██║   ██║      ██║
██║        ██║   ╚██████╔╝██║  ██║██║ ╚████║   ██║      ██║
╚═╝        ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝      ╚═╝
"""
    console.print(banner, style="bold bright_cyan")
    console.print("A command-line Python-based retro-Gantt chart tool, by Remie Stronks\n", style="italic white")

def show_menu():
    console.print("\n[bold green]--- Gantt Menu ---[/bold green]")
    console.print("[cyan]1.[/cyan] Add new projects")
    console.print("[cyan]2.[/cyan] Add task to existing project")
    console.print("[cyan]3.[/cyan] List projects")
    console.print("[cyan]4.[/cyan] Show gantt chart")
    console.print("[cyan]5.[/cyan] Delete project")
    console.print("[cyan]6.[/cyan] Delete task")
    console.print("[cyan]7.[/cyan] Exit")

def list_projects(projects):
    if not projects:
        console.print("[yellow]No projects available.[/yellow]")
        return

    table = Table(title="Current Projects")
    table.add_column("Project", style="cyan", no_wrap=True)
    table.add_column("Task", style="magenta")
    table.add_column("Assignee", style="green")
    table.add_column("Start", style="white")
    table.add_column("End", style="white")

    for project_name, tasks in projects.items():
        for task in tasks:
            table.add_row(
                project_name,
                task["task"],
                task["assignee"],
                task["start"].strftime("%Y-%m-%d"),
                task["end"].strftime("%Y-%m-%d"),
            )

    console.print(table)


def read_date(prompt):
    while True:
        value = input(prompt)
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            console.print("[bold yellow]Invalid format. Use YYYY-MM-DD.[/bold yellow]")


def read_task_dates():
    while True:
        start = read_date("  Start date (YYYY-MM-DD): ")
        end = read_date("  End date (YYYY-MM-DD): ")

        if end >= start:
            return start, end

        console.print("[bold yellow]End date cannot be earlier than start date.[/bold yellow]")

def serialize_projects(projects):
    serializable = {}

    for project_name, tasks in projects.items():
        serializable[project_name] = []

        for task in tasks:
            serializable[project_name].append({
                "task": task["task"],
                "assignee": task["assignee"],
                "start": task["start"].strftime("%Y-%m-%d"),
                "end": task["end"].strftime("%Y-%m-%d"),
            })

    return serializable


def deserialize_projects(data):
    projects = {}

    for project_name, tasks in data.items():
        projects[project_name] = []

        for task in tasks:
            projects[project_name].append({
                "task": task["task"],
                "assignee": task["assignee"],
                "start": datetime.strptime(task["start"], "%Y-%m-%d"),
                "end": datetime.strptime(task["end"], "%Y-%m-%d"),
            })

    return projects

def save_projects(projects):
    try:
        data = serialize_projects(projects)

        with SAVE_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        console.print(f"[bold green]Projects saved to {SAVE_FILE}.[/bold green]")

    except Exception as e:
        console.print(f"[bold red]Error saving projects: {e}[/bold red]")


def load_projects():
    console.print(f"[blue]Looking for save file at: {SAVE_FILE}[/blue]")

    if not SAVE_FILE.exists():
        console.print("[yellow]Save file not found.[/yellow]")
        return {}

    try:
        with SAVE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        projects = deserialize_projects(data)
        console.print(f"[bold green]Loaded projects from {SAVE_FILE}.[/bold green]")
        return projects

    except Exception as e:
        console.print(f"[bold red]Error loading projects: {e}[/bold red]")
        return {}

def delete_project(projects):
    if not projects:
        console.print("[yellow]No projects available to delete.[/yellow]")
        return False

    console.print("\n[bold red]Delete Project[/bold red]")
    project_names = list(projects.keys())

    for i, name in enumerate(project_names, start=1):
        console.print(f"[cyan]{i}.[/cyan] {name}")

    choice = input("Choose a project number or name to delete: ").strip()

    if choice.isdigit():
        index = int(choice)

        if index < 1 or index > len(project_names):
            console.print("[bold yellow]Invalid project number.[/bold yellow]")
            return False

        project_name = project_names[index - 1]

    else:
        matches = {name.lower(): name for name in project_names}

        if choice.lower() not in matches:
            console.print("[bold yellow]Project not found.[/bold yellow]")
            return False

        project_name = matches[choice.lower()]

    confirm = input(f"Are you sure you want to delete '{project_name}'? (y/n): ").strip().lower()

    if confirm == "y":
        del projects[project_name]
        console.print(f"[bold green]Project '{project_name}' deleted.[/bold green]")
        return True

    console.print("[yellow]Deletion cancelled.[/yellow]")
    return False

def delete_task(projects):
    if not projects:
        console.print("[yellow]No projects available.[/yellow]")
        return False

    console.print("\n[bold red]Delete Task[/bold red]")
    project_names = list(projects.keys())

    for i, name in enumerate(project_names, start=1):
        console.print(f"[cyan]{i}.[/cyan] {name}")

    project_choice = input("Choose a project number or name: ").strip()

    # Select project
    if project_choice.isdigit():
        project_index = int(project_choice)

        if project_index < 1 or project_index > len(project_names):
            console.print("[bold yellow]Invalid project number.[/bold yellow]")
            return False

        project_name = project_names[project_index - 1]

    else:
        matches = {name.lower(): name for name in project_names}

        if project_choice.lower() not in matches:
            console.print("[bold yellow]Project not found.[/bold yellow]")
            return False

        project_name = matches[project_choice.lower()]

    tasks = projects[project_name]

    if not tasks:
        console.print("[yellow]This project has no tasks.[/yellow]")
        return False

    console.print(f"\n[bold cyan]Tasks in '{project_name}':[/bold cyan]")
    for i, task in enumerate(tasks, start=1):
        console.print(
            f"[cyan]{i}.[/cyan] {task['task']} "
            f"([green]{task['assignee']}[/green], "
            f"{task['start'].strftime('%Y-%m-%d')} → {task['end'].strftime('%Y-%m-%d')})"
        )

    task_choice = input("Choose a task number to delete: ").strip()

    if not task_choice.isdigit():
        console.print("[bold yellow]Invalid input. Please enter a number.[/bold yellow]")
        return False

    task_index = int(task_choice)

    if task_index < 1 or task_index > len(tasks):
        console.print("[bold yellow]Invalid task number.[/bold yellow]")
        return False

    task_to_delete = tasks[task_index - 1]

    confirm = input(
        f"Are you sure you want to delete task '{task_to_delete['task']}' from project '{project_name}'? (y/n): "
    ).strip().lower()

    if confirm != "y":
        console.print("[yellow]Deletion cancelled.[/yellow]")
        return False

    del tasks[task_index - 1]
    console.print(f"[bold green]Task '{task_to_delete['task']}' deleted.[/bold green]")

    if not tasks:
        del projects[project_name]
        console.print(f"[yellow]Project '{project_name}' had no tasks left and was removed.[/yellow]")

    return True


def get_projects():
    projects = {}

    while True:
        project_name = input("Enter project name (or press Enter to finish): ").strip()
        if project_name == "":
            break

        tasks = []

        while True:
            task_name = input("  Task name (or press Enter to finish this project): ").strip()
            if task_name == "":
                break

            assignee = input("  Assignee: ").strip()
            start, end = read_task_dates()

            tasks.append({
                "task": task_name,
                "assignee": assignee,
                "start": start,
                "end": end
            })

        projects[project_name] = tasks

    return projects


def add_task_to_existing_project(projects):
    if not projects:
        console.print("[yellow]No projects available yet.[/yellow]")
        return

    console.print("\n[bold cyan]Existing projects:[/bold cyan]")
    project_names = list(projects.keys())

    for i, name in enumerate(project_names, start=1):
        console.print(f"[cyan]{i}.[/cyan] {name}")

    choice = input("Choose a project number: ").strip()

    if not choice.isdigit():
        console.print("[bold yellow]Invalid input. Please enter a number.[/bold yellow]")
        return

    choice = int(choice)

    if choice < 1 or choice > len(project_names):
        console.print("[bold yellow]Invalid project number.[/bold yellow]")
        return

    project_name = project_names[choice - 1]

    task_name = input("  Task name: ").strip()
    assignee = input("  Assignee: ").strip()
    start, end = read_task_dates()

    projects[project_name].append({
        "task": task_name,
        "assignee": assignee,
        "start": start,
        "end": end
    })

    console.print(f"[bold green]Task added to project '{project_name}'.[/bold green]")

def build_assignee_colors(projects):
    assignees = []
    
    for tasks in projects.values():
        for task in tasks:
            assignee = task["assignee"]
            if assignee not in assignees:
                assignees.append(assignee)

    color_map = {}

    for i, assignee in enumerate(assignees):
        color_map[assignee] = ASSIGNEE_COLORS[i % len(ASSIGNEE_COLORS)]

    return color_map

def fit_label(text, width):
    return text if len(text) <= width else text[:width - 3] + "..."

def print_task_row(label, cells):
    row = f"{label:<{LEFT_WIDTH}}"
    for cell in cells:
        row += f"|{cell}"
    row += "|"
    console.print(row)

def print_today_row(label, timeline):
    print(f"{label:<{LEFT_WIDTH}}", end="")

    today = datetime.today().date()

    for d in timeline:
        if d.date() == today:
            cell = "▲▲"
        else:
            cell = ""

        print(f"|{cell:^{COLUMN_WIDTH}}", end="")

    print("|")

def print_normal_row(label, values):
    print(f"{label:<{LEFT_WIDTH}}", end="")
    for value in values:
        print(f"|{value:^{COLUMN_WIDTH}}", end="")
    print("|")


def print_month_row(label, values, timeline):
    print(f"{label:<{LEFT_WIDTH}}", end="")
    previous_month = None

    for value, d in zip(values, timeline):
        if d.month != previous_month:
            cell = f"{value:^{COLUMN_WIDTH}}"
        else:
            cell = " " * COLUMN_WIDTH

        print(f"|{cell}", end="")
        previous_month = d.month

    print("|")


def print_week_row(label, timeline):
    print(f"{label:<{LEFT_WIDTH}}", end="")
    previous_week = None

    for d in timeline:
        week = d.isocalendar().week

        if week != previous_week:
            cell = f"{week:02d}"
        else:
            cell = ""

        print(f"|{cell:^{COLUMN_WIDTH}}", end="")
        previous_week = week

    print("|")


def show_gantt(projects):
    all_tasks = [task for task_list in projects.values() for task in task_list]

    if not all_tasks:
        console.print("[yellow]No tasks entered yet.[/yellow]")
        return

    console.print(Panel.fit("[bold cyan]Gantt Chart[/bold cyan]", border_style="cyan"))

    project_start = min(task["start"] for task in all_tasks)
    project_end = max(task["end"] for task in all_tasks)

    timeline = []
    current = project_start
    while current <= project_end:
        timeline.append(current)
        current += timedelta(days=1)

    assignee_colors = build_assignee_colors(projects)

    total_width = LEFT_WIDTH + len(timeline) * (COLUMN_WIDTH + 1) + 1
    print("_" * total_width)

    year_values = [f"{d.year}" for d in timeline]

    month_values = []
    previous_month = None
    for d in timeline:
        if d.month != previous_month:
            month_values.append(f"{d.month:02d}")
        else:
            month_values.append("")
        previous_month = d.month

    day_values = [f"{d.day:02d}" for d in timeline]
    weekday_values = [d.strftime("%a")[:2] for d in timeline]

    print_normal_row("Year", year_values)
    print_month_row("Month", month_values, timeline)
    print_week_row("Week", timeline)
    print_today_row("Today", timeline)
    print_normal_row("Day", day_values)
    print_normal_row("Weekday", weekday_values)

    weekend_days = {5, 6}

    for project_name, tasks in projects.items():
        console.print(f"\n[bold magenta]{project_name}[/bold magenta]")

        for task in tasks:
            cells = []
            color = assignee_colors.get(task["assignee"], "white")

            for d in timeline:
                is_weekend = d.weekday() in weekend_days
                is_task_day = task["start"] <= d <= task["end"]

                if is_task_day and is_weekend:
                    cells.append(f"[{color}]{'▓' * COLUMN_WIDTH}[/{color}]")
                elif is_task_day:
                    cells.append(f"[{color}]{'█' * COLUMN_WIDTH}[/{color}]")
                elif is_weekend:
                    cells.append("░" * COLUMN_WIDTH)
                else:
                    cells.append(" " * COLUMN_WIDTH)

            label = fit_label(f"{task['assignee']} - {task['task']}", LEFT_WIDTH)
            print_task_row(label, cells)

        print()

def main():
    projects = load_projects()
    show_header()

    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            new_projects = get_projects()
            if new_projects:
                projects.update(new_projects)
                save_projects(projects)
                console.print("[bold green]Projects added.[/bold green]")
            else:
                console.print("[yellow]No new projects were added.[/yellow]")

        elif choice == "2":
            add_task_to_existing_project(projects)
            save_projects(projects)

        elif choice == "3":
            list_projects(projects)

        elif choice == "4":
            show_gantt(projects)

        elif choice == "5":
            if delete_project(projects):
                save_projects(projects)

        elif choice == "6":
            if delete_task(projects):
                save_projects(projects)

        elif choice == "7":
            console.print("[bold red]Goodbye.[/bold red]")
            break

        else:
            console.print("[bold yellow]Invalid choice. Please enter 1, 2, 3, 4, 5, 6, or 7.[/bold yellow]")


if __name__ == "__main__":
    main()