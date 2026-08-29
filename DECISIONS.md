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
