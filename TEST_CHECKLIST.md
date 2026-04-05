# Manual Regression Checklist

Use this checklist before publishing a new release.

## Environment

- Windows machine
- AutoHotkey v1.1+
- Script launched from src/duplicated_compare_tool.ahk

## Main Flow

1. Open the script and trigger the hotkey (default Ctrl+Shift+Y) with non-empty clipboard.
   - Expected: Main window opens with duplicated and distinct sections populated.
2. Trigger hotkey with empty clipboard.
   - Expected: Friendly warning dialog about empty clipboard.
3. Click Copy Duplicates.
   - Expected: Clipboard gets duplicate output and tray notification appears.
4. Click Copy Distinct.
   - Expected: Clipboard gets distinct output and tray notification appears.

## Compare 2 Lists Flow

1. Open Compare 2 lists from the main window.
   - Expected: Compare modal opens with two input panes and result pane.
2. Enter names for both lists.
   - Expected: Names appear in final summary and section headers after Process.
3. Leave names empty and click Process.
   - Expected: Fallback naming uses A and B.
4. Enter sample data with overlaps and differences, then click Process.
   - Expected: Sections show common, only A, only B with correct counts.
5. Include repeated values in list A.
   - Expected: Duplicated in A section shows values with xN counts.
6. Include repeated values in list B.
   - Expected: Duplicated in B section shows values with xN counts.
7. Include casing variations (abc, ABC).
   - Expected: Treated as same value for compare and duplicate counting.
8. Include blank lines.
   - Expected: Blank lines are ignored.
9. Click Clear.
   - Expected: Both input panes, summary, and result pane are reset.

## Caret/Line Indicators

1. Type multiple lines in list A and move cursor through lines.
   - Expected: Right-side indicator updates as Ln current/total for list A.
2. Repeat in list B.
   - Expected: Right-side indicator updates as Ln current/total for list B.

## Resize Behavior

1. Resize compare window to larger size.
   - Expected: Three content panes remain balanced and controls stay aligned.
2. Resize compare window to smaller size.
   - Expected: Controls remain usable and no overlap occurs.
3. Resize main window.
   - Expected: Both main text areas resize correctly and buttons stay anchored.

## Lifecycle Stability

1. Open and close compare modal multiple times.
   - Expected: No errors, no stale UI behavior, indicators continue updating.
2. Close main window after opening compare.
   - Expected: Windows close cleanly.

## Release Gate

- Mark release as ready only if all checks above pass.
