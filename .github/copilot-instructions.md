<!-- .github/copilot-instructions.md: Guidance for AI coding agents working on this repository -->
# Python-Course — Copilot instructions

This repository is a collection of small, mostly standalone Python example tools used in a teaching/course context. The goal of these notes is to give an AI coding agent quick, actionable context so edits are correct and idiomatic for this codebase.

Keep suggestions minimal, concrete, and aligned with the repository's style: small single-file scripts, simple CLIs or GUI apps (PySide6), and no heavy refactor unless requested.

Key folders
- `Crop_PNG/` — A Qt6-based GUI bulk image cropper (`bulk_cropper.py`). Uses PySide6 + Pillow. Typical entry: `if __name__ == "__main__": main()`.
- `Encryption/` — Small CLI examples (e.g. `Cesar.py`) that read from `input()` and print results. Expect interactive behavior.
- `Restaurant/`, `Calculator/`, `User_Data/`, `Age_Machine/` — small scripts and demos. Many files are standalone scripts with `main()` entry points.

Project-wide patterns and conventions
- Scripts are simple, single-file programs. Prefer small, focused changes that preserve the original imperative style (interactive CLI or straightforward GUI), unless the user explicitly asks to modernize.
- Look for `if __name__ == "__main__":` blocks as script entrypoints. When adding tests or refactoring, keep `main()` behavior unchanged and ensure CLI/GUI entry still works.
- Dependencies are rarely pinned in a manifest. When modifying files that require external packages, mention the dependency in a one-line note and add it to a `requirements.txt` only if the user asks.
- Naming: some filenames use PascalCase (`Cesar.py`, `Book_Axe.py`) and others lowercase; follow the existing filename casing when creating new files in the same folder.

How to run common examples (developer workflows)
- GUI cropper (Crop_PNG): Requires Python 3.8+ and these packages: `PySide6`, `Pillow`.
  - Run locally: `python Crop_PNG/bulk_cropper.py` (opens a Qt window). The file header documents the dependency line: `pip install PySide6 Pillow`.
- CLI scripts (Encryption/Cesar.py): Run with `python Encryption/Cesar.py` (or `python -m Encryption.Cesar` if you convert to package layout). They prompt via `input()`.

Editing and adding features
- Small fixes: keep changes within the existing file unless you need to add tests or new helper modules. Preserve interactive prompts and printed messages unless requested otherwise.
- When adding parsing for CLI flags, prefer `argparse` but make it optional: keep the existing `input()` fallback to avoid breaking existing usage.
- For GUI code (PySide6), create non-invasive changes (add a new widget or option). If you add long-running operations, use QThread or worker objects as in `bulk_cropper.py` (see `CropWorker` pattern) and emit signals for progress/messages.

Testing and verification
- There are no global test harnesses in the repo. For small changes, run the affected script directly. Examples:
  - `python Crop_PNG/bulk_cropper.py` (manual GUI test)
  - `python Encryption/Cesar.py` (enter sample input when prompted)
- If you add automated tests, scope them per-module using `pytest` and add a minimal `requirements.txt` listing `pytest`.

Integration and external dependencies
- Image work uses Pillow (check `Crop_PNG` files for PIL usage). GUI code uses PySide6. Some folders include compiled artifacts (`Book_Axe.build/`) — avoid editing files under `*.build` and `*.dist` unless explicitly asked.

Files/locations to reference when making changes
- `Crop_PNG/bulk_cropper.py` — canonical PySide6 worker/thread pattern and run flow.
- `Encryption/Cesar.py` — canonical simple CLI input/output style.
- `README.md` (repo root) — very short project description; use it for high-level context only.

Do not change
- Do not modify generated/compiled folders: `Book_Axe.build/`, `Book_Axe.dist/`.

Examples to follow in edits
- When adding background work in GUIs, follow `Crop_PNG/bulk_cropper.py`:
  - Create a QObject worker, move it to QThread, connect `progress`, `message`, `finished` signals and start thread.
- When keeping CLI parity, preserve `input()` prompts and return values (see `Encryption/Cesar.py`).

If you need clarification
- Ask the user which script(s) you should target (file path(s)). If a refactor spans multiple files, propose a small plan and run quick smoke tests.

---
If this file misses any repository-specific quirks you expect the AI to know, tell me which files or patterns to inspect and I'll update these instructions.
