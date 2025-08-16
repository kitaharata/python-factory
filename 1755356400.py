import io
import os
import sys
import tkinter as tk
import zipfile
from tkinter import messagebox

from PIL import Image, ImageTk


class ZipImageViewer:
    """A Tkinter application for viewing images in a ZIP file."""

    def __init__(self, master, zip_path):
        self.master = master
        self.zip_path = zip_path
        self.image_files = []
        self.current_image_index = 0
        self.pil_image = None
        self.photo_image = None
        self.master.title(f"ZIP Image Viewer - {os.path.basename(zip_path)}")
        self.master.geometry("800x600")

        self.load_image_list()
        if not self.image_files:
            messagebox.showinfo("Info", "No viewable images found in the ZIP file.")
            self.master.destroy()
            return

        self.status_label = tk.Label(self.master, text="", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill=tk.BOTH, expand=True)
        self.image_label = tk.Label(main_frame)
        self.image_label.pack(pady=10, expand=True, fill=tk.BOTH)

        self.master.bind("<Configure>", self.on_resize)
        self.master.bind("<Left>", lambda e: self.prev_image())
        self.master.bind("<Right>", lambda e: self.next_image())
        self.master.bind("<Up>", lambda e: self.prev_image())
        self.master.bind("<Down>", lambda e: self.next_image())

        self.load_and_show_image()
        self.update_ui()

    def load_image_list(self):
        """Load a list of image files from the ZIP file."""
        try:
            with zipfile.ZipFile(self.zip_path, "r") as zf:
                for file_info in zf.infolist():
                    if file_info.is_dir():
                        continue
                    lower_filename = file_info.filename.lower()
                    if lower_filename.endswith((".png", ".jpg", ".jpeg", ".gif", ".tiff", ".webp")):
                        self.image_files.append(file_info.filename)
        except zipfile.BadZipFile:
            messagebox.showerror("Error", "Invalid ZIP file.")
            self.master.destroy()
        except FileNotFoundError:
            messagebox.showerror("Error", f"File not found: {self.zip_path}")
            self.master.destroy()

    def load_and_show_image(self):
        """Load and display the image at the current index from the ZIP file."""
        if not self.image_files:
            self.pil_image = None
            self.image_label.config(image=None, text="No image to display")
            return
        image_path = self.image_files[self.current_image_index]
        try:
            with zipfile.ZipFile(self.zip_path, "r") as zf:
                with zf.open(image_path) as image_file:
                    image_data = io.BytesIO(image_file.read())
                    self.pil_image = Image.open(image_data)
                    self.resize_and_display_image()
        except Exception as e:
            messagebox.showerror("Image Load Error", f"An error occurred while loading {image_path}.\n{e}")
            self.pil_image = None
            self.image_label.config(image=None, text=f"{image_path}\nLoad Error")
            self.photo_image = None

    def resize_and_display_image(self):
        """Resize and display the held PIL image to fit the current window size."""
        if self.pil_image is None:
            return
        max_width = self.image_label.winfo_width()
        max_height = self.image_label.winfo_height()
        if max_width <= 1 or max_height <= 1:
            return
        img_copy = self.pil_image.copy()
        img_copy.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(img_copy)
        self.image_label.config(image=self.photo_image)

    def on_resize(self, event):
        """Redraw the image when the window is resized."""
        self.resize_and_display_image()

    def next_image(self):
        """Display the next image."""
        if self.image_files and len(self.image_files) > 1:
            self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
            self.load_and_show_image()
            self.update_ui()

    def prev_image(self):
        """Display the previous image."""
        if self.image_files and len(self.image_files) > 1:
            self.current_image_index = (self.current_image_index - 1 + len(self.image_files)) % len(self.image_files)
            self.load_and_show_image()
            self.update_ui()

    def update_ui(self):
        """Update the status bar."""
        if self.image_files:
            image_count = len(self.image_files)
            current_filename = self.image_files[self.current_image_index]
            status_text = f"{self.current_image_index + 1} / {image_count} | {current_filename}"
            self.status_label.config(text=status_text)
        else:
            self.status_label.config(text="No images")


if __name__ == "__main__":
    """The entry point of the application."""
    if len(sys.argv) < 2:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Argument Error", "Please specify a ZIP file as an argument.")
        root.destroy()
        sys.exit()

    zip_path = sys.argv[1]
    root = tk.Tk()
    app = ZipImageViewer(root, zip_path)
    root.mainloop()
