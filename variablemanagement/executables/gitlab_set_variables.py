import argparse
import sys
from typing import List

from variablemanagement.manager import ProjectBuildVariablesManager
from variablemanagement.reader import read_variables


class _SetArgumentsRunConfig:
    """
    Run configuration for setting arguments.
    """
    def __init__(self, source: str, project: str, url: str, token: str):
        self.source = source
        self.project = project
        self.url = url
        self.token = token


def _parse_args(args: List[str]) -> _SetArgumentsRunConfig:
    """
    Parses the given CLI arguments to get a run configuration.
    :param args: CLI arguments
    :return: run configuration derived from the given CLI arguments
    """
    parser = argparse.ArgumentParser(
        prog="gitlab-set-variables", description="Tool for setting a GitLab project's build variables")
    parser.add_argument("source", type=str,
                        help="File to source build variables from. Can be a ini file or a shell script containing "
                             "'export' statements")
    parser.add_argument("project", type=str, help="The GitLab project to set the build variables for")
    parser.add_argument("--url", type=str, help="Location of GitLab")
    parser.add_argument("--token", type=str, help="GitLab access token")

    arguments = parser.parse_args(args)
    return _SetArgumentsRunConfig(arguments.source, arguments.project, arguments.url, arguments.token)


def main(run_config: _SetArgumentsRunConfig):
    """
    Main method.
    :param run_config: the run configuration
    """
    manager = ProjectBuildVariablesManager(run_config.url, run_config.token, run_config.project)
    variables = read_variables(run_config.source)
    manager.set_variables(variables)
    print("Variables for project \"%s\" set to: %s" % (run_config.project, manager.get_variables()))


if __name__ == "__main__":
    config = _parse_args(sys.argv[1:])
    main(config)
