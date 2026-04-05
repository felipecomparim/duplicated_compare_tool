# Refactor Phases (1-30)

## Status legend

- [x] Done
- [~] In progress
- [ ] Pending

## Execution

1. [x] Freeze baseline and confirm extraction target in original script.
2. [x] Create manual backup of core files.
3. [x] Map utility labels/functions/vars in original file.
4. [x] Define unique naming prefix (`DupTool`) to avoid collisions.
5. [x] Rename/extract handlers to prefixed standalone version.
6. [x] Rename/extract compare modal handlers to prefixed standalone version.
7. [x] Rename/extract helper functions to prefixed standalone version.
8. [x] Isolate standalone state (`hDupTool...`) and timer lifecycle.
9. [x] Review internal g-label bindings in standalone script.
10. [~] Validate runtime behavior in AutoHotkey v1 (pending local v1 runtime).

11. [x] Create extraction folder structure.
12. [x] Create initial standalone script.
13. [x] Copy functional utility block into standalone file.
14. [x] Remove unnecessary include dependencies.
15. [x] Add explicit standalone entrypoint (default hotkey).
16. [x] Keep clipboard empty fallback.
17. [x] Keep A/B fallback naming.
18. [x] Start/stop compare caret watcher timer correctly.
19. [x] Keep Ln X / Y indicator in both input panes.
20. [~] Validate responsive layout manually.

21. [~] Review and normalize UI text language.
22. [x] Keep all result sections output (including duplicates in A).
23. [x] Create README with overview and quick start.
24. [x] Add usage examples in README (basic flow).
25. [x] Add hotkey customization note in README.
26. [x] Add LICENSE.
27. [x] Add CHANGELOG v1.0.0.
28. [~] Run full regression checklist (checklist + run log prepared; pending local execution).
29. [x] Prepare GitHub-ready structure.
30. [~] Publish repo and create v1.0.0 release (publish guide prepared).
