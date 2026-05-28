#!/bin/bash
# Claude Code: postToolUseFailure -> error
DIR="$(cd "$(dirname "$0")" && pwd)"
_stdin="$(cat)"
[[ -n "$_stdin" ]] && export HOOK_INPUT="$_stdin"
export HOOK_SOURCE="claude-code"
exec "$DIR/../../agent-light.sh" denied
