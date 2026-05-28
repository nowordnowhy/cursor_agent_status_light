#!/bin/bash
# Claude Code: SessionEnd -> idle
DIR="$(cd "$(dirname "$0")" && pwd)"
cat >/dev/null
export HOOK_SOURCE="claude-code"
exec "$DIR/../../agent-light.sh" idle
