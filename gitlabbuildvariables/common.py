class GitLabConfig:
    """
    TODO
    """
    def __init__(self, location: str, token: str):
        """
        Constructor.
        :param location: the URL for GitLab (must be HTTPS to avoid
        https://github.com/gpocentek/python-gitlab/issues/218)
        :param token: GitLab access token
        """
        self.location = location
        self.token = token