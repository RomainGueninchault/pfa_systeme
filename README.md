# code-trainer

Lightweight command-line exercise trainer for managing, running and
validating programming exercises.

See `CREATE_EXERCISES.md` for the repository format required by the trainer.

## Installation

Install in editable mode for development:

```bash
pip install -e .
```

After installation the `trainer` CLI is available.

## Quick start

1. Import an exercises repository:

```bash
trainer import https://github.com/your-org/your-exercises-repo
```

2. List available exercises:

```bash
trainer ls
```

3. Run an exercise interactively:

```bash
trainer exec <exercise_alias>
```

4. Validate your solution:

```bash
trainer check
```

## Repository

Source repository:

- GitHub: https://github.com/RomainGueninchault/pfa_systeme

PyPI project:

- https://pypi.org/project/code-trainer/

