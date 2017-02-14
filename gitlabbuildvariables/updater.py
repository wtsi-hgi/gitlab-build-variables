import json
import os
from abc import ABCMeta, abstractmethod
from typing import List, Dict, Set

import logging

from gitlabbuildvariables.common import GitLabConfig
from gitlabbuildvariables.manager import ProjectVariablesManager
from gitlabbuildvariables.reader import read_variables

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler())


class VariablesUpdater(metaclass=ABCMeta):
    """
    Constructor.
    :param gitlab_config: configuration required to access GitLab
    :param setting_repositories: directories that may contain variable source files (highest preference first)
    :param default_setting_extensions: file extensions that variable source files could have if that given is not
    found(highest preference first, e.g. ["json", "init"])
    """
    def __init__(self, gitlab_config: GitLabConfig, setting_repositories: List[str]=None,
                 default_setting_extensions: List[str]=None):
        self.gitlab_config = gitlab_config
        self.setting_repositories = setting_repositories if setting_repositories is not None else []
        self.default_setting_extensions = default_setting_extensions if default_setting_extensions is not None else []

    @abstractmethod
    def update(self):
        """
        Updates the appropriate GitLab CI build variables.
        """


class ProjectVariablesUpdater(VariablesUpdater):
    """
    Updates variables for a project in GitLab CI.
    """
    def __init__(self, project: str, setting_sources: Set[str], *args, **kwargs):
        """
        Constructor.
        :param project: name or ID of the project to update variables for
        :param setting_sources: locations of variable settings that are to be sourced (lowest preference first)
        """
        super().__init__(*args, **kwargs)
        self.project = project
        self.setting_sources = setting_sources
        self._variables_manager = ProjectVariablesManager(self.gitlab_config, project)

    def update(self):
        variables = {}  # type: Dict[str, str]
        for setting_source_identifier in self.setting_sources:
            setting_location = self._resolve_setting_location(setting_source_identifier)
            setting_variables = read_variables(setting_location)
            variables.update(setting_variables)

        self._variables_manager.set_variables(variables)
        _logger.info("Set variables for \"%s\": %s" % (self.project, variables))

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


class ProjectsVariablesUpdater(VariablesUpdater):
    """
    Updates variables for projects in GitLab CI, as defined by a configuration file.
    """
    def __init__(self, config_location: str, *args, **kwargs):
        """
        Constructor.
        :param config_location: the location of the config file for setting project variables from variable sources
        """
        super().__init__(*args, **kwargs)
        self.config_location = config_location

    def update(self):
        with open(self.config_location, "r") as config_file:
            config = config_file.read()
        config = json.loads(config)
        _logger.info("Read config from \"%s\"" % self.config_location)
        _logger.debug("Config: %s" % config)

        for project, settings_sources in config.items():
            project_updater = ProjectVariablesUpdater(
                project, set(settings_sources), gitlab_config=self.gitlab_config,
                setting_repositories=self.setting_repositories,
                default_setting_extensions=self.default_setting_extensions)
            project_updater.update()
