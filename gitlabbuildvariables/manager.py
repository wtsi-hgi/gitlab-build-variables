from typing import Dict

from gitlab import Gitlab, GitlabGetError

SSL_VERIFY = False

_VARIABLE_KEY_PROPERTY = "key"
_VARIABLE_VALUE_PROPERTY = "value"


if not SSL_VERIFY:
    try:
        import requests
        from requests.packages.urllib3.exceptions import InsecureRequestWarning
        # Silence insecure messages
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    except ImportError:
        pass


class ProjectBuildVariablesManager:
    """
    Manages the build variables used by a project.
    """
    def __init__(self, url: str, token: str, project: str):
        """
        Constructor.
        :param url: the URL for GitLab (must be HTTPS to avoid https://github.com/gpocentek/python-gitlab/issues/218)
        :param token: GitLab access token
        :param project: the project of interest (preferably namespaced, e.g. "hgi/my-project")
        """
        self._connector = Gitlab(url, token, ssl_verify=SSL_VERIFY)
        self._connector.auth()
        try:
            self._project = self._connector.projects.get(project)
        except GitlabGetError as e:
            if "Project Not Found" in e.error_message:
                raise ValueError("Project '%s' not found. Valid projects are: %s"
                                 % (project,
                                    [project.path_with_namespace for project in self._connector.projects.list()]))

    def get_variables(self) -> Dict[str, str]:
        """
        Gets the build variables for the project.
        :return: the build variables
        """
        variables = self._project.variables.list()
        return {variable.key: variable.value for variable in variables}

    def clear_variables(self):
        """
        Clears all of the build variables.
        """
        for variable in self._project.variables.list():
            variable.delete()

    def set_variables(self, variables: Dict[str, str]):
        """
        Sets tje build variables (i.e. removes old ones, adds new ones)
        :param variables: the build variables to set
        """
        self.clear_variables()
        self.add_variables(variables)

    def add_variables(self, variables: Dict[str, str], overwrite: bool=False):
        """
        Adds the given build variables to those that already exist.
        :param variables: the build variables to add
        :param overwrite: whether the old variable should be overwritten in the case of a redefinition
        """
        preset_variables = self._project.variables.list()
        preset_variable_keys = [variable.key for variable in preset_variables]

        for key, value in variables.items():
            if key in preset_variable_keys:
                variable = preset_variables[preset_variable_keys.index(key)]
                if overwrite:
                    variable.value = value
                    variable.save()
            else:
                variable = self._project.variables.create({
                    _VARIABLE_KEY_PROPERTY: key, _VARIABLE_VALUE_PROPERTY: value})
                variable.save()
