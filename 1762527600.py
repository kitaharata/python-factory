import os
import time

import psutil


def bytes_to_gb(b):
    """Helper function to convert bytes to gigabytes."""
    return b / (1024**3)


def display_stats():
    """Clears the screen and displays system monitoring statistics."""
    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")

    cpu_percent = psutil.cpu_percent(interval=None)
    print(f"[1. CPU Usage]: {cpu_percent}%")

    mem = psutil.virtual_memory()
    mem_total_gb = bytes_to_gb(mem.total)
    mem_used_gb = bytes_to_gb(mem.used)
    print(f"[2. Memory Usage]: {mem.percent}% ({mem_used_gb:.2f} GB / {mem_total_gb:.2f} GB)")

    print("[3. Disk Usage]:")
    for partition in psutil.disk_partitions():
        if "cdrom" in partition.opts or partition.fstype == "":
            continue

        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disk_total_gb = bytes_to_gb(usage.total)
            disk_used_gb = bytes_to_gb(usage.used)
            disk_info = f"  {partition.device} ({partition.mountpoint}) [{partition.fstype}]: "
            usage_info = f"{usage.percent}% ({disk_used_gb:.2f} GB / {disk_total_gb:.2f} GB)"
            print(disk_info + usage_info)
        except Exception:
            pass

    net_io = psutil.net_io_counters()
    bytes_sent_mb = net_io.bytes_sent / (1024 * 1024)
    bytes_recv_mb = net_io.bytes_recv / (1024 * 1024)
    print(f"[4. Network I/O (Since Boot)]: Sent {bytes_sent_mb:.2f} MB, Received {bytes_recv_mb:.2f} MB")

    print("Updates every 3 seconds. Press Ctrl+C to exit.")


if __name__ == "__main__":
    psutil.cpu_percent(interval=0.1)

    try:
        while True:
            display_stats()
            time.sleep(3)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")
