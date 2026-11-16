#!/usr/bin/env bash
set -euo pipefail
umask 022
: "${APP_BASE_URL:?APP_BASE_URL must point to a disposable test environment}"
REPORT_DIR="${REPORT_DIR:-/reports}"
mkdir -p "$REPORT_DIR/allure-results" "$REPORT_DIR/log"
work="$(mktemp -d /tmp/realworld-tests.XXXXXX)"
export REPORT_DIR
# 保留原始退出状态；环境准备失败时也输出可归档的结果。
finish() {
  rc=$?
  trap - EXIT
  if [[ -d "$work/source/log" ]]; then cp -a "$work/source/log/." "$REPORT_DIR/log/" || true; fi
  if [[ ! -f "$REPORT_DIR/junit.xml" ]]; then
    python - "$rc" <<'PY'
import os,sys,xml.etree.ElementTree as ET
suite=ET.Element('testsuite', name='runner-setup', tests='1', errors='1')
case=ET.SubElement(suite,'testcase',name='prepare_test_environment')
ET.SubElement(case,'error',message='Runner stopped before Pytest produced a report').text='See Jenkins console log. Exit code: '+sys.argv[1]
ET.ElementTree(suite).write(os.path.join(os.environ['REPORT_DIR'],'junit.xml'),encoding='utf-8',xml_declaration=True)
PY
  fi
  printf '%s\n' "$rc" > "$REPORT_DIR/exit-code.txt"
  exit "$rc"
}
trap finish EXIT
export GIT_TERMINAL_PROMPT=0
if [[ -n "${TEST_REPO_URL:-}" ]]; then
  # 不在 URL 中传凭据，也不打印仓库地址到日志。
  python - <<'PY'
import os, urllib.parse
url=os.environ['TEST_REPO_URL']
p=urllib.parse.urlsplit(url)
if p.scheme in ('http','https') and (p.username or p.password):
    raise SystemExit('Use mounted Jenkins credentials, not credentials in a Git URL.')
if not (p.scheme in ('https','ssh') or url.startswith('git@')):
    raise SystemExit('TEST_REPO_URL must use HTTPS or SSH.')
PY
  if [[ -S "${SSH_AUTH_SOCK:-/nonexistent}" && -f /run/secrets/known-hosts ]]; then
    export GIT_SSH_COMMAND='ssh -o BatchMode=yes -o UserKnownHostsFile=/run/secrets/known-hosts -o StrictHostKeyChecking=yes'
  elif [[ -f /run/secrets/git-key && -f /run/secrets/known-hosts ]]; then
    export GIT_SSH_COMMAND='ssh -i /run/secrets/git-key -o IdentitiesOnly=yes -o UserKnownHostsFile=/run/secrets/known-hosts -o StrictHostKeyChecking=yes'
  fi
  git clone --quiet --depth 1 --single-branch --branch "${TEST_BRANCH:-main}" -- "$TEST_REPO_URL" "$work/source"
  cd "$work/source"
  git rev-parse HEAD > "$REPORT_DIR/test-commit.txt"
  printf 'git\n' > "$REPORT_DIR/source-mode.txt"
else
  [[ -d /source/tests && -f /source/requirements.txt ]] || { echo 'Mount the test project at /source, or provide TEST_REPO_URL.' >&2; exit 2; }
  mkdir -p "$work/source"
  tar -C /source --exclude='./venv' --exclude='./.venv' --exclude='./.git' --exclude='./.idea' \
    --exclude='./.ci-local' --exclude='./.env' --exclude='./reports' --exclude='./log' --exclude='./.pytest_cache' \
    --exclude='*/__pycache__' -cf - . | tar -C "$work/source" -xf -
  cd "$work/source"
  printf 'local-snapshot\n' > "$REPORT_DIR/source-mode.txt"
  # 本地尚无 Git 时，记录所有代码与数据文件的内容摘要。
  python - <<'PY'
import hashlib,os,pathlib,json
records={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(pathlib.Path('.').rglob('*')) if p.is_file()}
pathlib.Path(os.environ['REPORT_DIR'],'source-files.json').write_text(json.dumps(records,indent=2,ensure_ascii=False))
PY
fi
# 依赖随测试分支同步。额外的 Allure 插件由镜像提供。
python -m pip install --no-cache-dir -r requirements.txt
python -m pip check
python -m pip freeze > "$REPORT_DIR/python-packages.txt"
python - <<'PY'
import os,time,urllib.request,urllib.parse
base=os.environ['APP_BASE_URL'].rstrip('/')
p=urllib.parse.urlsplit(base)
if p.scheme not in ('http','https') or not p.netloc or p.username or p.password:
    raise SystemExit('APP_BASE_URL must be an HTTP(S) test environment URL without credentials.')
for attempt in range(12):
    try:
        with urllib.request.urlopen(base+'/tags',timeout=5) as response:
            if response.status==200: break
    except Exception:
        if attempt==11: raise SystemExit('Test API is not ready; check APP_BASE_URL and backend service.')
        time.sleep(2)
PY
args=(tests/ -q --junitxml="$REPORT_DIR/junit.xml" --alluredir="$REPORT_DIR/allure-results")
[[ -z "${TEST_MARKERS:-}" ]] || args+=(-m "$TEST_MARKERS")
# 不通过 eval 拼接参数；Pytest 退出码原样返回容器。
set +e
test_pid=''
trap '[[ -z "$test_pid" ]] || kill -TERM "$test_pid" 2>/dev/null; exit 143' TERM INT
python -m pytest "${args[@]}" "$@" &
test_pid=$!
wait "$test_pid"
result=$?
set -e
exit "$result"
