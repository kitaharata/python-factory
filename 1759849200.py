import json
import tkinter as tk
from tkinter import scrolledtext

import yaml


class YamlToJson(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YAML to JSON")
        self.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(main_frame, text="YAML Input:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Label(main_frame, text="JSON Output:").grid(row=0, column=2, padx=5, pady=5, sticky="w")

        self.yaml_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=20, width=45)
        self.yaml_text.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.convert_button = tk.Button(main_frame, text="Convert >>", command=self.convert)
        self.convert_button.grid(row=1, column=1, padx=10)

        self.json_text = scrolledtext.ScrolledText(main_frame, wrap=tk.WORD, height=20, width=45)
        self.json_text.grid(row=1, column=2, sticky="nsew", padx=5, pady=5)

        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(2, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)

    def convert(self):
        yaml_data = self.yaml_text.get("1.0", tk.END).strip()
        self.json_text.delete("1.0", tk.END)

        if not yaml_data:
            self.json_text.insert(tk.END, "Input YAML is empty.")
            return

        try:
            data = yaml.safe_load(yaml_data)
            if data is None:
                self.json_text.insert(tk.END, "YAML input appears empty or contains only comments/whitespace.")
                return
            json_output = json.dumps(data, indent=2, sort_keys=False)
            self.json_text.insert(tk.END, json_output)
        except yaml.YAMLError as e:
            error_message = f"YAML Parsing Error:\n{e}"
            self.json_text.insert(tk.END, error_message)
        except Exception as e:
            error_message = f"An unexpected error occurred:\n{e}"
            self.json_text.insert(tk.END, error_message)


if __name__ == "__main__":
    app = YamlToJson()
    app.mainloop()
