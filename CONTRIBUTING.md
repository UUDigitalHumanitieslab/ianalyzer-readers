# Contributing

## Getting started

Start by cloning this repository and creating a virtual environment for python. From the repository root, install dependencies with

```sh
pip install --editable '.[dev]'
```

## Unit tests

Run unit tests with

```sh
pytest
```

## Writing documentation

Documentation is based on [mkdocs](https://www.mkdocs.org).

### Commands

Start the live-reloading docs server:

```sh
mkdocs serve
```

Build the documentation site:

```sh
mkdocs build
```

Print help message and exit:

```sh
mkdocs -h
```
