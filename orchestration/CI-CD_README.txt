# CI/CD & Auto-Orchestration for AI Testing Suite

## What’s included:
- GitHub Actions workflow: `.github/workflows/ai_suite_autotest.yml`
- Local runner script: `ai_suite_runner.sh` (use with cron, Jenkins, or manual)
- Logs/artifacts auto-uploaded for review

## Setup:
- Ensure all scripts and folders are in place (see main README).
- Add all required API keys as GitHub Actions secrets or env vars for local use.
- Edit runner or workflow for custom test steps.

## Cron example (runs daily at 4:00am):
0 4 * * * /bin/bash /path/to/ai_suite_runner.sh

## Best Practice:
- Run on every push and on a daily/weekly schedule
- Review logs/artifacts after each run for new vulnerabilities, leaks, or exploits

# This makes your suite fully continuous and "attack-persistent".
