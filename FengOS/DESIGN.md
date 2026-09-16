# FengOS DESIGN — UI 设计宪法（所有界面唯一权威）

> 2026-09-13 二轮定稿（董事长指令："找一些大师的 UI，视觉/动画要耳目一新，可以炫技"）。
> **艺术方向 = Linear / Vercel / Raycast 大师公式**：近黑底 + 极光辉光 + 玻璃拟态卡 + 克制单色排版 + 单一紫蓝 accent（来源：[shadcn.io Vercel 风格拆解](https://www.shadcn.io/theme/vercel)、[Muzli 2026 仪表盘精选](https://muz.li/blog/best-dashboard-design-examples-inspirations-for-2026/)、[Awwwards Dark Mode 合集](https://www.awwwards.com/awwwards/collections/dark-mode/)）。
> 一轮的蓝白简洁版被否（"设计的不好"）；更早的黑金 3D 银河同样被否（"太浮夸"），降级为 /galaxy 画册页。
> 判定总纲：**FengOS 是"统一观景台"**——给要看的人看的只读聚合页（两层界面原则 L2），不承担操作。

## 1. 灵魂五条

1. **只读铁律：只聚合，不搬数据。** 只显示各系统探针/API 的真实数据；要操作 → 回对话层找 AI。
2. **近黑 + 极光 + 玻璃。** 底色 #0a0b10；三团极光辉光（紫蓝 #3b3f8f / 青 #1e5f5a / 品红 #5c2c56）以 26-38s 缓慢漂移；卡片 = 半透明白 3.5% + backdrop-blur 16px + 1px 白 8% 边 + 顶部高光线。
3. **一个 accent 家族**：紫蓝 #7c8cff（主）/ 青 #4dd6c1（数据）/ 品红 #e879b9（点缀），仅用于渐变文字、状态灯、曲线、hover 辉光；绝不再引入第四色。
4. **动效是主角**：入场瀑布 rise（卡片按 .04s 级联）、数字滚动 countUp（.9s 三次缓出）、曲线揭示动画、在线灯 pulse 呼吸环、卡片 hover 抬升 + 扫光、`prefers-reduced-motion` 全降级。
5. **一眼看状态**：Hero 大数字（今日提交）置顶，KPI 条其次，服务卡/战报/项目表/体征依序渐进披露。

## 2. 界面清单

| 路径 | 界面 | 说明 |
|---|---|---|
| `/`（index.html） | 统一观景台（默认） | 服务状态卡 + 今日战报 + 项目表 + 生命体征，蓝白简洁 |
| `/galaxy`（galaxy.html） | 帝国版图画册（旧版） | 黑金 3D 银河，保留但降级为展示页，非默认 |

## 3. 聚合清单（唯一真源，改服务列表只改这里）

| 系统 | 端口 | 入口 |
|---|---|---|
| FengInvest | 23456 | http://localhost:23456 |
| FengMedia | 23457 | http://localhost:23457 |
| AIExport | 8787 | http://localhost:8787 |
| CAO 舰队 | 9889 | http://localhost:9889 |
| webcli（FengCloud） | 8443 / 8788 | http://localhost:8443 |
| FlyGo 面板 | 8388 | http://localhost:8388 |

在线判定 = FengOS `/api/system` 返回的 `listenPorts` 是否包含该端口（本机真实探针，禁止假数据）。
