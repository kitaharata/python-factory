import tkinter as tk
from urllib.parse import urlparse

import requests


class DohResolverApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DNS over HTTPS Resolver")
        self.setup_ui()

    def setup_ui(self):
        frame = tk.Frame(self, padx=20, pady=20)
        frame.pack()

        tk.Label(frame, text="Enter a domain or URL:").pack()

        self.entry = tk.Entry(frame, width=50)
        self.entry.pack()

        self.record_type = tk.StringVar(value="A")
        tk.Label(frame, text="Select record type:").pack()

        record_options = ["A", "AAAA", "MX", "CNAME", "TXT", "NS"]
        type_menu = tk.OptionMenu(frame, self.record_type, *record_options)
        type_menu.pack()

        tk.Button(frame, text="Resolve DNS", command=self.resolve_dns).pack(pady=10)

        self.result_label = tk.Label(frame, text="", justify="left")
        self.result_label.pack()

    def extract_hostname(self, user_input):
        if "://" not in user_input:
            user_input = "http://" + user_input
        try:
            parsed = urlparse(user_input)
            return parsed.hostname
        except Exception:
            return None

    def resolve_dns(self):
        user_input = self.entry.get().strip()
        record_type = self.record_type.get().upper()

        hostname = self.extract_hostname(user_input)
        if not hostname:
            self.result_label.config(text="Invalid input. Please enter a valid domain or URL.")
            return

        url = "https://cloudflare-dns.com/dns-query"
        headers = {"Accept": "application/dns-json"}
        params = {"name": hostname, "type": record_type}

        try:
            response = requests.get(url, headers=headers, params=params)
            data = response.json()

            if "Answer" in data:
                answers = data["Answer"]
                results = [f"{ans['name']} ({ans['type']}): {ans['data']}" for ans in answers]
                self.result_label.config(text="\n".join(results))
            else:
                self.result_label.config(text="No DNS records found.")
        except Exception as e:
            self.result_label.config(text=f"Error occurred:\n{e}")


if __name__ == "__main__":
    app = DohResolverApp()
    app.mainloop()
