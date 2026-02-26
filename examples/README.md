# Examples

This directory contains runnable examples for the `aumos-certify` self-assessment toolkit.

## certify_sdk.py

Demonstrates the end-to-end self-assessment workflow against a mock in-memory implementation.

The example:

- Implements `ImplementationAdapter` over a simple in-memory agent governance system.
- Runs ATP, AIP, AEAP, AMGP, and AOAP conformance checks.
- Scores the result to determine the highest achieved certification level.
- Prints a per-protocol summary and the overall outcome.

**Run the example**

```bash
cd python/
pip install -e ".[dev]"
python ../examples/certify_sdk.py
```

Expected output (exact pass counts may vary by protocol version):

```
AumOS Self-Assessment Toolkit — Example Run
====================================================
Implementation : MockAgentSystem v0.1.0 (example)
Protocols      : ATP, AIP, AEAP, AMGP, AOAP

Protocol Results
----------------------------------------
  ATP       4 passed, 0 failed, 1 skipped  (100.0%)
  AIP       4 passed, 0 failed, 0 skipped  (100.0%)
  AEAP      4 passed, 0 failed, 0 skipped  (100.0%)
  AMGP      3 passed, 0 failed, 1 skipped  (100.0%)
  AOAP      3 passed, 0 failed, 1 skipped  (100.0%)

Overall score  : 100.0%
Achieved level : GOLD (Self-Assessed)
```

## Adapting the example

To test your own implementation, subclass `ImplementationAdapter` and replace `MockAgentSystem`
with a class that delegates `invoke()` calls to your actual agent governance layer.

See `docs/self-assessment.md` for CLI-based usage and `docs/certification-levels.md` for the
full protocol and threshold requirements at each level.
