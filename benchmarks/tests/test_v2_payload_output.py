import json

from .. import _benchmark


def test_publish_writes_result_payload_file(tmp_path, monkeypatch):
    monkeypatch.setenv("CONBENCH_RESULTS_DIR", str(tmp_path))
    communicator = _benchmark.ConbenchCommunicator()
    payload = {
        "run_id": "run-1",
        "tags": {"name": "example"},
        "context": {"benchmark_language": "Python"},
    }

    communicator.publish(payload)

    [path] = tmp_path.glob("result-*.json")
    assert json.loads(path.read_text()) == payload


def test_publish_normalizes_legacy_numeric_strings_for_v2(tmp_path, monkeypatch):
    monkeypatch.setenv("CONBENCH_RESULTS_DIR", str(tmp_path))
    communicator = _benchmark.ConbenchCommunicator()
    payload = {
        "run_id": "run-1",
        "tags": {"name": "example"},
        "machine_info": {
            "name": "worker",
            "cpu_core_count": "8",
            "cpu_thread_count": "16",
            "cpu_frequency_max_hz": "3200000000",
            "memory_bytes": "17179869184",
            "gpu_count": "0",
        },
        "stats": {
            "data": ["0.003838", None],
            "times": ["0.1", "0.2"],
            "iterations": 2,
            "min": "0.003838",
            "max": "0.004200",
            "mean": "0.004019",
            "median": "0.004019",
            "stdev": "0.000181",
            "q1": "0.003838",
            "q3": "0.004200",
            "iqr": "0.000362",
            "unit": "s",
        },
    }

    communicator.publish(payload)

    [path] = tmp_path.glob("result-*.json")
    written = json.loads(path.read_text())
    assert written["machine_info"]["cpu_core_count"] == 8
    assert written["machine_info"]["cpu_thread_count"] == 16
    assert written["machine_info"]["cpu_frequency_max_hz"] == 3200000000
    assert written["machine_info"]["memory_bytes"] == 17179869184
    assert written["machine_info"]["gpu_count"] == 0
    assert written["stats"]["data"] == [0.003838, None]
    assert written["stats"]["times"] == [0.1, 0.2]
    assert written["stats"]["mean"] == 0.004019
