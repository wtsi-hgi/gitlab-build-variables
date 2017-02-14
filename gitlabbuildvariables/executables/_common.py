from argparse import ArgumentParser


class RunConfig:
    """
    Run configuration for use against GitLab.
    """
    def __init__(self, url: str, token: str, project: str):
        self.url = url
        self.token = token
        self.project = project


def add_common_arguments(parser: ArgumentParser):
    """
    Adds common arguments to the given argument parser.
    :param parser: argument parser
    """
    parser.add_argument("--url", type=str, help="Location of GitLab")
    parser.add_argument("--token", type=str, help="GitLab access token")
    parser.add_argument("project", type=str, help="The GitLab project to set the build variables for")
