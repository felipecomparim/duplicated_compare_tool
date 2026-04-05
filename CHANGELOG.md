# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-04-04

### Added

- Standalone AutoHotkey v1 utility in src/duplicated_compare_tool.ahk.
- Main window for duplicate and distinct extraction from clipboard lines.
- Compare 2 lists modal with:
  - Common lines
  - Only in list A
  - Only in list B
  - Duplicated in list A
  - Duplicated in list B
- Custom list names (A/B) used in summary and section headers.
- Caret and total-line indicator on both input panes (Ln X / Y).
- Responsive layout behavior for main and compare windows.
- Project docs and GitHub-ready structure (README, LICENSE, PHASES).

### Notes

- Matching is case-insensitive.
- Empty lines are ignored.
- Distinct values preserve first-seen original casing.
