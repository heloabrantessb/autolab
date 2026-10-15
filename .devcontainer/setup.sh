#!/usr/bin/env bash
set -euo pipefail
umask 077

autolab_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$autolab_root"

python3 -m venv .venv
.venv/bin/python -m pip install --disable-pip-version-check -r requirements.txt
.venv/bin/python -m pip check

if [[ ! -e .env ]]; then
  cp .env.example .env
fi

mkdir -p var/results
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py check

printf '\nAutoLab preparado. Exercício: codespaces_exercises/arquivos/README.md\n'
printf 'Para iniciar o site: bash .devcontainer/start-site.sh\n'
