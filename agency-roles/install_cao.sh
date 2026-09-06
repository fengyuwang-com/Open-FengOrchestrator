#!/usr/bin/env bash
# Install converted CAO profiles via `cao install --provider opencode_cli`.
set -u
CAO=/root/.local/bin/cao
OUT=/opt/agency-agents-zh/cao_profiles
PASS=0
FAIL=0
FAILLIST=""
FILES=(
  engineering-frontend-developer
  engineering-backend-architect
  engineering-software-architect
  engineering-devops-automator
  engineering-ai-engineer
  engineering-data-engineer
  engineering-security-engineer
  engineering-code-reviewer
  security-penetration-tester
  security-compliance-auditor
  security-appsec-engineer
  product-manager
  product-sprint-prioritizer
  marketing-xiaohongshu-operator
  marketing-zhihu-strategist
)
for b in "${FILES[@]}"; do
  f="$OUT/$b.md"
  if "$CAO" install "$f" --provider opencode_cli </dev/null; then
    echo "INSTALL_OK: $b"
    PASS=$((PASS+1))
  else
    echo "INSTALL_FAIL: $b (rc=$?)"
    FAIL=$((FAIL+1))
    FAILLIST="$FAILLIST $b"
  fi
done
echo "SUMMARY pass=$PASS fail=$FAIL"
[ -n "$FAILLIST" ] && echo "FAILED:$FAILLIST"
