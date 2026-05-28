#!/bin/bash
# Claude Code: agent thinking phase (used as fallback)
DIR="$(cd "$(dirname "$0")" && pwd)"
cat >/dev/null
export HOOK_SOURCE="claude-code"
exec "$DIR/../../agent-light.sh" thinking
