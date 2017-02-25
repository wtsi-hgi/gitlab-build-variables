import os
from abc import ABCMeta, abstractmethod
from subprocess import run, PIPE

from typing import List

from gitlabbuildvariables.tests._common import TestWithGitLabProject

_ROOT_DIRECTORY = os.path.abspath(os.path.dirname(os.path.join(os.path.abspath(__file__), "../../../../..")))
_ENCODING = "UTF-8"


class TestExecutable(TestWithGitLabProject, metaclass=ABCMeta):
    """
    TODO
    """
    @property
    @abstractmethod
    def executable(self) -> str:
        """
        Gets the path to the executable being tested.
        :return: path to the executable
        """

    def test_help(self):
        result = execute([self.executable, "-h"])
        self.assertEqual("", result.stderr)
        self.assertEqual(0, result.exit_code)
        self.assertTrue(result.stdout.startswith("usage:"))
        print(result.stdout)

    def test_when_missing_credentials(self):
        result = execute([self.executable])
        self.assertNotEqual("", result.stderr)
        self.assertNotEqual(0, result.exit_code)


class ExecutionResult:
    """
    Model of a result of executing a program.
    """
    def __init__(self, exit_code: int, stdout: str, stderr):
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr


def execute(arguments: List[str]) -> ExecutionResult:
    """
    Executes the given arguments.
    :param arguments: arguments, where the first element should be the executable's name
    :return: the results
    """
    os.environ["PYTHONPROJECT"] = _ROOT_DIRECTORY
    completed_process = run(["python", *arguments], stdout=PIPE, stderr=PIPE)
    return ExecutionResult(completed_process.returncode, completed_process.stdout.decode(_ENCODING),
                           completed_process.stderr.decode(_ENCODING))
