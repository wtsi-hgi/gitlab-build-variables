import os
from subprocess import run, PIPE

from typing import List

_ROOT_DIRECTORY = os.path.abspath(os.path.dirname(os.path.join(os.path.abspath(__file__), "../../../../..")))
_ENCODING = "UTF-8"


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
