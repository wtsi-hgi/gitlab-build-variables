import json
import tempfile
import unittest

import gitlabbuildvariables.executables.gitlab_set_variables
from gitlabbuildvariables.tests._common import EXAMPLE_VARIABLES_1, convert_projects_variables_to_dicts
from gitlabbuildvariables.tests.executables._common import execute, TestExecutable


class TestGitLabSetVariablesExecutable(TestExecutable):
    """
    Tests for the `gitlab-set-variables` executable.
    """
    @property
    def executable(self) -> str:
        return gitlabbuildvariables.executables.gitlab_set_variables.__file__

    def test_set_from_json_file(self):
        with tempfile.NamedTemporaryFile("w+") as file:
            file.write(json.dumps(EXAMPLE_VARIABLES_1))
            file.flush()
            result = execute([self.executable, "--token", self.gitlab.private_token, "--url", self.gitlab_location,
                              self.project_name, file.name])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(EXAMPLE_VARIABLES_1, convert_projects_variables_to_dicts(self.project.variables.list()))

    def test_set_from_sh_file(self):
        with tempfile.NamedTemporaryFile("w+") as file:
            exports = "#!/usr/bin/env bash\n#Comments\n./other_command.sh\n"
            exports += "\n".join({f"export {key}={value}" for key, value in EXAMPLE_VARIABLES_1.items()})
            file.write(exports)
            file.flush()
            result = execute([self.executable, "--token", self.gitlab.private_token, "--url", self.gitlab_location,
                              self.project_name, file.name])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(EXAMPLE_VARIABLES_1, convert_projects_variables_to_dicts(self.project.variables.list()))

    def test_set_from_headerless_ini_file(self):
        with tempfile.NamedTemporaryFile("w+") as file:
            config = "\n".join({f"{key}={value}" for key, value in EXAMPLE_VARIABLES_1.items()})
            file.write(config)
            file.flush()
            result = execute([self.executable, "--token", self.gitlab.private_token, "--url", self.gitlab_location,
                              self.project_name, file.name])
        self.assertEqual(0, result.exit_code)
        self.assertEqual(EXAMPLE_VARIABLES_1, convert_projects_variables_to_dicts(self.project.variables.list()))


del TestExecutable


if __name__ == "__main__":
    unittest.main()
