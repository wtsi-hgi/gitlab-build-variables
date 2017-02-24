import json
import unittest

import gitlabbuildvariables.executables.gitlab_get_variables
from gitlabbuildvariables.tests._common import TestWithGitLabProject, EXAMPLE_VARIABLES_1, add_variables_to_project
from gitlabbuildvariables.tests.executables._common import execute

EXECUTABLE = gitlabbuildvariables.executables.gitlab_get_variables.__file__


class TestGitLabGetVariablesExecutable(TestWithGitLabProject):
    """
    Tests for the `gitlab-get-variables` executable.
    """
    def test_get_help(self):
        result = execute([EXECUTABLE, "-h"])
        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.exit_code)
        self.assertTrue(result.stdout.startswith("usage:"))
        print(result.stdout)

    def test_get_with_missing_credentials(self):
        result = execute([EXECUTABLE])
        self.assertNotEqual("", result.stderr)
        self.assertNotEqual(0, result.exit_code)

    def test_get(self):
        add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        result = execute([EXECUTABLE, "--token", self.gitlab.private_token, "--url", self.gitlab_location,
                          self.project_name])
        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.exit_code)
        self.assertEqual(EXAMPLE_VARIABLES_1, json.loads(result.stdout))


if __name__ == "__main__":
    unittest.main()
