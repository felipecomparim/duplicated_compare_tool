# Publish Guide (GitHub)

This guide documents the exact commands to publish version 1.0.0.

## 1) Pre-publish validation

1. Execute all checks from [TEST_CHECKLIST.md](TEST_CHECKLIST.md).
2. Record pass/fail in [TEST_RUN_LOG.md](TEST_RUN_LOG.md).
3. Proceed only when all release-gate checks pass.

## 2) Initialize repository (if needed)

Run in project root: duplicated-compare-tool

```powershell
git init
git add .
git commit -m "feat: initial standalone duplicated/compare tool"
```

## 3) Connect remote

```powershell
git branch -M main
git remote add origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```

If remote already exists:

```powershell
git remote set-url origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```

## 4) Tag release 1.0.0

```powershell
git tag -a v1.0.0 -m "v1.0.0"
git push origin v1.0.0
```

## 5) Create GitHub Release

1. Open the repository on GitHub.
2. Go to Releases > Draft a new release.
3. Choose tag: v1.0.0.
4. Title: v1.0.0.
5. Use highlights from [CHANGELOG.md](CHANGELOG.md).
6. Publish release.

## 6) Suggested release notes (copy/adapt)

- Initial standalone AutoHotkey v1 release.
- Duplicate and distinct extraction from clipboard lines.
- Compare 2 lists with common/only A/only B and duplicate analysis.
- Custom list naming in output.
- Input line indicator (Ln X / Y) for both compare panes.
- Responsive layouts for both windows.
