import os
import sys
import time
import tkinter as tk
from tkinter import ttk

MAX_AGE_SECONDS = 30 * 24 * 3600


def calculate_recency(mtime):
    """Calculates file recency score (0.0=cold, 1.0=hot) based on modification time."""
    current_time = time.time()
    time_diff = current_time - mtime
    if time_diff >= MAX_AGE_SECONDS:
        return 0.0
    recency_score = 1.0 - (time_diff / MAX_AGE_SECONDS)
    return recency_score


def get_file_stats(directory):
    """Scans a directory recursively and calculates recency for each file."""
    file_stats = []
    print(f"Scanning directory: {directory}")
    for root, _, files in os.walk(directory):
        for filename in files:
            filepath = os.path.join(root, filename)
            try:
                if os.path.exists(filepath) and not filename.startswith("~"):
                    stats = os.stat(filepath)
                    mtime = stats.st_mtime
                    recency = calculate_recency(mtime)
                    file_stats.append({"path": filepath, "mtime": mtime, "recency": recency})
            except OSError as e:
                print(f"Skipping {filepath} due to OS error: {e}")
                continue
    print(f"Found {len(file_stats)} files.")
    return file_stats


def get_heat_color(recency):
    """Converts recency score (0.0-1.0) to an RGB hex color string (Black -> Red -> Yellow) for Tkinter."""
    if recency < 0.5:
        R = int(255 * (recency * 2))
        G = 0
        B = 0
    else:
        R = 255
        G = int(255 * ((recency - 0.5) * 2))
        B = 0
    return f"#{R:02X}{G:02X}{B:02X}"


class FileRecencyApp(tk.Tk):
    """Displays file recency scores in a Tkinter window."""

    def __init__(self, target_dir):
        super().__init__()
        self.target_dir = target_dir

        file_stats = get_file_stats(target_dir)
        N = len(file_stats)

        if N == 0:
            print("No files found to display.")
            self.after(1, self.destroy)
            return

        self.title("File Access Heatmap")
        self.geometry("800x600")
        self.display_files(file_stats)

    def display_files(self, file_stats):
        file_stats.sort(key=lambda x: x["recency"], reverse=True)

        frame = ttk.Frame(self, padding="10")
        frame.pack(fill="both", expand=True)

        tree = ttk.Treeview(frame, columns=("Recency", "Modification Time"), show="tree headings")
        tree.heading("#0", text="File Path")
        tree.heading("Recency", text="Recency Score")
        tree.heading("Modification Time", text="Modification Time")
        tree.column("#0", minwidth=100, width=450, stretch=tk.NO, anchor=tk.W)
        tree.column("Recency", minwidth=100, width=100, stretch=tk.NO, anchor=tk.CENTER)
        tree.column("Modification Time", minwidth=100, width=200, stretch=tk.NO, anchor=tk.E)

        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill="both", expand=True)

        for i, stats in enumerate(file_stats):
            recency = stats["recency"]
            color_hex = get_heat_color(recency)
            tag_name = f"color{i}"
            tree.tag_configure(tag_name, background=color_hex, foreground="white")
            if recency > 0.8:
                tree.tag_configure(tag_name, foreground="black")
            filepath = stats["path"]
            mtime_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stats["mtime"]))
            tree.insert("", "end", text=filepath, values=(f"{recency:.4f}", mtime_str), tags=(tag_name,))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = os.getcwd()

    if not os.path.isdir(target_dir):
        print(f"Error: Directory not found: {target_dir}")
        sys.exit(1)

    app = FileRecencyApp(target_dir)
    app.mainloop()
