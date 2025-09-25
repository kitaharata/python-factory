import random
import tkinter as tk


class FlashCalcApp(tk.Tk):
    """A flash calculation quiz application using Tkinter."""

    def __init__(self):
        """Initialize the application, set up UI components, and generate first problem."""
        super().__init__()
        self.title("Flash Calculation Quiz")
        self.geometry("300x400")

        self.problem_label = tk.Label(self, text="", font=("Arial", 24))
        self.problem_label.pack(pady=20)

        self.answer_var = tk.StringVar()
        self.answer_label = tk.Label(self, text="", textvariable=self.answer_var, font=("Arial", 20))
        self.answer_label.pack(pady=10)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)

        for i in range(1, 10):
            row = (i - 1) // 3
            col = (i - 1) % 3
            btn = tk.Button(button_frame, text=str(i), width=5, height=2, command=lambda x=i: self.append_digit(x))
            btn.grid(row=row, column=col, padx=2, pady=2)

        btn_zero = tk.Button(button_frame, text="0", width=5, height=2, command=lambda: self.append_digit(0))
        btn_zero.grid(row=3, column=1, pady=2)

        btn_clear = tk.Button(self, text="Clear", width=10, height=2, command=self.clear_input)
        btn_clear.pack(pady=5)

        btn_enter = tk.Button(self, text="Enter", width=10, height=2, command=self.check_answer)
        btn_enter.pack(pady=5)

        self.score = 0
        self.timer = None
        self.score_label = tk.Label(self, text="Score: 0", font=("Arial", 16))
        self.score_label.pack(pady=10)

        self.new_problem()

    def new_problem(self):
        """Generate a new random math problem and display it."""
        a = random.randint(1, 9)
        b = random.randint(1, 9)
        op = random.choice(["+", "-", "*"])

        if op == "+":
            correct = a + b
        elif op == "-":
            if a < b:
                a, b = b, a
            correct = a - b
        else:  # '*'
            correct = a * b

        self.a, self.b, self.op, self.correct = a, b, op, correct
        self.expected_digits = 1 if self.correct < 10 else 2
        self.problem_label.config(text=f"{a} {op} {b} = ")
        self.clear_input()

    def append_digit(self, digit):
        """Append a digit to the current answer input and check if complete."""
        current = self.answer_var.get()
        if len(current) < self.expected_digits:
            new_current = current + str(digit)
            self.answer_var.set(new_current)
            if len(new_current) == self.expected_digits:
                self.check_answer()

    def clear_input(self):
        """Clear the current answer input."""
        self.answer_var.set("")

    def check_answer(self):
        """Check the user's answer, update score, and prepare next problem."""
        user_input = self.answer_var.get().strip()
        if not user_input:
            return
        try:
            user_answer = int(user_input)
            if user_answer == self.correct:
                self.answer_var.set("Correct!")
                self.score += 1
                self.score_label.config(text=f"Score: {self.score}")
            else:
                self.answer_var.set("Incorrect!")
            self.problem_label.config(text=f"{self.a} {self.op} {self.b} = {user_input}")
            self.after(1500, self.new_problem)
        except ValueError:
            self.answer_var.set("")

    def run(self):
        """Start the application's main loop."""
        self.mainloop()


if __name__ == "__main__":
    app = FlashCalcApp()
    app.run()
