from app import telemetry


def test_telemetry_excludes_payload_headers_and_prompts(monkeypatch):
    lines = []
    monkeypatch.setattr(telemetry.logger, "info", lines.append)
    telemetry.lifecycle(
        {
            "event_id": 1,
            "timestamp": "2026-10-14T00:00:00Z",
            "sandbox_role": "system",
            "type": "run.started",
            "run_id": "11111111-1111-1111-1111-111111111111",
            "payload": {"status": "running", "prompt": "DO NOT LOG THIS", "Authorization": "TEST_SECRET"},
        }
    )
    assert len(lines) == 1
    assert "DO NOT LOG" not in lines[0] and "TEST_SECRET" not in lines[0]
    assert "running" in lines[0]
