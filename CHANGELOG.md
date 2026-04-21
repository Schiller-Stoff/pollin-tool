# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.5.0]

### Changed

- introduced local dev proxy that allows to circumvent CORS when working with the gams-api
- GAMS_API_ORIGIN variable is rewritten internally to use the dev proxy (and not the real gams-staging address - see readme)
- updated README.md

### Added

- gams-frog-build.json in the output of stage and build command: stores metadata about the metadata (e.g. used version of gams-frog)

## [0.4.0]

### Changed

- adopted new /api/curation/v1 api instead of just /api/v1

## [0.3.0]

### Changed

- renamed tool to gams-frog (from pollin-tool)

## [0.0.2] - 13.04.2026 [YANKED]

### Added

- cli commands now default for gams-frog.toml to the current working directory of gams-frog
- added --version command
- corrected readme (for deployed tool)

## [0.0.1] - 13.04.2026 [YANKED]

### Added

- release of initial beta version of the software
- core features with SSR rendering with GAMS5