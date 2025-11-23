## Placeholder / Work Refusal Keywords
Working pattern: `rg -n --pretty '(?i)(todo|temporary|placeholder|legacy|simplified|for now|backwards compatibility|stub|mock implementation)'`
File types: *.py, *.ts(x), templates, docs
Example found: `apps/accounts/views.py:488-491` – comment admitting “For now, we'll assume it can handle a direct password” instead of confirming the implementation.

## Versioning Hotspots
Working pattern: `rg -n 'create_new_version' -n`
File types: apps/projects/**/*.py
Example found: `apps/projects/services.py:40-114` – entire version-cloning path where the red flags surfaced (drawing filters, placeholder history rows, forced obsoletion).
