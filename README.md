# Poll-In tool

Tool polls / pulls-in ("poll-in") digital objects from a GAMS5 project and performs static site rendering.
Informatics: polling-concept

Meant as replacement for the gams3 "gamsdev" development workflow.

## Basic usage

0. Have a running GAM5-API (OR external)
1. Clone or init project files
2. UV setup


```sh
# 01. Setup project files from templates: https://zimlab.uni-graz.at/gams5/projects/project_template/gams-www
# 01b. Install uv (python package)

# 02. Clone pollin tool
# 02b. uv sync
# 02c. Start virtual environment (venv)

# 03. Configure pollin tool via config file (pollin.toml) in template project folder

# 04. Use pollin tool from venv for development
# (point to project folder with config file)
pollin dev "C:\path\to\project"

# for production use
pollin build "C:\path\to\project"

 

```