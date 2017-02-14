import argparse
import sys
from typing import List

from gitlabbuildvariables.executables._common import add_common_arguments, RunConfig
from gitlabbuildvariables.manager import ProjectBuildVariablesManager
from gitlabbuildvariables.reader import read_variables


class _SetArgumentsRunConfig(RunConfig):
    """
    Run configuration for setting arguments.
    """
    def __init__(self, source: str, project: str, url: str, token: str):
        super().__init__(url, token, project)
        self.source = source


def _parse_args(args: List[str]) -> _SetArgumentsRunConfig:
    """
    Parses the given CLI arguments to get a run configuration.
    :param args: CLI arguments
    :return: run configuration derived from the given CLI arguments
    """
    parser = argparse.ArgumentParser(
        prog="gitlab-set-variables", description="Tool for setting a GitLab project's build variables")
    parser.add_argument("source", type=str, help="File to source build variables from. Can be a ini file or a shell "
                                                 "script containing 'export' statements")
    add_common_arguments(parser)

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
