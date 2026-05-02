Trainer — CLI Exercise Trainer

Trainer is a command-line exercise training tool to manage, run and
validate programming exercises. It supports importing repositories,
installing exercises into a working directory, running an interactive
sandboxed session, and validating solutions.

## Installation

Install the package in editable/development mode:

```bash
pip install -e .
```

This will install the package and its runtime dependencies (for example
`PyYAML`). After installation the `trainer` command (the CLI) is
available.

## Available Commands

The CLI supports the following subcommands (see `trainer <cmd> -h`
for full options):

- `import <git-url>` — Import an exercises repository into the local
  trainer base directory.
  - Options: `--base-dir` (default: `~/.trainer`)

- `ls` — List exercises available in the base directory.
  - Options: `--base-dir`, `--tag`, `-d/--done` (show already completed),
    `-r/--repo` (filter by repository name)

- `install <exs>` — Install an exercise into a (usually empty) target
  directory.
  - Options: `--base-dir` (where exercises are stored), `--user-dir`

- `exec <exs>` — Create a temporary working directory for the exercise,
  install it there and launch an interactive shell (with timer support).
  - Options: `--base-dir`

- `check` — Run the exercise validation command defined in the
  exercise `config.yml` in the current or provided directory.
  - Options: `--base-dir`, `--user-dir`

- `update` — Pull updates for repositories in the base directory (uses
  git).
  - Options: `--base-dir`, `--repo` (optional specific repo)

- `stats` — Show history statistics (done/failed exercises).
  - Options: `--filter`

- `recommend <reference_alias>` — Recommend similar exercises based on
  tags and difficulty.
  - Options: `--base-dir`, `--top-k`, `--include-done`,
    `--allow-lower-difficulty`, `--min-common-tags`

Note: some internal code paths reference a `time` action for reporting
timer state, but `time` is not defined as a top-level subcommand in the
CLI argument parser. Use `check` and the timer mechanisms that run with
`exec` and `install` workflows.

## Typical workflow

1. Import repositories that contain exercises:

```bash
trainer import https://github.com/your-org/exercises.git
```

2. List available exercises:

```bash
trainer ls --base-dir ~/.trainer
```

3. Run an exercise in a sandboxed shell (creates a temporary working
   directory):

```bash
trainer exec min_1
```

4. Work on the exercise in the interactive shell and then validate the
   solution from within the working directory (or from your user dir):

```bash
trainer check --user-dir /path/to/your/workdir
```

5. Optionally install an exercise into a user directory (useful for
   sharing or persistent workspaces):

```bash
trainer install min_1 --user-dir ~/workspace/min_1
```

## Configuration

Exercises may include a `config.yml` with fields such as `commands`,
`timeout`, `tags`, and `description`. The `check` command runs the
`commands.validate` command (if defined) from the merged configuration
(repository `config.yml` + exercise `config.yml`).

The trainer stores an index file `.trainer_index.yml` in the base
directory (default `~/.trainer`) and history in `~/.trainer/history.yml`.

## Help

General help:

```bash
trainer -h
```

Help for a specific command, e.g.:

```bash
trainer import -h
trainer ls -h
trainer install -h
trainer exec -h
trainer check -h
```
