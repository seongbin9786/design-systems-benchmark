# 분석 대상 소스 — 클론 매니페스트

> 클론 기준일: 2026-07-30 · 방식: `--depth 1 --single-branch` (일부 `--filter=blob:none --sparse`)
> 재현: `bash sources/clone.sh [key ...]` · 이 디렉터리는 `.gitignore` 처리됨 (커밋 대상 아님)

| key | repo | HEAD | HEAD 커밋일 | 용량 | 파일 수 | sparse 경로 |
|---|---|---|---|---:|---:|---|
| `ant-design` | ant-design/ant-design | `dae6efe` | 2026-07-30 | 71M | 4969 | components  |
| `carbon` | carbon-design-system/carbon | `0a75905` | 2026-07-29 | 22M | 9396 | packages/colors packages/elements packages/grid packages/layout packages/motion packages/react packages/styles packages/themes packages/type  |
| `fluentui` | microsoft/fluentui | `a50f6d4` | 2026-07-29 | 86M | 19063 | packages/react-components packages/tokens  |
| `material-ui` | mui/material-ui | `319668c` | 2026-07-29 | 20M | 41098 | packages/mui-material packages/mui-styled-engine packages/mui-system packages/mui-utils  |
| `material-web` | material-components/material-web | `70e259d` | 2026-07-23 | 31M | 1486 | (전체) |
| `polaris` | Shopify/polaris | `2b1ea88` | 2025-12-20 | 14M | 4642 | polaris-react polaris-tokens  |
| `radix-primitives` | radix-ui/primitives | `df8f89a` | 2026-07-28 | 6.6M | 683 | (전체) |
| `react-spectrum` | adobe/react-spectrum | `3823fb8` | 2026-07-30 | 64M | 10147 | packages/@adobe packages/@react-aria packages/@react-spectrum packages/@react-stately packages/@react-types  |
| `shadcn-ui` | shadcn-ui/ui | `5203f53` | 2026-07-29 | 23M | 5679 | apps/v4/registry apps/v4/styles packages  |
| `spectrum-css` | adobe/spectrum-css | `3762086` | 2026-04-06 | 20M | 1252 | (전체) |
| `spectrum-tokens` | adobe/spectrum-design-data | `ca0f605` | 2026-07-29 | 28M | 2011 | (전체) |
