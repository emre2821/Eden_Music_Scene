# Eden Music Scene

## Development setup

After cloning the repository, install and configure the Git hooks with [pre-commit](https://pre-commit.com/):

```bash
pip install pre-commit
pre-commit install
```

This enables `black`, `ruff`, and `prettier` to run automatically before each commit.
You can also run all checks manually:

```bash
pre-commit run --all-files
```

## Running tests

Execute the test suites with:

```bash
pytest tests
pytest EchoSplit/tests
```
