from datetime import datetime
from pathlib import Path
from typing import List
from utilities.colored import print_green, print_red
from utilities.errors import handle_generic_error
import os
import shutil
import tempfile

# Returns parent directory of current project
def get_parent_path() -> str:
    try:
        location = "utilities.backup.get_parent_path()"
        task = "getting parent path" 
        # Grabs the location of the current file (functions.py)
        functions_file_path = Path(__file__).resolve()
        
        # Get the directory where the current script exists
        utilities_directory = functions_file_path.parent
        
        # Grabs the parent directory of the child directory `utilities`
        parent_directory = utilities_directory.parent
        
        # Converts the parent directory path object to a string then returns it
        return str(parent_directory)
    
    except FileNotFoundError as e:
        handle_generic_error(location, task, e)
    except PermissionError as e:
        handle_generic_error(location, task, e)
    except Exception as e:
        handle_generic_error(location, task, e)
    return None

# Appends the backup directory to the parent directory
def get_backup_directory_path() -> str:
    parent_directory = get_parent_path()
    if parent_directory:
        return os.path.join(parent_directory, "data", "backups")
    return None

# Writes links.txt to a text file with current timestamp in the 'data/backups' directory
def backup_last_session() -> None:
    location:str = "utilities.backup.backup_old_links_files()"
    task:str = "getting parent path" 
    try:
        # Get a list of files in the current directory
        dir_list:List[str] = os.listdir(os.getcwd())

        # Filter out the only the last session files (links.txt and vulnerables.txt)
        old_links_files:List[str] = [file for file in dir_list if "links" in file and file.endswith(".txt")]
        old_vulnerables_files:List[str] = [file for file in dir_list if "vulnerables" in file and file.endswith(".txt")]

        # Create a directory to store the backup files if it doesn't exist
        backup_folder:str = get_backup_directory_path()
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        # Executes the actual action of backing up the files
        backup_old_session_files(old_links_files, old_vulnerables_files, backup_folder)

        if old_links_files or old_vulnerables_files:
            print_green("Successfully backed up last session.")

        else:
            print_red("No previous session found, continuing without backup.\n")
    
    except Exception as e:
        handle_generic_error(location, task, e)

def backup_old_session_files(old_links_files:List[str], old_vulnerables_files:List[str], backup_folder:str) -> None:
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Move or copy these files to the backup folder
    for file in old_links_files:
        # Construct the source and destination paths
        source_path = os.path.join(os.getcwd(), file)

        # Create a temporary directory to hold the copied file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, file)
            shutil.copy(source_path, temp_file)

            new_file = "links_" + current_time + ".txt"

            # Move the file from the temporary directory to the backup folder
            destination_path = os.path.join(os.getcwd(), backup_folder, new_file)
            shutil.move(temp_file, destination_path)

        os.remove(source_path)

    for file in old_vulnerables_files:
        # Construct the source and destination paths
        source_path = os.path.join(os.getcwd(), file)

        # Create a temporary directory to hold the copied file
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = os.path.join(temp_dir, file)
            shutil.copy(source_path, temp_file)
            new_file = "vulnerables_" + current_time + ".txt"

            # Move the file from the temporary directory to the backup folder
            destination_path = os.path.join(os.getcwd(), backup_folder, new_file)
            shutil.move(temp_file, destination_path)

        os.remove(source_path)
