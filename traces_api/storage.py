import uuid
import shutil
import os
import os.path

from datetime import datetime
import werkzeug.datastructures


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

    def is_compressed(self):
        """
        Is file compressed

        :return: True if compressed otherwise False
        """
        return self.location.endswith(".gz")

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

    def __init__(self, storage_folder, compression):
        """
        :param storage_folder: Storage folder where files will be saved.
                               Application should have correct permissions to write to this folder.
        :param compression: Used for compressing files
        """
        self._storage_folder = storage_folder
        self._compression = compression

    @staticmethod
    def _generate_file_name():
        """
        Generate random file name based on current time

        :return: random file name
        """
        t = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        return "{}_{}".format(t, str(uuid.uuid4())[:5])

    def save_file(self, file_stream):
        """
        :param file_stream:
        :return: Relative file location
        """

        file_name = "{}.gz".format(self._generate_file_name())
        file_path = "{}/{}".format(self._storage_folder, file_name)

        self._compression.compress(file_stream, file_path)

        return file_name

    def remove_file(self, relative_path):
        """
        Permanently remove file

        :param relative_path:
        :return:
        """
        file_path = self._get_absolute_file_path(relative_path)
        os.remove(file_path)

    def get_file(self, relative_path):
        """
        Get File using relative path

        :param relative_path:
        :return: File
        """
        abs_path = self._get_absolute_file_path(relative_path)
        return File(abs_path)

    def _get_absolute_file_path(self, relative_path):
        return "{}/{}".format(self._storage_folder, relative_path)
