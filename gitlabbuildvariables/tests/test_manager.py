import unittest

from gitlabbuildvariables.tests._common import EXAMPLE_VARIABLES_1, EXAMPLE_VARIABLES_2, \
    add_variables_to_project, convert_projects_variables_to_dicts, TestWithGitLabProject


class TestProjectVariablesManager(TestWithGitLabProject):
    """
    Tests for `ProjectVariablesManager`.
    """
    def test_get(self):
        assert len(self.project.variables.list()) == 0
        add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        self.assertEqual(EXAMPLE_VARIABLES_1, self.manager.get())

    def test_get_when_many_variables(self):
        variables = {str(i): str(i) for i in range(100)}
        add_variables_to_project(variables, self.project)
        self.assertEqual(variables, self.manager.get())

    def test_clear(self):
        add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        self.manager.clear()
        self.assertEqual(0, len(self.project.variables.list()))

    def test_clear_when_many_variables(self):
        variables = {str(i): str(i) for i in range(100)}
        add_variables_to_project(variables, self.project)
        self.manager.clear()
        self.assertEqual(0, len(self.project.variables.list()))

    def test_remove_by_key(self):
        add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        to_delete = list(EXAMPLE_VARIABLES_1.keys())[:1]
        kept = {key: EXAMPLE_VARIABLES_1[key] for key in list(EXAMPLE_VARIABLES_1.keys())[1:]}
        self.manager.remove(to_delete)
        self.assertEqual(kept, convert_projects_variables_to_dicts(self.project.variables.list()))

    def test_remove(self):
        add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        to_delete = {key: EXAMPLE_VARIABLES_1[key] for key in list(EXAMPLE_VARIABLES_1.keys())[:1]}
        kept = {key: EXAMPLE_VARIABLES_1[key] for key in list(EXAMPLE_VARIABLES_1.keys())[1:]}
        self.manager.remove(to_delete)
        self.assertEqual(kept, convert_projects_variables_to_dicts(self.project.variables.list()))

    def test_set(self):
        add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        self.manager.set(EXAMPLE_VARIABLES_2)
        self.assertEqual(EXAMPLE_VARIABLES_2,
                         convert_projects_variables_to_dicts(self.project.variables.list()))

    def test_set_as_same(self):
        add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        self.manager.set(EXAMPLE_VARIABLES_1)
        self.assertEqual(EXAMPLE_VARIABLES_1,
                         convert_projects_variables_to_dicts(self.project.variables.list()))

    def test_set_with_updated_values(self):
        variables = {str(i): str(i) for i in range(10)}
        add_variables_to_project(variables, self.project)
        updated_variables = {key: str(int(value) + 1) for key, value in variables.items()}
        self.manager.set(updated_variables)
        self.assertEqual(updated_variables,
                         convert_projects_variables_to_dicts(self.project.variables.list()))

    def test_add_no_overwrite(self):
        add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        variables = {**EXAMPLE_VARIABLES_2, list(EXAMPLE_VARIABLES_1.keys())[0]: "this_value_should_not_be_set"}
        self.manager.add(variables, overwrite=False)
        self.assertEqual({**EXAMPLE_VARIABLES_2, **EXAMPLE_VARIABLES_1},
                         convert_projects_variables_to_dicts(self.project.variables.list()))

    def test_add_with_overwrite(self):
        add_variables_to_project(EXAMPLE_VARIABLES_1, self.project)
        variables = {**EXAMPLE_VARIABLES_2, list(EXAMPLE_VARIABLES_1.keys())[0]: "this_value_should_be_set"}
        self.manager.add(variables, overwrite=True)
        self.assertEqual({**EXAMPLE_VARIABLES_1, **variables},
                         convert_projects_variables_to_dicts(self.project.variables.list()))


if __name__ == "__main__":
    unittest.main()
