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
