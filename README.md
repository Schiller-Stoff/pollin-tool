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

# 2. install gams_frog via 
# optionally specifiy version tag
uv tool install gams_frog

# verify installation via
frog --version

# 3. use the gams_frog
cd ./my/working/directory
frog dev # will use the gams_frog.toml from the current working dir
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

# 02b. Clone gams_frog
# 02b. uv sync (uv procedure)
# 02b. Start virtual environment (venv)

# 03. Configure gams_frog via config file (gams_frog.toml) in template project folder

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

## Dev server API proxy
 
During `frog dev`, the dev server acts as a same-origin proxy for the GAMS5 API.
This eliminates CORS friction: the browser sees one origin (the dev server), and
gams-frog transparently forwards `/api/*` requests to the real upstream configured in
`gams-frog.toml`.
 
### What this means for templates
 
Nothing changes. Templates continue to use `{{ env.GAMS_API_ORIGIN }}` to build
API URLs exactly as before. In dev mode, gams-frog rewrites that value to point at
the local dev server; in build/stage, it stays as the configured upstream.
 
```html
<!-- Works in dev, stage, and build — no conditional logic needed -->
<script>
  fetch('{{ context.env.GAMS_API_ORIGIN }}/api/v1/projects/{{ context.env.PROJECT_ABBR }}/objects')
    .then(r => r.json())
    .then(data => { /* ... */ });
</script>
```
 
### Semantic shift of `[dev].GAMS_API_ORIGIN`
 
The value of `[dev].GAMS_API_ORIGIN` in `gams-frog.toml` is now the **upstream the
proxy forwards to** — not what templates see. Existing `gams-frog.toml` files work
unchanged; only the mental model shifts.
 
```toml
[dev]
# The dev proxy forwards /api/* here. Templates see http://localhost:<port> instead.
GAMS_API_ORIGIN = "https://gams-staging.uni-graz.at"
IIIF_IMAGE_SERVER_ORIGIN = "https://gams-staging.uni-graz.at"
```
 
### Scope (intentional)
 
- **GET only.** Non-GET methods return `405 Allow: GET`. This is a forcing
  function: if templates ever need authenticated / state-changing requests, that
  requires an explicit design decision (cookie rewriting, CSRF handling, Keycloak
  login flow) — not a silent extension.
- **No cookie forwarding, no auth passthrough.** Works for unauthenticated reads
  of published project data (objects, datastreams, DC, SEARCH.json). If the
  upstream requires auth, requests fail with the upstream's 401/403.
- **Dev mode only.** `build` and `stage` are unaffected. Deployed gams-frog sites
  live on the same origin as the GAMS API (`gams.uni-graz.at/pub/<project>/`),
  so production never needs a proxy.
- 
### When things break
 
- **502 from frog dev with "GAMS_FROG PROXY ERROR"**: upstream unreachable. Check
  that the configured `[dev].GAMS_API_ORIGIN` is correct and the server is up.
- **405 from frog dev on an API call**: a template is issuing a non-GET
  request. By design; see scope above.
- **401/403 from frog dev on an API call**: the upstream requires authentication
  for that endpoint. The dev proxy doesn't forward credentials.


## Development

### Release

1. Increment version in pyproject.toml in feature branch (merging into develop):
    - make sure version follow vd.d.d pattern 
2. Merge changes to develop -> main
3. Create release on the gitlab webclient (from main branch) with new git tag that must be the same as in the pyproject.toml!
    - e.g. v0.1.1
    - create the release from the main branch!
    - gitlab will autodeploy the new version to pypi