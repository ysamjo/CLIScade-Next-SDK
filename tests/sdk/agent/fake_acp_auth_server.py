"""Kontrollierter ACP-Server für Anmeldung und tatsächliches Prozessverzeichnis."""

import json
import os
import sys
from pathlib import Path


def respond(request, result=None, error=None):
    response = {"jsonrpc": "2.0", "id": request["id"]}
    response["error" if error else "result"] = error or result or {}
    print(json.dumps(response), flush=True)


signed = False
for line in sys.stdin:
    request = json.loads(line)
    method = request["method"]
    params = request.get("params", {})
    if method == "initialize":
        respond(
            request,
            {
                "protocolVersion": 1,
                "authMethods": [{"id": "oauth-personal", "name": "Google"}],
            },
        )
    elif method == "authenticate":
        signed = params["methodId"] == "oauth-personal"
        respond(request)
    elif method == "session/new":
        if not signed:
            respond(
                request, error={"code": -32000, "message": "Authentication required"}
            )
            continue
        Path("native-start.json").write_text(
            json.dumps(
                {
                    "process_cwd": os.getcwd(),
                    "session_cwd": params["cwd"],
                }
            )
        )
        respond(
            request,
            {
                "sessionId": "test",
                "models": {
                    "currentModelId": "test",
                    "availableModels": [{"modelId": "test", "name": "Test"}],
                },
            },
        )
    elif "id" in request:
        respond(request)
