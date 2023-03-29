import docx_extract
import lcs
import os
import shutil
import tkinter.filedialog as tkd
import zipfile


def main():
    # Get a zip file from the user containing submissions
    zip_file_path = tkd.askopenfilename(filetypes=[('Zipped Files', '*.zip')])

    if zip_file_path == "":
        print("No file provided. Exiting...")
        exit()

    # Get the name of the file itself
    zip_file_name = os.path.basename(zip_file_path)

    # Get the directory in which the zip file is located.
    zip_file_dir = os.path.abspath(os.path.dirname(zip_file_path))

    # Extract the components of the zip file to a folder with the same name in the same directory
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        print("Extracting zip file", zip_file_name, "to", zip_file_dir)
        extract_dir = os.path.abspath(os.path.join(zip_file_dir, zip_file_name[:-4] + "/"))
        zip_ref.extractall(extract_dir)

    # Grab all the assignment files from the unextracted directory
    assignment_files: list[str] = list()
    for root, _, files in os.walk(extract_dir):
        for name in files:
            assignment_files.append(os.path.join(root, name))
    
    # List of tuples of (student, contents, dictionary(student, similarity))
    STUDENT_FILE = 0
    ASSIGNMENT_CONTENTS = 1
    SIMILARITIES = 2
    assignments: list[tuple[str, str, dict[str, float]]] = list()

    for file_name in assignment_files:
        with open(file_name, "r") as file:
            short_file_name = os.path.basename(file_name)
            print(f"Checking {short_file_name}...", end="")

            # Read in the entire contents of a file
            # Check for Word docx
            _, extension = os.path.splitext(file_name)
            if extension == ".docx":
                file_contents = docx_extract.get_docx_text(file_name)
            else:
                try:
                    file_contents = file.read()
                except UnicodeDecodeError:
                    print("Error reading file. Skipping")
                    continue
            print()
            # Add the student name and the context of the file to the list
            file_tuple = (short_file_name.split("_")[0], file_contents, dict())

            # Compare the file contents with the assignments that have already been read in
            for assignment in assignments:
                similarity = lcs.compare_text(file_contents, assignment[ASSIGNMENT_CONTENTS])

                file_tuple[SIMILARITIES][assignment[STUDENT_FILE]] = similarity
                assignment[SIMILARITIES][file_tuple[STUDENT_FILE]] = similarity

            assignments.append(file_tuple)

    # Try to remove the folder we created earlier
    try:
        shutil.rmtree(extract_dir)
    except Exception as e:
        print("You'll have to delete the  folder yourself. Error Message: ", e)

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
            student_file = assignment[STUDENT_FILE]
            similarities = assignment[SIMILARITIES]

            printed_student_file = False

            # Print out all the similar files and their match %
            for similar_file_name in similarities:
                if similarities[similar_file_name] >= percent:
                    # We only want to print this once
                    if not printed_student_file:
                        print(student_file)
                        printed_student_file = True

                    printed = True
                    print(f"\t{similar_file_name}: {round(similarities[similar_file_name] * 100, 2)}% match")

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
