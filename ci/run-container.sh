#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
image="${RUNNER_IMAGE:-realworld-api-runner:local}"
report_dir="${REPORT_HOST_DIR:-$root/.ci-local/reports/$(date +%Y%m%d-%H%M%S)-$$}"
mkdir -p "$report_dir"
report_dir="$(cd "$report_dir" && pwd)"
export APP_BASE_URL="${APP_BASE_URL:-http://host.docker.internal:8000/api}"
export TEST_BRANCH="${TEST_BRANCH:-main}" TEST_REPO_URL="${TEST_REPO_URL:-}" TEST_MARKERS="${TEST_MARKERS:-}"
args=(run --rm --init --add-host=host.docker.internal:host-gateway
      --env APP_BASE_URL --env TEST_REPO_URL --env TEST_BRANCH --env TEST_MARKERS
      --mount "type=bind,src=$report_dir,dst=/reports")
if [[ -z "$TEST_REPO_URL" ]]; then args+=(--mount "type=bind,src=$root,dst=/source,readonly"); fi
if [[ -n "$TEST_REPO_URL" && -n "${GIT_SSH_AGENT_SOCKET:-}" ]]; then
  : "${GIT_KNOWN_HOSTS_FILE:?A verified known_hosts file is required}"
  args+=(--mount "type=bind,src=$GIT_SSH_AGENT_SOCKET,dst=/run/ssh-agent,readonly"
         --env SSH_AUTH_SOCK=/run/ssh-agent
         --mount "type=bind,src=$GIT_KNOWN_HOSTS_FILE,dst=/run/secrets/known-hosts,readonly")
elif [[ -n "$TEST_REPO_URL" && -n "${GIT_KEY_FILE:-}" ]]; then
  : "${GIT_KNOWN_HOSTS_FILE:?Both SSH key and verified known_hosts are required}"
  args+=(--mount "type=bind,src=$GIT_KEY_FILE,dst=/run/secrets/git-key,readonly"
         --mount "type=bind,src=$GIT_KNOWN_HOSTS_FILE,dst=/run/secrets/known-hosts,readonly")
fi
# Docker 的前台退出码直接作为 Shell 和 Jenkins 的退出码。
exec docker "${args[@]}" "$image" "$@"
