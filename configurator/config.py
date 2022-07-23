import collections
import configparser
import distutils.util
import logging
import os

import expandvars

from . import exceptions

LOGGER = logging.getLogger(__name__)

_UNSET = object()


class Config:
    class ConfigInterpolation(configparser.BasicInterpolation):

        def before_get(self, parser, section, option, value, defaults):
            return expandvars.expandvars(value)

    instances = list()
    parser = configparser.ConfigParser(interpolation=ConfigInterpolation())
    directory = None
    file_names = None

    def __init__(self, data_type, section, option=None, fallback=_UNSET):
        self.__class__.instances.append(self)
        self._data_type = data_type
        self._is_none = False
        self._section = section
        self._option = option
        self._fallback = fallback
        self._gen_value = _UNSET

    @staticmethod
    def init(directory, *file_names, ignore_error=False):
        # Set the directory of the configuration files to use
        Config.directory = directory
        # Load the configuration files
        Config.load(*file_names, ignore_error=ignore_error)

    @staticmethod
    def path(target=""):
        yield os.path.join(Config.directory, target)

    @staticmethod
    def dir(target=""):
        return os.path.join(Config.directory, target)

    @staticmethod
    def load(*file_names, encoding=None, ignore_error=False):
        # If configuration should only be reloaded
        if not file_names: file_names = Config.file_names
        # Set file names
        Config.file_names = file_names
        # Build the real path of each configuration file
        config_file_paths = [os.path.join(Config.directory, file_name) for file_name in file_names]
        # Check if the file exists
        valid_file_paths = []
        for config_file_path in config_file_paths:
            if not os.path.isfile(config_file_path):
                if not ignore_error:
                    raise exceptions.ConfigFileDoesNotExists(config_file_path)
            else:
                valid_file_paths.append(config_file_path)
        # Parse and read the configurations
        Config.parser.read(valid_file_paths, encoding)

    def get(self, option=None, **kwargs):
        if self._is_none:
            return None
        option = self._option if option is None else option
        if self._fallback is _UNSET:
            value = Config.parser.get(self._section, option)
        else:
            value = Config.parser.get(self._section, option, fallback=self._fallback)
            if value == '':
                value = self._fallback
        # Check the value
        if value is None:
            return None
        if isinstance(value, collections.Generator):
            if self._gen_value is _UNSET:
                self._gen_value = next(value)
            return self._gen_value
        # Check data type
        if isinstance(self._data_type, type):
            if self._data_type == bool:
                if isinstance(value, bool):
                    return value
                elif isinstance(value, str):
                    return bool(distutils.util.strtobool(value))
            elif self._data_type == str and kwargs:
                value = str(value).format(**kwargs)
        elif isinstance(self._data_type, tuple) and isinstance(value, str):
            collection, data_type = self._data_type
            if collection == list:
                return [data_type(v) for v in value.split(",")]
        # Return the casted value
        return self._data_type(value)

    def set(self, value):
        if value is not None:
            if not isinstance(value, self._data_type):
                raise exceptions.ValueTypeNotAllowed(self._option, type(self._data_type).__name__)
            self._is_none = False
            value = self._data_type(value)
        else:
            self._is_none = True
            return
        if self._section not in Config.parser.sections():
            Config.parser.add_section(self._section)
        try:
            Config.parser.set(self._section, self._option, str(value))
        except Exception as e:
            raise exceptions.SetValueError(value, str(e))

    @staticmethod
    def update(data):
        for section, data in data.items():
            if section not in Config.parser.sections():
                Config.parser.add_section(section)
            for option, value in data:
                Config.parser.set(section, option, value)

    @staticmethod
    def save(filename):
        with open(Config.dir(filename), 'w') as f:
            Config.parser.write(f)

    @staticmethod
    def data():
        return {s: Config.parser.items(s) for s in Config.parser.sections()}
