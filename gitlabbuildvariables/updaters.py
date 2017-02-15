import json
import os
from abc import ABCMeta, abstractmethod
from typing import List, Dict, Set, Tuple, Iterable, Type, Generic, TypeVar

import logging

from gitlabbuildvariables.common import GitLabConfig
from gitlabbuildvariables.manager import ProjectVariablesManager
from gitlabbuildvariables.reader import read_variables

_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler())


class VariablesUpdater(metaclass=ABCMeta):
    """
    Has the ability to update build variables in GitLab CI.
    """
    @abstractmethod
    def update(self):
        """
        Updates build variables in GitLab CI.
        """

    @abstractmethod
    def update_required(self) -> bool:
        """
        Whether the build variables in GitLab CI should be updated.
        :return:
        """

    def __init__(self, gitlab_config: GitLabConfig):
        """
        Constructor.
        :param gitlab_config: configuration required to access GitLab
        """
        self.gitlab_config = gitlab_config


class ProjectVariablesUpdater(VariablesUpdater, metaclass=ABCMeta):
    """
    Updates variables for a project in GitLab CI.
    """
    @abstractmethod
    def _read_group_variables(self, group: str) -> Dict[str, str]:
        """
        Reads the setting variables associated to the given group identifier.
        :param group: the identifier of the group
        :return: the setting variables associated to the given group
        """

    def __init__(self, project: str, groups: Iterable[str], **kwargs):
        """
        Constructor.
        :param project: name or ID of the project to update variables for
        :param groups: lgroups of settings variables that are to be set (lowest preference first)
        :param kwargs: named arguments required in `VariablesUpdater` constructor
        """
        super().__init__(**kwargs)
        self.project = project
        self.groups = groups
        self._variables_manager = ProjectVariablesManager(self.gitlab_config, project)

    def update(self):
        variables = self._get_variables()
        self._variables_manager.set_variables(variables)
        _logger.info("Set variables for \"%s\": %s" % (self.project, variables))

    def update_required(self) -> bool:
        return self._variables_manager.get_variables() != self._get_variables()

    def _get_variables(self) -> Dict[str, str]:
        """
        Gets the variables that should be set for this project.
        :return: the variables
        """
        variables = {}  # type: Dict[str, str]
        for group in self.groups:
            setting_variables = self._read_group_variables(group)
            variables.update(setting_variables)
        return variables


class FileBasedProjectVariablesUpdater(ProjectVariablesUpdater):
    """
    Updates variables for a project in GitLab CI based on the values stored within a file.
    """
    def __init__(self, setting_repositories: List[str]=None, default_setting_extensions: List[str]=None, **kwargs):
        """
        Constructor.
        :param setting_repositories: directories that may contain variable source files (highest preference first)
        :param default_setting_extensions: file extensions that variable source files could have if that given is not
        found(highest preference first, e.g. ["json", "init"])
        :param kwargs: named arguments required for `ProjectVariablesUpdater`
        """
        super().__init__(**kwargs)
        self.setting_repositories = setting_repositories if setting_repositories is not None else []
        self.default_setting_extensions = default_setting_extensions if default_setting_extensions is not None else []

    def _read_group_variables(self, group: str) -> Dict[str, str]:
        setting_location = self._resolve_group_location(group)
        return read_variables(setting_location)

    def _resolve_group_location(self, group: str) -> str:
        """
        Resolves the location of a setting file based on the given identifier.
        :param group: the identifier for the group's settings file (~its location)
        :return: the absolute path of the settings location
        """
        if os.path.isabs(group):
            possible_paths = [group]
        else:
            possible_paths = []
            for repository in self.setting_repositories:
                possible_paths.append(os.path.join(repository, group))

        for default_setting_extension in self.default_setting_extensions:
            number_of_paths = len(possible_paths)
            for i in range(number_of_paths):
                path_with_extension = "%s.%s" % (possible_paths[i], default_setting_extension)
                possible_paths.append(path_with_extension)

        for path in possible_paths:
            if os.path.exists(path):
                return path
        raise ValueError("Could not resolve location of settings identified by: \"%s\"" % group)


ProjectVariablesUpdaterType = TypeVar("ProjectVariablesUpdater", bound=ProjectVariablesUpdater)


class ProjectVariablesUpdaterBuilder(Generic[ProjectVariablesUpdaterType], metaclass=ABCMeta):
    """
    Builder of `ProjectVariablesUpdater` instances.
    """
    @abstractmethod
    def build(self, project: str, groups: Iterable[str], gitlab_config: GitLabConfig) \
            -> ProjectVariablesUpdaterType:
        """
        Builds a `ProjectVariablesUpdater` instance using the given arguments.
        :param project: the project that variables are to be updated for
        :param groups: the groups of settings that should be set for the project
        :param gitlab_config: the configuration required to access GitLab
        :return: the project variable updater
        """

class FileBasedProjectVariablesUpdaterBuilder(ProjectVariablesUpdaterBuilder[FileBasedProjectVariablesUpdater]):
    """
    Builder of `FileBasedProjectVariablesUpdater` instances.
    """
    def __init__(self, setting_repositories: List[str]=None, default_setting_extensions: List[str]=None):
        """
        Constructor.
        :param setting_repositories: directories that may contain variable source files (highest preference first)
        :param default_setting_extensions: file extensions that variable source files could have if that given is not
        """
        self.setting_repositories = setting_repositories if setting_repositories is not None else []
        self.default_setting_extensions = default_setting_extensions if default_setting_extensions is not None else []

    def build(self, project: str, groups: Iterable[str], gitlab_config: GitLabConfig) \
            -> FileBasedProjectVariablesUpdater:
        return FileBasedProjectVariablesUpdater(
            project=project, groups=groups, gitlab_config=gitlab_config, setting_repositories=self.setting_repositories,
            default_setting_extensions=self.default_setting_extensions)


class ProjectsVariablesUpdater(VariablesUpdater):
    """
    Updates variables for projects in GitLab CI, as defined by a configuration file.
    """
    def __init__(self, config_location: str, project_variables_updater_builder: ProjectVariablesUpdaterBuilder,
                 gitlab_config: GitLabConfig):
        """
        Constructor.
        :param config_location: the location of the config file for setting project variables from settings groups
        :param project_variables_updater_builder: builder for project variables updaters
        :param gitlab_config: the configuration required to access GitLab
        """
        super().__init__(gitlab_config)
        self.config_location = config_location
        self.project_variables_updater_builder = project_variables_updater_builder

    def update(self):
        for project, settings_group in self._get_projects_and_settings_groups():
            project_updater = self.project_variables_updater_builder.build(
                project=project, groups=settings_group, gitlab_config=self.gitlab_config)
            project_updater.update()

    def update_required(self) -> bool:
        for project, settings_group in self._get_projects_and_settings_groups():
            project_updater = self.project_variables_updater_builder.build(
                project=project, groups=settings_group, gitlab_config=self.gitlab_config)
            if project_updater.update_required():
                return True
        return False

    def _get_projects_and_settings_groups(self) -> Iterable[Tuple[str, Iterable[str]]]:
        """
        Gets projects and their associated settings groups.
        :return: iterable of tuples where the first item is the project identifier and the second is a list of their
        settings groups
        """
        with open(self.config_location, "r") as config_file:
            config = config_file.read()
        config = json.loads(config)
        _logger.info("Read config from \"%s\"" % self.config_location)
        _logger.debug("Config: %s" % config)
        return config.items()
