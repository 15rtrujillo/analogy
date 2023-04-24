from diff_window import DifferenceWindow
from typing import Literal

import analogy
import lcs
import multiprocessing
import os
import time
import tkinter as tk
import tkinter.messagebox as msgbox
import tkinter.ttk as ttk


class AnalogyProgress:
    """A progress window for the comparison process"""

    def __init__(self, parent: tk.Tk, submissions_directory: str, submission_files: list[str], comparison_method: Literal["characters", "words"]):
        """Create a new progress window
        parent: The parent window
        submissions_directory: The directory containing the submission files
        submission_files: A list of the submission file paths
        comparison_method: How we are comparing the files, by characters or "words.\""""
        # Program stuff
        self.submissions_directory = submissions_directory
        self.submission_files = submission_files
        self.submissions: list[analogy.Submission] = list()
        self.comparison_method = comparison_method

        # Window stuff
        self.root = tk.Toplevel(parent)
        self.root.title("Comparing Submissions...")
        # self.root.overrideredirect(1)
        # self.root.bind("<Visibility>", lambda event: self.compare())

        row = 0

        self.label_title = tk.Label(self.root, text="Comparing Submissions...")
        self.label_title.grid(row=row, column=0)
        row += 1

        self.label_total_progress = tk.Label(self.root, text="Total Progress: ")
        self.label_total_progress.grid(row=row, column=0)
        row += 1

        self.progress_total = ttk.Progressbar(self.root, mode="determinate", length=200)
        self.progress_total.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        self.label_file_progress = tk.Label(self.root, text="Comparing Against Other Students:")
        self.label_file_progress.grid(row=row, column=0)
        row += 1

        self.progress_file = ttk.Progressbar(self.root, mode="determinate", length=200)
        self.progress_file.grid(row=row, column=0, padx=10, pady=10)
        row += 1

        parent_mid_x = parent.winfo_x() + (parent.winfo_width() / 2)
        parent_mid_y = parent.winfo_y() + (parent.winfo_height() / 2)

        self.root.geometry(f"+{int(parent_mid_x/2)}+{int(parent_mid_y)}")

    def compare(self):
        """Compare all the submissions in self.submissions_directory to populate self.submissions"""

        # Loop through all the submission files and set up the progress bar
        total_files = len(self.submission_files)
        self.progress_total.configure(maximum=total_files)
        for i in range(total_files):
            file_path = self.submission_files[i]
            short_file_name = analogy.get_file_name(file_path)
            self.label_total_progress.configure(text=f"Checking file {i}/{total_files}: {short_file_name}...")

            # Create the new submission object
            student_name = short_file_name.split("_")[0] 
            submission = analogy.Submission(student_name, file_path)

            # Read in the entire contents of a file to see if it throws an error
            # I don't know a better way to do this...
            if analogy.get_file_contents(file_path) == "UnicodeDecodeError":
                submission.submission_file_path = "UnicodeDecodeError"
                self.submissions.append(submission)
                continue

            # Compare the file contents with the assignments that have already been read in
            # Also configure the second progress bar
            total_submissions = len(self.submissions)
            self.progress_file.configure(maximum=total_submissions)

            # Set up the objects required for multiprocessing
            manager = multiprocessing.Manager()
            result_list = manager.list()
            processes: list[tuple[str, str, multiprocessing.Process]] = list()

            # Loop through all the submissions that have already been read in
            for cmp_submission in self.submissions:
                # Start multiprocess comparisons
                if cmp_submission.submission_file_path == "UnicodeDecodeError":
                    continue
                process = multiprocessing.Process(target=compare_process, args=(submission, cmp_submission, self.comparison_method, result_list))
                process.start()
                processes.append((submission.student_name, cmp_submission.student_name, process))

            # Wait for all the processes to complete
            j = 0
            for student1, student2, process in processes:
                # Update the label
                self.label_file_progress.configure(text=f"Comparing {student1} and {student2}...")
                # Update the file progress bar
                self.progress_file.configure(value=j+1)
                j += 1
                self.root.update()
                process.join()

            # Get the results back from the processes
            for cmp_student_name, similarity in result_list:
                # Look for the submission we were comparing against
                for cmpsub in self.submissions:
                    if cmpsub.student_name == cmp_student_name:
                        cmp_submission = cmpsub
                        break

                # Set the similarities in the dictionaries
                submission.similarities[cmp_student_name] = similarity
                cmp_submission.similarities[submission.student_name] = similarity

            # Add the newely read in submission to the list
            self.submissions.append(submission)

            # Update the progress bar
            self.progress_total.configure(value=i+1)
            self.root.update()

        self.root.destroy()


def compare_process(sub1: analogy.Submission, sub2: analogy.Submission, comparison_method: Literal["characters", "words"], result_list: list):
    """Function to compare two submissions. Returns the name of the second student and the similarity percent between the two submissions. Used in multiprocessing.
    sub1: The first submission to compare
    sub2: The second submission to compare
    comparison_method: How we are comparing the files, by characters or "words."
    result_list: The list to add our return values to"""
    # Do the comparison
    if comparison_method == "characters":
        similarity, c = lcs.compare_text(analogy.get_file_contents(sub1.submission_file_path), analogy.get_file_contents(sub2.submission_file_path))
    elif comparison_method == "words":
        similarity, c = lcs.compare_text(analogy.get_file_contents(sub1.submission_file_path), analogy.get_file_contents(sub2.submission_file_path))
    
    # Write the cmp file with the C array
    sub1.set_lcs_array(sub2.student_name, c)
    
    # Add the return values to the list so they can be retrieved by the parent process
    result_list.append((sub2.student_name, similarity))


class AnalogyGUI:
    """The main window for the program"""

    def __init__(self):
        """Create a new analogy window"""
        # Program stuff
        self.submissions_file: str = ""
        self.submissions_directory: str = ""
        self.submission_files: list[str] = list()
        self.submissions: list[analogy.Submission] = list()
        self.comparison_method: str = "characters"

        # Window stuff
        self.root = tk.Tk()
        self.root.title("Analogy")

        row = 0

        self.label_instructions = tk.Label(self.root, text="This program will scan through assignment submissions and report how similar assignments are to each other.")
        self.label_instructions.grid(row=row, column=0)
        row += 1

        self.separator = ttk.Separator(self.root, orient="horizontal")
        self.separator.grid(row=row, column=0)
        row += 1

        self.label_select_file = tk.Label(self.root, text="1. Please select a zip file containing assignment submissions")
        self.label_select_file.grid(row=row, column=0)
        row += 1

        self.frame_select_file = tk.Frame(self.root)
        self.frame_select_file.grid(row=row, column=0)
        row += 1

        self.label_file_select = tk.Label(self.frame_select_file, text="Submissions File: ")
        self.label_file_select.grid(row=0, column=0)

        self.entry_file_select = tk.Entry(self.frame_select_file, width=50)
        self.entry_file_select.grid(row=0, column=1)

        self.button_file_select = tk.Button(self.frame_select_file, text="Browse", command=self.browse)
        self.button_file_select.grid(row=0, column=2)

        self.label_comparison_method = tk.Label(self.root, text="2. Choose a comparison method.\nComparing characters is a more robust comparison, but will take longer to process.\nComparing words is faster, but will be less accurate.")
        self.label_comparison_method.grid(row=row, column=0)
        row += 1

        self.comparison_method_radio = tk.StringVar(value="characters")
        self.radio_characters = tk.Radiobutton(self.root, text="Compare characters (Slower, but more robust comparison)", variable=self.comparison_method_radio, value="characters")
        self.radio_characters.grid(row=row, column=0)
        row += 1

        self.radio_words = tk.Radiobutton(self.root, text="Compare words (Faster, but less accurate comparison)", variable=self.comparison_method_radio, value="words")
        self.radio_words.grid(row=row, column=0)
        row += 1

        self.label_choose_percent = tk.Label(self.root, text="3. Choose a similarity-percentage threshold for the generated report")
        self.label_choose_percent.grid(row=row, column=0)
        row += 1

        self.frame_percent = tk.Frame(self.root)
        self.frame_percent.grid(row=row, column=0)
        row += 1

        self.label_percent = tk.Label(self.frame_percent, text="Similarity-percent Threshold: ")
        self.label_percent.grid(row=0, column=0)

        self.spinbox_percent = tk.Spinbox(self.frame_percent, from_=0, to=100, width=4)
        self.spinbox_percent.grid(row=0, column=1)

        self.label_percent_sign = tk.Label(self.frame_percent, text="%")
        self.label_percent_sign.grid(row=0, column=2)

        self.label_generate_report = tk.Label(self.root, text="4. Click the following button to generate a report with the above options.\nChanging your selection for 1 or 2 will require the submissions to be re-compared.\nChanging your selection for the similarity-percent threshold (3) will regenerate results instantly and does not require re-comparison.")
        self.label_generate_report.grid(row=row, column=0)
        row += 1

        self.button_generate_report = tk.Button(self.root, text="Generate Report", command=self.generate_report)
        self.button_generate_report.grid(row=row, column=0)
        row += 1

        self.treeview = ttk.Treeview(self.root, columns=["#1", "#2"])
        self.treeview.column("#0", width=10)
        self.treeview.heading("#1", text="Student Name")
        self.treeview.heading("#2", text="Similarity")
        self.treeview.bind("<Double-1>", self.display_diff)
        self.treeview.grid(row=row, column=0)
        row += 1

        self.label_results_time = tk.Label(self.root)
        self.label_results_time.grid(row=row, column=0)
        row += 1

    def show_window(self):
        """Starts the mainloop to display the window"""
        self.root.mainloop()

    def browse(self):
        """Shows the Select File dialog and sets the entry box to the file path"""
        new_file = analogy.get_submissions_file()
        if new_file != "":
            self.entry_file_select.delete("0", "end")
            self.entry_file_select.insert("0", new_file)

    def generate_report(self):
        """Checks all inputs and starts the file comparison"""
        # Disable the Generate button
        self.button_generate_report.configure(state="disabled")

        # Verify that a path has been specified
        if self.entry_file_select.get() == "":
            msgbox.showerror("No File Specified", "Please specify a submissions zip file.")
            self.button_generate_report.configure(state="normal")
            return
        
        # Verify that we have entered a proper similarity-percent threshold
        try:
            float(self.spinbox_percent.get())
        except ValueError:
            msgbox.showerror("Invalid Percent", "Please enter a valid number in the Similarity-percent Threshold field")
            self.button_generate_report.configure(state="normal")
            return
        
        # If we have not specified a new zip file, or changed the comparison method, we don't need to recompare, we can just change the report displayed in the treeview.
        if self.entry_file_select.get() == self.submissions_file and self.comparison_method == self.comparison_method_radio.get():
            self.button_generate_report.configure(state="normal")
            self.populate_treeview()
            return
        
        # Try to remove the old directory
        if os.path.isdir(self.submissions_directory):
            analogy.remove_directory(self.submissions_directory)

        # Set the submission file to what's in the entry box
        self.submissions_file = self.entry_file_select.get()

        # Try to extract the files
        self.submissions_directory = analogy.extract_files(self.submissions_file)

        if self.submissions_directory == "":
            msgbox.showerror("Error Extacting Files", "There was an error extracting the submission files. Perhaps the file path is incorrect?")
            self.entry_file_select.delete("0", "end")
            self.button_generate_report.configure(state="normal")
            return
        
        # Try to get all the newly-extracted files
        self.submission_files = analogy.get_submission_files(self.submissions_directory)

        if len(self.submission_files) == 0:
            msgbox.showerror("No Files", "The submissions zip file you provided yielded no contents.")
            self.entry_file_select.delete("0", "end")
            self.button_generate_report.configure(state="normal")
            return
        
        # Take note of the selected comparison method
        self.comparison_method = self.comparison_method_radio.get()

        # Create a progress window and begin doing the comparisons
        progress = AnalogyProgress(self.root, self.submissions_directory, self.submission_files, self.comparison_method)
        
        start_time = time.time_ns()
        progress.compare()
        end_time = time.time_ns()

        elapsed_time_ns = end_time - start_time
        elapsed_time_ms = elapsed_time_ns // 1_000_000
        elapsed_time_s = elapsed_time_ns // 1_000_000_000
        elapsed_time_min = elapsed_time_s // 60
        elapsed_time_s %= 60
        elapsed_time_ms %= 1000

        self.label_results_time.configure(text=f"Results generated in {elapsed_time_min} minutes, {elapsed_time_s} seconds, and {elapsed_time_ms} milliseconds.")

        self.submissions = progress.submissions

        self.button_generate_report.configure(state="normal")

        self.populate_treeview()

    def populate_treeview(self):
        """Fill the treeview with the relevant information depending on the similarity-percent threshold"""
        # Get percent to check for
        percent = min(1.0, float(self.spinbox_percent.get()) / 100)

        # Clear out the treeview
        for item in self.treeview.get_children():
            self.treeview.delete(item)

        for submission in self.submissions:
            # Get variables
            student_name = submission.student_name
            similarities = submission.similarities

            # If the submission was illegible, we will skip it
            if submission.submission_file_path == "UnicodeDecodeError":
                self.treeview.insert("", "end", student_name, values=[student_name, "Could not read file contents"])
                continue
            else:
                self.treeview.insert("", "end", student_name, values=[student_name])

            # Loop through the similarities dictionary to add children to the treeview item.
            added_child = False
            for similar_student_name in similarities:
                if submission.get_similar_percent(similar_student_name) >= percent:
                    self.treeview.insert(student_name, "end", values=[similar_student_name, f"{round(submission.get_similar_percent(similar_student_name) * 100, 2)}%"])
                    added_child = True

            # If we didn't add any children for the parent item, we can just remove it
            if not added_child:
                self.treeview.delete(student_name)

    def display_diff(self, event: tk.Event):
        """Identify the selected treeview item and display the difference window with the relevant comparison"""
        # Identify the item that was clicked on at the mouse location
        item_id = self.treeview.identify("item", event.x, event.y)

        # If it doesn't have a parent, we've clicked on a top-level item and return
        parent_id = self.treeview.parent(item_id)
        if parent_id == "":
            return
        
        sub1content = ""
        sub2content = ""
        c_array = None

        # Get the name of the student from the treeview item
        student_name = self.treeview.item(item_id, "values")[0]

        # Grab the submission contents and the c array using the parent of the item that was clicked on
        for submission in self.submissions:
            if submission.student_name == parent_id:
                c_array = submission.get_lcs_array(student_name)
                sub1content = analogy.get_file_contents(submission.submission_file_path)
                break
        
        # Now grab the submission of the actual item that was clicked on
        for submission in self.submissions:
            if submission.student_name == student_name:
                sub2content = analogy.get_file_contents(submission.submission_file_path)
                break

        diff_window = DifferenceWindow(self.root, parent_id, student_name, sub1content, sub2content, c_array)
        
        diff_window.display_diff(self.comparison_method)


if __name__ == "__main__":
    window = AnalogyGUI()
    window.show_window()

    if os.path.isdir(window.submissions_directory):
        analogy.remove_directory(window.submissions_directory)
