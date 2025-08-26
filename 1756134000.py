import colorsys
import tkinter as tk

from PIL import Image, ImageTk


class ColorMeditationApp:
    def __init__(self, master):
        self.master = master
        master.title("Color Meditation")
        master.geometry("800x600")

        self.width = 800
        self.height = 600
        self.hue = 0.0
        self.saturation = 1.0
        self.brightness_min = 0.1
        self.brightness_max = 0.9
        self.hue_speed = 0.0001
        self.update_interval_ms = 40

        self.label = tk.Label(master)
        self.label.pack(expand=True, fill="both")

        self.master.bind("<Configure>", self.on_resize)
        self.update_color()

    def on_resize(self, event):
        """Handles window resize events."""
        if self.width != event.width or self.height != event.height:
            self.width = event.width
            self.height = event.height
            self._update_image_display()

    def generate_gradient_image(self):
        """Generates a vertical gradient image."""
        effective_width = max(1, self.width)
        effective_height = max(1, self.height)
        img = Image.new("RGB", (effective_width, effective_height))
        pixels = img.load()
        for y in range(effective_height):
            if effective_height > 1:
                value = self.brightness_max - (self.brightness_max - self.brightness_min) * (y / (effective_height - 1))
            else:
                value = (self.brightness_max + self.brightness_min) / 2
            r, g, b = colorsys.hsv_to_rgb(self.hue, self.saturation, value)
            R, G, B = int(r * 255), int(g * 255), int(b * 255)
            for x in range(effective_width):
                pixels[x, y] = (R, G, B)
        return img

    def _update_image_display(self):
        """Generates and displays the current gradient image."""
        pil_image = self.generate_gradient_image()
        self.tk_image = ImageTk.PhotoImage(pil_image)
        self.label.config(image=self.tk_image)

    def update_color(self):
        """Updates hue and schedules the next update."""
        self._update_image_display()
        self.hue = (self.hue + self.hue_speed) % 1.0
        self.master.after(self.update_interval_ms, self.update_color)


if __name__ == "__main__":
    root = tk.Tk()
    app = ColorMeditationApp(root)
    root.mainloop()
