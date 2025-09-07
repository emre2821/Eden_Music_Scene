# Eden Music Scene

## Development setup

Install and configure the Git hooks:

```bash
pip install pre-commit
pre-commit install
```

Run all checks:

```bash
pre-commit run --all-files
```

## Running tests

Execute the test suites with:

```bash
pytest tests
pytest EchoSplit/tests
```
