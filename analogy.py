import docx_extract
import json
import os
import shutil
import tkinter.filedialog as tkd
import zipfile


STUDENT_FILE = 0
ASSIGNMENT_CONTENTS = 1
SIMILARITIES = 2

class Submission:
    def __init__(self, student_name: str, submission_file_path: str):
        self.student_name = student_name
        self.submission_file_path = submission_file_path
        self.similarities: dict[str, float] = dict()
        self.json_file_path = os.path.abspath(os.path.dirname(self.submission_file_path))

    def get_similar_percent(self, student_name: str) -> float:
        """Get the similarity between this submission and the provided one
        student_name: The name of the student to retrieve the similarity percent for"""
        if student_name not in self.similarities.keys():
            raise KeyError(f"{student_name} is not a valid key")
        return self.similarities[student_name]
    
    def get_lcs_array(self, student_name: str) -> list[list[int]]:
        json_file_name = os.path.abspath(os.path.join(self.json_file_path, f"{self.student_name}-{student_name}.json"))
        if not os.path.isfile(json_file_name):
            raise KeyError(f"{student_name} is not a valid key")
        with open(json_file_name, "r") as json_file:
            return json.load(json_file)
    
    def set_lcs_array(self, student_name: str, c: list[list[int]]):
        json_file_name = os.path.abspath(os.path.join(self.json_file_path, f"{self.student_name}-{student_name}.json"))
        with open(json_file_name, "w") as json_file:
            json.dump(c, json_file)
        

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