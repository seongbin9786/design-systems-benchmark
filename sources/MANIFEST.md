# 분석 대상 소스 — 클론 매니페스트

> 클론 기준일: 2026-07-30 · 방식: `--depth 1 --single-branch` (일부 `--filter=blob:none --sparse`)
> 재현: `bash sources/clone.sh [key ...]` — 아래 **전체 SHA** 를 fetch 해 체크아웃한다.
> 짧은 SHA 로는 `git fetch <sha>` 가 되지 않으므로 전체 SHA 를 기록한다.
> 이 디렉터리는 `.gitignore` 처리됨 (커밋 대상 아님)

| key | repo | HEAD (전체) | 커밋일 | 용량 | 파일 수 | sparse 경로 |
|---|---|---|---|---:|---:|---|
| `ant-design` | ant-design/ant-design | `dae6efed9e3713e281312697b326868d95fb358c` | 2026-07-30 | 71M | 4969 | components |
| `carbon` | carbon-design-system/carbon | `0a75905da8e49901d60354c779fea2245a7a434d` | 2026-07-29 | 22M | 9396 | packages/colors packages/elements packages/grid packages/layout packages/motion packages/react packages/styles packages/themes packages/type |
| `fluentui` | microsoft/fluentui | `a50f6d4d680e8bdb811866473e3a89aea3c89def` | 2026-07-29 | 86M | 19063 | packages/react-components packages/tokens |
| `material-ui` | mui/material-ui | `319668c95b56b44c53541b48c09a2515d07704f5` | 2026-07-29 | 20M | 41098 | packages/mui-material packages/mui-styled-engine packages/mui-system packages/mui-utils |
| `material-web` | material-components/material-web | `70e259d464f627a21c7831cb4e871e0061bc0644` | 2026-07-23 | 31M | 1486 | (전체) |
| `polaris` | Shopify/polaris | `2b1ea88625e0613853ca8577c9acd1980a90f382` | 2025-12-20 | 14M | 4642 | polaris-react polaris-tokens |
| `radix-primitives` | radix-ui/primitives | `df8f89ac8e22e9cd4159e100a644ae94596fdd3a` | 2026-07-28 | 6.6M | 683 | (전체) |
| `react-spectrum` | adobe/react-spectrum | `3823fb84918e5819953092cfba9a603a7200c546` | 2026-07-30 | 64M | 10147 | packages/@adobe packages/@react-aria packages/@react-spectrum packages/@react-stately packages/@react-types |
| `shadcn-ui` | shadcn-ui/ui | `5203f537d152844a920caa66e865bc61c6ff4860` | 2026-07-29 | 25M | 5679 | apps/v4/app apps/v4/lib apps/v4/registry apps/v4/styles packages |
| `spectrum-css` | adobe/spectrum-css | `37620864c60c4c142a506017e1a15348a26abb0e` | 2026-04-06 | 20M | 1252 | (전체) |
| `spectrum-tokens` | adobe/spectrum-design-data | `ca0f605e617e27b3b7a5e0edefcf4ce45400a8fe` | 2026-07-29 | 28M | 2011 | (전체) |
