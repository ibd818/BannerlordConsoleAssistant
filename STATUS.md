# Project status

Last updated: 2026-09-06 UTC

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
- Added selector metadata v2 for troops, items, settlements, buildings, and
  modifiers; catalog-backed fields now show compact metadata and a detail line
  below the input while preserving the original command value.
- Added compact metadata filter chips to editable catalog selectors. Item,
  troop, settlement, and modifier selectors now expose only relevant type or
  effect facets while keeping text input and original command values intact.
- Removed visible detail-panel scrollbars and constrained catalog selectors to
  the available column width; long forms remain wheel-scrollable without a
  horizontal drag bar.
- Added tests covering troop tier/culture metadata, item category, and
  settlement initial-faction metadata.
- Replaced name-based troop Tier estimates with values derived from the module
  character `level` for all 227 catalog troops. The corrected catalog contains
  seven T6 troops and records both level and source; regression tests pin the
  complete T6 set and the level-to-tier calculation.
- Pushed troop-tier fix commit `1645e14`; GitHub Actions Windows run
  `34044433638` completed successfully and uploaded artifact `9992671993`.
- Committed the current source and workflow as `586f5fa` and pushed it to the
  public GitHub repository `ibd818/BannerlordConsoleAssistant`.
- GitHub Actions run 1 completed successfully on `windows-latest`; artifact
  `BannerlordConsoleAssistant-windows` was uploaded and is not expired.

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
- GitHub repository: `https://github.com/ibd818/BannerlordConsoleAssistant`
- Latest Actions run: `https://github.com/ibd818/BannerlordConsoleAssistant/actions/runs/34044433638`
- Current binary: `outputs/BannerlordConsoleAssistant.exe`
- No server service or network port is used.

## Current version

- Python package: 1.1.0
- Command target: Bannerlord 1.4.8.119303 / War Sails 1.2.8.119303 (`r3`)
- Entity catalog: metadata schema v2, catalog revision `r5`

## Unfinished work

- Run GUI smoke tests in an environment with PySide6 when GUI changes are made.
- Launch and smoke-test the downloaded Windows artifact before distributing a
  new EXE.
- Download and launch the successful metadata-selector Actions artifact on
  Windows for final GUI smoke testing.

## Next step

- Download and launch artifact `9992671993` from Actions run `34044433638` on
  Windows for final GUI smoke testing before distribution.

## Risks and notes

- Game updates may invalidate command names, parameters, or behavior.
- Chinese target labels are reference localization labels; the game’s own
  module data and in-game `help` output remain authoritative.
- Oracle can validate core logic but cannot fully replace Windows GUI/build
  acceptance for this Windows desktop application.
