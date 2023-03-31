import docx_extract
import lcs
import os
import shutil
import tkinter.filedialog as tkd
import zipfile


STUDENT_FILE = 0
ASSIGNMENT_CONTENTS = 1
SIMILARITIES = 2

class Submission:
    def __init__(self, student_name: str, submission_contents: str):
        self.student_name = student_name
        self.submission_contents = submission_contents
        self.similarities: dict[str, tuple[float, list[list[int]]]]= dict()

    def get_similar_percent(self, student_name: str) -> float:
        """Get the similarity between this submission and the provided one
        student_name: The name of the student to retrieve the similarity percent for"""
        if student_name not in self.similarities.keys():
            raise KeyError(f"{student_name} is not a valid key")
        return self.similarities[student_name][0]
    
    def get_lcs_array(self, student_name: str) -> list[list[int]]:
        if student_name not in self.similarities.keys():
            raise KeyError(f"{student_name} is not a valid key")
        return self.similarities[student_name][1]
        

def get_submissions_file() -> str:
    """Shows the File Select Dialog and returns the path to the file selected by the user"""
    return tkd.askopenfilename(filetypes=[('Zipped Files', '*.zip')])


def extract_files(zip_file_path) -> str:
    """Extract all the files in zip file to a directory of the same name. Returns the path to that directory
    zip_file_path: The path to the zip file"""
    # Get the name of the file itself
    zip_file_name = os.path.basename(zip_file_path)

    # Get the directory in which the zip file is located.
    zip_file_dir = os.path.abspath(os.path.dirname(zip_file_path))

    # Get a path to the new directory where we want to extract all the files
    extract_dir = os.path.abspath(os.path.join(zip_file_dir, zip_file_name[:-4] + "/"))

    # Extract the components of the zip file to a folder with the same name in the same directory
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            print("Extracting zip file", zip_file_name, "to", zip_file_dir)
            zip_ref.extractall(extract_dir)
        return extract_dir
    except:
        return ""
    

def get_assignment_files(path_to_assignments: str) -> list[str]:
    """Grab all the recently-extracted assignment files in the directory"""
    assignment_files: list[str] = list()
    for root, _, files in os.walk(path_to_assignments):
        for name in files:
            assignment_files.append(os.path.join(root, name))

    return assignment_files


def get_file_name(path: str) -> str:
    """Returns the name of a file given the path to a file"""
    return os.path.basename(path)


def get_file_contents(path_to_file: str) -> str:
    """Return the contents of a text or docx file"""
    # Check for word docx
    _, extension = os.path.splitext(path_to_file)
    if extension == ".docx":
        file_contents = docx_extract.get_docx_text(path_to_file)
    else:
        try:
            with open(path_to_file, "r") as file:
                file_contents = file.read()
        except UnicodeDecodeError:
            return "UnicodeDecodeError"
    return file_contents


def remove_directory(directory: str):
    # Try to remove the folder we created earlier
    try:
        shutil.rmtree(directory)
    except Exception as e:
        print("You'll have to delete the folder yourself. Error Message: ", e)


def main():
    # Get a zip file from the user containing submissions
    zip_file_path = get_submissions_file()

    if zip_file_path == "":
        print("No file provided. Exiting...")
        exit()

    extract_dir = extract_files(zip_file_path)

    if extract_dir == "":
        print("There was an error opening the zip file and extracting its contents. Exiting...")
        exit(1)

    # Grab all the assignment files from the unextracted directory
    assignment_files = get_assignment_files(extract_dir)
    
    # List of tuples of (student, contents, dictionary(student, similarity))
    assignments: list[Submission] = list()

    for file_name in assignment_files:
        short_file_name = get_file_name(file_name)
        print(f"Checking {short_file_name}...", end="")

        # Read in the entire contents of a file
        file_contents = get_file_contents(file_name)
        if file_contents == "UnicodeDecodeError":
            print("Error reading file, skipping")
            continue

        print()
        # Add the student name and the context of the file to the list
        submission = Submission(short_file_name.split("_")[0], file_contents)

        # Compare the file contents with the assignments that have already been read in
        for assignment in assignments:
            similarity, c = lcs.compare_text(file_contents, assignment.submission_contents)

            submission.similarities[assignment.student_name] = (similarity, c)
            assignment.similarities[submission.student_name] = (similarity, c)

        assignments.append(submission)

    remove_directory(extract_dir)

    # Print out the list of similar assignments
    while True:
        print()
        try:
            print("Type a similarity-percent threshold to generate a report for or \"exit\" to exit.")
            percent = input(": ")
            percent = float(percent) / 100
        except ValueError:
            if percent.lower() == "exit":
                break
            print("Please enter a number")
            continue
        printed = False
        for assignment in assignments:
            # Grab relevent data from the tuple
            student_file = assignment.student_name
            similarities = assignment.similarities

            printed_student_file = False

            # Print out all the similar files and their match %
            for similar_file_name in similarities:
                if assignment.get_similar_percent(similar_file_name) >= percent:
                    # We only want to print this once
                    if not printed_student_file:
                        print(student_file)
                        printed_student_file = True

                    printed = True
                    print(f"\t{similar_file_name}: {round(assignment.get_similar_percent(similar_file_name) * 100, 2)}% match")

        # Hurray! No cheaters
        if not printed:
            print("No similarities found in files")

        input("Press ENTER to continue...")


def compare_text(text1: str, text2: str) -> float:
    """Compares to strings. Returns the percent of tokens (words) that are the same
    This is no longer used"""
    # Split the text out into tokens
    tokens1 = text1.split()
    tokens2 = text2.split()

    # Compare and keep track of similar tokens
    similar = 0

    # We only want to loop over the shortest list of tokens
    min_tokens = min(len(tokens1), len(tokens2))

    for i in range(min_tokens):
        if tokens1[i].lower() == tokens2[i].lower():
            similar += 1

    # Return a percent of how many tokens were similar
    # This is probably scuffed
    return similar / max(len(tokens1), len(tokens2))


if __name__ == "__main__":
    main()
