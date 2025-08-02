import tkinter as tk
from tkinter import messagebox


class TimerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Timer App")
        self.geometry("350x250")
        self.resizable(False, False)

        self.remaining_time = 0
        self.timer_id = None
        self.is_running = False

        self.time_label = tk.Label(self, text="00:00:00", font=("Arial", 48))
        self.time_label.pack(pady=20)

        input_frame = tk.Frame(self)
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Set time (HH:MM:SS):").pack(side=tk.LEFT, padx=5)
        self.entry = tk.Entry(input_frame, width=10)
        self.entry.pack(side=tk.LEFT)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(button_frame, text="Start", width=8, command=self.start_timer)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = tk.Button(button_frame, text="Stop", width=8, command=self.stop_timer, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(button_frame, text="Reset", width=8, command=self.reset_timer, state=tk.DISABLED)
        self.reset_button.pack(side=tk.LEFT, padx=5)

    def format_time(self, seconds):
        """Formats seconds into HH:MM:SS string."""
        mins, secs = divmod(seconds, 60)
        hours, mins = divmod(mins, 60)
        return f"{hours:02d}:{mins:02d}:{secs:02d}"

    def set_time_from_entry(self):
        """Parses time from entry and sets remaining_time. Returns True on success."""
        try:
            time_str = self.entry.get()
            seconds = 0
            if ":" in time_str:
                parts = time_str.split(":")
                if len(parts) == 2:
                    mins = int(parts[0])
                    secs = int(parts[1])
                    seconds = mins * 60 + secs
                elif len(parts) == 3:
                    hours = int(parts[0])
                    mins = int(parts[1])
                    secs = int(parts[2])
                    seconds = hours * 3600 + mins * 60 + secs
                else:
                    raise ValueError
            else:
                seconds = int(time_str)

            if seconds <= 0:
                messagebox.showerror("Invalid Input", "Please enter a positive time.")
                self.remaining_time = 0
                return False

            self.remaining_time = seconds
            return True
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid time (e.g., 1:00:00, 60:00, or 3600).")
            return False

    def start_timer(self):
        """Starts or resumes the countdown."""
        if self.is_running:
            return

        if self.remaining_time <= 0:
            if not self.set_time_from_entry():
                return

        self.is_running = True
        self.toggle_buttons()
        self.countdown()

    def stop_timer(self):
        """Stops/pauses the countdown."""
        if not self.is_running:
            return

        self.is_running = False
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.toggle_buttons()

    def reset_timer(self):
        """Stops and resets the timer to its initial state."""
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None

        self.is_running = False
        self.remaining_time = 0
        self.time_label.config(text=self.format_time(0))
        self.entry.delete(0, tk.END)
        self.toggle_buttons()

    def countdown(self):
        """Handles the per-second countdown logic."""
        if self.is_running and self.remaining_time >= 0:
            self.time_label.config(text=self.format_time(self.remaining_time))
            if self.remaining_time == 0:
                self.is_running = False
                messagebox.showinfo("Timer", "Time's up!")
                self.reset_timer()
            else:
                self.remaining_time -= 1
                self.timer_id = self.after(1000, self.countdown)

    def toggle_buttons(self):
        """Enables/disables buttons based on the timer's state."""
        if self.is_running:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.NORMAL)
            self.entry.config(state=tk.DISABLED)
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            if self.remaining_time > 0:
                self.reset_button.config(state=tk.NORMAL)
                self.entry.config(state=tk.DISABLED)
            else:
                self.reset_button.config(state=tk.DISABLED)
                self.entry.config(state=tk.NORMAL)


if __name__ == "__main__":
    app = TimerApp()
    app.mainloop()
