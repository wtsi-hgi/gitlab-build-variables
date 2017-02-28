import unittest
import uuid
from abc import ABCMeta, abstractmethod
from threading import Lock

import atexit
from gitlab import Project, ProjectVariable, Gitlab
from typing import Dict, Iterable
from useintest.models import DockerisedServiceWithUsers
from useintest.predefined.gitlab import GitLab8_16_6_ce_0ServiceController

from gitlabbuildvariables.common import GitLabConfig
from gitlabbuildvariables.manager import ProjectVariablesManager

_GITLAB_PORT = 80

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


class _LazyService(metaclass=ABCMeta):
    """
    A service that starts opnly when asked to.
    """
    @abstractmethod
    def _start(self):
        """
        Starts the service.
        """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._start_lock = Lock()
        self._started = False

    def start_if_not_started(self):
        """
        Starts up GitLab if not yet started.
        """
        if not self._started:
            with self._start_lock:
                if not self._started:
                    self._start()
                    self._started = True


class _GitLabService(_LazyService):
    @property
    def gitlab_location(self) -> str:
        self.start_if_not_started()
        return self._gitlab_location

    @property
    def gitlab(self) -> Gitlab:
        self.start_if_not_started()
        return self._gitlab

    def __init__(self):
        super().__init__()
        self._gitlab_controller = GitLab8_16_6_ce_0ServiceController()
        self._gitlab_service = None
        self._gitlab_location = None
        self._gitlab = None
        atexit.register(self.tear_down)

    def tear_down(self):
        if self._gitlab is not None:
            self._gitlab_controller.stop_service(self._gitlab_service)

    def _start(self):
        self._gitlab_service = self._gitlab_controller.start_service()
        self._gitlab_location = f"http://{self._gitlab_service.host}:{self._gitlab_service.ports[_GITLAB_PORT]}"
        self._gitlab = Gitlab(url=self._gitlab_location, email=self._gitlab_service.root_user.username,
                             password=self._gitlab_service.root_user.password)
        self._gitlab.auth()


class TestWithGitLabProject(_LazyService, unittest.TestCase, metaclass=ABCMeta):
    """
    Superclass for tests that require a GitLab project.

    Lazily starts GitLab when required.
    """
    _SHARED_GITLAB_SERVICE = _GitLabService()

    @property
    def gitlab(self) -> Gitlab:
        self.start_if_not_started()
        return self._gitlab_service.gitlab

    @property
    def gitlab_location(self) -> str:
        self.start_if_not_started()
        return self._gitlab_service.gitlab_location

    @property
    def project(self) -> Project:
        self.start_if_not_started()
        return self._project

    @property
    def project_name(self) -> str:
        self.start_if_not_started()
        return self._project_name

    @property
    def manager(self) -> ProjectVariablesManager:
        self.start_if_not_started()
        return self._manager

    def setUp(self):
        self._gitlab_service = TestWithGitLabProject._SHARED_GITLAB_SERVICE
        self._project = None
        self._project_name = None
        self._manager = None

    def tearDown(self):
        if self._project is not None:
            self.gitlab.projects.delete(self.project.id)

    def _start(self):
        """
        Starts up GitLab and creates a project.
        """
        gitlab = self._gitlab_service.gitlab
        project_name = str(uuid.uuid4())

        self._project = gitlab.projects.create({"name": project_name})
        self._project_name = f"{gitlab.user.username}/{project_name}"

        gitlab_config = GitLabConfig(self._gitlab_service.gitlab_location, gitlab.private_token)
        self._manager = ProjectVariablesManager(gitlab_config, self._project_name)
