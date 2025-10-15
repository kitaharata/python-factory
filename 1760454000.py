import csv
import io
import json
import tkinter as tk
from tkinter import scrolledtext


class CsvToJson(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CSV to JSON")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(main_frame, text="CSV Input:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Label(main_frame, text="JSON Output:").grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.csv_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=20, width=45)
        self.csv_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.convert_button = tk.Button(main_frame, text="Convert >>", command=self.convert)
        self.convert_button.grid(row=1, column=1, padx=10)

        self.json_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=20, width=45)
        self.json_text.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

    def convert(self):
        csv_data = self.csv_text.get("1.0", tk.END).strip()
        self.json_text.delete("1.0", tk.END)

        if not csv_data:
            self.json_text.insert(tk.END, "Input CSV is empty.")
            return

        try:
            csv_file = io.StringIO(csv_data)
            reader = csv.DictReader(csv_file)
            if not reader.fieldnames:
                self.json_text.insert(tk.END, "CSV input is missing a header row.")
                return
            rows = list(reader)
            json_output = json.dumps(rows, indent=2, sort_keys=False)
            self.json_text.insert(tk.END, json_output)
        except csv.Error as e:
            error_message = f"CSV Parsing Error:\n{e}"
            self.json_text.insert(tk.END, error_message)
        except Exception as e:
            error_message = f"An unexpected error occurred:\n{e}"
            self.json_text.insert(tk.END, error_message)


if __name__ == "__main__":
    app = CsvToJson()
    app.mainloop()
