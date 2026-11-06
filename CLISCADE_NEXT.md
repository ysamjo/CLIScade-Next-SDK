# CLIScade Next: ACP-Start und Kontoanmeldung

Basis: offizieller SDK-Release 1.55.1; eigene Paketversion
`1.55.1+cliscade.1`. Der Integrationsfork enthält zwei fachliche Korrekturen:

1. Jeder native ACP-Prozess erhält sein eigenes `cwd` aus dem Workspace. Der
   Prozess-CWD des Agent Servers wird nicht umgestellt. CodeBuddy 2.168.0
   ignorierte im echten Test das `session/new.cwd` und schrieb ohne diese
   Korrektur außerhalb des vorgesehenen Test-Workspaces.
2. `ACPAgent.acp_auth_method` und `ACPAgentSettings.acp_auth_method` wählen eine
   explizit angebotene ACP-Anmeldemethode. `None` bewahrt die automatische
   Credential-Erkennung. Eine unbekannte Methode scheitert vor `session/new`.
   Factory, JSON-Serialisierung, Modellabfrage und TypeScript-Vertrag führen
   die Option durch. Antigravity 1.4.0 verwendet `oauth-personal` für Google.

Die Funktion enthält keinen Terminal-/Headless-Adapter und implementiert weder
OAuth noch den ACP-Transport erneut. Persönliche Logins bleiben beim nativen
Anbieter. Das generierte TypeScript-Schema stammt aus dem kanonischen
`create_app().openapi()` mit eingefrorenen Workspace-Abhängigkeiten.

## Prüfung

```sh
uvx --from uv==0.12.23 uv sync --frozen --package openhands-agent-server --group dev
env -u ANTHROPIC_API_KEY .venv/bin/pytest tests/sdk/agent/test_acp_start_context.py tests/sdk/agent/test_acp_model_discovery.py tests/sdk/agent/test_acp_agent.py -q
cd clients/typescript
npm ci
npm run build
```

496 ACP-Tests bestanden. Der zusätzliche Prozess-Fixture prüft tatsächlichen
Prozess-CWD, Session-CWD, Auth-Handshake, serialisierte Factory-Settings und
Modellabfrage. Der reale CodeBuddy-Dateitest in CLIScade Next bestand nach dem
Fix. Antigravity-Handshake und Google-Login-Start sind geprüft; eine persönliche
Google-Kontofreigabe und authentifizierte Inferenz werden nicht behauptet.
