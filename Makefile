# make test, coverage, documentation, etc
SHELL := /bin/bash

.PHONY: all test clean build

all: test lint build

test:
	@uv run pytest tests

lint:
	@uv run ruff check src

build:
	@uv build

