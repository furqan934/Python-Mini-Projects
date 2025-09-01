
import os # for file operations 
# save notes to a file
def save_notes_to_file(notes, filename):
    with open(filename, "a") as f: # a appends notes to the file
        f.write(notes + "\n")
    print(f"Notes saved to {filename} successfully.")

# read notes from a file
def read_notes_from_file(filename):
    try:
        with open(filename, "r") as f:
            notes = f.readlines()
            if not notes:
                print("No notes found.")
            else:
                print("Your notes:")
                for i, note in enumerate(notes, start=1):
                    print(f"{i}. {note.strip()}")
    except FileNotFoundError:
        print(f"No notes found. The file {filename} does not exist.")

# delete notes file 
def delete_notes_file(filename):
    if os.path.exists(filename):
        os.remove(filename)
        print(f"All notes deleted. The file {filename} has been removed.")
    else:
        print(f"The file {filename} does not exist.")
    


