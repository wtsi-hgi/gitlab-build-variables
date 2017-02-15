from abc import ABCMeta, abstractmethod
from typing import TypeVar, Generic, Iterable, List, Dict

from gitlabbuildvariables.common import GitLabConfig
from gitlabbuildvariables.update._single_project_updaters import ProjectVariablesUpdater, \
    FileBasedProjectVariablesUpdater, DictBasedProjectVariablesUpdater

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
        :param setting_repositories: see `FileBasedProjectVariablesUpdater.__init__`
        :param default_setting_extensions: see `FileBasedProjectVariablesUpdater.__init__`
        """
        self.setting_repositories = setting_repositories if setting_repositories is not None else []
        self.default_setting_extensions = default_setting_extensions if default_setting_extensions is not None else []

    def build(self, project: str, groups: Iterable[str], gitlab_config: GitLabConfig) \
            -> FileBasedProjectVariablesUpdater:
        return FileBasedProjectVariablesUpdater(
            project=project, groups=groups, gitlab_config=gitlab_config, setting_repositories=self.setting_repositories,
            default_setting_extensions=self.default_setting_extensions)


class DictBasedProjectVariablesUpdaterBuilder(ProjectVariablesUpdaterBuilder[DictBasedProjectVariablesUpdater]):
    """
    Builder of `DictBasedProjectVariablesUpdater` instances.
    """
    def __init__(self, settings: Dict[str, Dict[str, str]]):
        """
        Constructor.
        :param settings: see `DictBasedProjectVariablesUpdater.__init__`
        """
        self.settings = settings

    def build(self, project: str, groups: Iterable[str], gitlab_config: GitLabConfig) \
            -> DictBasedProjectVariablesUpdater:
        return DictBasedProjectVariablesUpdater(
            project=project, groups=groups, gitlab_config=gitlab_config, settings=self.settings)
