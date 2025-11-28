import calendar
import tkinter as tk
from datetime import datetime


class CalendarApp(tk.Tk):
    """Initializes and displays a calendar for the current month."""

    def __init__(self):
        super().__init__()
        self.title("Tkinter Calendar")
        self.geometry("800x600")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        now = datetime.now()
        self.year = now.year
        self.month = now.month
        cal_content = calendar.month(self.year, self.month)
        self.calendar_display = tk.Text(self, font=("Courier", 36), height=10, width=25, wrap=tk.NONE, relief=tk.FLAT)
        self.calendar_display.insert(tk.END, cal_content)
        self.calendar_display.config(state=tk.DISABLED)
        self.calendar_display.grid(row=0, column=0, padx=10, pady=10)


if __name__ == "__main__":
    app = CalendarApp()
    app.mainloop()
