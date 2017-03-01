[![Build Status](https://travis-ci.org/wtsi-hgi/gitlab-build-variables-manager.svg)](https://travis-ci.org/wtsi-hgi/gitlab-build-variables-manager)
[![codecov.io](https://codecov.io/gh/wtsi-hgi/gitlab-build-variables-manager/graph/badge.svg)](https://codecov.io/github/wtsi-hgi/gitlab-build-variables-manager)

# GitLab Build Variables
_Tools for dealing with GitLab CI pipeline build variables._


## Tools
### Managing Multiple Projects
### Updating GitLab Build Variables
Sets project build variables based on a configuration file:
```bash
gitlab-update-variables --url ${gitlabUrl} --token ${accessToken} --default-setting-extension ${extensions} \
    --setting-repository ${repositoryDirectories} -- ${configLocation}
```
_[See Example 1](#example-1) for a more intuitive example of how to use this tool!_

### Managing a Single Project
#### Setting a GitLab Build Variables
This tool allows a GitLab CI project's build variables to be set from a ini config file, a JSON file or a shell script 
that just exports variables:
```bash
gitlab-set-variables --url ${gitlabUrl} --token ${accessToken} ${project} ${locationOfVariables}
```

#### Getting GitLab Build Variables
```bash
gitlab-get-variables --url ${gitlabUrl} --token ${accessToken} ${project}
```


## Examples
### Example 1
Using the [example configuration](examples/config.json) to update the variables for a number of projects:
```bash
$ export gitlabUrl=https://gitlab.example.com 
$ export accessToken=personalAccessToken

$ gitlab-get-variables --url ${gitlabUrl} --token ${accessToken} cn13/my-project-1
{'VALUE_1': 'other'}

$ gitlab-get-variables --url ${gitlabUrl} --token ${accessToken} cn13/my-project-2
{}

$ gitlab-update-variables --url ${gitlabUrl} --token ${accessToken} --default-setting-extension json ini sh \
    --setting-repository examples/settings -- examples/config.json
Read config from "examples/config.json"
Set variables for "cn13/my-project-1": {'VALUE_1': 'abc', 'VALUE_2': 'other', 'VALUE_3': 'other'}
Set variables for "cn13/my-project-2": {'VALUE_1': 'abc', 'VALUE_2': 'other', 'VALUE_3': 'ghi'}
```

### Example 2
Using the settings defined in [the example directory](examples/settings) to update a project's variables:
```bash
$ export gitlabUrl=https://gitlab.internal.example.com 
$ export accessToken=applicationAccessToken

$ gitlab-get-variables --url ${gitlabUrl} --token ${accessToken} my-project
{'VALUE_1': 'other'}

$ gitlab-set-variables --url ${gitlabUrl} --token ${accessToken} group/my-project common.json s3.sh project.ini  
Variables for project "my-project" set to: {'VALUE_1': 'abc', 'VALUE_2': 'def', 'VALUE_3': 'ghi'}
```
