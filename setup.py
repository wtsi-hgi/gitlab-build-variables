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
    author="Colin Nolan",
    author_email="colin.nolan@sanger.ac.uk",
    version="1.1.0",
    packages=find_packages(exclude=["tests"]),
    install_requires=open("requirements.txt", "r").readlines(),
    url="https://github.com/wtsi-hgi/gitlab-build-variables",
    license="GPL3",
    description="Tools for dealing with GitLab CI build variables",
    long_description=read_markdown("README.md"),
    entry_points={
        "console_scripts": [
            "gitlab-set-variables=gitlabbuildvariables.executables.gitlab_set_variables:main",
            "gitlab-get-variables=gitlabbuildvariables.executables.gitlab_get_variables:main",
            "gitlab-update-variables=gitlabbuildvariables.executables.gitlab_update_variables:main"
        ]
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ]
)
