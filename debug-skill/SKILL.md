---
name: debug
description: Debug and troubleshoot the daily stock email pipeline. Use when: (1) daily email fails or doesn't send, (2) AI analysis errors occur, (3) user reports issues with the stock analysis email, (4) testing or verifying the email system is working correctly, (5) checking API keys and configuration.
---

# Debug Skill

Debug tools for the daily stock email pipeline.

## Quick Commands

Run from project root:

```bash
# Check all API configurations
python -m debug-skill.scripts.check_config

# Test email sending only
python -m debug-skill.scripts.test_email

# Test AI analysis with sample stock
python -m debug-skill.scripts.test_ai

# Run full daily analysis dry-run
python -m debug-skill.scripts.dry_run

# View recent logs
python -m debug-skill.scripts.view_logs
```

## Debug Workflow

1. **Check configuration** - Run `check_config` to verify all API keys and settings are set
2. **Test email** - Use `test_email` to send a test email independently
3. **Test AI** - Use `test_ai` to verify AI service works
4. **Dry run** - Use `dry_run` to run full pipeline with verbose output

## Configuration

Required environment variables (see `.env`):
- `GEMINI_API_KEY` - Google Gemini API key
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` - Email settings
- `EMAIL_FROM`, `EMAIL_TO` - Email addresses

## Scripts

- `scripts/check_config.py` - Verify all API keys and settings
- `scripts/test_email.py` - Send test email
- `scripts/test_ai.py` - Test AI with sample stock data
- `scripts/dry_run.py` - Run full analysis with verbose logging
- `scripts/view_logs.py` - Display recent error logs
