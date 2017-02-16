import logging
import os
from abc import ABCMeta, abstractmethod
from typing import List, Dict, Iterable

from gitlabbuildvariables.manager import ProjectVariablesManager
from gitlabbuildvariables.reader import read_variables
from gitlabbuildvariables.update._common import VariablesUpdater

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


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
        logger.info("Set variables for \"%s\": %s" % (self.project, variables))

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


class DictBasedProjectVariablesUpdater(ProjectVariablesUpdater):
    """
    Updates variables for a project in GitLab CI based on the values in a Python dictionary object.
    """
    def __init__(self, settings: Dict[str, Dict[str, str]], **kwargs):
        """
        Constructor.
        :param settings: settings dictionary where projects names or identifiers are keys and their values are
        key-value pairs representing variable names and values
        :param kwargs: named arguments required for `ProjectVariablesUpdater`
        """
        super().__init__(**kwargs)
        self.settings = settings

    def _read_group_variables(self, group: str) -> Dict[str, str]:
        return self.settings[group]
