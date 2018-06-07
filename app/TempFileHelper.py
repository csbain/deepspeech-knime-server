import logging
import os
import tempfile
import shutil

class TempFileHelper:
    temp_folder_base = "/tmp/"
    working_temp_folder = None

    def __init__(self):
        self.working_temp_folder = self.temp_folder_base+next(tempfile._get_candidate_names())+"/"
        if not os.path.exists(self.working_temp_folder):
            os.makedirs(self.working_temp_folder)


    def generate_temp_filename(self, ext=None):
        file_name = next(tempfile._get_candidate_names())
        if ext:
            file_name += "." + ext
        path = os.path.join(self.working_temp_folder.name, file_name)
        # print(path)
        logging.debug("new tempfile generated: " + path)
        return path

    def __del__(self):
        try:
            shutil.rmtree(self.working_temp_folder)
        except OSError:
            pass
