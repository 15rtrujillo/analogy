from typing import Literal

import lcs
import re
import tkinter as tk
import tkinter.ttk as ttk


class DifferenceWindow:
    """A window displaying the differences between two student submissions"""

    def __init__(self, parent: tk.Tk, student1: str, student2: str, submission1_contents: str, submission2_contents: str, submissions_c: list[list[int]]):
        # Program stuff
        self.student1 = student1
        self.student2 = student2
        self.submission1_contents = submission1_contents
        self.submission2_contents = submission2_contents
        self.submissions_c = submissions_c

        # Window stuff
        self.root = tk.Toplevel(parent)
        # self.root = tk.Tk()
        
        row = 0

        self.label_diff = tk.Label(self.root, text="Differences")
        self.label_diff.grid(row=row, column=0)
        row += 1

        self.frame_submissions = tk.Frame(self.root)
        self.frame_submissions.grid(row=row, column=0)
        row += 1

        self.label_submission1 = tk.Label(self.frame_submissions, text=self.student1)
        self.label_submission1.grid(row=0, column=0)

        self.text_submission1 = tk.Text(self.frame_submissions)
        self.text_submission1.bind("<Key>", lambda _: "break")
        self.text_submission1.grid(row=2, column=0)

        self.label_submission2 = tk.Label(self.frame_submissions, text=self.student2)
        self.label_submission2.grid(row=0, column=1)

        self.separator = ttk.Separator(self.frame_submissions, orient="vertical")
        self.separator.grid(row=1, column=1)

        self.text_submission2 = tk.Text(self.frame_submissions)
        self.text_submission2.bind("<Key>", lambda _: "break")
        self.text_submission2.grid(row=2, column=1)

    def display_diff(self, comparison_type: Literal["characters", "words"]):
        if comparison_type == "characters":
            # string1 = "".join(self.submission1_contents.split())
            # string2 = "".join(self.submission2_contents.split())
            string1 = self.submission1_contents
            string2 = self.submission2_contents
        elif comparison_type == "words":
            string1 = self.submission1_contents.split()
            string2 = self.submission2_contents.split()
        else:
            raise ValueError
        
        sub1diff = lcs.get_diff(self.submissions_c, string1, string2)
        sub2diff = lcs.get_diff(lcs.transpose_c(self.submissions_c), string2, string1)

        self.add_to_textbox(sub1diff, self.text_submission1)
        self.add_to_textbox(sub2diff, self.text_submission2)

    def add_to_textbox(self, text: str, textbox: tk.Text):
        matches = [match for match in re.finditer("[@][g|r][@]", text)]
        match_num = 0
        char_index = 0
        while match_num < len(matches):
            open_tag = matches[match_num]
            close_tag = matches[match_num + 1]
            # Insert everything up to the beginning of the tag
            text_before_tag = text[char_index:open_tag.start()]
            textbox.insert("end", text_before_tag)

            # Insert everything between the two tags with the Text tag
            text_between_tag = text[open_tag.end():close_tag.start()]
            tag = "green" if "g" in text[open_tag.start():open_tag.end()] else "red"
            textbox.insert("end", text_between_tag, tag)

            char_index = close_tag.end()
            match_num += 2
        # Insert everything else
        textbox.insert("end", text[char_index:])
        textbox.tag_configure("green", background="#92fa7d")
        textbox.tag_configure("red", background="#fa9c7d")


if __name__ == "__main__":
    main_window = tk.Tk()
    window = DifferenceWindow(main_window, "Hi", "Hi","hi", "hi", list())
    window.add_to_textbox("H@g@i@g@", window.text_submission1)
    window.add_to_textbox("H@r@i@r@", window.text_submission2)
    main_window.mainloop()
