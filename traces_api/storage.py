import uuid
import shutil
import os

from datetime import datetime


class File:
    """
    This class represents file on disc
    Class allows make basic operations with file
    """

    def __init__(self, location):
        """
        :param location: Current file location
        """
        self.location = location

    def move_file(self, new_location):
        """
        Move file to specific location

        :param new_location: New location of file
        """
        shutil.move(self.location, new_location)
        self.location = new_location

    @staticmethod
    def create_new():
        """
        Create new empty file
        :return: File object
        """
        random_file_path = "/tmp/trace_api_%s" % str(uuid.uuid4())
        with open(random_file_path, "wb"):
            pass

        return File(location=random_file_path)


class FileStorage:

    def __init__(self, storage_folder):
        """
        :param storage_folder: Storage folder where files will be saved.
                               Application should have correct permissions to write to this folder.
        """
        self._storage_folder = storage_folder

    @staticmethod
    def _generate_file_name():
        """
        Generate random file name based on current time
        :return: random file name
        """
        t = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        return "{}_{}".format(t, str(uuid.uuid4())[:5])

    def save_file(self, file, expected_mime_types=None):
        """
        :param file: werkzeug.datastructures.FileStorage
        :param expected_mime_types:
        :return: Relative file location
        """
        if expected_mime_types and file.mimetype not in expected_mime_types:
            raise Exception("Invalid MIME type {}, expected: {}".format(file.mimetype, expected_mime_types))

        file_name = self._generate_file_name()
        file_path = "{}/{}".format(self._storage_folder, file_name)

        file.save(file_path)

        return file_name

    def remove_file(self, relative_path):
        os.remove(self.get_absolute_file_path(relative_path))

    def save_file2(self, file: File):
        file_name = self._generate_file_name()
        file_path = "{}/{}".format(self._storage_folder, file_name)

        file.move_file(file_path)

        return file_name

    def get_absolute_file_path(self, relative_path):
        return "{}/{}".format(self._storage_folder, relative_path)
