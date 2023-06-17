# Contributing

Thank you for having interest in contributing this project!

## Bugs

Please create an issue or pull request.

## Proposing a Change

I recommend to create an issue.

## Developing

* The development branch is `develop`.
* All pull requests should be opened against `develop`.
* The changes on the `develop` branch are published to https://test.pypi.org/project/autoload-module/ .
    * You can install the `develop` package by
      executing `pip install -i https://test.pypi.org/simple/ autoload-module` .

To develop locally:

1. Install [poetry](https://python-poetry.org/docs/) .
2. Clone this repository.
3. Create a new branch.
4. Install the dependencies with:
   `poetry install`
5. Enable [`pre-commit`](https://pre-commit.com/) .

## Testing

* Please update the tests to reflect your code changes.
* Pull requests will not be accepted if they are failing on GitHub Actions.
* You can also check your code by executing `python -m unittest` .

## Docs

I'm not familiar with English, so I especially thank you for documents' corrections.

## Release

I release `autoload-module` by merging from `develop` into `master` branch.