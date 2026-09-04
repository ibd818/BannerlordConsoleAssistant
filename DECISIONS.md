# Decisions

## 2026-08-29 — Keep official-console-only product scope

- Decision: Generate and copy official Bannerlord console commands without
  modifying game files, injecting into the process, or reading game memory.
- Reason: This keeps the tool simple, auditable, and aligned with its existing
  product promise.
- Alternatives: Memory editing and process injection are outside the accepted
  scope.

## 2026-08-29 — Keep commands as versioned external data

- Decision: Maintain the default command library as UTF-8 JSON separate from UI
  and rendering logic.
- Reason: Commands and localized metadata can evolve without restructuring the
  application, and schema behavior remains unit-testable.
- Alternatives: Hard-coding commands in Python would couple data updates to UI
  releases.

## 2026-08-29 — Exclude regenerable Windows build caches from Oracle migration

- Decision: Preserve source, tests, build scripts, selected build inputs, and
  the current EXE; exclude `work/build-venv`, dependency copies, PyInstaller
  intermediates, and smoke-test caches.
- Reason: The excluded 272 MB uncompressed content is reproducible and would
  add noise and platform-specific dependencies to the canonical Oracle copy.
- Alternatives: Copying the archive byte-for-byte was rejected because the
  migration requirements explicitly exclude reinstallable dependencies and
  meaningless caches.

## 2026-09-03 — Use versioned bilingual target catalogs with original-value rendering

- Decision: Store finite Bannerlord target records in `entities.json`, reference
  them from command parameters with `catalog`, display `value（中文标签）`, and
  render only the original `value` into the copied command. Keep save-dependent
  names and user-created names as editable text inputs.
- Reason: Heroes, troops, items, settlements, factions, and similar module
  records can be searched reliably by ID, English name, Chinese label, or
  alias; runtime-only objects cannot be made complete by a static list.
- Alternatives: A Chinese-only command value would fail in the game, while a
  single unannotated text field recreates the original lookup problem. The
  static catalog therefore supplements, rather than replaces, manual input.
- Note: Chinese labels are reference localization data and are not treated as
  authoritative command syntax; the target game’s module data and in-game
  `help` output remain authoritative.

## 2026-09-03 — Build Windows EXE with GitHub Actions

- Decision: Run the existing `build.ps1` on `windows-latest` after setting up
  Python 3.10, then upload `outputs/BannerlordConsoleAssistant.exe` as an
  immutable workflow artifact.
- Reason: The project’s release target is a Windows desktop EXE, while Oracle
  cannot validate the PySide6 GUI or PyInstaller Windows output. Reusing the
  existing script keeps local and CI build behavior aligned.
- Alternatives: Building on Oracle would produce a non-Windows executable;
  duplicating the PyInstaller command in YAML would create a second build path.

## 2026-09-04 — Add metadata-only entity selectors

- Decision: Extend catalog entries with display metadata and show a compact
  summary plus detail line for catalog-backed inputs, while keeping `value`
  as the only command-rendered value.
- Reason: Large flat lists made it difficult to choose the correct troop,
  item, or settlement even when the ID search was successful. Metadata improves
  selection without changing official command syntax.
- Boundaries: Troop tiers without a direct ID field are marked as first-pass
  estimates; settlement faction is explicitly initial/static faction because
  current ownership is save-dependent and outside the official-console-only
  product scope.
- Alternatives: A single cross-category quality score was rejected because
  weapons, armor, and trade goods require different comparison criteria.

## 2026-09-04 — Add compact type facets to catalog selectors

- Decision: Keep editable combo boxes as the primary selection control and add
  small metadata filter chips above them for catalogs with useful facets.
  Items use category labels, troops use combat type, settlements use
  settlement type, and modifiers use effect direction.
- Reason: Large catalogs need quick narrowing, but permanent candidate cards or
  a separate result panel consume space and obscure the relationship between a
  filter and the command parameter.
- Alternatives: A separate candidate-card grid was rejected as redundant with
  the dropdown; free-text-only selection was rejected because it hides valid
  values and metadata.

## 2026-09-04 — Hide detail-panel drag bars while preserving overflow access

- Decision: Keep the detail panel's scroll container for long commands, but
  hide both scrollbars and force catalog controls to fit the available width.
  Mouse-wheel scrolling remains available for unusually tall forms.
- Reason: The visible horizontal bar was caused by long catalog labels being
  used as the combo box minimum width. A compact selector should not widen the
  whole detail panel or expose a draggable page bar.
- Alternative: Removing the scroll container entirely would clip parameters
  on smaller windows and make long commands inaccessible.
