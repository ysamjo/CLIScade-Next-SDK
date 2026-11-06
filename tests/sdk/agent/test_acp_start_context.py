"""ACP-Startverzeichnis und explizite Anmeldung über echte stdio-Prozesse."""

import json
import sys
from pathlib import Path

from openhands.sdk import Conversation
from openhands.sdk.agent.acp_model_discovery import discover_acp_models
from openhands.sdk.settings.model import ACPAgentSettings


def fixture(tmp_path):
    return [sys.executable, str(Path(__file__).with_name("fake_acp_auth_server.py"))]


def test_start_uses_workspace_and_auth_survives_serialization(tmp_path):
    command = fixture(tmp_path)
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    settings = ACPAgentSettings(
        acp_server="custom", acp_command=command, acp_auth_method="oauth-personal"
    )
    restored = ACPAgentSettings.model_validate(settings.model_dump(mode="json"))
    agent = restored.create_agent()
    assert agent.acp_auth_method == "oauth-personal"
    conversation = Conversation(
        agent=agent,
        workspace=str(workspace),
        persistence_dir=str(tmp_path / "state"),
        visualizer=None,
    )
    try:
        conversation.send_message("Nur initialisieren")
        with conversation.state:
            agent.init_state(conversation.state, on_event=lambda event: None)
        proof = json.loads((workspace / "native-start.json").read_text())
        assert proof == {"process_cwd": str(workspace), "session_cwd": str(workspace)}
    finally:
        conversation.close()
        agent.close()


def test_discovery_uses_explicit_auth_and_rejects_unknown_method(tmp_path):
    command = fixture(tmp_path)
    settings = ACPAgentSettings(
        acp_server="custom", acp_command=command, acp_auth_method="oauth-personal"
    )
    assert discover_acp_models(settings, work_root=tmp_path).error is None
    settings.acp_auth_method = "not-advertised"
    result = discover_acp_models(settings, work_root=tmp_path)
    assert result.error is not None
    assert "nicht angeboten" in result.error.detail
