import hashlib
import time
import tkinter as tk
from tkinter import ttk


class SHA256CalculatorApp(tk.Tk):
    """A real-time SHA256 hash calculator application built with Tkinter."""

    def __init__(self):
        super().__init__()
        self.title("SHA256 Calculator (Real-Time)")
        self.geometry("800x200")
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.input_var.trace_add("write", self.update_sha256_calculation)
        self.create_widgets()

    def update_sha256_calculation(self, *args):
        """Calculates the SHA256 hash and updates the result and calculation time whenever input text changes."""
        start_time = time.perf_counter()
        input_text = self.input_var.get()
        try:
            sha256_hash = hashlib.sha256(input_text.encode("utf-8")).hexdigest()
            output_text = sha256_hash
        except Exception as e:
            output_text = f"Error: {e}"
        end_time = time.perf_counter()
        elapsed_time = (end_time - start_time) * 1000
        self.output_var.set(output_text)
        self.time_var.set(f"Calculation Time: {elapsed_time:.4f} ms")

    def create_widgets(self):
        """Creates and arranges the Tkinter widgets for the application."""
        ttk.Label(self, text="Input Text:").pack(pady=(10, 0))
        input_entry = ttk.Entry(self, textvariable=self.input_var)
        input_entry.pack(pady=5, padx=10, fill="x")
        ttk.Label(self, text="SHA256 Hash:").pack(pady=(10, 0))
        output_display = ttk.Entry(self, textvariable=self.output_var, state="readonly")
        output_display.pack(pady=5, padx=10, fill="x")
        ttk.Label(self, textvariable=self.time_var).pack(pady=(10, 0))
        input_entry.focus_set()


if __name__ == "__main__":
    app = SHA256CalculatorApp()
    app.mainloop()
