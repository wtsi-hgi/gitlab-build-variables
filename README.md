# GitLab Build Variables
_Tools for dealing with GitLab CI build variables._


## Tools
### Managing Multiple Projects
### Updating GitLab Build Variables
With a
- Projects configuration file.
- Collection of files containing variable settings.
```bash
gitlab-update-variables --url ${gitlab_url} --token ${access_token} ${project} ${location_of_variables}
```

### Managing a Single Project
#### Setting a GitLab Build Variables
This tool allows a GitLab CI project's build variables to be set from a ini config file, a JSON file or a shell script 
that just exports variables:
```bash
gitlab-set-variables --url ${gitlab_url} --token ${access_token} ${project} ${location_of_variables}
```

#### Getting GitLab Build Variables
```bash
gitlab-get-variables --url ${gitlab_url} --token ${access_token} ${project}
```


## Examples
### Example 1
Using the settings defined in [the example directory](examples/settings) to update a project's variables:
```bash
$ gitlab-get-variables --url ${gitlab_url} --token ${access_token} my-project
{'VALUE_1': 'other'}

$ gitlab-set-variables --url ${gitlab_url} --token ${access_token} group/my-project common.json group.sh project.ini  
Variables for project "my-project" set to: {'VALUE_1': 'abc', 'VALUE_2': 'def', 'VALUE_3': 'ghi'}
```

### Example 2
Using the configuration defined in [the example directory](examples/config.json) to update the variables for a number 
of projects:
```bash
$ gitlab-get-variables --url ${gitlab_url} --token ${access_token} cn13/my-project-1
{'VALUE_1': 'other'}

$ gitlab-get-variables --url ${gitlab_url} --token ${access_token} cn13/my-project-2
{}

$ gitlab-update-variables --url ${gitlab_url} --token ${access_token} --default-setting-extension json ini sh \
    --setting-repository examples/settings examples/config.json
Read config from "examples/config.json"
Set variables for "cn13/my-project-1": {'VALUE_1': 'abc', 'VALUE_2': 'other', 'VALUE_3': 'other'}
Set variables for "cn13/my-project-2": {'VALUE_1': 'abc', 'VALUE_2': 'other', 'VALUE_3': 'ghi'}
```


