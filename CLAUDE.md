@AGENTS.md

## Spécifique à Claude Code

- Commandes : `.claude/commands/` (renvoient à `procedures/`).
- Terminal : PowerShell sous Windows → `.\w2r.ps1 <commande>`.
- Hook `PostToolUse` (`.claude/settings.json`) : chaque `.feature`, `.robot` et `.resource` écrit est validé
  dans le conteneur ; une erreur renvoyée par le hook se corrige avant de continuer. Trace de chaque
  déclenchement : `.w2r/hook.log`.
- Serveurs MCP : `.mcp.json` (lancés par `w2r.ps1` dans le conteneur Podman).
