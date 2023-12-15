import json
import tkinter as tk
from tkinter import ttk
from pathlib import Path


REPLACEMENTS = {
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
    "`": "'",
    "´": "'",
    "–": "-",
    "\u2014": " - ",
    "  ": " ",
}


class TextsAdder:
    def __init__(self, texts_file_path) -> None:
        self.texts_file_path = texts_file_path
        try:
            with open(texts_file_path, "r") as texts_file:
                self.existing_texts = json.load(texts_file)
        except FileNotFoundError:
            self.existing_texts = []

        self.root = tk.Tk()

    def draw_window(self) -> None:
        self.root.title("Add new texts")

        text_label = ttk.Label(self.root, text="Enter text:")
        text_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.text_widget = tk.Text(self.root, height=12, width=60, wrap="word")
        self.text_widget.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.text_widget.focus_force()

        source_label = ttk.Label(self.root, text="Enter source:\n(optional)")
        source_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.source_widget = tk.Text(self.root, height=4, width=60)
        self.source_widget.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        add_button = ttk.Button(
            self.root,
            text="Add",
            command=self.add_entry,
        )
        add_button.grid(row=2, column=1, pady=10)

        self.added_notification = ttk.Label(self.root, text="")
        self.added_notification.grid(row=3, column=1, pady=20)

        # center the window
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_reqwidth()
        window_height = self.root.winfo_reqheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"+{x}+{y}")

        self.root.mainloop()

    @staticmethod
    def process_string(string) -> str:
        string = string.strip()
        string = " ".join(line for line in string.splitlines())
        for symbol, replacement in REPLACEMENTS.items():
            string = string.replace(symbol, replacement)

        return string

    def add_entry(self) -> None:
        text = self.text_widget.get("1.0", "end-1c")
        source = self.source_widget.get("1.0", "end-1c")

        if not text:
            return

        text = self.process_string(text)
        source = self.process_string(source)

        new_entry = {"text": text, "source": source}
        self.existing_texts.append(new_entry)
        with open(self.texts_file_path, "w") as file:
            json.dump(self.existing_texts, file, indent=4)

        # clear widgets
        self.text_widget.delete("1.0", "end")
        self.source_widget.delete("1.0", "end")
        self.text_widget.focus_set()

        self.added_notification.config(text="Added successfully", foreground="green")
        self.added_notification.after(
            1000, lambda: self.added_notification.config(text="")
        )  # display for 1 second


def main():
    texts_file_path = Path(__file__).parent / "texts.json"
    texts_adder = TextsAdder(texts_file_path)
    texts_adder.draw_window()


if __name__ == "__main__":
    main()
