# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Freshly scaffolded `uv` project (`uv init --package`). The only code is a placeholder `main()` in `src/code_router/__init__.py`; `README.md` is empty and there are no tests, linter, or formatter configured yet. Update this file as real architecture emerges.

## Commands

Package/env management is `uv` (Python `>=3.15`, pinned in `.python-version`; build backend `uv_build`).

- Install/sync deps: `uv sync`
- Run the CLI entry point (`code-router = "code_router:main"`): `uv run code-router`
- Add a dependency: `uv add <pkg>`

## Configuration

- Runtime deps: `python-dotenv` (load `.env`) and `typesafe-sdk`.
- `.env` holds `TYPESAFE_API_KEY` and is gitignored.
