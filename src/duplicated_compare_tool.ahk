#NoEnv
#SingleInstance, Force
SendMode Input
SetWorkingDir %A_ScriptDir%

; Hotkey default for standalone version.
; Change if it conflicts with your environment.
^+y::
DupTool_RunFromClipboard()
return

DupTool_RunFromClipboard()
{
	global DupToolLblHeader, DupToolLblDup, DupToolDupEdit, DupToolLblDistinct, DupToolDistinctEdit
	global DupToolBtnCopyDup, DupToolBtnCopyDistinct, DupToolBtnCompare, DupToolBtnClose

	selected_text := Clipboard
	if (selected_text = "")
	{
		MsgBox, 48, Duplicates, Clipboard is empty.
		return
	}

	counts := Object()
	originals := Object()

	Loop, Parse, selected_text, `r`n
	{
		line := Trim(A_LoopField)
		if (line = "")
			continue

		upper := line
		StringUpper, upper, upper

		if !originals.HasKey(upper)
			originals[upper] := line

		counts[upper] := counts.HasKey(upper) ? counts[upper] + 1 : 1
	}

	CRLF := Chr(13) . Chr(10)
	dupes := ""
	for k, v in counts
		if (v > 1)
			dupes .= originals[k] " (x" v ")" . CRLF

	distinct := ""
	for k, v in originals
		distinct .= v . CRLF

	if (dupes = "")
		dupes := "No duplicates found." . CRLF

	dupeCount := 0
	for k, v in counts
		if (v > 1)
			dupeCount++

	distinctCount := originals.Count()

	Gui, DupToolMain:New, +AlwaysOnTop +Resize, Duplicated & Distinct lines
	Gui, DupToolMain:Margin, 10, 8
	Gui, DupToolMain:Add, Text, vDupToolLblHeader cBlue, Found %distinctCount% distinct values - %dupeCount% duplicates
	Gui, DupToolMain:Add, Text, vDupToolLblDup, Duplicated (case-insensitive) lines:
	Gui, DupToolMain:Add, Edit, vDupToolDupEdit ReadOnly +Multi
	Gui, DupToolMain:Add, Text, vDupToolLblDistinct, Distinct values (case-insensitive) from selection:
	Gui, DupToolMain:Add, Edit, vDupToolDistinctEdit ReadOnly +Multi
	Gui, DupToolMain:Add, Button, vDupToolBtnCopyDup gDupToolCopyDup, Copy Duplicates
	Gui, DupToolMain:Add, Button, vDupToolBtnCopyDistinct gDupToolCopyDistinct, Copy Distinct
	Gui, DupToolMain:Add, Button, vDupToolBtnCompare gDupToolOpenCompare, Compare 2 lists
	Gui, DupToolMain:Add, Button, vDupToolBtnClose gDupToolClose, Close

	GuiControl,, DupToolDupEdit, %dupes%
	GuiControl,, DupToolDistinctEdit, %distinct%

	Gui, DupToolMain:Show, w720 h540
}

DupToolCopyDup:
Gui, DupToolMain:Submit, NoHide
Clipboard := DupToolDupEdit
TrayTip, Duplicates, Duplicates copied., 2, 1
return

DupToolCopyDistinct:
Gui, DupToolMain:Submit, NoHide
Clipboard := DupToolDistinctEdit
TrayTip, Distinct, Distinct list copied., 2, 1
return

DupToolOpenCompare:
Gui, DupToolCompare:New, +AlwaysOnTop +Resize +HwndhDupToolCompare, Compare 2 lists
Gui, DupToolCompare:Margin, 10, 8
Gui, DupToolCompare:Add, Text, vDupToolCmpLblAPrefix, List
Gui, DupToolCompare:Add, Edit, x+6 yp-2 w140 vDupToolCmpNameA, A
Gui, DupToolCompare:Add, Text, x+6 yp+2 vDupToolCmpLblASuffix, (one line per item):
Gui, DupToolCompare:Add, Text, x+6 yp vDupToolCmpPosA Right w90, Ln 1 / 1
Gui, DupToolCompare:Add, Edit, vDupToolCmpListA gDupToolListAChanged +Multi WantTab
Gui, DupToolCompare:Add, Text, vDupToolCmpLblBPrefix, List
Gui, DupToolCompare:Add, Edit, x+6 yp-2 w140 vDupToolCmpNameB, B
Gui, DupToolCompare:Add, Text, x+6 yp+2 vDupToolCmpLblBSuffix, (one line per item):
Gui, DupToolCompare:Add, Text, x+6 yp vDupToolCmpPosB Right w90, Ln 1 / 1
Gui, DupToolCompare:Add, Edit, vDupToolCmpListB gDupToolListBChanged +Multi WantTab
Gui, DupToolCompare:Add, Button, vDupToolCmpBtnProcess gDupToolCompareProcess, Process
Gui, DupToolCompare:Add, Button, vDupToolCmpBtnClear gDupToolCompareClear, Clear
Gui, DupToolCompare:Add, Button, vDupToolCmpBtnClose gDupToolCompareClose, Close
Gui, DupToolCompare:Add, Text, vDupToolCmpSummary cBlue,
Gui, DupToolCompare:Add, Edit, vDupToolCmpResult ReadOnly +Multi

GuiControlGet, hDupToolCmpListA, DupToolCompare:Hwnd, DupToolCmpListA
GuiControlGet, hDupToolCmpListB, DupToolCompare:Hwnd, DupToolCmpListB
DupTool_UpdateCompareLineInfo()
SetTimer, DupToolCompareCaretWatcher, 120
Gui, DupToolCompare:Show, w980 h680
return

DupToolCompareClear:
GuiControl, DupToolCompare:, DupToolCmpListA,
GuiControl, DupToolCompare:, DupToolCmpListB,
GuiControl, DupToolCompare:, DupToolCmpSummary,
GuiControl, DupToolCompare:, DupToolCmpResult,
DupTool_UpdateCompareLineInfo()
return

DupToolListAChanged:
DupTool_UpdateCompareLineInfo("A")
return

DupToolListBChanged:
DupTool_UpdateCompareLineInfo("B")
return

DupToolCompareProcess:
Gui, DupToolCompare:Submit, NoHide

nameA := Trim(DupToolCmpNameA)
nameB := Trim(DupToolCmpNameB)
if (nameA = "")
	nameA := "A"
if (nameB = "")
	nameB := "B"

countsA := Object(), originalsA := Object(), distinctA := Object(), dupesA := Object()
countsB := Object(), originalsB := Object(), distinctB := Object(), dupesB := Object()

DupTool_BuildCaseInsensitiveMaps(DupToolCmpListA, countsA, originalsA)
DupTool_BuildCaseInsensitiveMaps(DupToolCmpListB, countsB, originalsB)

for k, v in originalsA
	distinctA[k] := v
for k, v in originalsB
	distinctB[k] := v

for k, v in countsA
	if (v > 1)
		dupesA[k] := v
for k, v in countsB
	if (v > 1)
		dupesB[k] := v

CRLF := Chr(13) . Chr(10)
common := ""
onlyA := ""
onlyB := ""
dupesAText := ""
dupesBText := ""

commonCount := 0
onlyACount := 0
onlyBCount := 0
dupesACount := 0
dupesBCount := 0

for k, v in distinctA
{
	if (distinctB.HasKey(k))
	{
		common .= originalsA[k] . CRLF
		commonCount++
	}
	else
	{
		onlyA .= originalsA[k] . CRLF
		onlyACount++
	}
}

for k, v in distinctB
{
	if !distinctA.HasKey(k)
	{
		onlyB .= originalsB[k] . CRLF
		onlyBCount++
	}
}

for k, v in dupesA
{
	dupesAText .= originalsA[k] " (x" v ")" . CRLF
	dupesACount++
}

for k, v in dupesB
{
	dupesBText .= originalsB[k] " (x" v ")" . CRLF
	dupesBCount++
}

if (common = "")
	common := "(none)" . CRLF
if (onlyA = "")
	onlyA := "(none)" . CRLF
if (onlyB = "")
	onlyB := "(none)" . CRLF
if (dupesAText = "")
	dupesAText := "(none)" . CRLF
if (dupesBText = "")
	dupesBText := "(none)" . CRLF

result := "=== Common to " nameA " and " nameB " (" commonCount ") ===" . CRLF
result .= common . CRLF
result .= "=== In " nameA " and not in " nameB " (" onlyACount ") ===" . CRLF
result .= onlyA . CRLF
result .= "=== In " nameB " and not in " nameA " (" onlyBCount ") ===" . CRLF
result .= onlyB . CRLF
result .= "=== Duplicated in " nameA " (" dupesACount ") ===" . CRLF
result .= dupesAText . CRLF
result .= "=== Duplicated in " nameB " (" dupesBCount ") ===" . CRLF
result .= dupesBText

summary := "Distinct " nameA ": " distinctA.Count() " | Distinct " nameB ": " distinctB.Count() " | Common: " commonCount " | Only " nameA ": " onlyACount " | Only " nameB ": " onlyBCount
GuiControl, DupToolCompare:, DupToolCmpSummary, %summary%
GuiControl, DupToolCompare:, DupToolCmpResult, %result%
return

DupToolCompareClose:
DupToolCompareGuiClose:
DupToolCompareGuiEscape:
SetTimer, DupToolCompareCaretWatcher, Off
Gui, DupToolCompare:Destroy
return

DupToolClose:
DupToolMainGuiClose:
Gui, DupToolMain:Destroy
return

DupToolMainGuiSize:
if (A_EventInfo = 1)
	return

w := A_GuiWidth, h := A_GuiHeight
marginX := 10, marginY := 8, gap := 6, txtH := 18, btnH := 26, btnGap := 8

availableH := h - (marginY + txtH + gap + gap + txtH + btnH + marginY + 40)
halfH := Floor(availableH / 2)

yHeader := marginY
yDupLbl := yHeader + txtH + gap
yDupEd := yDupLbl + txtH + gap
yDisLbl := yDupEd + halfH + gap
yDisEd := yDisLbl + txtH + gap
btnY := h - (btnH + marginY)

GuiControl, Move, DupToolLblHeader, % "x" marginX " y" yHeader " w" (w-2*marginX) " h" txtH
GuiControl, Move, DupToolLblDup, % "x" marginX " y" yDupLbl " w" (w-2*marginX) " h" txtH
GuiControl, Move, DupToolDupEdit, % "x" marginX " y" yDupEd " w" (w-2*marginX) " h" halfH
GuiControl, Move, DupToolLblDistinct, % "x" marginX " y" yDisLbl " w" (w-2*marginX) " h" txtH
GuiControl, Move, DupToolDistinctEdit, % "x" marginX " y" yDisEd " w" (w-2*marginX) " h" (availableH - halfH)

btnW := 120
GuiControl, Move, DupToolBtnCopyDup, % "x" marginX " y" btnY " w" btnW " h" btnH
GuiControl, Move, DupToolBtnCopyDistinct, % "x" (marginX + btnW + btnGap) " y" btnY " w" btnW " h" btnH
GuiControl, Move, DupToolBtnCompare, % "x" (marginX + (btnW + btnGap) * 2) " y" btnY " w" 140 " h" btnH
GuiControl, Move, DupToolBtnClose, % "x" (w - marginX - 70) " y" btnY " w" 70 " h" btnH
return

DupToolCompareGuiSize:
if (A_EventInfo = 1)
	return

w := A_GuiWidth, h := A_GuiHeight
marginX := 10, marginY := 8, gap := 6, txtH := 18, btnH := 26, btnGap := 8

paneTotalH := h - (2 * marginY + 3 * txtH + btnH + 6 * gap)
if (paneTotalH < 90)
	paneTotalH := 90

paneH := Floor(paneTotalH / 3)
pane3H := paneTotalH - (2 * paneH)

yA := marginY
yAEd := yA + txtH + gap
yB := yAEd + paneH + gap
yBEd := yB + txtH + gap
btnY := yBEd + paneH + gap
ySum := btnY + btnH + gap
yRes := ySum + txtH + gap

nameW := 140
prefixW := 26
posW := 90
suffixX := marginX + prefixW + 6 + nameW + 6
posX := w - marginX - posW
suffixW := posX - 6 - suffixX
if (suffixW < 80)
	suffixW := 80

GuiControl, Move, DupToolCmpLblAPrefix, % "x" marginX " y" yA " w" prefixW " h" txtH
GuiControl, Move, DupToolCmpNameA, % "x" (marginX + prefixW + 6) " y" (yA - 2) " w" nameW " h" (txtH + 4)
GuiControl, Move, DupToolCmpLblASuffix, % "x" suffixX " y" yA " w" suffixW " h" txtH
GuiControl, Move, DupToolCmpPosA, % "x" posX " y" yA " w" posW " h" txtH
GuiControl, Move, DupToolCmpListA, % "x" marginX " y" yAEd " w" (w-2*marginX) " h" paneH

GuiControl, Move, DupToolCmpLblBPrefix, % "x" marginX " y" yB " w" prefixW " h" txtH
GuiControl, Move, DupToolCmpNameB, % "x" (marginX + prefixW + 6) " y" (yB - 2) " w" nameW " h" (txtH + 4)
GuiControl, Move, DupToolCmpLblBSuffix, % "x" suffixX " y" yB " w" suffixW " h" txtH
GuiControl, Move, DupToolCmpPosB, % "x" posX " y" yB " w" posW " h" txtH
GuiControl, Move, DupToolCmpListB, % "x" marginX " y" yBEd " w" (w-2*marginX) " h" paneH

GuiControl, Move, DupToolCmpBtnProcess, % "x" marginX " y" btnY " w" 100 " h" btnH
GuiControl, Move, DupToolCmpBtnClear, % "x" (marginX + 100 + btnGap) " y" btnY " w" 80 " h" btnH
GuiControl, Move, DupToolCmpBtnClose, % "x" (w - marginX - 70) " y" btnY " w" 70 " h" btnH

GuiControl, Move, DupToolCmpSummary, % "x" marginX " y" ySum " w" (w-2*marginX) " h" txtH
GuiControl, Move, DupToolCmpResult, % "x" marginX " y" yRes " w" (w-2*marginX) " h" pane3H
return

DupToolCompareCaretWatcher:
if !WinExist("ahk_id " hDupToolCompare)
{
	SetTimer, DupToolCompareCaretWatcher, Off
	return
}

ControlGetFocus, focusedCtrl, ahk_id %hDupToolCompare%
if (focusedCtrl = "")
	return

ControlGet, focusedHwnd, Hwnd,, %focusedCtrl%, ahk_id %hDupToolCompare%
if (focusedHwnd = hDupToolCmpListA)
	DupTool_UpdateCompareLineInfo("A")
else if (focusedHwnd = hDupToolCmpListB)
	DupTool_UpdateCompareLineInfo("B")
return

DupTool_BuildCaseInsensitiveMaps(listText, ByRef counts, ByRef originals)
{
	Loop, Parse, listText, `r`n
	{
		line := Trim(A_LoopField)
		if (line = "")
			continue

		upper := line
		StringUpper, upper, upper

		if !originals.HasKey(upper)
			originals[upper] := line

		counts[upper] := counts.HasKey(upper) ? counts[upper] + 1 : 1
	}
}

DupTool_UpdateCompareLineInfo(which := "")
{
	global hDupToolCmpListA, hDupToolCmpListB

	if (which = "" || which = "A")
		DupTool_UpdateOneEditLineInfo(hDupToolCmpListA, "DupToolCmpPosA")

	if (which = "" || which = "B")
		DupTool_UpdateOneEditLineInfo(hDupToolCmpListB, "DupToolCmpPosB")
}

DupTool_UpdateOneEditLineInfo(hEdit, labelVar)
{
	if !hEdit
		return

	lineCount := DupTool_GetEditLineCount(hEdit)
	curLine := DupTool_GetEditCurrentLine(hEdit)

	if (lineCount < 1)
		lineCount := 1
	if (curLine < 1)
		curLine := 1

	GuiControl, DupToolCompare:, %labelVar%, % "Ln " curLine " / " lineCount
}

DupTool_GetEditLineCount(hEdit)
{
	static EM_GETLINECOUNT := 0xBA
	SendMessage, %EM_GETLINECOUNT%, 0, 0,, ahk_id %hEdit%
	return ErrorLevel
}

DupTool_GetEditCurrentLine(hEdit)
{
	static EM_GETSEL := 0xB0
	static EM_LINEFROMCHAR := 0xC9

	SendMessage, %EM_GETSEL%, 0, 0,, ahk_id %hEdit%
	caretPos := ErrorLevel & 0xFFFF

	SendMessage, %EM_LINEFROMCHAR%, %caretPos%, 0,, ahk_id %hEdit%
	return ErrorLevel + 1
}
