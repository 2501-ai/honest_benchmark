import os
import shutil


def remove_previous_folders(files_dir):
    """
    Remove all previous folders in the files directory.

    Args:
        files_dir (str): The directory containing the files.
    """
    for item in os.listdir(files_dir):
        item_path = os.path.join(files_dir, item)
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
