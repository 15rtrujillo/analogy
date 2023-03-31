from typing import Literal

import lcs
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
            sub1diff = lcs.get_diff(self.submissions_c, "".join(self.submission1_contents.split()), "".join(self.submission2_contents.split()))
            sub2diff = lcs.get_diff(self.submissions_c, "".join(self.submission2_contents.split()), "".join(self.submission1_contents.split()))
        elif comparison_type == "words":
            sub1diff = lcs.get_diff(self.submissions_c, self.submission1_contents.split(), self.submission2_contents.split())
            sub2diff = lcs.get_diff(self.submissions_c, self.submission2_contents.split(), self.submission1_contents.split())
        else:
            raise ValueError
        
        self.text_submission1.insert("1.0", sub1diff)
        self.text_submission2.insert("1.0", sub2diff)


if __name__ == "__main__":
    window = DifferenceWindow(None, "Hi", "Hi", "hi", "hi", list())
