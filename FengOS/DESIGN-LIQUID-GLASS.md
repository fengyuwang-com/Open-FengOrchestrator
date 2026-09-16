# Liquid Glass（iOS 26 / WWDC 2025）Web CSS 实现规范

> 研究来源：Apple HIG「Materials」、Apple 官方文档《Liquid Glass》《Adopting Liquid Glass》、WWDC25 Session 219《Meet Liquid Glass》与 Session 356、kube.io《Liquid Glass in the Browser》、cloudfour《The Math Behind Nesting Rounded Corners》等社区逆向文章。
>
> **一句话定义**（Apple 官方）：Liquid Glass 是一种动态材质，把底层内容的折射与其色彩融合，同时动态高光和阴影响应周围内容与交互。兼具「光学特性（透镜折射）」与「流动性（果冻形变）」。

## 1. 两种材质变体：Regular vs Clear

| 维度 | Regular（90% 场景） | Clear |
|---|---|---|
| 语义 | 通用、自适应 | 永久透明，仅用于内容可控场景 |
| 透明度 | 底色约 20–40% 叠加强模糊 | 底色 ≤ 8%，靠折射和 rim light 成形 |
| 模糊 | blur ≈ 20–40px | blur 0–4px |
| 场景 | 浮动 TabBar、导航胶囊、工具栏、通知、玻璃卡片 | 控制中心磁贴、媒体全屏悬浮控件 |

**Web 基线（Regular）：**

```css
.glass-regular {
  backdrop-filter: blur(24px) saturate(180%) brightness(1.06);
  background: rgba(255,255,255,.55);   /* dark: rgba(28,28,30,.55), saturate(150%) */
}
```

> `saturate(≥150%)` 是灵魂：模拟 vibrancy，缺了它就是「毛玻璃」不是 Liquid Glass。

## 2. 层级规则：控件层与内容层分离

1. **玻璃悬浮，内容垫底**：导航/控件用玻璃悬浮；正文内容用不透明底层。
2. 控件与内容无固定对位、需跨内容滚动 → 悬浮玻璃（独立投影+rim light）；控件即内容一部分 → 嵌入式薄玻璃（无大投影）。
3. **玻璃上不叠玻璃**（模糊叠加发糊），控件层内用细线 8% 白或间距分隔。
4. 同层级玻璃配方一致。

## 3. 同心圆角（Concentricity）

```
innerRadius = outerRadius − padding
```

- 父 28px 圆角 + 12px padding → 子 16px 圆角，共用曲率圆心。
- 圆角不同心是假玻璃第一破绽。

```css
.glass-card { --pad:12px; border-radius:28px; padding:var(--pad); }
.glass-card__inner { border-radius: calc(28px - var(--pad)); }
```

## 4. 光学细节：rim light、光带、投影、折射

```css
.glass {
  border: 1px solid rgba(255,255,255,.25);
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.45),   /* top rim light */
    inset 0 -1px 0 rgba(255,255,255,.08),  /* bottom rim（暗一档） */
    inset 0 0 20px rgba(255,255,255,.06),
    0 16px 40px rgba(0,0,0,.16),           /* ambient 双层软影 */
    0 2px 8px rgba(0,0,0,.10);             /* contact */
}
.glass::before {  /* 顶部光带 */
  content:""; position:absolute; inset:0; border-radius:inherit;
  background: linear-gradient(180deg, rgba(255,255,255,.22), rgba(255,255,255,.04) 28%, transparent 45%);
  pointer-events:none;
}
```

**折射（lensing）**：backdrop-filter 做不到真折射；进阶用 SVG feDisplacementMap + 位移贴图（R=x, G=y, 128 灰=零偏移），Chrome 系可用，Safari 差。工程上作 progressive enhancement：

```css
.glass { backdrop-filter: blur(20px) saturate(180%); }
@supports (backdrop-filter: url(#liquid-glass)) {
  .glass { backdrop-filter: url(#liquid-glass) blur(6px) saturate(160%); }
}
```

**动效（果冻感）**：`transition: transform .55s cubic-bezier(.34,1.56,.64,1);`（弹簧过冲，response≈0.5s/damping≈0.8）。按压 `scale(.94)` 回弹。

## 5. 色彩与字体

玻璃上文字只用半透明黑/白（vibrancy）：

| 层级 | light | dark |
|---|---|---|
| Primary | rgba(0,0,0,.88) | rgba(255,255,255,.95) |
| Secondary | rgba(0,0,0,.55) | rgba(255,255,255,.65) |
| Tertiary | rgba(0,0,0,.3) | rgba(255,255,255,.4) |
| tint | #007AFF | #0A84FF |

SF Pro 字号：Large Title 34 / Title1 28 / Headline 17(600) / Body 17 / Subhead 15 / Footnote 13 / Caption 12。行高 1.35–1.45。

字体栈：`-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif`。

## 6. Token 表（dark 模式随 media query 切换）

```css
:root {
  --lg-blur:24px; --lg-saturate:180%;
  --lg-bg-light: rgba(255,255,255,.55);  --lg-bg-dark: rgba(28,28,30,.55);
  --lg-rim-top: rgba(255,255,255,.45); --lg-rim-side: rgba(255,255,255,.25);
  --lg-rim-bottom: rgba(255,255,255,.08);
  --lg-shadow-ambient: 0 16px 40px rgba(0,0,0,.16);
  --lg-shadow-contact: 0 2px 8px rgba(0,0,0,.10);
  --lg-radius-card:28px; --lg-radius-inner:16px;
  --lg-tint:#007AFF;
  --lg-spring: cubic-bezier(.34,1.56,.64,1); --lg-spring-dur:.55s;
}
```

## 7. 假玻璃穿帮清单（负规则）

1. 均匀白雾（无层次 rgba .8 + 大 blur）——最常见 AI slop
2. 没有 rim light（塑料贴片感）
3. 圆角不同心
4. 单层硬投影
5. 纯黑纯白实色文字
6. 忘了 saturate()
7. 玻璃叠玻璃
8. dark 模式沿用亮玻璃参数
9. 按压无弹簧回弹
10. 全页滥用玻璃（玻璃只属于导航/控件层）
