# 派生声明 / Attribution Notice

本目录 `agency-roles/` 中的 `cao_profiles/*.md`（共 **263** 个 CAO agent profile，其中 **260** 个
派生自开源项目 [agency-agents-zh](https://github.com/jnMetaCode/agency-agents-zh)（19 部门全量，
MIT License）；另 3 个（analysis_supervisor / data_analyst / report_generator）为 CAO 框架原生。

原作版权（见 `LICENSE`）：
- Copyright (c) 2025 Michael Sitarzewski（英文原版 agency-agents）
- Copyright (c) 2026 jnMetaCode（中文翻译与本地化）

**署名合规（2026-08-23 修复）**：依 MIT License "版权与许可声明须随副本传播"条款，全部 260 个派生
profile 的正文顶部已逐文件嵌入来源署名行（含上游仓库链接 + 双版权声明 + 派生说明）。转换脚本
`scripts/convert_all_full.sh` 已内置该署名逻辑，后续再生成自动携带，不会再剥离。

转换脚本由 FengOrchestrator 项目编写：
- `scripts/convert_all_full.sh` —— 全量转换（当前使用，含 MIT 署名）
- `convert_to_cao.sh` / `install_cao.sh` / `fix_placeholders.sh` —— 早期 15 角色精选版（已被全量版取代）

依据 MIT License，本目录保留上述版权与许可声明。任何后续扩充或再分发须继续保留原作者署名。
