#!/bin/bash
# Claude Code: AskUserQuestion -> alarm
DIR="$(cd "$(dirname "$0")" && pwd)"
cat >/dev/null
export HOOK_SOURCE="claude-code"
exec "$DIR/../../agent-light.sh" await-user
