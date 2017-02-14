from setuptools import setup, find_packages

try:
    from pypandoc import convert
    def read_markdown(file: str) -> str:
        return convert(file, "rst")
except ImportError:
    def read_markdown(file: str) -> str:
        return open(file, "r").read()

setup(
    name="gitlabbuildvariables",
    version="0.1.0",
    packages=find_packages(exclude=["tests"]),
    install_requires=open("requirements.txt", "r").readlines(),
    url="https://github.com/wtsi-hgi/gitlab-build-variables-manager",
    license="GPL3",
    description="Tools for dealing with GitLab CI build variables",
    long_description=read_markdown("README.md"),
    entry_points={
        "console_scripts": [
            "gitlab-set-variables=gitlabbuildvariables.executables.gitlab_set_variables:main",
            "gitlab-get-variables=gitlabbuildvariables.executables.gitlab_get_variables:main"
        ]
    }
)
