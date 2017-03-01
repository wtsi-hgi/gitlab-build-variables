import argparse
import sys

from typing import List, Dict

from gitlabbuildvariables.common import GitLabConfig
from gitlabbuildvariables.executables._common import add_common_arguments, ProjectRunConfig
from gitlabbuildvariables.manager import ProjectVariablesManager
from gitlabbuildvariables.reader import read_variables


class _SetArgumentsRunConfig(ProjectRunConfig):
    """
    Run configuration for setting arguments.
    """
    def __init__(self, source: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source = source


def _parse_args(args: List[str]) -> _SetArgumentsRunConfig:
    """
    Parses the given CLI arguments to get a run configuration.
    :param args: CLI arguments
    :return: run configuration derived from the given CLI arguments
    """
    parser = argparse.ArgumentParser(
        prog="gitlab-set-variables", description="Tool for setting a GitLab project's build variables")
    add_common_arguments(parser, project=True)
    parser.add_argument("source", nargs="+", type=str,
                        help="File to source build variables from. Can be a ini file, JSON file or a shell script "
                             "containing 'export' statements")

    arguments = parser.parse_args(args)
    return _SetArgumentsRunConfig(arguments.source, arguments.project, arguments.url, arguments.token, arguments.debug)


def main():
    """
    Main method.
    """
    run_config = _parse_args(sys.argv[1:])
    gitlab_config = GitLabConfig(run_config.url, run_config.token)
    manager = ProjectVariablesManager(gitlab_config, run_config.project)
    variables = {}  # type: Dict[str, str]
    for source in run_config.source:
        variables.update(read_variables(source))
    manager.set(variables)
    print("Variables for project \"%s\" set to: %s" % (run_config.project, manager.get()))


if __name__ == "__main__":
    main()
