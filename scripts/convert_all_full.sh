#!/usr/bin/env bash
# 全量导入：agency-agents-zh 所有角色（不评判、不剔除任何角色）
# 扫描全部 19 个角色部门，260 个 .md 全部转成 CAO opencode profile。
# - 在编核心打 【在编】 标记（仅标记，不决定导入与否）
# - reviewer 类设 role: reviewer
# - 不改动 MIT 署名（用户统一处理）
# - 不剔除任何角色（含游戏/GIS/学术/空间计算/垂直行业/C-level）
set -u

SRC=/opt/agency-agents-zh
OUT=~/.aws/cli-agent-orchestrator/agent-store
mkdir -p "$OUT"

# 全部角色部门（含游戏/GIS/学术/空间计算等）
DEPTS="academic design engineering finance game-development gis hr legal marketing paid-media product project-management sales security spatial-computing specialized supply-chain support testing"

# 在编核心标记（高频+中国本地化精品，仅打标不影响导入）
CORE="engineering-ai-engineer engineering-backend-architect engineering-frontend-developer engineering-software-architect engineering-devops-automator engineering-data-engineer engineering-security-engineer engineering-code-reviewer engineering-senior-developer engineering-sre engineering-incident-response-commander engineering-prompt-engineer engineering-wechat-mini-program-developer engineering-feishu-integration-developer engineering-dingtalk-integration-developer engineering-multi-agent-systems-architect design-ui-designer design-ux-architect design-ux-researcher design-brand-guardian design-image-prompt-engineer design-visual-storyteller design-inclusive-visuals-specialist design-persona-walkthrough design-whimsy-injector marketing-growth-hacker marketing-content-creator marketing-seo-specialist marketing-xiaohongshu-operator marketing-xiaohongshu-specialist marketing-douyin-strategist marketing-wechat-official-account marketing-wechat-operator marketing-bilibili-strategist marketing-zhihu-strategist marketing-private-domain-operator marketing-livestream-commerce-coach marketing-china-ecommerce-operator marketing-pr-communications-manager marketing-email-strategist marketing-baidu-seo-specialist finance-financial-analyst finance-tax-strategist finance-fraud-detector finance-fpa-analyst finance-bookkeeper-controller sales-deal-strategist sales-outbound-strategist sales-proposal-strategist sales-coach sales-account-strategist sales-pipeline-analyst hr-recruiter hr-performance-reviewer legal-contract-reviewer legal-policy-writer product-manager product-sprint-prioritizer product-trend-researcher product-feedback-synthesizer project-management-studio-producer project-management-project-shepherd project-manager-senior project-management-meeting-notes-specialist project-management-jira-workflow-steward support-support-responder support-executive-summary-generator support-analytics-reporter testing-api-tester testing-evidence-collector testing-reality-checker testing-performance-benchmarker testing-accessibility-auditor paid-media-ppc-strategist paid-media-paid-social-strategist paid-media-creative-strategist specialized-mcp-builder specialized-workflow-architect automation-governance-architect agents-orchestrator data-privacy-officer specialized-ai-policy-writer customer-success-manager business-strategist specialized-chief-of-staff specialized-pricing-optimizer"

# reviewer 角色（role: reviewer）
REVIEWERS="engineering-code-reviewer security-compliance-auditor testing-evidence-collector testing-reality-checker testing-accessibility-auditor testing-api-tester testing-performance-benchmarker testing-test-results-analyzer support-legal-compliance-checker finance-hk-stock-compliance-reviewer"

in_list() { local needle="$1"; shift; for x in "$@"; do [ "$x" = "$needle" ] && return 0; done; return 1; }

TOTAL=0; CORE_N=0; SKIP_N=0
for d in $DEPTS; do
  for f in "$SRC/$d"/*.md; do
    [ -f "$f" ] || continue
    base=$(basename "$f" .md)
    name=$(awk -F': ' '$1=="name"{print substr($0,index($0,$2));exit}' "$f")
    desc=$(awk -F': ' '$1=="description"{print substr($0,index($0,$2));exit}' "$f")
    emoji=$(awk -F': ' '$1=="emoji"{print substr($0,index($0,$2));exit}' "$f")
    [ -z "$name" ] && { echo "SKIP(no-frontmatter): $base"; SKIP_N=$((SKIP_N+1)); continue; }
    role=developer
    in_list "$base" $REVIEWERS && role=reviewer
    mark=""
    if in_list "$base" $CORE; then mark="【在编】"; CORE_N=$((CORE_N+1)); fi
    awk '/^---$/{if(fm==0){fm=1;next}else{fm=2;next}} fm==2{print}' "$f" > /tmp/cao_body.txt
    {
      echo "---"
      echo "name: $name"
      echo "description: $emoji $mark$desc"
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
      # MIT 合规：保留上游版权与许可声明（MIT 要求署名随副本传播）
      echo ""
      echo "> 来源：[agency-agents-zh](https://github.com/jnMetaCode/agency-agents-zh)（MIT License）｜ Copyright (c) 2025 Michael Sitarzewski（英文原版 agency-agents） / Copyright (c) 2026 jnMetaCode（中文翻译与本地化）。本文件为 CAO profile 派生转换，依 MIT 协议保留原署名。"
      cat /tmp/cao_body.txt
    } > "$OUT/$base.md"
    TOTAL=$((TOTAL+1))
  done
done
echo "DONE. 导入=$TOTAL 在编核心=$CORE_N 跳过(无frontmatter)=$SKIP_N"
echo "agent-store profile 总数: $(ls "$OUT"/*.md | wc -l)"
