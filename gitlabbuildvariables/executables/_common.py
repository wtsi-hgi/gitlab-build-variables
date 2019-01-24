import os

from argparse import ArgumentParser

GITLAB_URL_ENVIRONMENT_VARIABLE = "GITLAB_URL"
GITLAB_TOKEN_ENVIRONMENT_VARIABLE = "GITLAB_TOKEN"


class RunConfig:
    """
    Run configuration for use against GitLab.
    """
    def __init__(self, url: str=None, token: str=None, debug: bool=False):
        self.url = url
        self.token = token
        self.debug = debug


class ProjectRunConfig(RunConfig):
    """
    Run configuration for use against GitLab for a particular project.
    """
    def __init__(self, project: str=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.project = project


def add_common_arguments(parser: ArgumentParser, project: bool=False):
    """
    Adds common arguments to the given argument parser.
    :param parser: argument parser
    :param url: whether the URL named argument should be added
    :param token: whether the access token named argument should be added
    :param project: whether the project positional argument should be added
    """
    parser.add_argument("--url", type=str, help="Location of GitLab")
    parser.add_argument("--token", type=str, help="GitLab access token")
    parser.add_argument("--debug", action="store_true", default=False, help="Turns on debugging")
    if project:
        parser.add_argument("project", type=str, help="The GitLab project to set the build variables for")


def read_configuration_from_environment() -> RunConfig:
    """
    Reads configuration set in the environment.
    :return: configuration read from the environment
    """
    return RunConfig(
        url=os.environ.get(GITLAB_URL_ENVIRONMENT_VARIABLE),
        token=os.environ.get(GITLAB_TOKEN_ENVIRONMENT_VARIABLE))
