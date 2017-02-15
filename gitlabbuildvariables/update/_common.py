from abc import ABCMeta, abstractmethod

from gitlabbuildvariables.common import GitLabConfig


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