import unittest
from typing import Dict, Iterable

from gitlab import Gitlab, Project, ProjectVariable
from useintest.predefined.gitlab import GitLab8_16_6_ce_0ServiceController

from gitlabbuildvariables.common import GitLabConfig
from gitlabbuildvariables.manager import ProjectVariablesManager

EXAMPLE_PROJECT_NAME = "my-project"
EXAMPLE_VARIABLES_1 = {"thisKey": "thatValue", "otherKey": "otherValue"}
EXAMPLE_VARIABLES_2 = {"a": "b", "c": "d"}


def _add_variables_to_project(variables: Dict[str, str], project: Project):
    """
    Adds the given build variables to the given GitLab project.
    :param variables: variables to add
    :param project: project to add variables to
    """
    for key, value in variables.items():
        project.variables.create({"key": key, "value": value})


def _convert_projects_variables_to_dicts(project_variables: Iterable[ProjectVariable]) -> Dict[str, str]:
    """
    Converts the GitLab's library project variable models to a dictionary representation.
    :param project_variables: the project variable models
    :return: the dicitionary representation
    """
    return {variable.key: variable.value for variable in project_variables}


class TestProjectVariablesManager(unittest.TestCase):
    """
    Tests for `ProjectVariablesManager`.
    """
    def setUp(self):
        self._gitlab_controller = GitLab8_16_6_ce_0ServiceController()
        self.gitlab_service = self._gitlab_controller.start_service()

        gitlab_location = f"http://{self.gitlab_service.host}:{self.gitlab_service.ports[80]}"
        self.gitlab = Gitlab(url=gitlab_location, email=self.gitlab_service.root_user.username,
                             password=self.gitlab_service.root_user.password)
        self.gitlab.auth()
        self.project = self.gitlab.projects.create({"name": EXAMPLE_PROJECT_NAME})

        gitlab_config = GitLabConfig(gitlab_location, self.gitlab.private_token)
        self.manager = ProjectVariablesManager(
            gitlab_config, f"{self.gitlab_service.root_user.username}/{EXAMPLE_PROJECT_NAME}")

    def tearDown(self):
        self._gitlab_controller.stop_service(self.gitlab_service)

    def test_get_variables(self):
        assert len(self.project.variables.list()) == 0
        _add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        self.assertEqual(EXAMPLE_VARIABLES_1, self.manager.get_variables())

    def test_get_many_variables(self):
        variables = {i: str(i) for i in range(100)}
        _add_variables_to_project(variables, self.project)
        self.assertEqual(variables, self.manager.get_variables())

    def test_clear_variables(self):
        _add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        self.manager.clear_variables()
        self.assertEqual(0, len(self.project.variables.list()))

    def test_clear_many_variables(self):
        variables = {i: str(i) for i in range(100)}
        _add_variables_to_project(variables, self.project)
        self.manager.clear_variables()
        self.assertEqual(0, len(self.project.variables.list()))

    def test_set_variables(self):
        _add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        self.manager.set_variables(EXAMPLE_VARIABLES_2)
        self.assertEqual(EXAMPLE_VARIABLES_2,
                         _convert_projects_variables_to_dicts(self.project.variables.list()))

    def test_add_variables_no_overwrite(self):
        _add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        variables = {**EXAMPLE_VARIABLES_2, list(EXAMPLE_VARIABLES_1.keys())[0]: "this_value_should_not_be_set"}
        self.manager.add_variables(variables, overwrite=False)
        self.assertEqual({**EXAMPLE_VARIABLES_2, **EXAMPLE_VARIABLES_1},
                         _convert_projects_variables_to_dicts(self.project.variables.list()))

    def test_add_variables_with_overwrite(self):
        _add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        variables = {**EXAMPLE_VARIABLES_2, list(EXAMPLE_VARIABLES_1.keys())[0]: "this_value_should_be_set"}
        self.manager.add_variables(variables, overwrite=True)
        self.assertEqual({**EXAMPLE_VARIABLES_1, **variables},
                         _convert_projects_variables_to_dicts(self.project.variables.list()))


if __name__ == "__main__":
    unittest.main()
