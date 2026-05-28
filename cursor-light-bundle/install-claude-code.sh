#!/bin/bash
# 在 Claude Code 上安装 CursorLight BLE 联动
# 用法：bash install-claude-code.sh
# 可选：bash install-claude-code.sh /path/to/cursor-light-bundle

set -euo pipefail

SRC="${1:-$(cd "$(dirname "$0")" && pwd)}"
CLAUDE_DIR="${HOME}/.claude"
DEST="${HOME}/.cursor-light"
SETTINGS_JSON="${CLAUDE_DIR}/settings.json"
HOOKS_DIR="${DEST}/claude-code"

echo "==> 源目录: $SRC"
echo "==> 目标:   $DEST"

mkdir -p "$HOOKS_DIR"

# 复制核心脚本
for f in agent-light.sh ble_gate.py cursor_light_ble_enhanced.py; do
  if [[ -f "$SRC/$f" ]]; then
    cp "$SRC/$f" "$DEST/"
    chmod +x "$DEST/$f" 2>/dev/null || true
    echo "  -> $f"
  fi
done

# 复制 Claude Code hook 脚本
if [[ -d "$SRC/claude-code" ]]; then
  for f in "$SRC/claude-code/"hook-*.sh; do
    if [[ -f "$f" ]]; then
      cp "$f" "$HOOKS_DIR/"
      chmod +x "$HOOKS_DIR/$(basename "$f")"
      echo "  -> claude-code/$(basename "$f")"
    fi
  done
fi

# 初始化状态文件
touch "$DEST/ble.log" 2>/dev/null || true
[[ -f "$DEST/state.json" ]] || echo '{}' >"$DEST/state.json"

echo ""
echo "==> 安装 Python 依赖 bleak ..."
python3 -m pip install --user bleak

echo ""
echo "==> 测试 BLE（需 CursorLight 已开机且在旁）..."
if python3 "$DEST/cursor_light_ble_enhanced.py" green; then
  echo "BLE 测试通过。"
else
  echo "BLE 测试未通过，请检查蓝牙权限与硬件（见 PDF 手册）。"
fi

# 生成 settings.json hook 配置指南
echo ""
echo "============================================"
echo "  请将以下 hooks 配置合并到:"
echo "  ${SETTINGS_JSON}"
echo "  (项目级: .claude/settings.json)"
echo "============================================"
echo ""
cat <<'EOF'
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "command": "bash ~/.cursor-light/claude-code/hook-turn-start.sh",
        "matcher": ""
      }
    ],
    "beforeToolUse": [
      {
        "command": "bash ~/.cursor-light/claude-code/hook-busy.sh",
        "matcher": ""
      },
      {
        "command": "bash ~/.cursor-light/claude-code/hook-await-user.sh",
        "matcher": "AskUserQuestion"
      }
    ],
    "Stop": [
      {
        "command": "bash ~/.cursor-light/claude-code/hook-stop.sh",
        "matcher": ""
      }
    ],
    "postToolUseFailure": [
      {
        "command": "bash ~/.cursor-light/claude-code/hook-denied.sh",
        "matcher": ""
      }
    ],
    "SessionEnd": [
      {
        "command": "bash ~/.cursor-light/claude-code/hook-idle.sh",
        "matcher": ""
      }
    ]
  }
}
EOF

echo ""
echo "完成。请重启 Claude Code 使 hooks 生效。"
echo "日志: $DEST/ble.log"
