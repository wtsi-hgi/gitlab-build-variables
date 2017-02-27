import json
import unittest

import gitlabbuildvariables.executables.gitlab_get_variables
from gitlabbuildvariables.tests._common import EXAMPLE_VARIABLES_1, add_variables_to_project
from gitlabbuildvariables.tests.executables._common import execute, TestExecutable


class TestGitLabGetVariablesExecutable(TestExecutable):
    """
    Tests for the `gitlab-get-variables` executable.
    """
    @property
    def executable(self) -> str:
        return gitlabbuildvariables.executables.gitlab_get_variables.__file__

    def test_get(self):
        add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        result = execute([self.executable, "--token", self.gitlab.private_token, "--url", self.gitlab_location,
                          self.project_name])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(EXAMPLE_VARIABLES_1, json.loads(result.stdout))


del TestExecutable


if __name__ == "__main__":
    unittest.main()
