#!/usr/bin/env bash
# Convert agency-agents-zh role .md files into CAO opencode agent format.
set -u
SRC=/opt/agency-agents-zh
OUT=/opt/agency-agents-zh/cao_profiles
mkdir -p "$OUT"

# Roles that are review / read-only -> role: reviewer
REVIEWERS="engineering-code-reviewer security-compliance-auditor"

FILES=(
  engineering/engineering-frontend-developer
  engineering/engineering-backend-architect
  engineering/engineering-software-architect
  engineering/engineering-devops-automator
  engineering/engineering-ai-engineer
  engineering/engineering-data-engineer
  engineering/engineering-security-engineer
  engineering/engineering-code-reviewer
  security/security-penetration-tester
  security/security-compliance-auditor
  security/security-appsec-engineer
  product/product-manager
  product/product-sprint-prioritizer
  marketing/marketing-xiaohongshu-operator
  marketing/marketing-zhihu-strategist
)

get_field() {
  # $1 = src file, $2 = key
  awk -v k="$2" 'BEGIN{FS=": "}$1==k{print substr($0, index($0,$2)); exit}' "$1"
}

for rel in "${FILES[@]}"; do
  src="$SRC/$rel.md"
  [ -f "$src" ] || { echo "MISSING: $src"; continue; }
  base=$(basename "$rel")
  out="$OUT/$base.md"
  name=$(get_field "$src" name)
  desc=$(get_field "$src" description)
  emoji=$(get_field "$src" emoji)
  role=developer
  for r in $REVIEWERS; do
    [ "$base" = "$r" ] && role=reviewer
  done
  # body = everything after the second '---'
  awk '/^---$/{if(fm==0){fm=1;next}else{fm=2;next}} fm==2{print}' "$src" > /tmp/cao_body.txt
  {
    echo "---"
    echo "name: $name"
    echo "description: $emoji $desc"
    echo "mode: all"
    echo "role: $role"
    echo "permission:"
    echo "  bash: allow"
    echo "  codesearch: deny"
    echo "  edit: allow"
    echo "  glob: allow"
    echo "  grep: allow"
    echo "  question: deny"
    echo "  read: allow"
    echo "  skill: allow"
    echo "  task: deny"
    echo "  todowrite: allow"
    echo "  webfetch: deny"
    echo "  websearch: deny"
    echo "  write: allow"
    echo "---"
    cat /tmp/cao_body.txt
  } > "$out"
  echo "converted: $base -> role=$role"
done
echo "DONE. Output in $OUT"
