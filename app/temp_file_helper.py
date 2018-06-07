import logging
import os
import shutil
import random
import string


class TempFileHelper:
    temp_folder_base = "/tmp/"
    working_temp_folder = None

    def __init__(self):
        tmp_folder = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        self.working_temp_folder = self.temp_folder_base+tmp_folder+"/"
        if not os.path.exists(self.working_temp_folder):
            os.makedirs(self.working_temp_folder)


    def generate_temp_filename(self, ext=None):
        file_name = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        if ext:
            file_name += "." + ext
        path = os.path.join(self.working_temp_folder, file_name)
        # print(path)
        logging.debug("new tempfile generated: " + path)
        return path

    def __del__(self):
        try:
            shutil.rmtree(self.working_temp_folder)
        except OSError:
            pass
