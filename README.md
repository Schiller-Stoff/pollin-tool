# Poll-In tool

CLI tool that polls / pulls-in ("poll-in") digital objects from a GAMS5 project and performs static site rendering.
(Informatics: polling-concept)
Supplies a development workflow for GAMS5-based web projects.

Meant as replacement for the gams3 "gamsdev" development workflow.

## Quickstart

```sh

# optionally specifiy version tag
uv tool install pollin-tool

# use 
pollin dev "C:\path\to\project"

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

# 02b. Clone pollin-tool
# 02b. uv sync (uv procedure)
# 02b. Start virtual environment (venv)

# 03. Configure pollin tool via config file (pollin.toml) in template project folder

# (point to project folder with config file)
pollin dev "C:\path\to\project"

# for production use
pollin build "C:\path\to\project"

```

### Staging

```sh
pollin stage "/path/to/project"

```


### Production

```sh
# use build command to generate the production files
pollin build "/path/to/project"

```


### Deployment

- use the -d flag to deploy to staging or production environment

```sh
# staging deployment
pollin stage "/path/to/project" -d

# production deployment
pollin build "/path/to/project" -d


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