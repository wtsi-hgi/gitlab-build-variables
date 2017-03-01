from dictdiffer import DictDiffer
from gitlab import Gitlab, GitlabGetError
from typing import Dict, Iterable, List, Union

from gitlabbuildvariables.common import GitLabConfig

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


class ProjectVariablesManager:
    """
    Manages the build variables used by a project.
    """
    def __init__(self, gitlab_config: GitLabConfig, project: str):
        """
        Constructor.
        :param gitlab_config: configuration to access GitLab
        :param project: the project of interest (preferably namespaced, e.g. "hgi/my-project")
        """
        self._connector = Gitlab(gitlab_config.location, gitlab_config.token, ssl_verify=SSL_VERIFY)
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
        variables = self._project.variables.list(all=True)
        return {variable.key: variable.value for variable in variables}

    def clear_variables(self):
        """
        Clears all of the build variables.
        """
        for variable in self._project.variables.list(all=True):
            variable.delete()

    def remove_variables(self, variables: Union[Iterable[str], Dict[str, str]]=None):
        """
        Removes the given variables. Will only remove a key if it has the given value if the value has been defined.
        :param variables: the variables to remove
        """
        keys = list(variables.keys()) if isinstance(variables, Dict) else variables     # type: Iterable[str]
        for key in keys:
            variable = self._project.variables.get(key)
            if isinstance(variables, Dict):
                if variables[key] != variable.value:
                    continue
            variable.delete()

    def set_variables(self, variables: Dict[str, str]):
        """
        Sets the build variables (i.e. removes old ones, adds new ones)
        :param variables: the build variables to set
        """
        current_variables = self.get_variables()
        difference = DictDiffer(variables, current_variables)

        removed_keys = difference.removed()
        self.remove_variables(removed_keys)

        changed_keys = difference.added() | difference.changed()
        changed = {key: variables[key] for key in changed_keys}
        self.add_variables(changed, overwrite=True)

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
