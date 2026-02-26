# Running a Self-Assessment

The `aumos-certify` CLI runs conformance checks entirely on your local machine.
No network connection is required. No data leaves your environment.

## Prerequisites

- Python 3.10 or later
- The `aumos-certify` package installed

```bash
cd python/
pip install -e .
```

Verify the installation:

```bash
aumos-certify --version
```

## Implement an adapter

Before running checks, you must provide an `ImplementationAdapter` that connects the
conformance runner to your agent governance system.

Create a Python file that subclasses `ImplementationAdapter` and implements the `invoke`
method for each protocol operation you want to certify:

```python
from aumos_certify.types import ImplementationAdapter
from typing import Any

class MyAgentSystem(ImplementationAdapter):
    def get_implementation_name(self) -> str:
        return "MyAgentSystem v1.0"

    async def invoke(
        self,
        protocol: str,
        operation: str,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        # Delegate to your actual implementation
        ...
```

See `examples/certify_sdk.py` for a complete working example.

## Run the checks

Pass your adapter file to the CLI using the `--implementation` flag and specify the
target certification level:

```bash
aumos-certify run \
    --implementation path/to/my_adapter.py \
    --level silver
```

The runner will execute all conformance checks required for the specified level (and above),
then display a pass/fail summary per protocol.

To run checks for a specific set of protocols instead of a full level:

```bash
aumos-certify run \
    --implementation path/to/my_adapter.py \
    --protocols atp aeap aoap
```

## Generate a report

After a run, generate an offline Markdown or JSON report:

```bash
# Markdown report
aumos-certify report --format md

# JSON report (machine-readable)
aumos-certify report --format json
```

Reports are written to the current directory by default. Use `--output` to specify a path:

```bash
aumos-certify report --format md --output ./reports/aumos-self-assessment.md
```

## Generate a badge SVG

Once you have a passing result, generate an SVG badge for your README:

```bash
aumos-certify badge --level silver --output ./aumos-certified-silver.svg
```

See `docs/badge-usage.md` for instructions on embedding the badge in your project README.

## Understanding results

Each check produces one of four statuses:

| Status | Meaning |
|--------|---------|
| `pass` | The check succeeded |
| `fail` | The check found a conformance problem |
| `skip` | The check was not run (SHOULD-level requirement, operation not implemented) |
| `error` | An unexpected exception occurred during the check |

Only `pass` and `fail` counts toward the overall pass rate. `skip` and `error` counts are
excluded from the denominator.

A certification level is awarded when the pass rate meets the level's minimum threshold
**and** all required protocols have at least one MUST-level check that passed. See
`docs/certification-levels.md` for the full criteria.
