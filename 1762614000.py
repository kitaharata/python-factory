import psutil


def display_processes():
    """Display information about currently running processes."""

    header = f"{'PID':<10} {'Name':<40} {'Status':<10} {'CPU %':<10} {'Memory %':<10}"
    print(header)
    print("-" * len(header))

    for proc in psutil.process_iter(["pid", "name", "status", "cpu_percent", "memory_percent"]):
        try:
            pinfo = proc.info
            pid = pinfo["pid"]
            name = pinfo["name"]
            status = pinfo["status"]
            cpu_percent = pinfo["cpu_percent"]
            memory_percent = pinfo["memory_percent"]

            print(f"{pid:<10} {name:<40.40} {status:<10} {cpu_percent:<10.2f} {memory_percent:<10.2f}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue


if __name__ == "__main__":
    display_processes()
