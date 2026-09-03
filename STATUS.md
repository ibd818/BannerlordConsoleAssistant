# Project status

Last updated: 2026-09-03 UTC

## Current goal

Continue long-term development on Oracle while preserving a verified Windows
build path for the Bannerlord official-console command assistant.

## Completed

- Migrated verified source, documentation, tests, command data, build scripts,
  and the current Windows EXE from the Windows archive.
- Preserved 166 data-driven commands targeting Bannerlord v1.4.8.119303 and
  War Sails v1.2.8.119303.
- Added the versioned `entities.json` catalog with 21 bilingual target
  directories, including 440 heroes, 227 eligible troops, 947 items, 539
  settlement IDs, 105 factions, and fixed-value catalogs for skills, traits,
  buildings, languages, teams, and item modifiers.
- Added substring completion by ID, English name, Chinese label, and aliases;
  selected entries render their original English value into the command while
  dynamic save-only targets remain editable text fields.
- Bumped the command library to `...-r3` so existing `r2` user libraries are
  backed up and upgraded with the new catalog references.
- Excluded 4,816 regenerable dependency/build-cache files during migration.
- Passed all 13 core unit tests on Oracle.
- Validated every migrated JSON file and found no credential-pattern matches.
- Added a GitHub Actions Windows workflow that installs dependencies, runs core
  tests, builds the EXE with `build.ps1`, and uploads a downloadable artifact.

## Current environment

- Primary source location: `/opt/projects/BannerlordConsoleAssistant`
- Oracle Python: 3.10.12
- Windows is still required to validate the PySide6 GUI and single-file EXE.
- PySide6 is not installed in the current Oracle Python environment.

## Key paths, services, and ports

- Application source: `src/bannerlord_assistant/`
- Command library: `src/bannerlord_assistant/data/commands.json`
- Target catalogs: `src/bannerlord_assistant/data/entities.json`
- Tests: `tests/`
- Windows build script: `build.ps1`
- GitHub Actions workflow: `.github/workflows/windows-build.yml`
- Current binary: `outputs/BannerlordConsoleAssistant.exe`
- No server service or network port is used.

## Current version

- Python package: 1.0.0
- Command target: Bannerlord 1.4.8.119303 / War Sails 1.2.8.119303 (`r3`)

## Unfinished work

- Run GUI smoke tests in an environment with PySide6 when GUI changes are made.
- Run the Windows build and launch checks before publishing a new EXE.
- Run the new GitHub Actions workflow on GitHub to validate the Windows runner
  build and artifact upload.
- Configure a Git remote if off-server source replication is desired.

## Next step

- Run GUI smoke tests in a Windows/PySide6 environment and rebuild the EXE
  before distributing the catalog-enabled release; the GitHub Actions workflow
  now provides the repeatable Windows build path.

## Risks and notes

- Game updates may invalidate command names, parameters, or behavior.
- Chinese target labels are reference localization labels; the game’s own
  module data and in-game `help` output remain authoritative.
- Oracle can validate core logic but cannot fully replace Windows GUI/build
  acceptance for this Windows desktop application.
