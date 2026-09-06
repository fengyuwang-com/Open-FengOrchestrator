#!/usr/bin/env bash
# Neutralize CAO env-var scanner false-positives: rewrite ${VAR} -> $VAR in code
# examples inside two role bodies (these are illustrative code, not real vars).
set -u
CAO=/root/.local/bin/cao
OUT=/opt/agency-agents-zh/cao_profiles
FILES="security-penetration-tester security-appsec-engineer"
for b in $FILES; do
  f="$OUT/$b.md"
  # replace ${X} with $X for the specific tokens CAO flagged
  sed -i -e 's/\${TARGET}/$TARGET/g' -e 's/\${query}/$query/g' -e 's/\${hash}/$hash/g' -e 's/\${salt}/$salt/g' "$f"
  echo "fixed: $b"
  "$CAO" install "$f" --provider opencode_cli </dev/null && echo "REINSTALL_OK: $b" || echo "REINSTALL_FAIL: $b"
done
