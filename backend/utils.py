import os
import time
import logging

def wait_for_file(file_path, timeout=30):
    """wait for a file to exist until timeout."""
    start_time = time.time()
    while True:
        if os.path.exists(file_path):
            logging.info(f"file {file_path} found, proceeding with conversion.")
            return True
        elif (time.time() - start_time) > timeout:
            logging.error(f"file {file_path} not found after {timeout} seconds.")
            return False
        time.sleep(1)  # sleep for a second before retrying
