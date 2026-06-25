# Arrow Python Benchmarks

Python benchmark suite for Apache Arrow. This fork is part of the Conbench v2
migration path and currently targets branch `v2-conbench-submit` on
`wesm/benchmarks`.

## Agent workflow

- Commit repository changes before ending the turn unless the user explicitly
  asks not to commit. Keep unrelated user changes out of commits; stage only
  the paths you changed for the task.
- Do not commit benchmark data, generated result payloads, local virtualenvs,
  credentials, reporter tokens, or full environment dumps.
- Do not add tautological content-matching tests that only assert that strings,
  labels, headings, or resource names you just wrote are still present. Tests
  must verify behavior or a meaningful contract: parse structured output when
  possible, exercise code paths, validate rendered artifacts with an external
  consumer, or check invariants that would catch a real regression.

## Conbench v2 migration

- Benchmark commands may still use temporary legacy execution dependencies, but
  publishing must go through v2 JSON payload files and the Go `conbench` CLI.
- Do not reintroduce legacy `.conbench` email/password auth, `benchclients`,
  `benchconnect`, or `benchalerts` publishing paths.
- Preserve Buildkite-facing environment contracts such as `CONBENCH_RESULTS_DIR`,
  `CONBENCH_TOKEN`, `CONBENCH_CLI`, `RUN_ID`, `RUN_NAME`, and `RUN_REASON`
  unless a migration issue explicitly changes them.

## Validation

- Run focused `pytest` for touched benchmark or payload code. The broad test
  command from the README is `pytest -vv benchmarks/tests/`.
- Run `black` and `isort` on changed Python files where formatting is needed.
- Always run `git diff --check` before committing.
