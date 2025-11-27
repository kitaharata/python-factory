import tkinter as tk
from datetime import datetime

SEGMENT_WIDTH = 70
SEGMENT_HEIGHT = 140
SEGMENT_THICKNESS = 10
LIT_COLOR = "red"
DIM_COLOR = "#300000"
SEGMENT_MAP = {
    0: (1, 1, 1, 1, 1, 1, 0),
    1: (0, 1, 1, 0, 0, 0, 0),
    2: (1, 1, 0, 1, 1, 0, 1),
    3: (1, 1, 1, 1, 0, 0, 1),
    4: (0, 1, 1, 0, 0, 1, 1),
    5: (1, 0, 1, 1, 0, 1, 1),
    6: (1, 0, 1, 1, 1, 1, 1),
    7: (1, 1, 1, 0, 0, 0, 0),
    8: (1, 1, 1, 1, 1, 1, 1),
    9: (1, 1, 1, 1, 0, 1, 1),
}


class DigitalClock(tk.Tk):
    """A 7-segment digital clock application."""

    def __init__(self):
        super().__init__()
        self.title("Digital Clock")
        self.geometry("800x600")
        self.canvas_width = 800
        self.canvas_height = 600
        self.center_x = self.canvas_width // 2
        self.center_y = self.canvas_height // 2
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="black")
        self.canvas.pack(padx=10, pady=10)
        self.digit_segment_ids = []
        self.colon_dots = []
        self._initialize_display_layout()
        self.update_clock()

    def _get_segment_polygon_coords(self, index, x_off, y_off):
        """Calculates polygon coordinates for a segment based on its index (0=A, 6=G)."""
        W = SEGMENT_WIDTH
        H = SEGMENT_HEIGHT
        T = SEGMENT_THICKNESS
        S = T / 2
        L = (H - T) / 2
        coords = []
        if index == 0:
            coords = [S, 0, W - S, 0, W, S, W - T, T, T, T, 0, S]
        elif index == 1:
            coords = [W - S, T, W, S, W, L + S, W - S, L + T, W - T, L + S, W - T, T]
        elif index == 2:
            coords = [W - S, L + T, W, L + S + T, W, H - S, W - S, H, W - T, H - T, W - T, L + T]
        elif index == 3:
            coords = [S, H, W - S, H, W, H - S, W - S, H - T, S, H - T, 0, H - S]
        elif index == 4:
            coords = [S, H - T, 0, H - S, 0, L + S + T, S, L + T, T, L + T + S, T, H - T]
        elif index == 5:
            coords = [S, T, 0, S, 0, L + S, S, L + T, T, L + S, T, T]
        elif index == 6:
            center_y = L + S
            coords = [
                S,
                center_y - S,
                W - S,
                center_y - S,
                W,
                center_y,
                W - S,
                center_y + S,
                S,
                center_y + S,
                0,
                center_y,
            ]
        shifted_coords = []
        for i in range(0, len(coords), 2):
            shifted_coords.append(coords[i] + x_off)
            shifted_coords.append(coords[i + 1] + y_off)
        return shifted_coords

    def _initialize_display_layout(self):
        W = SEGMENT_WIDTH
        H = SEGMENT_HEIGHT
        T = SEGMENT_THICKNESS
        SPACING = 20
        total_content_width = 6 * W + 5 * SPACING + 2 * T
        start_x = (self.canvas_width - total_content_width) / 2
        start_y = (self.canvas_height - H) / 2
        current_x = start_x
        dot_y1 = start_y + H / 4
        dot_y2 = start_y + 3 * H / 4
        dot_size = T / 2
        for i in range(6):
            segments_for_digit = []
            for j in range(7):
                coords = self._get_segment_polygon_coords(j, current_x, start_y)
                seg_id = self.canvas.create_polygon(coords, fill=DIM_COLOR, width=0)
                segments_for_digit.append(seg_id)
            self.digit_segment_ids.append(segments_for_digit)
            current_x += W
            if i == 1 or i == 3:
                current_x += SPACING
                self.colon_dots.append(
                    self.canvas.create_oval(
                        current_x, dot_y1 - dot_size, current_x + T, dot_y1 + dot_size, fill=DIM_COLOR, width=0
                    )
                )
                self.colon_dots.append(
                    self.canvas.create_oval(
                        current_x, dot_y2 - dot_size, current_x + T, dot_y2 + dot_size, fill=DIM_COLOR, width=0
                    )
                )
                current_x += T + SPACING
            elif i < 5:
                current_x += SPACING

    def update_clock(self):
        now = datetime.now()
        time_str = now.strftime("%H%M%S")
        for i in range(6):
            try:
                digit = int(time_str[i])
                segment_map = SEGMENT_MAP.get(digit, SEGMENT_MAP[8])
            except (ValueError, IndexError):
                segment_map = SEGMENT_MAP[8]
            for j in range(7):
                seg_id = self.digit_segment_ids[i][j]
                color = LIT_COLOR if segment_map[j] == 1 else DIM_COLOR
                self.canvas.itemconfig(seg_id, fill=color)
        if now.second % 2 == 0:
            colon_color = LIT_COLOR
        else:
            colon_color = DIM_COLOR
        for dot_id in self.colon_dots:
            self.canvas.itemconfig(dot_id, fill=colon_color)
        self.after(1000, self.update_clock)


if __name__ == "__main__":
    clock = DigitalClock()
    clock.mainloop()
