# 디자인 토큰 종합 비교 분석

> 분석 기준일: 2026-07-26
> 분석 대상: 7개 디자인 시스템의 코드 레벨 토큰 아키텍처
> 분석 프레임워크: 정의(Definition) / 소비(Consumption) / 거버넌스(Governance) 3축

---

## 1. 한눈에 보는 비교

| 시스템 | 총 토큰 수 | 계층 | Source of Truth | 런타임 포맷 | 네이밍 | 다크모드 |
|--------|:---------:|:----:|----------------|-----------|--------|---------|
| **Spectrum** | 수백 (JSON) | 3 (palette→semantic→component) | JSON | CSS vars (`--spectrum-*`) | kebab-case | sets (light/dark/wireframe) |
| **Material Web** | ~1,700 | 3 (ref→sys→comp) | SCSS | CSS vars (`--md-sys-*`) | kebab-case | CSS vars 값 교체 |
| **MUI** | ~200 | 2 (palette→component) | JS 객체 | JS context / CSS vars (`--mui-*`) | camelCase | palette.mode / CssVarsProvider |
| **Fluent 2** | ~463 | 2 (Global→Alias) | TypeScript | CSS vars (FluentProvider 주입) | camelCase | 테마 객체 교체 |
| **Carbon** | ~602 (282+243+77) | 3 (Primitive→Core→Component) | TypeScript | CSS vars (`--cds-*`) | kebab-case ($ Sass) | theme() mixin |
| **Polaris** | ~477 | 2 (global→component-private) | TypeScript | CSS vars (`--p-*`, `--pc-*`) | kebab-case | CSS vars 값 교체 |
| **shadcn/ui** | ~32 | 2 (CSS vars→Tailwind) | globals.css | CSS vars | kebab-case | .dark class 토글 |
| **Ant Design** | ~270+ 글로벌 + 컴포넌트별 | 3 (Seed→Map→Alias) | TypeScript | CSS-in-JS → CSS vars (`--ant-*`) | camelCase | 알고리즘 교체 |

---

## 2. 토큰 정의 (Definition) 비교

### 2.1 계층 구조

```
3계층 (primitive → semantic → component):
  Spectrum    palette(blue-100) → semantic(accent-color-100) → component(avatar-border-color)
  Material    ref(md-ref-palette-primary40) → sys(md-sys-color-primary) → comp(md-comp-filled-button-*)
  Carbon      primitive($blue-60) → core($text-primary) → component($button-primary)
  Ant Design  Seed(colorPrimary) → Map(colorPrimaryBg) → Alias(colorLink) + ComponentToken

2계층 (semantic → consumption):
  Fluent 2    Global(colorPaletteRedForeground1) → Alias(colorNeutralBackground1)
  Polaris     Global(--p-color-bg-surface) → Component-private(--pc-button-bg)
  shadcn/ui   CSS vars(--primary) → Tailwind utility(bg-primary)
  MUI         Theme object(palette.primary.main) → Component styles
```

**핵심 차이**: 3계층 시스템은 primitive 값과 semantic 역할을 명시적으로 분리한다. 2계층 시스템은 이 구분이 암묵적이거나 생략된다.

### 2.2 파생 메커니즘

| 방식 | 시스템 | 메커니즘 |
|------|--------|---------|
| **알고리즘 파생** | Ant Design | Seed → `defaultAlgorithm`/`darkAlgorithm` → Map/Alias 자동 생성. HSB 팔레트 알고리즘 (hueStep=2, saturationStep=0.16) |
| **알고리즘 파생** | Material | Dynamic Color: HCT(Hue-Chroma-Tone) 알고리즘으로 벽지 색 → 전체 팔레트 자동 생성 (Android 12+) |
| **참조 기반** | Spectrum | JSON `{blue-100}` 참조 구문으로 상위 토큰 alias |
| **참조 기반** | Carbon | Sass `map.get()` + `theme()` mixin으로 테마별 값 매핑 |
| **참조 기반** | Fluent 2 | TS 객체에서 alias가 global을 직접 참조 |
| **수동 정의** | Polaris | TypeScript에서 테마별로 값 직접 정의, `deepmerge(base, partial)` |
| **수동 정의** | shadcn/ui | globals.css에 light/dark 값을 직접 작성 |
| **수동 정의** | MUI | `createTheme()` JS 객체에 값 직접 정의 |

**Ant Design이 유일한 "입력값 하나로 전체 팔레트 자동 생성" 모델.** `colorPrimary: '#1677ff'` 하나면 10단계 팔레트 + hover/active/bg/border 전부 자동 파생.

### 2.3 Source of Truth

| 시스템 | 원본 포맷 | 원본 위치 | 빌드 파이프라인 |
|--------|----------|----------|---------------|
| Spectrum | JSON | `spectrum-design-data/packages/tokens/src/*.json` | Rust CLI → JSON Schema 검증 → npm |
| Material Web | SCSS | `material-web/tokens/*.scss` | codegen (`versions/v0_192/` 자동 생성) |
| MUI | JavaScript | `@mui/material/styles/createPalette.js` | 없음 (런타임) |
| Fluent 2 | TypeScript | `fluentui/packages/tokens/src/` | token pipeline (자동 생성 주석 확인) |
| Carbon | TypeScript | `carbon/packages/colors/src/colors.ts` | TS → Sass + DTCG JSON 빌드 |
| Polaris | TypeScript | `polaris-tokens/src/` | Rollup → CJS/ESM/CSS/SCSS |
| shadcn/ui | CSS | 사용자 프로젝트 `globals.css` | 없음 (직접 편집) |
| Ant Design | TypeScript | `ant-design/components/theme/interface/` | CSS-in-JS 런타임 / CSS vars 추출 |

**TypeScript가 source of truth인 시스템**: Fluent, Carbon, Polaris, Ant Design (4개)
**CSS/SCSS가 source of truth**: Material Web, shadcn/ui (2개)
**JSON이 source of truth**: Spectrum (1개)
**JavaScript가 source of truth**: MUI (1개)

### 2.4 네이밍 컨벤션

| 시스템 | 컨벤션 | 패턴 | 예시 |
|--------|--------|------|------|
| Spectrum | kebab-case | `{category}-{role}-{variant}` | `accent-color-100`, `avatar-border-color` |
| Material | kebab-case | `md-{layer}-{scope}-{property}` | `md-sys-color-primary`, `md-comp-filled-button-container-color` |
| MUI | camelCase (JS) | `palette.{color}.{shade}` | `palette.primary.main`, `typography.body1` |
| Fluent 2 | camelCase | `{type}{palette}{role}{state}` | `colorNeutralBackground1Hover` |
| Carbon | kebab-case ($) | `${category}-{role}-{level}` | `$text-primary`, `$layer-01`, `$border-subtle-selected-01` |
| Polaris | kebab-case | `--p-{group}-{property}-{role}-{state}` | `--p-color-bg-fill-brand-hover` |
| shadcn/ui | kebab-case | `--{role}` / `--{role}-foreground` | `--primary`, `--muted-foreground` |
| Ant Design | camelCase | `{type}{Category}{Role}{State}` | `colorPrimary`, `colorBgContainer`, `controlHeightLG` |

**camelCase (TS-first)**: Fluent, Ant Design, MUI
**kebab-case (CSS-first)**: Spectrum, Material, Carbon, Polaris, shadcn

### 2.5 다크모드 토큰 처리

| 시스템 | 방식 | 메커니즘 |
|--------|------|---------|
| Spectrum | sets 기반 | JSON `sets` 필드에 light/dark/wireframe 값 분리 정의 |
| Material Web | CSS vars 교체 | `--md-sys-color-primary`: light `#6750a4` → dark `#d0bcff` (tone 역전) |
| MUI | JS 객체 재생성 | `palette.mode: 'dark'` → 테마 객체 재생성 |
| Fluent 2 | 테마 객체 교체 | `webLightTheme` → `webDarkTheme` (alias 토큰 값만 다름) |
| Carbon | Sass mixin | `theme.theme(themes.$g90)` → `--cds-*` CSS vars 값 교체 |
| Polaris | CSS vars 교체 | `deepmerge(base, dark)` → 변경분만 CSS 출력 |
| shadcn/ui | class 토글 | `.dark` 셀렉터에서 동일 변수명 다른 oklch 값 |
| Ant Design | 알고리즘 교체 | `darkAlgorithm` = 팔레트 인덱스 역전 매핑 |

---

## 3. 토큰 소비 (Consumption) 비교

### 3.1 컴포넌트 내 토큰 참조 패턴

| 시스템 | 소비 패턴 | 실제 코드 예시 |
|--------|----------|-------------|
| Spectrum | CSS vars 3단계 fallback | `var(--highcontrast-accent-background-color-default, var(--mod-accent-background-color-default, var(--spectrum-accent-background-color-default)))` |
| Material Web | SCSS mixin → CSS vars | `@include theme.styles();` → `var(--md-sys-color-primary)` |
| MUI | JS theme 접근 | `theme.vars ? theme.vars.palette.primary.main : theme.palette.primary.main` |
| Fluent 2 | Griffel + tokens 객체 | `backgroundColor: tokens.colorNeutralBackground1` |
| Carbon | CSS vars (Sass 경유) | `background: var(--cds-button-primary)` |
| Polaris | CSS vars state machine | `background: var(--pc-button-bg); :hover { background: var(--pc-button-bg_hover); }` |
| shadcn/ui | Tailwind utilities | `className="bg-primary text-primary-foreground hover:bg-primary/90"` |
| Ant Design | CSS-in-JS 토큰 참조 | `backgroundColor: token.colorPrimary` (genStyleHooks 내) |

### 3.2 고유 소비 패턴

**Spectrum — 3단계 CSS fallback**:
```css
/* highcontrast override > module override > system default */
color: var(--highcontrast-alias-color,
       var(--mod-alias-color,
       var(--spectrum-alias-color)));
```
High Contrast 모드와 모듈レベル 오버라이드를 CSS cascade로 해결.

**Polaris — Custom Property State Machine**:
```css
.Button {
  --pc-button-bg: transparent;           /* 기본값 */
  --pc-button-bg_hover: var(--pc-button-bg);
  background: var(--pc-button-bg);
}
.variantPrimary {
  --pc-button-bg: var(--p-color-bg-fill-brand);  /* 변수만 재할당, CSS 선언 없음 */
}
:hover { background: var(--pc-button-bg_hover); }
```
Variant 클래스가 **CSS 프로퍼티 없이 변수만 재할당** — 가장 우아한 패턴.

**Ant Design — 알고리즘 파생 체인**:
```
colorPrimary: '#1677ff' (Seed)
  → genColorMapToken(): colorPrimaryBg, colorPrimaryHover, colorPrimaryActive... (Map)
  → AliasToken: colorLink = colorPrimary (Alias)
  → prepareComponentToken(): Button.colorPrimary = global.colorPrimary (Component)
```
Seed 하나 변경 → 전체 시스템 자동 반영.

**Fluent 2 — Griffel Atomic CSS-in-JS**:
```ts
const useStyles = makeStyles({
  primary: { backgroundColor: tokens.colorBrandBackground },
  subtle: { backgroundColor: tokens.colorSubtleBackground },
});
state.root.className = mergeClasses(baseStyle, styles[appearance], styles[size]);
```
토큰 참조가 스타일 파일에 분산. Component-level 토큰 계층이 의도적으로 없음.

### 3.3 커스터마이징 API

| 시스템 | 전역 | 컴포넌트 | 인스턴스 | 타입 안전성 |
|--------|:----:|:------:|:------:|:---------:|
| Spectrum | Theme 객체 | `--mod-*` CSS vars | `styles` prop | ⚠️ |
| Material Web | CSS vars 오버라이드 | 컴포넌트별 CSS vars | style 속성 | ❌ |
| MUI | `createTheme()` | `components.MuiButton.styleOverrides` | `sx` prop | ✅ |
| Fluent 2 | `FluentProvider theme` | theme designer | slot props | ✅ |
| Carbon | Sass map 오버라이드 | 컴포넌트 SCSS 변수 | className | ⚠️ |
| Polaris | ThemeProvider | ❌ (의도적 제약) | ❌ (탈출구 없음) | ✅ |
| shadcn/ui | globals.css 편집 | globals.css 편집 | className (자유) | ❌ |
| Ant Design | `theme.token` | `theme.components.Button` | `styles`/`classNames` (v6) | ✅ |

**Polaris가 가장 제한적** (의도적), **shadcn/ui가 가장 자유** (full ownership).

---

## 4. 토큰 거버넌스 (Governance) 비교

### 4.1 검증 도구

| 시스템 | 스키마 검증 | lint | diff/changelog | 자동 생성 |
|--------|:---------:|:----:|:------------:|:--------:|
| Spectrum | ✅ JSON Schema (Draft 2020-12) + rule catalog (SPEC-001~006) | ❌ | ✅ `tdiff` CLI (UUID rename 감지) | ✅ Rust CLI |
| Material Web | ❌ | ❌ | ❌ | ✅ codegen (`versions/`) |
| MUI | ✅ TS types | ✅ eslint | ✅ changelog | ❌ |
| Fluent 2 | ✅ TS types | ✅ eslint | ✅ Beachball | ✅ token pipeline |
| Carbon | ✅ TS types + DTCG JSON | ✅ stylelint | ✅ changelog | ✅ TS→Sass/JSON 빌드 |
| Polaris | ✅ TS types | ✅ stylelint-polaris (7개 플러그인) | ✅ changelog | ✅ Rollup 빌드 |
| shadcn/ui | ❌ | ❌ | ❌ | ❌ |
| Ant Design | ✅ TS types (컴파일 타임) | ✅ eslint | ✅ changelog | ✅ CSS-in-JS 런타임 |

**Spectrum이 가장 다층적 검증** (JSON Schema + rule catalog + snapshot + diff + Rust CLI).
**shadcn/ui는 검증 도구 전무** — 사용자 globals.css에 대한 통제 없음.

### 4.2 Deprecation 처리

| 시스템 | 방식 | 예시 |
|--------|------|------|
| Spectrum | `deprecated` + `renamed` + `replaced_by` + `plannedRemoval` 필드 | 가장 체계적 |
| Carbon | v10→v11 이름 변경 매핑 테이블 + `@carbon/upgrade` codemod | `$ui-01` → `$layer-01` |
| MUI | codemod (`@mui/codemod`) | v5→v6 breaking changes |
| Ant Design | v5→v6 토큰 이름 변경 없음, API만 변경 | 단계적 폐기 (v6 경고 → v7 제거) |
| Fluent 2 | Beachball changelog | 패키지별 SemVer |
| Polaris | changelog | React archived로 중단 |
| shadcn/ui | ❌ 없음 | registry `--overwrite` 수동 |
| Material Web | ❌ (maintenance mode) | 토큰 동결 |

### 4.3 다중 포맷 출력

| 시스템 | CSS | JS/TS | JSON | SCSS | Figma |
|--------|:---:|:-----:|:----:|:----:|:-----:|
| Spectrum | ✅ | ✅ | ✅ | ❌ | ❌ |
| Material Web | ✅ | ❌ | ❌ | ✅ (원본) | ❌ |
| MUI | ✅ (CssVars) | ✅ (원본) | ❌ | ❌ | ❌ |
| Fluent 2 | ✅ (런타임) | ✅ (원본) | ❌ | ✅ (별도) | ❌ |
| Carbon | ✅ (--cds-*) | ✅ | ✅ (DTCG) | ✅ (원본) | ❌ |
| Polaris | ✅ | ✅ | ✅ | ✅ | ❌ |
| shadcn/ui | ✅ (원본) | ❌ | ❌ | ❌ | ❌ |
| Ant Design | ✅ (--ant-*) | ✅ (원본) | ❌ | ❌ | ❌ |

**Carbon이 DTCG(W3C Design Tokens Community Group) 표준 JSON을 출력하는 유일한 시스템.**
**Polaris가 4가지 포맷(CJS/ESM/CSS/SCSS) 동시 발행으로 가장 다양.**

### 4.4 AI/도구 통합

| 시스템 | AI 통합 | 특화 도구 |
|--------|--------|---------|
| Spectrum | ✅ MCP 서버 3개 + AI suggest | Rust CLI, tdiff, Figma plugin |
| Ant Design | ✅ DESIGN.md (AI 가드레일) | Theme Editor, @ant-design/cli |
| Fluent 2 | ❌ | theme-designer 패키지 |
| Carbon | ❌ | @carbon/upgrade codemod |
| Polaris | ❌ | stylelint-polaris |
| Material | ❌ | — |
| shadcn/ui | ⚠️ v0.dev (Vercel) | registry CLI |

---

## 5. 핵심 인사이트

### 5.1 토큰 수 ≠ 토큰 품질

| 시스템 | 토큰 수 | 평가 |
|--------|:------:|------|
| Material Web | ~1,700 | 가장 많으나 maintenance mode로 동결 |
| Carbon | ~602 | 3계층 + Layer Level System으로 구조적 |
| Polaris | ~477 | state machine 패턴으로 효율적 소비 |
| Fluent 2 | ~463 | 2계층이나 alias 설계가 정교 |
| Ant Design | ~270+ | 알고리즘 파생으로 "적은 Seed로 많은 파생" |
| MUI | ~200 | 가장 적으나 sx prop으로 유연성 보완 |
| shadcn/ui | ~32 | 최소. 의도적 단순함 |

**shadcn/ui의 32개 토큰은 "부족"이 아니라 "철학"이다.** 상태 토큰(hover/active)을 opacity modifier로 대체하고, primitive 계층 없이 semantic만으로 운영한다.

### 5.2 다크모드 처리의 3가지 패러다임

| 패러다임 | 시스템 | 장단점 |
|---------|--------|--------|
| **알고리즘 반전** | Ant Design | ✅ Seed 하나로 자동 / ❌ 세밀한 제어 어려움 |
| **별도 값 정의** | Spectrum, Fluent, Carbon, Polaris, shadcn | ✅ 세밀한 제어 / ❌ 토큰 수 2배 |
| **톤 역전 매핑** | Material | ✅ 체계적 (primary40↔primary80) / ❌ 구현체별 상이 |

### 5.3 "CSS Custom Properties 미사용" 시스템은 없다

초기 분석에서 Carbon이 "CSS vars 미기본"으로 분류되었으나, **코드 레벨 검증 결과 모든 시스템이 CSS custom properties를 사용한다.** 차이점은:

| 시스템 | CSS vars 역할 |
|--------|-------------|
| Spectrum | 최종 소비 포맷 (3단계 fallback) |
| Material Web | 최종 소비 포맷 |
| MUI | opt-in (CssVarsProvider) |
| Fluent 2 | 런타임 주입 (FluentProvider) |
| Carbon | theme() mixin이 자동 출력 (`--cds-*`) |
| Polaris | 최종 소비 포맷 + state machine |
| shadcn/ui | 원본이자 최종 소비 포맷 |
| Ant Design | v6부터 기본 (`--ant-*`) |

### 5.4 토큰 거버넌스 성숙도

```
높음 ──────────────────────────────────────────── 낮음

Spectrum > Carbon > Polaris > Fluent > Ant > MUI > Material > shadcn
(JSON Schema  (DTCG JSON  (stylelint  (Beachball (TS types (codemod  (동결)  (없음)
+rule catalog  +codemod    7개 플러그인) +pipeline) 만)      만)
+tdiff+Rust)  +upgrade)
```

### 5.5 Figma Variables ↔ Code 토큰: 여전히 미해결

7개 시스템 중 **Figma Variables와 Code 토큰을 자동으로 동기화하는 곳은 없다.**

| 시스템 | Figma 측 | Code 측 | 간극 |
|--------|---------|---------|------|
| Spectrum | Figma plugin (스키마) | JSON → CSS vars | 반자동 (Schema 계약) |
| Material | Figma kit styles | SCSS → CSS vars | 수동 |
| Fluent 2 | Figma Variables | TS → CSS vars | 수동 (동일 조직 정렬) |
| Carbon | Figma Variables (color) | TS → Sass → CSS vars | 수동 |
| Polaris | 미확인 | TS → CSS vars | N/A |
| Ant Design | 서드파티만 | TS → CSS-in-JS/vars | N/A |
| shadcn/ui | 커뮤니티 수동 | CSS vars | N/A |

**이것은 업계 전체의 미해결 문제이다.** DTCG 표준(W3C)이 진행 중이나 아직 Figma Variables ↔ Code tokens의 보편적 브리지가 없다.

---

## 6. 파일 인덱스

| 파일 | 내용 |
|------|------|
| `systems/spectrum-tokens.md` | Spectrum 토큰 코드 레벨 분석 (803줄) |
| `systems/material-tokens.md` | Material 토큰 코드 레벨 분석 (904줄) |
| `systems/fluent-tokens.md` | Fluent 2 토큰 코드 레벨 분석 (1,128줄) |
| `systems/carbon-tokens.md` | Carbon 토큰 코드 레벨 분석 (994줄) |
| `systems/polaris-tokens.md` | Polaris 토큰 코드 레벨 분석 (1,017줄) |
| `systems/shadcn-tokens.md` | shadcn/ui 토큰 코드 레벨 분석 (711줄) |
| `systems/antd-tokens.md` | Ant Design 토큰 코드 레벨 분석 (1,298줄) |
| `comparison/token-analysis-framework.md` | 토큰 분석 프레임워크 |
