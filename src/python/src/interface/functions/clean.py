import os
import glob

from interface.data.config import EXPORT_PATH

MAX_FILES = 30

async def clean_history():
    files = sorted(glob.glob(os.path.join(EXPORT_PATH, '*.csv')), key=os.path.getmtime)

    if len(files) > MAX_FILES:
        files_to_delete = files[:-MAX_FILES]
        for file in files_to_delete:
            os.remove(file)
            print(f"Deleted file: {file}")