import json
import os
import unittest

from hgicommon.managers import TempManager
from typing import Dict, List

import gitlabbuildvariables.executables.gitlab_update_variables
from gitlabbuildvariables.tests._common import EXAMPLE_VARIABLES_1, convert_projects_variables_to_dicts, \
    EXAMPLE_VARIABLES_2
from gitlabbuildvariables.tests.executables._common import execute, TestExecutable

_GROUP_1 = ("example-1.json", EXAMPLE_VARIABLES_1)
_GROUP_2 = ("example-2.data", EXAMPLE_VARIABLES_2)


class TestGitLabUpdateVariablesExecutable(TestExecutable):
    """
    Tests for the `gitlab-update-variables` executable.
    """
    @property
    def executable(self) -> str:
        return gitlabbuildvariables.executables.gitlab_update_variables.__file__

    def setUp(self):
        super().setUp()
        self._temp_manager = TempManager()

    def tearDown(self):
        super().tearDown()
        self._temp_manager.tear_down()

    def test_update_single_project(self):
        settings_repository = self._create_settings_repository(dict([_GROUP_1, _GROUP_2]))
        config_file = self._create_config_file({self.project.path_with_namespace: [_GROUP_1[0], _GROUP_2[0]]})

        result = execute([self.executable, "--token", self.gitlab.private_token, "--url", self.gitlab_location,
                          "--setting-repository", settings_repository, "--", config_file])

        self.assertEqual(0, result.exit_code)
        self.assertEqual({**_GROUP_1[1], **_GROUP_2[1]},
                         convert_projects_variables_to_dicts(self.project.variables.list()))

    def test_update_multiple_projects(self):
        project_1 = self.project
        project_2 = self.create_project()

        settings_repository = self._create_settings_repository(dict([_GROUP_1, _GROUP_2]))
        config_file = self._create_config_file({
            project_1.path_with_namespace: [_GROUP_1[0]],
            project_2.path_with_namespace: [_GROUP_2[0]]
        })
        result = execute([self.executable, "--token", self.gitlab.private_token, "--url", self.gitlab_location,
                          "--setting-repository", settings_repository, "--", config_file])

        self.assertEqual(0, result.exit_code)
        self.assertEqual(_GROUP_1[1], convert_projects_variables_to_dicts(project_1.variables.list()))
        self.assertEqual(_GROUP_2[1], convert_projects_variables_to_dicts(project_2.variables.list()))

    def test_update_with_default_setting_extension(self):
        assert "." in _GROUP_1[0] and "." in _GROUP_2[0]
        settings_repository = self._create_settings_repository(dict([_GROUP_1, _GROUP_2]))
        group_names = [_GROUP_1[0], _GROUP_2[0]]
        config_file = self._create_config_file({
            self.project.path_with_namespace: [name.split(".")[0] for name in group_names]
        })
        extensions = [name.split(".")[1] for name in group_names]

        result = execute([self.executable, "--token", self.gitlab.private_token, "--url", self.gitlab_location,
                          "--setting-repository", settings_repository, "--default-setting-extension", *extensions, "--",
                          config_file])

        self.assertEqual(0, result.exit_code)
        self.assertEqual({**_GROUP_1[1], **_GROUP_2[1]},
                         convert_projects_variables_to_dicts(self.project.variables.list()))

    def _create_settings_repository(self, setting_groups: Dict[str, Dict[str, str]]) -> str:
        """
        Creates a setting repository with the given setting groups.
        :param setting_groups: setting groups where they key is the name of the group file and the value is the file's
        contents
        :return: the location of the created settings repository
        """
        directory = self._temp_manager.create_temp_directory()
        for file_name, contents in setting_groups.items():
            with open(os.path.join(directory, file_name), "w") as file:
                file.write(json.dumps(contents))
        return directory

    def _create_config_file(self, configuration: Dict[str, List[str]]) -> str:
        """
        Creates a projects' groups configuration file.
        :param configuration: project configurations where they key is the name of the project and the list is the group
        configurations
        :return: the location of the created config file
        """
        _, temp_file =  self._temp_manager.create_temp_file()
        with open(temp_file, "w") as file:
            file.write(json.dumps(configuration))
        return temp_file


del TestExecutable


if __name__ == "__main__":
    unittest.main()
