# BannerlordConsoleAssistant project rules

- Read `/opt/codex-context/USER_CONTEXT.md`, this file, `STATUS.md`, and
  `DECISIONS.md` when prior design or deployment choices matter.
- Treat `src/bannerlord_assistant/data/commands.json` as versioned product data;
  preserve UTF-8 Chinese text and validate schema changes through core tests.
- Keep the application limited to generating official Bannerlord console
  commands. Do not add game-file modification, process injection, or memory
  access unless the user explicitly changes the product scope.
- `work/` contains build inputs plus regenerable environments and intermediate
  output. Do not commit virtual environments, dependency copies, PyInstaller
  output, or smoke-test caches.
- Run core checks with
  `PYTHONPATH=src python3 -m unittest discover -s tests -p 'test_core.py' -v`.
  Run `test_gui_smoke.py` only where PySide6 is installed; validate Windows EXE
  builds on Windows before release.
- After meaningful work, update `STATUS.md`. Record only important technical,
  architecture, deployment, or design decisions in `DECISIONS.md`.
- Never place passwords, API keys, tokens, cookies, SSH keys, OAuth credentials,
  or other secrets in context files or the repository.
