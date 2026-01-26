---
name: pants-format-check
description: Runs pants formatting, linting, and type checking on Python code, fixing issues automatically. Use when finishing implementation, before committing code, or when the user asks to format, lint, or check code quality.
---

# Pants Format and Lint Check

## When to Use

Apply this skill automatically when:
- Finishing implementation of a feature or fix
- User asks to format, lint, or check code
- Before committing changes
- After modifying Python files

## Workflow

Follow these steps in order:

### Step 1: Remove Unused Imports

Remove unused imports first to prevent common linting errors:

```bash
pants --changed-since=HEAD fix ::
```

This fixes import issues automatically before running full checks.

### Step 2: Run Full Format, Lint, and Check

Run the complete pants check suite:

```bash
pants fmt lint check ::
```

This command:
- **fmt**: Auto-formats code (isort, black, etc.)
- **lint**: Runs linters (flake8, pylint, etc.)
- **check**: Runs type checking (mypy)

### Step 3: Review and Fix Remaining Issues

If errors remain after Step 2:

1. **Read the error output** - pants provides specific file locations and line numbers
2. **Fix the issues** - address each error reported
3. **Re-run**: `pants fmt lint check ::`
4. **Repeat** until all checks pass

## Common Issues and Solutions

### Import Errors
If you see "unused import" or "import not found":
- Remove unused imports
- Add missing dependencies to BUILD files
- Check import paths are correct

### Type Errors
If mypy reports type issues:
- Add type hints where missing
- Fix incorrect type annotations
- Use `# type: ignore` comments only as a last resort

### Style Errors
If flake8/pylint reports style issues:
- Most are auto-fixed by `pants fmt`
- For manual fixes, follow the error message guidance
- Check `.flake8` and `.isort.cfg` for project conventions

## Success Criteria

✅ All checks pass with no errors
✅ No warnings that need attention
✅ Code is properly formatted and typed

## Notes

- Run this from the repository root (where `pants.toml` is located)
- The `::` selector checks all targets in the repo
- For faster checks on specific files, use: `pants fmt lint check path/to/file.py`
- Always run before creating commits to catch issues early
