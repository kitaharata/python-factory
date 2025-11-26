import math
import tkinter as tk
from datetime import datetime


class AnalogClock(tk.Tk):
    """An analog clock application."""

    def __init__(self):
        super().__init__()
        self.title("Analog Clock")
        self.geometry("800x600")
        self.canvas_width = 800
        self.canvas_height = 600
        self.center_x = self.canvas_width // 2
        self.center_y = self.canvas_height // 2
        self.radius = 200
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(padx=10, pady=10)
        self.draw_clock_face()
        self.second_hand = None
        self.minute_hand = None
        self.hour_hand = None
        self.update_clock()

    def draw_clock_face(self):
        self.canvas.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            outline="black",
            width=2,
        )
        pivot_radius = 5
        self.canvas.create_oval(
            self.center_x - pivot_radius,
            self.center_y - pivot_radius,
            self.center_x + pivot_radius,
            self.center_y + pivot_radius,
            fill="black",
        )
        marker_length = 10
        for i in range(12):
            angle = math.pi / 2 - (i / 12) * 2 * math.pi
            r_inner = self.radius - marker_length
            r_outer = self.radius
            x1 = self.center_x + r_inner * math.cos(angle)
            y1 = self.center_y - r_inner * math.sin(angle)
            x2 = self.center_x + r_outer * math.cos(angle)
            y2 = self.center_y - r_outer * math.sin(angle)
            self.canvas.create_line(x1, y1, x2, y2, width=3, fill="black")
            num = 12 if i == 0 else i
            text_r = self.radius - 25
            tx = self.center_x + text_r * math.cos(angle)
            ty = self.center_y - text_r * math.sin(angle)
            self.canvas.create_text(tx, ty, text=str(num), font=("Arial", 12, "bold"))

    def get_hand_coords(self, angle, length):
        x = self.center_x + length * math.sin(angle)
        y = self.center_y - length * math.cos(angle)
        return x, y

    def update_clock(self):
        now = datetime.now()
        h = now.hour % 12
        m = now.minute
        s = now.second
        s_angle = s * (2 * math.pi / 60)
        m_angle = (m + s / 60) * (2 * math.pi / 60)
        h_angle = (h + m / 60 + s / 3600) * (2 * math.pi / 12)
        hour_len = self.radius * 0.5
        minute_len = self.radius * 0.7
        second_len = self.radius * 0.8
        hx, hy = self.get_hand_coords(h_angle, hour_len)
        mx, my = self.get_hand_coords(m_angle, minute_len)
        sx, sy = self.get_hand_coords(s_angle, second_len)
        if self.second_hand:
            self.canvas.delete(self.second_hand)
            self.canvas.delete(self.minute_hand)
            self.canvas.delete(self.hour_hand)
        self.hour_hand = self.canvas.create_line(
            self.center_x, self.center_y, hx, hy, width=6, fill="blue", capstyle=tk.ROUND
        )
        self.minute_hand = self.canvas.create_line(
            self.center_x, self.center_y, mx, my, width=4, fill="green", capstyle=tk.ROUND
        )
        self.second_hand = self.canvas.create_line(self.center_x, self.center_y, sx, sy, width=2, fill="red")
        pivot_radius = 5
        self.canvas.create_oval(
            self.center_x - pivot_radius,
            self.center_y - pivot_radius,
            self.center_x + pivot_radius,
            self.center_y + pivot_radius,
            fill="black",
        )
        self.canvas.after(1000, self.update_clock)


if __name__ == "__main__":
    clock = AnalogClock()
    clock.mainloop()
