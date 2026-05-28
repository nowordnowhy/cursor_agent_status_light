#!/bin/bash
# Claude Code: UserPromptSubmit -> thinking
DIR="$(cd "$(dirname "$0")" && pwd)"
cat >/dev/null
export HOOK_SOURCE="claude-code"
exec "$DIR/../../agent-light.sh" turn-start
