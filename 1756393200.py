import os
import sys
import tkinter as tk
import zipfile
from tkinter import messagebox


class ZipTextViewer:
    """A Tkinter application for viewing text files in a ZIP file."""

    def __init__(self, master, zip_path):
        self.master = master
        self.zip_path = zip_path
        self.viewable_files = []
        self.current_file_index = 0
        self.master.title(f"ZIP Text Viewer - {os.path.basename(zip_path)}")
        self.master.geometry("800x600")

        self.load_file_list()
        if not self.viewable_files:
            messagebox.showinfo("Info", "No viewable text files found in the ZIP file.")
            self.master.destroy()
            return

        self.status_label = tk.Label(self.master, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.text_widget = tk.Text(main_frame, wrap=tk.WORD, bg="white", fg="black")
        self.text_scroll = tk.Scrollbar(main_frame, command=self.text_widget.yview)
        self.text_widget.config(yscrollcommand=self.text_scroll.set)
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_widget.pack(pady=10, expand=True, fill=tk.BOTH)

        self.master.bind("<Left>", lambda e: self.prev_file())
        self.master.bind("<Right>", lambda e: self.next_file())
        self.master.bind("<Up>", lambda e: self.prev_file())
        self.master.bind("<Down>", lambda e: self.next_file())

        self.load_and_show_file()
        self.update_ui()

    def load_file_list(self):
        """Load a list of viewable text files from the ZIP file."""
        try:
            with zipfile.ZipFile(self.zip_path, "r") as zf:
                for file_info in zf.infolist():
                    if file_info.is_dir():
                        continue
                    lower_filename = file_info.filename.lower()
                    if lower_filename.endswith((".txt", ".csv", ".json", ".htm", ".html", ".md")):
                        self.viewable_files.append(file_info.filename)
        except zipfile.BadZipFile:
            messagebox.showerror("Error", "Invalid ZIP file.")
            self.master.destroy()
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {self.zip_path}")
            self.master.destroy()

    def load_and_show_file(self):
        """Load and display the text file at the current index from the ZIP file."""
        if not self.viewable_files:
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(tk.END, "No file to display")
            return
        file_path = self.viewable_files[self.current_file_index]
        try:
            with zipfile.ZipFile(self.zip_path, "r") as zf:
                with zf.open(file_path) as text_file:
                    file_content = text_file.read()
                    self.text_widget.delete(1.0, tk.END)
                    try:
                        decoded_content = file_content.decode("utf-8")
                    except UnicodeDecodeError:
                        decoded_content = file_content.decode("shift_jis", errors="replace")
                    self.text_widget.insert(tk.END, decoded_content)
        except Exception as e:
            messagebox.showerror("File Load Error", f"An error occurred while loading {file_path}.\n{e}")
            self.text_widget.delete(1.0, tk.END)
            self.text_widget.insert(tk.END, f"{file_path}\nLoad Error")

    def next_file(self):
        """Display the next file."""
        if self.viewable_files and len(self.viewable_files) > 1:
            self.current_file_index = (self.current_file_index + 1) % len(self.viewable_files)
            self.load_and_show_file()
            self.update_ui()

    def prev_file(self):
        """Display the previous file."""
        if self.viewable_files and len(self.viewable_files) > 1:
            self.current_file_index = (self.current_file_index - 1 + len(self.viewable_files)) % len(
                self.viewable_files
            )
            self.load_and_show_file()
            self.update_ui()

    def update_ui(self):
        """Update the status bar."""
        if self.viewable_files:
            file_count = len(self.viewable_files)
            current_filename = self.viewable_files[self.current_file_index]
            status_text = f"{self.current_file_index + 1} / {file_count} | {current_filename}"
            self.status_label.config(text=status_text)
        else:
            self.status_label.config(text="No files")


if __name__ == "__main__":
    """The entry point of the application."""
    if len(sys.argv) < 2:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Argument Error", "Please specify a ZIP file as an argument.")
        root.destroy()
        sys.exit()

    zip_path = sys.argv[1]
    root = tk.Tk()
    app = ZipTextViewer(root, zip_path)
    root.mainloop()
