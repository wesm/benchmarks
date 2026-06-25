import copy
import json

import pytest

from .. import js_micro_benchmarks
from ..tests import _asserts

HELP = """
Usage: conbench js-micro [OPTIONS]

  Run the Arrow JavaScript micro benchmarks.

Options:
  --src TEXT             Specify Arrow source directory.
  --show-result BOOLEAN  [default: true]
  --show-output BOOLEAN  [default: false]
  --run-id TEXT          Group executions together with a run id.
  --run-name TEXT        Free-text name of run (commit ABC, pull request 123,
                         etc).
  --run-reason TEXT      Low-cardinality reason for run (commit, pull request,
                         manual, etc).
  --help                 Show this message and exit.
"""


def assert_benchmark(result):
    munged = copy.deepcopy(result)
    _asserts.assert_info_and_context(munged, language="JavaScript")
    assert munged["tags"] == {}  # TODO
    assert munged["stats"]["unit"] == "s"
    assert munged["stats"]["time_unit"] == "s"
    assert len(munged["stats"]["data"]) == 1
    assert len(munged["stats"]["times"]) == 0


def test_parse_benchmark_tags():
    name = "dataset: tracks, column: lng, length: 1,000,000, type: Float32"
    tags = js_micro_benchmarks._parse_benchmark_tags(name)
    assert tags == {
        "dataset": "tracks",
        "column": "lng",
        "length": "1,000,000",
        "type": "Float32",
    }

    name = "dataset: tracks, column: origin, length: 1,000,000, type: Dictionary<Int8, Utf8>, test: eq, value: Seattle"
    tags = js_micro_benchmarks._parse_benchmark_tags(name)
    assert tags == {
        "dataset": "tracks",
        "column": "origin",
        "length": "1,000,000",
        "test": "eq",
        "type": "Dictionary<Int8, Utf8>",
        "value": "Seattle",
    }

    # last value has a comma in it
    name = "dataset: tracks, column: origin, length: 1,000,000, type: Dictionary<Int8, Utf8>"
    tags = js_micro_benchmarks._parse_benchmark_tags(name)
    assert tags == {
        "dataset": "tracks",
        "column": "origin",
        "length": "1,000,000",
        "type": "Dictionary<Int8, Utf8>",
    }


def test_get_run_command():
    actual = js_micro_benchmarks.get_run_command()
    assert actual == ["yarn", "perf", "--json"]


@pytest.mark.slow
def test_javascript_micro():
    benchmark = js_micro_benchmarks.RecordJavaScriptMicroBenchmarks()
    [(result, output)] = benchmark.run()
    assert_benchmark(result)
    assert output is None


def test_javascript_micro_writes_one_v2_payload_per_result(tmp_path, monkeypatch):
    monkeypatch.setenv("CONBENCH_RESULTS_DIR", str(tmp_path))
    monkeypatch.delenv("DRY_RUN", raising=False)
    tool_output = [
        {
            "suite": "vector-filter",
            "name": "dataset: tracks, column: lng, length: 1,000,000, type: Float32",
            "details": {"sampleResults": [0.1]},
        },
        {
            "suite": "vector-filter",
            "name": "dataset: tracks, column: lat, length: 1,000,000, type: Float32",
            "details": {"sampleResults": [0.2]},
        },
        {
            "suite": "table-select",
            "name": "dataset: trips, column: vendor_id, length: 10,000, type: Int32",
            "details": {"sampleResults": [0.3]},
        },
    ]

    benchmark = js_micro_benchmarks.RecordJavaScriptMicroBenchmarks()
    benchmark.execute_command = lambda command: ("", json.dumps(tool_output))

    results = list(benchmark.run(run_id="js-run-1", run_reason="manual-smoke"))

    assert len(results) == 3
    payloads = [json.loads(path.read_text()) for path in tmp_path.glob("result-*.json")]
    assert len(payloads) == 3
    assert {payload["tags"]["source"] for payload in payloads} == {"js-micro"}
    assert {payload["run_id"] for payload in payloads} == {"js-run-1"}
    assert {payload["context"]["benchmark_language"] for payload in payloads} == {
        "JavaScript"
    }
    assert {payload["tags"]["dataset"] for payload in payloads} == {"tracks", "trips"}


def test_javascript_micro_cli():
    command = ["conbench", "js-micro", "--help"]
    _asserts.assert_cli(command, HELP)
