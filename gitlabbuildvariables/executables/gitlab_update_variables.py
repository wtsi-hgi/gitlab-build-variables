import argparse
import logging
import sys
from typing import List

from gitlabbuildvariables.common import GitLabConfig
from gitlabbuildvariables.executables._common import add_common_arguments, RunConfig
from gitlabbuildvariables.updater import ProjectsVariablesUpdater, _logger


class _UpdateArgumentsRunConfig(RunConfig):
    """
    Run configuration for setting arguments.
    """
    def __init__(self, config_location: str, setting_repositories: List[str],
                 default_setting_extensions: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config_location = config_location
        self.setting_repositories = setting_repositories
        self.default_setting_extensions = default_setting_extensions


def _parse_args(args: List[str]) -> _UpdateArgumentsRunConfig:
    """
    Parses the given CLI arguments to get a run configuration.
    :param args: CLI arguments
    :return: run configuration derived from the given CLI arguments
    """
    parser = argparse.ArgumentParser(
        prog="gitlab-update-variables", description="Tool for setting a GitLab project's build variables")
    add_common_arguments(parser)
    parser.add_argument("config_location", type=str, help="Location of the configuration file")
    parser.add_argument("--setting-repository", dest="setting_repository", nargs="+", type=str,
                        help="Directory from which variable settings groups may be sourced")
    parser.add_argument("--default-setting-extension", dest="default_setting_extensions",nargs="+", type=str,
                        help="Extensions to try adding to the variable to source location if it does not exist")

    arguments = parser.parse_args(args)
    return _UpdateArgumentsRunConfig(arguments.config_location, arguments.setting_repository,
                                     arguments.default_setting_extensions, url=arguments.url, token=arguments.token,
                                     debug=arguments.debug)


def main():
    """
    Main method.
    """
    run_config = _parse_args(sys.argv[1:])
    if run_config.debug:
        _logger.setLevel(logging.DEBUG)
    else:
        _logger.setLevel(logging.INFO)
    gitlab_config = GitLabConfig(run_config.url, run_config.token)

    updater = ProjectsVariablesUpdater(run_config.config_location, gitlab_config=gitlab_config,
                                       setting_repositories=run_config.setting_repositories,
                                       default_setting_extensions=run_config.default_setting_extensions)
    updater.update()


if __name__ == "__main__":
    main()
