import unittest
from abc import ABCMeta
from threading import Lock

from gitlab import Project, ProjectVariable, Gitlab
from typing import Dict, Iterable
from useintest.models import DockerisedServiceWithUsers
from useintest.predefined.gitlab import GitLab8_16_6_ce_0ServiceController

from gitlabbuildvariables.common import GitLabConfig
from gitlabbuildvariables.manager import ProjectVariablesManager

_GITLAB_PORT = 80

EXAMPLE_PROJECT_NAME = "my-project"
EXAMPLE_VARIABLES_1 = {"thisKey": "thatValue", "otherKey": "otherValue"}
EXAMPLE_VARIABLES_2 = {"a": "b", "c": "d"}


def add_variables_to_project(variables: Dict[str, str], project: Project):
    """
    Adds the given build variables to the given GitLab project.
    :param variables: variables to add
    :param project: project to add variables to
    """
    for key, value in variables.items():
        project.variables.create({"key": key, "value": value})


def convert_projects_variables_to_dicts(project_variables: Iterable[ProjectVariable]) -> Dict[str, str]:
    """
    Converts the GitLab's library project variable models to a dictionary representation.
    :param project_variables: the project variable models
    :return: the dicitionary representation
    """
    return {variable.key: variable.value for variable in project_variables}


class TestWithGitLabProject(unittest.TestCase, metaclass=ABCMeta):
    """
    Superclass for tests that require a GitLab project.

    Lazily starts GitLab when required.
    """
    @property
    def gitlab_service(self) -> DockerisedServiceWithUsers:
        self._start_if_not_started()
        return self._gitlab_service

    @property
    def gitlab_location(self) -> str:
        self._start_if_not_started()
        return self._gitlab_location

    @property
    def gitlab(self) -> Gitlab:
        self._start_if_not_started()
        return self._gitlab

    @property
    def project(self) -> Project:
        self._start_if_not_started()
        return self._project

    @property
    def project_name(self) -> str:
        self._start_if_not_started()
        return self._project_name

    @property
    def manager(self) -> ProjectVariablesManager:
        self._start_if_not_started()
        return self._manager

    def setUp(self):
        self._gitlab_controller = GitLab8_16_6_ce_0ServiceController()
        self._gitlab_service = None
        self._gitlab_location = None
        self._gitlab = None
        self._project = None
        self._project_name = None
        self._manager = None
        self._start_lock = Lock()
        self._started = False

    def tearDown(self):
        if self._gitlab_service is not None:
            self._gitlab_controller.stop_service(self._gitlab_service)

    def _start(self):
        """
        Starts up GitLab and creates a project.
        """
        self._gitlab_service = self._gitlab_controller.start_service()

        self._gitlab_location = f"http://{self._gitlab_service.host}:{self._gitlab_service.ports[_GITLAB_PORT]}"
        self._gitlab = Gitlab(url=self._gitlab_location, email=self._gitlab_service.root_user.username,
                             password=self._gitlab_service.root_user.password)
        self._gitlab.auth()

        self._project = self._gitlab.projects.create({"name": EXAMPLE_PROJECT_NAME})
        self._project_name = f"{self._gitlab_service.root_user.username}/{EXAMPLE_PROJECT_NAME}"

        gitlab_config = GitLabConfig(self._gitlab_location, self._gitlab.private_token)
        self._manager = ProjectVariablesManager(gitlab_config, self._project_name)

    def _start_if_not_started(self):
        """
        Starts up GitLab if not yet started.
        """
        if not self._started:
            with self._start_lock:
                if not self._started:
                    self._start()
                    self._started = True
