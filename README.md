# Duplicated & Compare Lists Tool (AutoHotkey v1)

Utility extracted from a personal script to help with line-based list analysis.

## Features

- Finds duplicated lines (case-insensitive)
- Builds distinct lines list (case-insensitive)
- Compare 2 lists with:
  - Common lines
  - Lines only in A
  - Lines only in B
  - Duplicated lines in A
  - Duplicated lines in B
- Custom names for list A and B in results
- Line indicator on each input: `Ln X / Y`

## Requirements

- Windows
- AutoHotkey v1.1+

## Usage

1. Run `src/duplicated_compare_tool.ahk`.
2. Copy lines to clipboard.
3. Press `Ctrl+Shift+Y`.
4. Use the main window actions or open `Compare 2 lists`.

## Hotkey

Default hotkey is:

- `Ctrl+Shift+Y`

You can edit this near the top of the script.

## Notes

- Comparison is case-insensitive.
- Empty lines are ignored.
- Distinct output keeps first-seen original casing.

## Validation

- Manual regression checklist: [TEST_CHECKLIST.md](TEST_CHECKLIST.md)
- Release notes: [CHANGELOG.md](CHANGELOG.md)

## License

MIT. See [LICENSE](LICENSE).
