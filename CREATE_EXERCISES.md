Exercise repository format for Trainer
====================================

This document explains how to create exercises and exercise repositories
compatible with the `trainer` CLI tool in this repository.

Overview
--------

- Exercises are stored under a base directory (default: `~/.trainer`).
- Each exercise is a directory containing the exercise sources and a
  `config.yml` describing how to prepare, distribute and validate the
  exercise.
- Repositories may include a `common/` folder whose contents are merged
  with each exercise at install time (useful for shared helpers or test
  assets).

Repository layout
-----------------

Recommended structure for a single exercise repository containing one
or more exercises:

```
my-exercises/              # repo root (to be imported by `trainer import`)
├─ config.yml               # OPTIONAL: repo-level defaults merged into exercises
├─ common/                  # OPTIONAL: files copied/merged into every exercise
│  └─ helpers/...
├─ exercises/
│  ├─ ex1/                  # exercise directory (alias used by trainer)
│  │  ├─ config.yml         # REQUIRED for exercise metadata and commands
│  │  ├─ skeleton.c         # sample starting file(s)
│  │  └─ tests/...
│  └─ ex2/
│     ├─ config.yml
│     └─ ...
└─ README.md
```

Important files
---------------

- `config.yml` (exercise-level): core file that describes how to run,
  prepare, distribute and validate the exercise. Exercise `config.yml`
  is merged with an optional repository-level `config.yml` when
  installing.
- `common/` (repo-level): optional directory with shared code or tests
  that will be merged into the exercise working directory when
  installing.

`config.yml` keys
------------------

Typical keys and usages used by the trainer codebase:

- `description`: short textual description of the exercise.
- `language`: programming language hint, e.g. `python`, `javascript`.
- `tags`: list of tag strings used for recommendations and filtering.
- `difficulty`: optional difficulty label or numeric value.
- `timeout`: integer seconds used by the timer to mark overtime.

- `commands` (mapping): commands run by the trainer:
  - `prepare`: shell command executed in a temporary copy of the
    exercise before distributing files (used for compilation or build).
  - `validate`: shell command used by `trainer check` to validate the
    user solution. This command will be run in the user's working
    directory and should exit with status 0 on success.

- `distribute` / `distributes`: list of files/folders to copy from the
  temporary prepared exercise to the user directory. Each item may be:
  - a string: path relative to the exercise root (copied to same
    relative path in target), or
  - a mapping: `{ "source/path": "dest/path" }` to copy/rename.

Note: the installer will automatically add `config.yml` to the list of
files sent to the user's directory if it is not already present in
`distribute`/`distributes`.

- `test`: (optional) list of files (paths relative to the repo base)
  to copy into the user's directory before running validation, used by
  some languages (e.g. JavaScript test harnesses).

Minimal example `config.yml`
----------------------------

```yaml
description: "Sum two integers"
language: python
tags:
  - math
  - beginner
difficulty: 1
timeout: 300
commands:
  prepare: ""   # optional: compile or prepare step
  validate: "python -m pytest -q"   # command executed in user dir
distribute:
  - skeleton.py
  - tests/
```

Notes and best practices
------------------------

- Always provide a `commands.validate` entry; `trainer check` requires
  it and will fail without it.
- If your exercise requires compilation, provide a `commands.prepare`
  command that builds artifacts into the exercise directory before
  distribution.
- Use `distribute` to control exactly which files are copied to the
  user's working directory. If `config.yml` is not listed in
  `distribute`, the installer will automatically include it.
- If you need to copy files to different target paths, use a mapping
  in `distribute`, e.g. `{ "build/myprog": "bin/myprog" }`.
- To include shared helpers or test data across many exercises,
  create a `common/` directory at repo root; its files are merged into
  every exercise at install time unless explicitly overridden by
  `distribute` entries.
- For JavaScript exercises the trainer may copy test files from the
  repository into the user dir when `language: javascript` and a
  `test` list is present.

Indexing and aliases
--------------------

When a repository is imported via `trainer import <git-url>`, an index
is created under the trainer base directory (default `~/.trainer`) in
`.trainer_index.yml`. Exercises are referenced by aliases (directory
names). The trainer sets the environment variable `TRAINER_ALIAS` when
running validation and history recording; your `validate` command may
use this variable if needed.

Quick checklist for authors
--------------------------

- [ ] Add `exercises/<alias>/config.yml` with `commands.validate`.
- [ ] Add `skeleton` files and any tests listed in `distribute`.
- [ ] If compilation is needed, add `commands.prepare`.
- [ ] (Optional) Add repo-level `common/` for shared test helpers.

Questions or improvements
-------------------------

If you want the trainer to support extra config keys or a new
distribution pattern, open an issue or a PR. I can also help update the
CLI to accept additional options (for example explicit alias fields).
