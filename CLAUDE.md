# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

`uv` project (`uv init --package`) with a small CLI package: `src/code_router/__init__.py` (entry point) and `src/code_router/lib/tools.py` (detection logic). It reads a file and identifies its programming language via the TypeSafe API. `README.md` is written (Korean); tests live in `tests/` (pytest); no linter or formatter is configured yet. Update this file as real architecture emerges.

Remote: private GitHub repo `animasana/code-router`, default branch `main`.

## Architecture

Imports inside the package are relative (`from .lib.tools import ...`); a bare `from lib.tools import ...` fails because `lib` is a subpackage of `code_router`, not a top-level package.

`src/code_router/__init__.py`:

- `main()` — loads `.env` (`load_dotenv()`), parses the `file` arg with `argparse`, reads it as UTF-8, prints it, then prints the detected language. A `TypeSafeError` is turned into a `SystemExit` message instead of a traceback.
`src/code_router/lib/tools.py`:

- `detect_language(code)` — one `TypeSafeClient().system_one(...)` call with the code as `state` and a single `Choice` question (`"language"`) whose `criteria` come from `LANGUAGES`. Returns `(choice, confidence)` from `response.choices["language"]`.
- `LANGUAGES` — the candidate labels. The model must pick one, so non-code input needs a fitting label (`plaintext`, `other`) or it gets forced onto the nearest wrong one (plain Korean text was classified as `json` before `plaintext` existed).
- `DESCRIPTIONS` — optional per-label descriptions for labels that are ambiguous by name alone.
- `MIN_CONFIDENCE` (0.6) — below this, output is shown as `언어: 불확실 (가장 유력: ...)`.

The "Jev API" in the user's wording means this `typesafe-sdk` dependency.

## Commands

Package/env management is `uv` (Python `>=3.15`, pinned in `.python-version`; build backend `uv_build`).

- Install/sync deps: `uv sync`
- Run the CLI entry point (`code-router = "code_router:main"`): `uv run code-router <file>` (makes a real API call, needs `TYPESAFE_API_KEY`)
- Add a dependency: `uv add <pkg>`
- Run tests: `uv run pytest` (the TypeSafe client is faked, so no API key or network is needed)
- Add a dev dependency: `uv add --dev <pkg>`

## Configuration

- Runtime deps: `python-dotenv` (load `.env`) and `typesafe-sdk`.
- `.env` holds `TYPESAFE_API_KEY` and is gitignored.
