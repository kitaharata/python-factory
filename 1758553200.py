import os
import tkinter as tk
from tkinter import filedialog, messagebox


class HexDumpViewer(tk.Tk):
    """A Tkinter-based hex dump viewer for binary files."""

    def __init__(self):
        """Initialize the hex dump viewer window and UI components."""
        super().__init__()
        self.title("Hex Dump Viewer")

        self.frame = tk.Frame(self)
        self.frame.pack(expand=True, fill="both")

        self.text = tk.Text(self.frame, width=100, height=30, font=("Courier", 10))
        self.scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbar.set)

        self.text.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.button = tk.Button(self, text="Open File", command=self.open_file)
        self.button.pack(pady=5)

    def open_file(self):
        """Open a binary file selected via dialog and load its content for display."""
        file_path = filedialog.askopenfilename(title="Select Binary File", filetypes=[("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, "rb") as f:
                    data = f.read()
                    self.title(f"Hex Dump Viewer - {os.path.basename(file_path)}")
                self.display_hex(data)
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open file: {e}")

    def display_hex(self, data):
        """Display the binary data as a formatted hex dump in the text widget."""
        self.text.delete(1.0, tk.END)
        bytes_per_line = 16
        for i in range(0, len(data), bytes_per_line):
            chunk = data[i : i + bytes_per_line]
            offset = f"{i:08x}"
            hex_part = []
            for j in range(len(chunk)):
                hex_part.append(f"{chunk[j]:02x}")
                if j == 7:
                    hex_part.append("")
            hex_str = " ".join(hex_part)
            if len(chunk) < bytes_per_line:
                hex_str += " " * (3 * (bytes_per_line - len(chunk)))
            ascii_part = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
            ascii_part += " " * (bytes_per_line - len(chunk))
            line = f"{offset}  {hex_str}  {ascii_part}\n"
            self.text.insert(tk.END, line)


if __name__ == "__main__":
    app = HexDumpViewer()
    app.mainloop()
