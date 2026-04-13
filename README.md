# gams-frog

CLI tool that generates frontends for GAMS5 projects.
Supplies a development workflow for GAMS5-based web projects.

Meant as replacement for the gams3 "gamsdev" development workflow.

## Quickstart

1. Setup project files for gams-frog

2. Install gams-frog itself

```sh

# 1. install uv
# mac might need brew to install uv

# 2. install gams-frog via 
# optionally specifiy version tag
uv tool install gams-frog

# verify installation via
frog --version

# 3. use the gams-frog
cd ./my/working/directory
frog dev # will use the gams-frog.toml from the current working dir
# alternatively specifiy a path
frog dev "C:\path\to\project"
# check for basic commands
frog 

```

## Basic usage

1. Have a running GAM5-API (OR external)
2. Clone or init project files
3. UV setup (install via pypi or clone via git)


```sh
# 01. Setup project files from templates: https://zimlab.uni-graz.at/gams5/projects/project_template/gams-www
# 01b. Install uv (python package)

# 02a. Install via pypi
# 02a. uv install / pip install

# 02b. Clone gams-frog
# 02b. uv sync (uv procedure)
# 02b. Start virtual environment (venv)

# 03. Configure gams-frog via config file (gams-frog.toml) in template project folder

# (point to project folder with config file)
frog dev "C:\path\to\project"

# for production use
frog build "C:\path\to\project"

```

### Staging

```sh
frog stage "/path/to/project"

```


### Production

```sh
# use build command to generate the production files
frog build "/path/to/project"

```


### Deployment

- use the -d flag to deploy to staging or production environment

```sh
# staging deployment
frog stage "/path/to/project" -d

# production deployment
frog build "/path/to/project" -d


```


## Development

### Release

1. Increment version in pyproject.toml in feature branch (merging into develop):
    - make sure version follow vd.d.d pattern 
2. Merge changes to develop -> main
3. Create release on the gitlab webclient (from main branch) with new git tag that must be the same as in the pyproject.toml!
    - e.g. v0.1.1
    - create the release from the main branch!
    - gitlab will autodeploy the new version to pypi