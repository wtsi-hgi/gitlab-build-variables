import unittest

from gitlabbuildvariables.tests._common import EXAMPLE_VARIABLES_1, EXAMPLE_VARIABLES_2, \
    add_variables_to_project, convert_projects_variables_to_dicts, TestWithGitLabProject


class TestProjectVariablesManager(TestWithGitLabProject):
    """
    Tests for `ProjectVariablesManager`.
    """
    def test_get_variables(self):
        assert len(self.project.variables.list()) == 0
        add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        self.assertEqual(EXAMPLE_VARIABLES_1, self.manager.get_variables())

    def test_get_many_variables(self):
        variables = {str(i): str(i) for i in range(100)}
        _add_variables_to_project(variables, self.project)
        self.assertEqual(variables, self.manager.get_variables())

    def test_clear_variables(self):
        add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        self.manager.clear_variables()
        self.assertEqual(0, len(self.project.variables.list()))

    def test_clear_many_variables(self):
        variables = {str(i): str(i) for i in range(100)}
        _add_variables_to_project(variables, self.project)
        self.manager.clear_variables()
        self.assertEqual(0, len(self.project.variables.list()))

    def test_set_variables(self):
        add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        self.manager.set_variables(EXAMPLE_VARIABLES_2)
        self.assertEqual(EXAMPLE_VARIABLES_2,
                         convert_projects_variables_to_dicts(self.project.variables.list()))

    def test_add_variables_no_overwrite(self):
        add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        variables = {**EXAMPLE_VARIABLES_2, list(EXAMPLE_VARIABLES_1.keys())[0]: "this_value_should_not_be_set"}
        self.manager.add_variables(variables, overwrite=False)
        self.assertEqual({**EXAMPLE_VARIABLES_2, **EXAMPLE_VARIABLES_1},
                         convert_projects_variables_to_dicts(self.project.variables.list()))

    def test_add_variables_with_overwrite(self):
        add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        variables = {**EXAMPLE_VARIABLES_2, list(EXAMPLE_VARIABLES_1.keys())[0]: "this_value_should_be_set"}
        self.manager.add_variables(variables, overwrite=True)
        self.assertEqual({**EXAMPLE_VARIABLES_1, **variables},
                         convert_projects_variables_to_dicts(self.project.variables.list()))


if __name__ == "__main__":
    unittest.main()
