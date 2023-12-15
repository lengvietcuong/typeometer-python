import json
import tkinter as tk
from tkinter import messagebox
from string import punctuation
from time import perf_counter
from pathlib import Path
from random import shuffle
from itertools import cycle
from datetime import date


WINDOW_WIDTH = 720
WINDOW_HEIGHT = 480
PADDING_X = 40
PADDING_Y = 40
TEXT_FONT_SIZE = 20
SOURCE_FONT_SIZE = 12
FONT = "Courier"
PUNCTUATIONS = set(punctuation)
DARK_GRAY = "#16161d"
LIGHT_GRAY = "#666666"
GREEN = "#5acc88"
RED = "#e02d2d"


class Typeometer:
    def __init__(self, texts_file_path, stats_file_path) -> None:
        self.text_data = self._load_text_data(texts_file_path)
        self.existing_stats = self._load_existing_stats(stats_file_path)
        self.stats_file_path = stats_file_path
        self.root = tk.Tk()

    def _load_text_data(self, file_path):
        with open(file_path, "r") as texts_file:
            text_data = json.load(texts_file)
            shuffle(text_data)
            return cycle(text_data)

    def _load_existing_stats(self, file_path):
        try:
            with open(file_path, "r") as stats_file:
                return json.load(stats_file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def start(self) -> None:
        self.text_to_type, self.source = next(self.text_data).values()
        self.total_chars = len(self.text_to_type)
        self.current_index = 0
        self.last_correct_index = -1
        self.incorrect_entries = 0
        self.start_time = None

        self.draw_screen()
        self.set_up_text_widget()
        self.set_up_source_label()
        self.root.mainloop()

    def draw_screen(self) -> None:
        x_position = (self.root.winfo_screenwidth() - WINDOW_WIDTH) // 2
        y_position = (self.root.winfo_screenheight() - WINDOW_HEIGHT) // 2
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_position}+{y_position}")
        self.root.configure(bg=DARK_GRAY)
        self.root.title("Typeometer - Typing Speed Test")

    def set_up_text_widget(self) -> None:
        self.text_widget = tk.Text(
            self.root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            bg=DARK_GRAY,
            fg="white",
            font=(FONT, TEXT_FONT_SIZE),
            wrap="word",
            highlightthickness=0,
        )
        self.text_widget.pack(padx=PADDING_X, pady=PADDING_Y)
        self.text_widget.insert("1.0", self.text_to_type)
        self.text_widget.configure(bd=0)
        self.text_widget.tag_configure("correct", foreground=GREEN)
        self.text_widget.tag_configure("incorrect", foreground=RED)
        self.text_widget.tag_configure("incorrect space", background=RED)
        self.text_widget["state"] = "disabled"  # fixed chars
        self.text_widget.focus_set()

        self.root.bind("<KeyPress>", self._handle_key_press)
        self.root.bind("<BackSpace>", self._handle_backspace)

    def set_up_source_label(self) -> None:
        self.source_label = tk.Label(
            self.root,
            text=self.source,
            font=(FONT, SOURCE_FONT_SIZE),
            bg=DARK_GRAY,
            fg=LIGHT_GRAY,
        )
        self.source_label.place(x=PADDING_X, y=WINDOW_HEIGHT - PADDING_Y)

    def _handle_key_press(self, event) -> None:
        if self.current_index == self.total_chars:
            return

        if self.start_time is None:
            self.start_time = perf_counter()

        typed_char = event.char
        if not (
            typed_char.isalnum() or typed_char.isspace() or typed_char in PUNCTUATIONS
        ):
            return

        previous_char_correct = self.last_correct_index == self.current_index - 1
        expected_char = self.text_to_type[self.current_index]

        if previous_char_correct and typed_char == expected_char:
            self.last_correct_index += 1
            tag = "correct"
        else:
            self.incorrect_entries += 1
            tag = "incorrect space" if expected_char.isspace() else "incorrect"

        self.text_widget.tag_add(
            tag, f"1.{self.current_index}", f"1.{self.current_index + 1}"
        )

        self.current_index += 1
        if self.last_correct_index == self.total_chars - 1:  # finished
            self.root.update_idletasks()
            self.root.unbind_all("<KeyPress>")
            self.root.unbind_all("<BackSpace>")

            speed, accuracy = self.calculate_stats()
            self.record_stats(speed, accuracy)
            self.show_stats(speed, accuracy)

    def _handle_backspace(self, _) -> None:
        # move current_index back unless it is at 0
        self.current_index = max(self.current_index - 1, 0)
        # ensure last_correct_index <= self.current_index - 1
        self.last_correct_index = min(self.last_correct_index, self.current_index - 1)
        # erase any coloring
        for tag in ("correct", "incorrect", "incorrect space"):
            self.text_widget.tag_remove(
                tag, f"1.{self.current_index}", f"1.{self.current_index + 1}"
            )

    def calculate_stats(self) -> tuple[float]:
        end_time = perf_counter()
        elapsed_time_minutes = (end_time - self.start_time) / 60
        words = self.total_chars / 5

        speed = words / elapsed_time_minutes
        accuracy = self.total_chars / (self.total_chars + self.incorrect_entries) * 100
        return round(speed, 2), round(accuracy, 2)

    def record_stats(self, speed, accuracy) -> None:
        current_date = date.today().strftime("%d/%m/%Y")
        new_entry = {
            "date": current_date,
            "text": self.text_to_type,
            "speed": speed,
            "accuracy": accuracy,
        }

        self.existing_stats.append(new_entry)
        with open(self.stats_file_path, "w") as file:
            json.dump(self.existing_stats, file, indent=4)

    def show_stats(self, speed, accuracy) -> None:
        messagebox.showinfo(
            "Statistics",
            f"""Speed: {speed:.2f} WPM
            Accuracy: {accuracy}%""",
        )
        # after the user closes the stats message, reset text widget for next text
        self.text_widget.destroy()
        self.source_label.destroy()
        self.start()


def main():
    texts_file_path = Path(__file__).parent / "texts.json"
    stats_file_path = Path(__file__).parent / "stats.json"
    app = Typeometer(texts_file_path, stats_file_path)
    app.start()


if __name__ == "__main__":
    main()
