import json
import os
from typing import List, Dict

import logging

from gitlabbuildvariables.manager import ProjectBuildVariablesManager
from gitlabbuildvariables.reader import read_variables

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler())


class ProjectVariablesUpdater:
    """
    Updates variables for projects in GitLab CI, as defined by a configuration file.
    """
    def __init__(self, config_location: str, gitlab_location: str, gitlab_access_token: str,
                 setting_repositories: List[str]=None, default_setting_extensions: List[str]=None):
        """
        Constructor.
        :param config_location: the location of the config file for setting project variables from variable sources
        :param gitlab_location: the location of GitLab
        :param gitlab_access_token: access token for GitLab
        :param setting_repositories: directories that may contain variable source files (highest preference first)
        :param default_setting_extensions: file extensions that variable source files could have if that given is not
        found(highest preference first, e.g. ["json", "init"])
        """
        self.config_location = config_location
        self.gitlab_location = gitlab_location
        self.gitlab_access_token = gitlab_access_token
        self.setting_repositories = setting_repositories if setting_repositories is not None else []
        self.default_setting_extensions = default_setting_extensions if default_setting_extensions is not None else []

    def update(self):
        """
        Updates the project variables in GitLab to match those specified in the configuration file.
        """
        with open(self.config_location, "r") as config_file:
            config = config_file.read()
        config = json.loads(config)
        _logger.info("Read config from \"%s\"" % self.config_location)
        _logger.debug("Config: %s" % config)

        for project, settings in config.items():
            self._update_project(project, settings)

    def _update_project(self, project: str, settings_locations: List[str]):
        """
        Updates the build variables for the given project based on the variable settings sourced from the given
        locations.
        :param project: project to update build variables for
        :param settings_locations: locations of variable settings that are to be sourced (lowest preference first)
        """
        variables = {}  # type: Dict[str, str]
        for setting in settings_locations:
            setting_location = self._resolve_setting_location(setting)
            setting_variables = read_variables(setting_location)
            variables.update(setting_variables)

        variables_manager = ProjectBuildVariablesManager(self.gitlab_location, self.gitlab_access_token, project)
        variables_manager.set_variables(variables)
        _logger.info("Set variables for \"%s\": %s" % (project, variables))

    def _resolve_setting_location(self, identifier: str) -> str:
        """
        Resolves the location of a setting file based on the given identifier.
        :param identifier: the identifier for the settings file (~its location)
        :return: the absolute path of the settings location
        """
        if os.path.isabs(identifier):
            possible_paths = [identifier]
        else:
            possible_paths = []
            for repository in self.setting_repositories:
                possible_paths.append(os.path.join(repository, identifier))

        for default_setting_extension in self.default_setting_extensions:
            number_of_paths = len(possible_paths)
            for i in range(number_of_paths):
                path_with_extension = "%s.%s" % (possible_paths[i], default_setting_extension)
                possible_paths.append(path_with_extension)

        for path in possible_paths:
            if os.path.exists(path):
                return path
        raise ValueError("Could not resolve location of settings identified by: \"%s\"" % identifier)
