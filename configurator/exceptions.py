class ConfiguratorError(Exception):
    """Raised when an Configurator error occurs."""

    def __init__(self, message="An unspecified Configurator error has occurred"):
        super().__init__(message)


class ConfigFileDoesNotExists(ConfiguratorError):

    def __init__(self, config_file_path):
        super().__init__("Config file '{c}' does not exist".format(**{
            "c": config_file_path
        }))


class ValueTypeNotAllowed(ConfiguratorError):

    def __init__(self, option, data_type):
        super().__init__("Value of '{o}' must be None or type '{t}'".format(**{
            "o": option,
            "t": data_type
        }))


class SetValueError(ConfiguratorError):

    def __init__(self, value, reason):
        super().__init__("Could not set the value '{v}'. Reason: {r}".format(**{
            "v": value,
            "r": reason
        }))
