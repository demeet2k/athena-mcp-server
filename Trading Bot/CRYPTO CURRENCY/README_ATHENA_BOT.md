# Athena Bot Runtime

This runtime adds a live-aligned paper-trading layer on top of the existing
time-fractal research stack.

## Install

```powershell
.\.venv\Scripts\python -m pip install -r "CRYPTO CURRENCY\requirements-athena-bot.txt"
```

## Commands

From the repo root:

```powershell
.\.venv\Scripts\python "CRYPTO CURRENCY\athena_cli.py" refresh-data
.\.venv\Scripts\python "CRYPTO CURRENCY\athena_cli.py" scan --once
.\.venv\Scripts\python "CRYPTO CURRENCY\athena_cli.py" paper-loop --iterations 1
.\.venv\Scripts\python "CRYPTO CURRENCY\athena_cli.py" status
.\.venv\Scripts\python "CRYPTO CURRENCY\athena_cli.py" replay --from 2026-01-01 --to 2026-03-01
```

The runtime writes generated artifacts under `CRYPTO CURRENCY/runtime/`.
