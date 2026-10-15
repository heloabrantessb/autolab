#!/usr/bin/env bash
set -euo pipefail

autolab_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$autolab_root"

if [[ ! -x .venv/bin/python ]]; then
  printf 'Execute primeiro: bash .devcontainer/setup.sh\n' >&2
  exit 1
fi

autolab_bind="127.0.0.1:8000"
if [[ "${CODESPACES:-false}" == "true" ]]; then
  : "${CODESPACE_NAME:?Nome do Codespace não informado}"
  : "${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:?Domínio de encaminhamento não informado}"
  autolab_host="${CODESPACE_NAME}-8000.${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN}"
  export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1,${autolab_host}"
  export DJANGO_CSRF_TRUSTED_ORIGINS="https://${autolab_host}"
  autolab_bind="0.0.0.0:8000"
fi

# Desenvolvimento apenas. A porta do Codespaces deve permanecer privada.
export LLM_ENABLED=false
exec .venv/bin/python manage.py runserver "$autolab_bind"
