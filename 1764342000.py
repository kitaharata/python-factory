import base64
import tkinter as tk
from tkinter import ttk


class Base64EncoderApp(tk.Tk):
    """A real-time Base64 encoder application built with Tkinter."""

    def __init__(self):
        super().__init__()
        self.title("Base64 Encoder (Real-Time)")
        self.geometry("800x150")
        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar()
        self.input_var.trace_add("write", self.update_base64_conversion)
        self.create_widgets()

    def update_base64_conversion(self, *args):
        """Performs Base64 conversion and updates the result whenever input text changes."""
        input_text = self.input_var.get()
        try:
            encoded_bytes = base64.b64encode(input_text.encode("utf-8"))
            output_text = encoded_bytes.decode("utf-8")
        except Exception as e:
            output_text = f"Error: {e}"
        self.output_var.set(output_text)

    def create_widgets(self):
        """Creates and arranges the Tkinter widgets for the application."""
        ttk.Label(self, text="Input Text:").pack(pady=(10, 0))
        input_entry = ttk.Entry(self, textvariable=self.input_var)
        input_entry.pack(pady=5, padx=10, fill="x")
        ttk.Label(self, text="Base64 Result:").pack(pady=(10, 0))
        output_display = ttk.Entry(self, textvariable=self.output_var, state="readonly")
        output_display.pack(pady=5, padx=10, fill="x")
        input_entry.focus_set()


if __name__ == "__main__":
    app = Base64EncoderApp()
    app.mainloop()
