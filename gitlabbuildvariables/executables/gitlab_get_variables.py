import argparse
import json
import sys
from pprint import pprint
from typing import List

from gitlabbuildvariables.executables._common import RunConfig, add_common_arguments
from gitlabbuildvariables.manager import ProjectBuildVariablesManager


def _parse_args(args: List[str]) -> RunConfig:
    """
    Parses the given CLI arguments to get a run configuration.
    :param args: CLI arguments
    :return: run configuration derived from the given CLI arguments
    """
    parser = argparse.ArgumentParser(prog="gitlab-get-variables", description="Tool for getting a GitLab project's "
                                                                              "build variables")
    add_common_arguments(parser)
    arguments = parser.parse_args(args)
    return RunConfig(arguments.url, arguments.token, arguments.project)


def main():
    """
    Main method.
    """
    run_config = _parse_args(sys.argv[1:])
    manager = ProjectBuildVariablesManager(run_config.url, run_config.token, run_config.project)
    output = json.dumps(manager.get_variables(), sort_keys=True, indent=4, separators=(",", ": "))
    print(output)


if __name__ == "__main__":
    main()
