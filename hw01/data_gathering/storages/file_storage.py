import os
import zipfile

from storages.storage import Storage


class FileStorage(Storage):
    """
    Class provides access to file storage
    """

    def __init__(self, file_name):
        self.file_name = file_name
        self.user_ids = []

    def read_data(self):
        if not os.path.exists(self.file_name):
            raise StopIteration

        data = {}
        with zipfile.ZipFile(self.file_name) as zf:
            self.user_ids = zf.namelist()
            for file in self.user_ids:
                data[file] = zf.read(file).decode('utf-8')
        return data

    def write_data(self, data):
        """
        :param data_array: dict content user name and user data
        """
        with zipfile.ZipFile(self.file_name, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            for key, value in data.items():
                zf.writestr(key, value.encode('utf-8'))

    def append_data(self, data):
        """
        :param data: dict content user name and user data
        """
        old_data = self.read_data()
        old_data.update(data)
        self.write_data(old_data)
