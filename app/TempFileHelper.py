import os
import tempfile
import logging


class TempFileHelper:
    working_temp_folder = None

    def __init__(self):
        self.working_temp_folder = tempfile.TemporaryDirectory()

    def generate_temp_filename(self, ext=None):
        file_name = next(tempfile._get_candidate_names())
        if ext:
            file_name += "." + ext
        path = os.path.join(self.working_temp_folder.name, file_name)
        # print(path)
        logging.debug("new tempfile generated: "+path)
        return path
