# 토큰 아키텍처 비교 분석

## 계층 구조 비교

| 시스템 | 계층 수 | 구조 | Source of Truth | 런타임 포맷 |
|--------|:------:|------|----------------|-----------|
| Spectrum | 3 | palette → semantic → component | JSON (spectrum-design-data) | CSS custom properties (--spectrum-*) |
| Material (Web) | 3 | ref → sys → comp | SCSS partials (57개 파일) | CSS custom properties (--md-sys-*) |
| Material (MUI) | 2 | palette/typography → component | JS theme object (createTheme) | CSS vars (--mui-*) or JS context |
| Fluent 2 | 2 | Global → Alias | TypeScript (@fluentui/tokens) | CSS custom properties (FluentProvider 주입) |
| Carbon | 3 | Primitive → Core/Semantic → Component | Sass variables (@carbon/themes) | Sass variables (CSS vars 비기본) |
| Polaris | 2 | Global (--p-*) → Component-private (--pc-*) | TypeScript (polaris-tokens) | CSS custom properties |
| shadcn/ui | 2 | CSS Variables → Tailwind theme | globals.css | CSS custom properties |
| Ant Design | 3 | Seed → Map → Alias (알고리즘 파생) | TypeScript types (camelCase) | CSS-in-JS → CSS vars (v6 기본) |

## 핵심 차이점

### 1. 토큰 파생 방식

| 방식 | 시스템 | 설명 |
|------|--------|------|
| **정적 매핑** | Spectrum, Material, Fluent, Carbon, Polaris, shadcn | 상위 토큰 → 하위 토큰 수동/반자동 참조 |
| **알고리즘 파생** | Ant Design | Seed 토큰 → 알고리즘 함수 → Map/Alias 자동 생성 |

Ant Design의 `darkAlgorithm`, `compactAlgorithm`은 Seed 값 하나로 전체 팔레트/사이즈를 자동 파생한다. 다른 시스템은 다크모드 시 별도 토큰 세트를 수동 정의한다.

### 2. CSS Custom Properties 지원

| 시스템 | CSS vars 기본 | 비고 |
|--------|:-----------:|------|
| Spectrum | ✅ | --spectrum-* |
| Material Web | ✅ | --md-sys-*, --md-comp-* |
| MUI | ✅ (CssVarsProvider) | --mui-*, opt-in |
| Fluent 2 | ✅ | FluentProvider가 DOM 주입 |
| Carbon | ❌ | Sass-first, CSS vars 공식 미지원 |
| Polaris | ✅ | --p-*, --pc-* |
| shadcn/ui | ✅ | --primary 등 |
| Ant Design | ✅ (v6) | --ant-*, v5는 CSS-in-JS |

**Carbon이 유일한 Sass-first 시스템.** 런타임 테마 전환이 제한적.

### 3. 네이밍 컨벤션

| 시스템 | 컨벤션 | 예시 |
|--------|--------|------|
| Spectrum | kebab-case | --spectrum-alias-background-color-primary |
| Material | kebab-case (md- prefix) | --md-sys-color-primary |
| MUI | camelCase (JS) / kebab (CSS) | palette.primary.main / --mui-palette-primary-main |
| Fluent 2 | camelCase | colorNeutralBackground1 |
| Carbon | kebab-case ($ Sass) | $text-primary, $border-subtle-01 |
| Polaris | kebab-case (--p-) | --p-color-bg-fill-brand-hover |
| shadcn/ui | kebab-case | --primary, --muted-foreground |
| Ant Design | camelCase (TS) | colorPrimary, borderRadius |

**camelCase vs kebab-case 분할**: Fluent/Ant = camelCase (TS-first), 나머지 = kebab-case (CSS-first)

### 4. 테마/다크모드 메커니즘

| 시스템 | 방식 | 테마 수 | 중첩 |
|--------|------|:------:|:----:|
| Spectrum | Provider colorScheme + Theme 객체 | 3 (default/dark/light) × 2 scale | ✅ |
| Material Web | CSS vars 값 교체 | light/dark | — |
| MUI | palette.mode 또는 CssVarsProvider | light/dark + custom | ✅ |
| Fluent 2 | FluentProvider theme 객체 | 6 (web/teams × light/dark/HC) | ✅ |
| Carbon | Sass theme mixin | 4 (white/g10/g90/g100) | ✅ (셀렉터 스코프) |
| Polaris | CSS vars 값 교체 | 5 (light/dark/HC/mobile/base) | ✅ |
| shadcn/ui | .dark class 토글 | light/dark | ❌ |
| Ant Design | 알고리즘 교체 (darkAlgorithm) | light/dark/compact + 조합 | ✅ (ConfigProvider) |

### 5. 고유 패턴

| 시스템 | 고유 토큰 패턴 |
|--------|-------------|
| Spectrum | 전용 Rust CLI + JSON Schema 검증 + diff 엔진 |
| Material | Dynamic Color (Android 12+ 벽지 → 팔레트 자동 생성) |
| Fluent 2 | High Contrast 전용 alias 세트, Teams 전용 테마 |
| Carbon | 레이어 레벨 시스템 (01/02/03 중첩 깊이), inverse 토큰 |
| Polaris | custom-property state machine (--pc-* variant가 CSS 선언 없이 변수만 재할당) |
| shadcn/ui | oklch 색상 공간, foreground/background 쌍 구조 |
| Ant Design | Seed→Map→Alias 알고리즘 파생, 컴포넌트 토큰 격리 (genStyleHooks) |

## Figma Variables ↔ Code 토큰 동기화

| 시스템 | Figma Variables | Code 토큰 | 자동 동기화 |
|--------|:--------------:|:---------:|:---------:|
| Spectrum | ✅ (추정) | JSON → CSS vars | ❌ (반자동, Schema 계약) |
| Material | ✅ (킷 내) | SCSS / CSS vars | ❌ |
| Fluent 2 | ✅ (Design Language) | TS → CSS vars | ❌ (비공개) |
| Carbon | ✅ (color 한정) | Sass vars | ❌ |
| Polaris | 미확인 | TS → CSS vars | N/A |
| Ant Design | ❌ (서드파티만) | TS → CSS-in-JS/CSS vars | ❌ |
| shadcn/ui | ❌ | CSS vars | N/A |

**결론: 7개 시스템 모두 Figma Variables → Code tokens 완전 자동 파이프라인이 없다.**
이것은 업계 전체의 미해결 문제이다.
