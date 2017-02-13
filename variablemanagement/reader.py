import configparser
from typing import Dict, List

_FAKE_SECTION_NAME = "all"
_FAKE_SECTION = "[%s]\n" % _FAKE_SECTION_NAME
_EXPORT_COMMAND = "export "


def read_variables(config_location: str) -> Dict[str, str]:
    """
    Reads variables out of a config file. Variables can be in a (section-less) ini file or in a shell file used to
    source the variables (i.e. one that has just got "export *" like statements in it.
    :param config_location: the location of the config file
    :return: dictionary where the variable names are key and their values are the values
    """
    with open(config_location, "r") as config_file:
        config_lines = config_file.readlines()
    config_lines = _shell_to_ini(config_lines)
    return _read_ini_config("\n".join(config_lines))


def _read_ini_config(ini_file_contents: str) -> Dict[str, str]:
    """
    Parses the given ini file contents and converts to a dictionary of key/value pairs.
    :param ini_file_contents: the contents of the ini file
    :return: dictionary where the variable names are key and their values are the values
    """
    config = configparser.ConfigParser()
    config.read_string(_FAKE_SECTION + ini_file_contents)

    if len(config.sections()) > 1:
        raise ValueError("Config should only have one (fake) section")

    return dict(config[_FAKE_SECTION_NAME].items())


def _shell_to_ini(shell_file_contents: List[str]) -> List[str]:
    """
    Converts a shell file, which just contains comments and "export *" statements into an ini file.
    :param shell_file_contents: the contents of the shell file
    :return: lines of an equivalent ini file
    """
    line_number = 0
    while line_number < len(shell_file_contents):
        line = shell_file_contents[line_number].strip()
        if line.startswith("#") or line == "":
            del shell_file_contents[line_number]
        else:
            if line.startswith(_EXPORT_COMMAND):
                shell_file_contents[line_number] = line.replace(_EXPORT_COMMAND, "").strip()
            line_number += 1
    return shell_file_contents

