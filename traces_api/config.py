import configparser


class Config:
    """
    This class is used for parsing config
    """

    def __init__(self, config_file):
        """
        :param config_file: Location of configuration file
        """
        self.config = configparser.ConfigParser()
        self.config.read(config_file)

    def get(self, section, key):
        """
        Read value from config
        :param section:
        :param key:
        :return: Value in config
        """
        section = self.config[section]
        return section.get(key, False)

