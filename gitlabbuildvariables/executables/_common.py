from argparse import ArgumentParser


class RunConfig:
    """
    Run configuration for use against GitLab.
    """
    def __init__(self, url: str, token: str, debug: bool=False):
        self.url = url
        self.token = token
        self.debug = debug


class ProjectRunConfig(RunConfig):
    """
    Run configuration for use against GitLab for a particular project.
    """
    def __init__(self, project: str, *args, **kwargs):
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
