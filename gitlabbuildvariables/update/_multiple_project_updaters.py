import json
from abc import ABCMeta, abstractmethod
from typing import Iterable, Tuple, Dict

from gitlabbuildvariables.common import GitLabConfig
from gitlabbuildvariables.update._builders import ProjectVariablesUpdaterBuilder
from gitlabbuildvariables.update._single_project_updaters import logger
from gitlabbuildvariables.update._common import VariablesUpdater


class ProjectsVariablesUpdater(VariablesUpdater, metaclass=ABCMeta):
    """
    Updates variables for projects in GitLab CI.
    """
    @abstractmethod
    def _get_projects_and_settings_groups(self) -> Iterable[Tuple[str, Iterable[str]]]:
        """
        Gets projects and their associated settings groups.
        :return: iterable of tuples where the first item is the project identifier and the second is a list of their
        settings groups
        """

    def __init__(self, project_variables_updater_builder: ProjectVariablesUpdaterBuilder, gitlab_config: GitLabConfig):
        """
        Constructor.
        :param project_variables_updater_builder: builder for project variables updaters
        :param gitlab_config: the configuration required to access GitLab
        """
        super().__init__(gitlab_config)
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


class FileBasedProjectsVariablesUpdater(ProjectsVariablesUpdater):
    """
    Updates variables for projects in GitLab CI, as defined by a configuration file.
    """
    def __init__(self, config_location: str, project_variables_updater_builder: ProjectVariablesUpdaterBuilder,
                 gitlab_config: GitLabConfig):
        """
        Constructor.
        :param config_location: the location of the config file for setting project variables from settings groups
        :param project_variables_updater_builder: see `ProjectsVariablesUpdater.__init__`
        :param gitlab_config: see `ProjectsVariablesUpdater.__init__`
        """
        super().__init__(project_variables_updater_builder, gitlab_config)
        self.config_location = config_location

    def _get_projects_and_settings_groups(self) -> Iterable[Tuple[str, Iterable[str]]]:
        with open(self.config_location, "r") as config_file:
            config = config_file.read()
        config = json.loads(config)
        logger.info("Read config from \"%s\"" % self.config_location)
        logger.debug("Config: %s" % config)
        return config.items()


class DictBasedProjectsVariablesUpdater(ProjectsVariablesUpdater):
    """
    Updates variables for projects in GitLab CI, as defined by a configuration Python dictionary.
    """
    def __init__(self, configuration: Dict[str, Dict[str, str]],
                 project_variables_updater_builder: ProjectVariablesUpdaterBuilder, gitlab_config: GitLabConfig):
        """
        Constructor.
        :param configuration: project variables configuration
        :param project_variables_updater_builder: see `ProjectsVariablesUpdater.__init__`
        :param gitlab_config: see `ProjectsVariablesUpdater.__init__`
        """
        super().__init__(project_variables_updater_builder, gitlab_config)
        self.configuration = configuration

    def _get_projects_and_settings_groups(self) -> Iterable[Tuple[str, Iterable[str]]]:
        return self.configuration.items()
