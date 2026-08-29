# Project status

Last updated: 2026-08-29 UTC

## Current goal

Continue long-term development on Oracle while preserving a verified Windows
build path for the Bannerlord official-console command assistant.

## Completed

- Migrated verified source, documentation, tests, command data, build scripts,
  and the current Windows EXE from the Windows archive.
- Preserved 166 data-driven commands targeting Bannerlord v1.4.8.119303 and
  War Sails v1.2.8.119303.
- Excluded 4,816 regenerable dependency/build-cache files during migration.
- Passed all 11 core unit tests on Oracle.
- Validated every migrated JSON file and found no credential-pattern matches.

## Current environment

- Primary source location: `/opt/projects/BannerlordConsoleAssistant`
- Oracle Python: 3.10.12
- Windows is still required to validate the PySide6 GUI and single-file EXE.
- PySide6 is not installed in the current Oracle Python environment.

## Key paths, services, and ports

- Application source: `src/bannerlord_assistant/`
- Command library: `src/bannerlord_assistant/data/commands.json`
- Tests: `tests/`
- Windows build script: `build.ps1`
- Current binary: `outputs/BannerlordConsoleAssistant.exe`
- No server service or network port is used.

## Current version

- Python package: 1.0.0
- Command target: Bannerlord 1.4.8.119303 / War Sails 1.2.8.119303

## Unfinished work

- Run GUI smoke tests in an environment with PySide6 when GUI changes are made.
- Run the Windows build and launch checks before publishing a new EXE.
- Configure a Git remote if off-server source replication is desired.

## Next step

- Continue with the next requested feature or command-library update from this
  Oracle project root.

## Risks and notes

- Game updates may invalidate command names, parameters, or behavior.
- Oracle can validate core logic but cannot fully replace Windows GUI/build
  acceptance for this Windows desktop application.
