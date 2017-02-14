import argparse
import json
import sys
from typing import List

from gitlabbuildvariables.common import GitLabConfig
from gitlabbuildvariables.executables._common import add_common_arguments, ProjectRunConfig
from gitlabbuildvariables.manager import ProjectVariablesManager


def _parse_args(args: List[str]) -> ProjectRunConfig:
    """
    Parses the given CLI arguments to get a run configuration.
    :param args: CLI arguments
    :return: run configuration derived from the given CLI arguments
    """
    parser = argparse.ArgumentParser(prog="gitlab-get-variables", description="Tool for getting a GitLab project's "
                                                                              "build variables")
    add_common_arguments(parser, project=True)
    arguments = parser.parse_args(args)
    return ProjectRunConfig(project=arguments.project, url=arguments.url, token=arguments.token, debug=arguments.debug)


def main():
    """
    Main method.
    """
    run_config = _parse_args(sys.argv[1:])
    gitlab_config = GitLabConfig(run_config.url, run_config.token)
    manager = ProjectVariablesManager(gitlab_config, run_config.project)
    output = json.dumps(manager.get_variables(), sort_keys=True, indent=4, separators=(",", ": "))
    print(output)


if __name__ == "__main__":
    main()
