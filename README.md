# GitLab Build Variables
_Helper for dealing with GitLab CI build variables._


## Tools
### Setting GitLab Build Variables
This tool allows a GitLab CI project's build variables to be set from a ini config file (or from a shell script that 
just exports variables):
```bash
gitlab-set-variables --url ${gitlab_url} --token ${access_token} ${location_of_variables} ${project}
```

### Getting GitLab Build Variables
```bash
gitlab-get-variables --url ${gitlab_url} --token ${access_token} ${project}
```


## Examples
### Example 1
```bash
$ cat my-variables.ini
VALUE_1=abc
VALUE_2=def
VALUE_3=ghi

$ gitlab-get-variables --url ${gitlab_url} --token ${access_token} my-project
{'VALUE_1': 'other'}

$ gitlab-set-variables --url ${gitlab_url} --token ${access_token} my-variables.ini my-project
Variables for project "my-project" set to: {'VALUE_1': 'abc', 'VALUE_2': 'def', 'VALUE_3': 'ghi'}
```

### Example 2
```bash
$ cat my-variables.sh
#!/usr/bin/env bash
export VALUE_1=abc
export VALUE_2=def
export VALUE_3=ghi

$ gitlab-get-variables --url ${gitlab_url} --token ${access_token} my-project
{'VALUE_1': 'other'}

$ gitlab-set-variables --url ${gitlab_url} --token ${access_token} my-variables.ini my-project
Variables for project "my-project" set to: {'VALUE_1': 'abc', 'VALUE_2': 'def', 'VALUE_3': 'ghi'}
```