import json
from typing import Iterable, Tuple

from gitlabbuildvariables.common import GitLabConfig
from gitlabbuildvariables.update._builders import ProjectVariablesUpdaterBuilder
from gitlabbuildvariables.update._single_project_updaters import logger
from gitlabbuildvariables.update._common import VariablesUpdater


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
        logger.info("Read config from \"%s\"" % self.config_location)
        logger.debug("Config: %s" % config)
        return config.items()