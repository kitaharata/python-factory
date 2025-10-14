import tkinter as tk
import unicodedata


class App(tk.Tk):
    """A GUI tool to count characters, lines, and byte sizes."""

    def __init__(self):
        """Initializes the GUI, sets up the window, and creates widgets."""
        super().__init__()
        self.title("Text Stats Tool")
        self.geometry("800x600")

        self.text_input = tk.Text(self, height=20, width=80)
        self.text_input.pack(pady=10, padx=10, fill=tk.X)
        self.count_button = tk.Button(self, text="Analyze Text", command=self.analyze_text)
        self.count_button.pack(pady=5)
        label_frame = tk.Frame(self)
        label_frame.pack(pady=10, padx=10, fill=tk.X)

        self.char_count_label = tk.Label(self, text="Characters: 0", anchor="w")
        self.char_count_label.pack(fill="x", padx=10)
        self.char_no_space_label = tk.Label(self, text="Characters (no whitespace): 0", anchor="w")
        self.char_no_space_label.pack(fill="x", padx=10)
        self.line_count_label = tk.Label(self, text="Lines: 0", anchor="w")
        self.line_count_label.pack(fill="x", padx=10)
        self.non_empty_line_label = tk.Label(self, text="Lines (non-empty): 0", anchor="w")
        self.non_empty_line_label.pack(fill="x", padx=10)
        self.shift_jis_byte_label = tk.Label(self, text="Shift_JIS bytes: 0", anchor="w")
        self.shift_jis_byte_label.pack(fill="x", padx=10)
        self.euc_jp_byte_label = tk.Label(self, text="EUC-JP bytes: 0", anchor="w")
        self.euc_jp_byte_label.pack(fill="x", padx=10)
        self.utf8_byte_label = tk.Label(self, text="UTF-8 bytes: 0", anchor="w")
        self.utf8_byte_label.pack(fill="x", padx=10)

    def analyze_text(self):
        """Analyzes the text and updates the labels with statistics."""
        text = self.text_input.get("1.0", tk.END).rstrip()

        visible_chars = [ch for ch in text if not unicodedata.combining(ch)]
        visible_no_space = [ch for ch in visible_chars if not ch.isspace()]
        char_count = len(visible_chars)
        char_no_space = len(visible_no_space)

        lines = text.splitlines()
        line_count = len(lines)
        non_empty = [line for line in lines if line.strip() != ""]
        non_empty_lines = len(non_empty)

        try:
            shift_jis_bytes = len(text.encode("shift_jis", errors="replace"))
        except LookupError:
            shift_jis_bytes = 0
        try:
            euc_jp_bytes = len(text.encode("euc_jp", errors="replace"))
        except LookupError:
            euc_jp_bytes = 0
        utf8_bytes = len(text.encode("utf-8"))

        self.char_count_label.config(text=f"Characters: {char_count}")
        self.char_no_space_label.config(text=f"Characters (no whitespace): {char_no_space}")
        self.line_count_label.config(text=f"Lines: {line_count}")
        self.non_empty_line_label.config(text=f"Lines (non-empty): {non_empty_lines}")
        self.shift_jis_byte_label.config(text=f"Shift_JIS bytes: {shift_jis_bytes}")
        self.euc_jp_byte_label.config(text=f"EUC-JP bytes: {euc_jp_bytes}")
        self.utf8_byte_label.config(text=f"UTF-8 bytes: {utf8_bytes}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
