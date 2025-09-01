import notes_module

FILENAME = "notes.txt"

while True:
    print("\n--- Notes Management ---")
    print("1. Add Note")
    print("2. View Notes")
    print("3. Delete All Notes")
    print("4. Exit")
    
    choice = input("Choose an option (1-4): ")
    
    if choice == '1':
        note = input("Enter your note: ")
        notes_module.save_notes_to_file(note, FILENAME)
    elif choice == '2':
        notes_module.read_notes_from_file(FILENAME)
    elif choice == '3':
        confirm = input("Are you sure you want to delete all notes? (y/n): ")
        if confirm.lower() == 'y':
            notes_module.delete_notes_file(FILENAME)
        else:
            print("Deletion cancelled.")
    elif choice == '4':
        print("Exiting the program.")
        break
    else:
        print("Invalid choice. Please select a valid option.")