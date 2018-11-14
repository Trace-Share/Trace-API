import uuid

from datetime import datetime


class FileStorage:

    def __init__(self, storage_folder):
        self._storage_folder = storage_folder

    @staticmethod
    def _generate_file_name():
        t = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")
        return "{}_{}".format(t, str(uuid.uuid4())[:5])

    def save_file(self, file, expected_mime_types) -> str:
        """
        :param file: werkzeug.datastructures.FileStorage
        :param expected_mime_types:
        :return: Relative file location
        """
        if file.mimetype not in expected_mime_types:
            raise Exception("Invalid MIME type {}, expected: {}".format(file.mimetype, expected_mime_type))

        file_name = self._generate_file_name()
        file_path = "{}/{}".format(self._storage_folder, file_name)

        file.save(file_path)

        return file_name
