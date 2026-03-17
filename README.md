# Poll-In tool

CLI tool that polls / pulls-in ("poll-in") digital objects from a GAMS5 project and performs static site rendering.
(Informatics: polling-concept)
Supplies a development workflow for GAMS5-based web projects.

Meant as replacement for the gams3 "gamsdev" development workflow.

## Basic usage

0. Have a running GAM5-API (OR external)
1. Clone or init project files
2. UV setup (install via pypi or clone via git)


```sh
# 01. Setup project files from templates: https://zimlab.uni-graz.at/gams5/projects/project_template/gams-www
# 01b. Install uv (python package)

# 02a. Install via pypi
# 02a. uv install / pip install

# 02b. Clone pollin-tool or install via pypi
# 02b. uv sync
# 02b. Start virtual environment (venv)

# 03. Configure pollin tool via config file (pollin.toml) in template project folder

# (point to project folder with config file)
pollin dev "C:\path\to\project"

# for production use
pollin build "C:\path\to\project"

```

## Staging

```sh
pollin stage "/path/to/project"

```


## Production

```sh
# use build command to generate the production files
pollin build "/path/to/project"

```


## Deployment

- use the -d flag to deploy to staging or production envrionment

```sh
# staging deployment
pollin stage "/path/to/project" -d

# production deployment
pollin build "/path/to/project" -d


```


## Development