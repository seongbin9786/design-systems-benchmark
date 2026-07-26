# Shopify Polaris — 벤치마크 분석

> **분석 대상**: Shopify Polaris Design System
> **주요 코드 구현체**: Polaris React (`@shopify/polaris` v13.9.5), Polaris Tokens (`@shopify/polaris-tokens` v9.4.2)
> **후속 구현체**: Polaris Web Components (2025-10-01 릴리스, `<s-button>` 등 커스텀 엘리먼트)
> **GitHub**: [Shopify/polaris-react](https://github.com/Shopify/polaris-react) (2026-01-06 archived, read-only)
> **문서**: [polaris-react.shopify.com](https://polaris-react.shopify.com) (구 polaris.shopify.com → 리다이렉트)
> **분석 기준일**: 2026-07-26

---

## 0. 구조적 특수성: 단일 제품 디자인 시스템 → Web Components 전환기

Polaris는 **Shopify admin** 전용 디자인 시스템으로, 범용 디자인 시스템(Material, Carbon)과 달리 단일 제품 생태계에 강하게 결합되어 있다.

| 구현체 | 플랫폼 | 상태 |
|--------|--------|------|
| Polaris React (`@shopify/polaris`) | React | **Deprecated** (2026-01-06 archived) |
| Polaris Web Components (`<s-button>` 등) | Framework-agnostic (Custom Elements) | **활성** — 2025-10-01 릴리스 |
| Polaris Tokens (`@shopify/polaris-tokens`) | CSS custom properties / JS / JSON | React와 Web Components 공통 토큰 계층 |

**핵심 전환**: Shopify는 React 종속성을 제거하고 프레임워크 비종속적 Web Components로 전환했다. 이는 Figma↔Code 매핑 분석에서 중요한 맥락이다 — 기존 React 구현의 매핑 충실도는 "역사적 스냅샷"이며, 새 Web Components 구현은 아직 문서/커뮤니티 커버리지가 제한적이다.

**라이선스 특수성**: 소스 코드는 MIT 기반이나 **Shopify 연동 애플리케이션으로 사용 제한**. 아이콘/이미지는 별도 Polaris Design Guidelines License Agreement 적용.

---

## 1. 토큰 아키텍처

### 1.1 계층 구조: 2-layer (global token → component-private variable)

Polaris는 Material Design의 3단계(ref → sys → comp)와 달리 **2단계 구조**를 사용한다:

```
Global Design Tokens (--p-*)  →  Component-Private Variables (--pc-{component}-*)
     시맨틱 토큰                      컴포넌트 내부 상태 머신
```

| 계층 | 접두사 | 정의 위치 | 역할 | 예시 |
|------|--------|-----------|------|------|
| **Global tokens** | `--p-` | `@shopify/polaris-tokens` | 크로스-컴포넌트 시맨틱 값 | `--p-color-bg-fill-brand`, `--p-space-400` |
| **Component vars** | `--pc-button-` 등 | 각 컴포넌트 `.module.css` | 컴포넌트 내부 상태별 값 매핑 | `--pc-button-bg_hover`, `--pc-button-color_disabled` |

**Component-private 변수 패턴** (Button 예시):

```css
.Button {
  /* 기본값 선언 — 상태별 cascade */
  --pc-button-bg: transparent;
  --pc-button-bg_hover: var(--pc-button-bg);      /* 미지정 시 기본 상속 */
  --pc-button-bg_active: var(--pc-button-bg);
  --pc-button-bg_disabled: var(--p-color-bg-fill-disabled);  /* global token 참조 */
}

/* Variant는 선언 없이 변수만 재할당 */
.variantPrimary {
  --pc-button-bg: var(--p-color-bg-fill-brand);
  --pc-button-bg_hover: var(--p-color-bg-fill-brand-hover);
  --pc-button-color: var(--p-color-text-brand-on-bg-fill);
}
```

이 구조는 **custom-property state machine**이라 부를 수 있다: variant/tone/size 클래스는 실제 CSS 선언을 변경하지 않고 `--pc-*` 변수만 재할당하며, 기본 `.Button` 클래스의 pseudo-class(`:hover`, `:active`, `:disabled`)가 해당 변수를 소비한다.

### 1.2 네이밍 컨벤션

**Global token**: `--p-{group}-{property}-{role?}-{prominence?}-{state?}`

```
--p-color-bg-fill-brand-hover
│  │     │  │    │     │
│  │     │  │    │     └─ state (hover/active/selected/disabled/focus)
│  │     │  │    └─ semantic role (brand/success/critical/info/caution/warning/magic)
│  │     │  └─ prominence (secondary/tertiary)
│  │     └─ property group (surface/fill → bg 하위)
│  └─ token group (color/space/font/border/shadow/motion/...)
└─ Polaris prefix
```

**Component-private**: `--pc-{component}-{property}_{state}`

```
--pc-button-bg_hover
│  │      │  │
│  │      │  └─ state (underscore 구분)
│  │      └─ property
│  └─ component name
└─ Polaris component prefix
```

**특징**:
- Global token은 **kebab-case** + hyphen(`-`) 구분
- Component-private은 **kebab-case** + state는 underscore(`_`) 구분
- `stylelint-polaris` 패키지가 `--p-*` custom property 사용 규칙과 mainline coverage를 lint로 강제

### 1.3 토큰 그룹 (11개)

| 그룹 | 구조 | 예시 | 용도 |
|------|------|------|------|
| **Color** | `--p-color-[element]-[role?]-[prominence?]-[state?]` | `--p-color-bg-surface`, `--p-color-text-critical` | 배경, 텍스트, 보더, 아이콘 색상 |
| **Space** | `--p-space-[scale]` | `--p-space-400` (16px) | 간격 (4px 기반 스케일, 0~128px, 22개 토큰) |
| **Font** | `--p-font-[property]-[alias]` | `--p-font-size-300`, `--p-font-family-sans` | 폰트 패밀리, 크기, 줄 높이 |
| **Text** | `--p-text-[variant]-[property]` | `--p-text-heading-xl-font-size` | 복합 타이포그래프리셋 |
| **Border** | `--p-border-[property]-[scale]` | `--p-border-radius-200`, `--p-border-width-100` | 보더 너비, 반경 |
| **Shadow** | `--p-shadow-[variant?]-[scale]-[state?]` | `--p-shadow-300`, `--p-shadow-button-primary` | 그림자, elevation |
| **Motion** | `--p-motion-[property]-[alias]` | `--p-motion-duration-100`, `--p-motion-ease-in` | 애니메이션 시간, 이징, 키프레임 |
| **Breakpoints** | `--p-breakpoints-[alias]` | `--p-breakpoints-md` | 반응형 뷰포트 분기점 |
| **Height** | `--p-height-[scale]` | `--p-height-800` | 고정/시맨틱 높이 |
| **Width** | `--p-width-[scale]` | `--p-width-800` | 고정/시맨틱 너비 |
| **Z-Index** | `--p-z-index-[alias]` | `--p-z-index-modal`, `--p-z-index-tooltip` | 스태킹 순서 |

#### Color token 상세 아키텍처

Color는 가장 복잡한 그룹으로, **7개 하위 계층**을 가진다:

| 계층 | 내용 |
|------|------|
| Scheme | `--p-color-scheme: light` — 활성 스킴 식별 |
| Background | `bg-surface`(대형 컨테이너) vs `bg-fill`(소형 컨트롤) 이분 구조 |
| Text | 전경색 + `on-bg-fill` 페어링 토큰 (배경 위 전경색 보장) |
| Border | 보더, focus ring, 상태 보더 |
| Icon | 아이콘 전경색 |
| Component-specific | `--p-color-avatar-*`, `--p-color-input-*`, `--p-color-nav-*` 등 |
| Inverse | 다크 서피스 위 요소용 (`--p-color-text-inverse`) |

**Semantic role 체계**: `brand`, `info`, `success`, `caution`, `warning`, `critical`, `emphasis`, `magic`(AI 관련 UI), `inverse`, `transparent`

**Foreground/background 페어링 토큰**:
```css
--p-color-text-brand-on-bg-fill        /* brand 배경 위 텍스트 */
--p-color-text-success-on-bg-fill      /* success 배경 위 텍스트 */
--p-color-text-critical-on-bg-fill     /* critical 배경 위 텍스트 */
```
이 페어링 토큰은 **접근성(대비율)을 토큰 수준에서 구조적으로 보장**하는 설계이다.

#### Space token 스케일

4px 기반, 18개 코어 + 4개 시맨틱 = **22개 토큰**:

```
0, 1, 2, 4, 6, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96, 112, 128 (px)
```

시맨틱 별칭: `--p-space-button-group-gap`(8px), `--p-space-card-gap`(16px), `--p-space-card-padding`(16px), `--p-space-table-cell-padding`(6px)

### 1.4 테마 전환 / 다크모드

`polaris-tokens/src/themes/` 디렉토리에 **5개 테마**가 TypeScript로 정의되어 있다:

| 테마 파일 | 용도 |
|-----------|------|
| `light.ts` | 기본 라이트 테마 |
| `dark.ts` | 다크모드 |
| `light-high-contrast.ts` | 고대비 라이트 (접근성) |
| `light-mobile.ts` | 모바일 라이트 |
| `base/` | 테마 공통 기반 값 |

**메커니즘**: 동일한 토큰 이름(`--p-color-bg-surface`)에 테마별로 다른 값을 매핑. CSS custom properties 값 교체 방식이므로 **런타임 전환 가능**, React re-render 불필요.

`--p-color-scheme` 토큰이 활성 스킴을 식별하며, `inverse` 토큰 그룹(`--p-color-bg-inverse`, `--p-color-text-inverse`)은 현재 스킴 내에서 반전 컨텍스트를 처리한다.

### 1.5 토큰 포맷

`@shopify/polaris-tokens` 패키지는 **4가지 출력 포맷**을 동시 발행:

| 포맷 | 진입점 | 사용처 |
|------|--------|--------|
| **JavaScript/TypeScript** | `import { tokens } from '@shopify/polaris-tokens'` | React 컴포넌트, JS 로직 |
| **Metadata** | `import { metadata } from '@shopify/polaris-tokens'` | 토큰 value + description |
| **CSS custom properties** | `@shopify/polaris-tokens/css/styles.css` | 브라우저 런타임 |
| **JSON** | `require('@shopify/polaris-tokens/json/spacing.json')` | 빌드 도구, 외부 통합 |

**소스 포맷**: TypeScript (`colors.ts`, `size.ts`, `themes/*.ts`) — Style Dictionary나 Figma Variables가 아닌 **코드-first** 정의. Rollup으로 빌드.

### 1.6 Figma Variables ↔ Code token 동기화

**자동화된 동기화 파이프라인: 확인되지 않음.**

- 토큰 소스는 TypeScript 코드(`polaris-tokens/src/`)이며, Figma Variables에서 생성되지 않는다
- 공식 도구 목록(Tools 페이지)에 Figma 관련 도구가 **없다**
- GitHub 토픽에 `figma-plugin` 태그가 있으나, 문서화된 Figma↔Code 토큰 동기화 파이프라인은 발견되지 않음
- Style Dictionary, Tokens Studio 등 외부 도구 사용 흔적 없음

**판단**: Code-first 토큰 관리. Figma kit가 존재하더라도 토큰 값의 권위 있는 소스(source of truth)는 코드이며, Figma로의 반영은 수동 또는 반자동으로 추정된다.

---

## 2. 컴포넌트 인벤토리

### 2.1 컴포넌트 수

| 소스 | 수 | 비고 |
|------|---:|------|
| **Code (GitHub 디렉토리)** | **122** | `polaris-react/src/components/` 하위 디렉토리 |
| **문서 사이트 공개** | **89** | 67 active + 22 deprecated |
| **내부 전용 (Shopifolk)** | 미공개 | 문서에 "Internal (shopifolk only)" 카테고리 존재 |

Code 122개 중 문서에 노출되지 않는 ~33개는 내부 유틸리티 컴포넌트:
- `AfterInitialMount`, `EphemeralPresenceManager`, `EventListener`, `Focus`, `FocusManager`, `KeypressListener`, `MediaQueryProvider`, `Portal`, `PortalsManager`, `PositionedOverlay`, `ScrollLock`, `Sticky`, `TrapFocus`, `ThemeProvider`, `PolarisTestProvider` 등
- `UnstyledButton`, `UnstyledLink`, `Truncate`, `InlineCode`, `ShadowBevel` 등 내부 기반 컴포넌트
- `Connected`, `Labelled`, `Label`, `Choice`, `CheckableButton` 등 합성용 내부 컴포넌트

### 2.2 분류 체계 (12개 카테고리)

| 카테고리 | Active 수 | 주요 컴포넌트 |
|----------|----------:|--------------|
| **Actions** | 3 | Button, ButtonGroup, AccountConnection |
| **Layout and structure** | 14 | Box, BlockStack, InlineStack, InlineGrid, Grid, Card, Page, Layout, Divider, Bleed, CalloutCard, EmptyState, FormLayout, MediaCard |
| **Selection and input** | 16 | TextField, Select, Checkbox, RadioButton, ChoiceList, Autocomplete, Combobox, DatePicker, DropZone, Filters, IndexFilters, ColorPicker, RangeSlider, Tag, Form, InlineError |
| **Images and icons** | 5 | Icon, Avatar, Thumbnail, VideoThumbnail, KeyboardKey |
| **Feedback indicators** | 10 | Badge, Banner, ProgressBar, Spinner, ExceptionList, SkeletonBodyText, SkeletonDisplayText, SkeletonPage, SkeletonTabs, SkeletonThumbnail |
| **Typography** | 1 | Text |
| **Tables** | 2 | DataTable, IndexTable |
| **Lists** | 7 | ActionList, DescriptionList, List, Listbox, OptionList, ResourceItem, ResourceList |
| **Navigation** | 4 | Link, Pagination, Tabs, FooterHelp |
| **Overlays** | 2 | Popover, Tooltip |
| **Utilities** | 3 | AppProvider, Collapsible, Scrollable |
| **Deprecated** | 22 | Modal, Frame, Navigation, TopBar, Toast, Sheet, LegacyCard, LegacyStack, LegacyTabs, LegacyFilters 등 |

### 2.3 커버리지 분석

| 영역 | 커버리지 | 비고 |
|------|----------|------|
| 폼/입력 | ★★★★★ | 16개, 가장 풍부한 카테고리 |
| 레이아웃 | ★★★★★ | Box + Stack 계열(Box, BlockStack, InlineStack, InlineGrid, Grid, Bleed) — 토큰 기반 레이아웃 프리미티브 |
| 데이터 표시 | ★★★★☆ | DataTable, IndexTable, ResourceList, DescriptionList |
| 피드백 | ★★★★☆ | Banner, Badge, ProgressBar, Spinner + 5개 Skeleton |
| 네비게이션 | ★★★☆☆ | Tabs, Pagination, Link — Frame/Navigation/TopBar는 deprecated |
| 오버레이 | ★★☆☆☆ | Popover, Tooltip만 active — Modal, Sheet deprecated |
| 타이포그래피 | ★★☆☆☆ | `Text` 단일 컴포넌트로 통합 (구 DisplayText, Heading, Caption, Subheading, TextStyle deprecated) |

**Deprecated 패턴**: v12→v13 전환에서 다수 컴포넌트가 deprecated되고 통합되었다:
- 5개 타이포그래피 컴포넌트 → `Text` 1개로 통합
- `LegacyCard` (props 기반) → `Card` (composition 기반)
- `Frame`, `Navigation`, `TopBar` 등 앱 셸 컴포넌트 deprecated

### 2.4 복합 컴포넌트 (Compound Components)

Polaris는 **compound component 패턴을 적극 사용**한다:

| 컴포넌트 | Sub-components | 패턴 |
|----------|---------------|------|
| `Card` | `Card.Header`, `Card.Section`, `Card.Subsection`, `Card.Footer` | 구조적 합성 |
| `IndexTable` | `IndexTable.Row`, `IndexTable.Cell` 등 | 테이블 구조 |
| `Autocomplete` | `Autocomplete.ComboBox` 등 | 복합 입력 |
| `ActionList` | `ActionList.Item`, `ActionList.Section` | 목록 구조 |
| `ResourceList` | `ResourceList.Item` | 리소스 목록 |
| `Filters` | 필터 항목 합성 | 필터 패널 |

**흥미로운 전환**: `LegacyCard`(props 기반 configuration) → `Card`(JSX composition)로의 마이그레이션은 Polaris가 **configuration에서 composition으로 설계 철학을 이동**했음을 보여준다.

---

## 3. Figma↔Code 매핑 충실도 (핵심)

### 3.1 공식 Figma kit 현황

**공식 도구 목록에 Figma kit가 없다.** Polaris React 문서의 Tools 섹션에는 다음만 포함:
- Polaris for VS Code (VS Code 확장)
- Polaris Migrator (codemod)
- Stylelint Polaris (lint 규칙)
- Sandbox (프로토타이핑, alpha)

Figma Community에서 "Shopify Polaris" 검색 시 서드파티 키트가 존재할 수 있으나, **Shopify 공식 Figma kit의 공개 여부는 확인되지 않는다**. GitHub 저장소 토픽에 `figma-plugin` 태그가 있으나, 저장소가 archived되어 상세 확인이 제한적이다.

### 3.2 1:1 대응률

| 항목 | 평가 |
|------|------|
| Figma 컴포넌트 수 | **확인 불가** (공식 kit 미발견) |
| Code 컴포넌트 수 | 122 (code) / 89 (docs) |
| 1:1 매핑 비율 | **측정 불가** |

공식 Figma kit가 공개되어 있지 않으므로 정량적 1:1 대응률 산출이 불가능하다.

### 3.3 네이밍 정합성 (추정)

Figma kit가 확인되지 않으므로, 문서와 코드 간 정합성으로 대체 분석:

| 항목 | 정합도 | 근거 |
|------|--------|------|
| 컴포넌트명 | ★★★★★ | 문서명 = 코드명 (Button, Card, TextField 등 PascalCase 일치) |
| Props명 | ★★★★☆ | 문서 props 테이블 = TypeScript interface (`ButtonProps`, `CardProps`) |
| Variant 값 | ★★★★★ | `variant="primary"`, `tone="critical"`, `size="large"` — 문서/코드 동일 enum |
| Token명 | ★★★★★ | 문서 토큰 페이지 = CSS custom properties = JS token 객체 (3방향 일치) |

### 3.4 Variant 정합성

Button 기준, 문서/코드 variant 매트릭스:

| 차원 | 값 | Figma 매핑 |
|------|-----|-----------|
| `variant` | `plain`, `primary`, `secondary`, `tertiary`, `monochromePlain` | 확인 불가 |
| `tone` | `success`, `critical` | 확인 불가 |
| `size` | `micro`, `slim`, `medium`, `large` | 확인 불가 |
| `fullWidth` | boolean | 확인 불가 |
| `disabled` | boolean | 확인 불가 |
| `loading` | boolean | 확인 불가 |

CSS 구현에서 variant × tone × size는 `:is()` 셀렉터로 조합되며, 이는 Figma의 variant property 구조와 개념적으로 대응한다.

### 3.5 토큰 정합성

**Code 내부 3방향 정합성은 매우 높다**:

```
TypeScript source (colors.ts)
    ↓ Rollup build
CSS custom properties (--p-color-bg-surface)  ←→  JS token object (tokens.color['color-bg'])
    ↓ 문서 사이트 자동 생성
Token reference page (polaris-react.shopify.com/tokens/color)
```

- `metadata` 객체에 각 토큰의 `value` + `description` 포함 → 문서 자동 생성
- `stylelint-polaris`가 소비 앱에서 `--p-*` 토큰 사용 규칙을 lint로 강제

**Figma Variables와의 정합성**: 확인 불가. Code-first 구조이므로 Figma가 code token을 미러링하는 방향일 것으로 추정.

### 3.6 구조적 대응

| Figma 개념 | Code 대응 | 정합도 |
|-----------|----------|--------|
| Auto Layout | CSS Flexbox (`display: inline-flex`, `gap: var(--pc-button-gap)`) | 높음 (추정) |
| Component Properties | React props (TypeScript interface) | 높음 (추정) |
| Variants | CSS Module 클래스 + custom property 재할당 | 높음 (추정) |
| Styles (color, text) | CSS custom properties (`--p-*`) | 높음 (추정) |
| Constraints | 반응형 props (`padding?: {[Breakpoint]?: T}`, `roundedAbove`) | 중간 |

### 3.7 매핑 방향

**Code-first.**

근거:
1. 토큰 소스가 TypeScript 코드(`polaris-tokens/src/`)
2. 공식 도구 목록에 Figma 관련 도구 없음
3. 문서 사이트가 코드에서 자동 생성
4. `stylelint-polaris`, `polaris-for-vscode` 등 코드 중심 도구만 존재
5. GitHub 저장소 토픽에 `figma-plugin`이 있으나, 이는 Figma→Code가 아닌 Code→Figma 방향의 플러그인일 가능성

**Polaris Web Components 전환의 영향**: 2025-10-01 Web Components 릴리스로 코드 구현체가 React에서 Custom Elements로 전환되면서, 기존 Figma kit(존재한다면)와의 매핑이 재정의되어야 하는 상황이다.

### 3.8 종합 평가

| 항목 | 점수 | 비고 |
|------|------|------|
| 1:1 대응률 | **N/A** | 공식 Figma kit 미확인 |
| 네이밍 정합성 | **N/A** (code 내부: ★★★★★) | Figma 측 측정 불가 |
| Variant 정합성 | **N/A** | Figma 측 측정 불가 |
| 토큰 정합성 | **N/A** (code 내부: ★★★★★) | Figma Variables 미확인 |
| 구조적 대응 | **N/A** | Figma kit 미확인 |
| 매핑 방향 | **Code-first** | 명확 |

> **분석 한계**: Polaris는 공식 Figma kit를 공개하지 않거나, 공개했더라도 문서/도구 목록에서 발견되지 않는다. 이는 Figma↔Code 매핑 충실도라는 벤치마크 핵심 질문에 대해 **구조적으로 평가가 어려운 시스템**임을 의미한다. Polaris의 설계 철학 자체가 "코드가 권위 있는 소스"이며, Figma는 디자인 탐색 도구로만 사용될 가능성이 높다.

---

## 4. API 설계 철학

### 4.1 패턴: Configuration + Composition 하이브리드

Polaris는 컴포넌트 성격에 따라 두 패턴을 **의도적으로 분리**한다:

#### Configuration 기반 (제어형 컴포넌트)

**Button**이 대표적:

```jsx
<Button variant="primary" size="large" tone="critical" icon={DeleteIcon} loading disabled>
  Delete
</Button>
```

- `children`이 `string | string[]`로 제한 — **JSX 합성 불가**
- 아이콘, disclosure, 스피너 모두 props로 주입
- `url` prop으로 `<a>` 렌더링 (polymorphic), `as` prop 없음
- 외형은 100% props 결정, **`className`/`style` 탈출구 없음**

이 패턴은 Button, Badge, Banner, TextField, Select 등 **원자적 UI 컨트롤**에 적용된다.

#### Composition 기반 (구조적 컴포넌트)

**Card**가 대표적:

```jsx
<Card>
  <Card.Header actions={[{content: 'Edit'}]}>
    <Text as="h2" variant="headingMd">주문 상세</Text>
  </Card.Header>
  <Card.Section title="배송" subdued>
    <BlockStack gap="400">...</BlockStack>
  </Card.Section>
  <Card.Footer actions={[{content: '저장'}]} />
</Card>
```

- `children: React.ReactNode` — 자유 합성
- Static sub-components (`Card.Header`, `Card.Section`, `Card.Subsection`, `Card.Footer`)
- `LegacyCard`(props 기반) → `Card`(composition) 마이그레이션 = **설계 철학 전환의 증거**

이 패턴은 Card, IndexTable, ActionList, ResourceList 등 **구조적 컨테이너**에 적용된다.

#### 레이아웃 프리미티브

`Box`, `BlockStack`, `InlineStack`, `InlineGrid`, `Grid`, `Bleed` — **토큰 기반 레이아웃 시스템**:

```jsx
<Box padding="400" background="bg-surface" borderRadius="200">
  <BlockStack gap="200">
    <Text as="p" variant="bodyMd">내용</Text>
  </BlockStack>
</Box>
```

- 스타일 값을 **토큰 별칭**(`SpaceScale`, `ColorBackgroundAlias`)으로만 받음
- raw CSS 값 전달 불가 → 디자인 시스템 준수를 API 수준에서 강제

### 4.2 스타일링: CSS Modules + Custom Properties 이중 구조

| 계층 | 기술 | 역할 |
|------|------|------|
| **스코핑** | CSS Modules (`.module.css`) | 클래스명 해싱, 컴포넌트 격리 |
| **테마/상태** | CSS Custom Properties (`--p-*`, `--pc-*`) | 테마 전환, 상태 머신 |
| **lint** | `stylelint-polaris` | `--p-*` 토큰 사용 강제, 임의 CSS 값 차단 |

**소비자 측면**: `className`, `style`, `sx` prop 등 **어떤 스타일 탈출구도 제공하지 않는다**. 이는 Material UI(`sx` prop), Chakra UI(`styled-system`)와 근본적으로 다른 철학이다.

> "Polaris는 커스터마이징이 아닌 **일관성**을 위해 존재한다" — Shopify admin 생태계의 통일성을 위한 의도적 제약.

### 4.3 Headless 분리

**없음.** Polaris는 headless/styled 분리를 제공하지 않는다.

- Radix UI, Headless UI와 달리 로직-스타일 분리 계층 없음
- `UnstyledButton`, `UnstyledLink` 등 내부 기반 컴포넌트가 있으나, 이는 공개 API가 아닌 내부 구현체
- 모든 컴포넌트가 Polaris 비주얼로 고정

### 4.4 커스터마이징

| 방법 | 지원 여부 | 비고 |
|------|-----------|------|
| 테마 (light/dark/high-contrast) | ✅ | `ThemeProvider`, 토큰 값 교체 |
| 토큰 오버라이드 | ⚠️ 제한적 | `--p-*` CSS 변수 오버라이드 기술적으로 가능하나 비권장 |
| `className`/`style` | ❌ | 제공하지 않음 |
| Slot/Recipe 시스템 | ❌ | 없음 |
| Compound composition | ✅ | Card, IndexTable 등 구조적 컴포넌트 |
| Responsive props | ✅ | `{xs: '400', sm: '500'}` breakpoint-keyed 객체 |

---

## 5. 접근성

### 5.1 표준 준수

| 항목 | 수준 |
|------|------|
| **WCAG** | **2.1 Level A + AA** 목표 |
| **WAI-ARIA** | 네이티브 HTML 우선, ARIA는 보충적으로 사용 |
| **테스트** | 자동화 + 수동 + 통합 후 태스크 플로우 테스트 |

### 5.2 내장 ARIA

Button 컴포넌트에서 확인되는 ARIA 설계:

| 기능 | 구현 |
|------|------|
| 시맨틱 엘리먼트 자동 전환 | `url` prop → `<a>`, 기본 → `<button>` |
| `accessibilityLabel` | `aria-label` 매핑, 아이콘 전용 버튼에 필수 |
| `pressed` | `aria-pressed` (토글 버튼) |
| `ariaControls` + `ariaExpanded` | disclosure/expand-collapse 패턴 |
| `ariaChecked` | 스위치 토글 |
| `role` | WAI-ARIA role 오버라이드 |
| `disabled` / `loading` | 시각 + 프로그래매틱 동시 전달 |

**설계 철학**: ARIA를 소비자가 직접 작성하는 것이 아니라, **props를 통해 라이브러리가 자동 적용**. 올바른 props 선택 = 올바른 ARIA.

### 5.3 키보드 네비게이션

| 원칙 | 내용 |
|------|------|
| 브라우저 기본 동작 우선 | Tab/Shift+Tab 포커스, Enter/Space 활성화 |
| 커스텀 키 조작 최소화 | 비표준 키 바인딩 지양 |
| 포커스 관리 자동화 | Modal, Popover 등 오버레이 열림 시 포커스 자동 이동 |
| 예기치 않은 포커스 이동 금지 | 백그라운드 콘텐츠 업데이트 시 포커스 이동 ❌ |

### 5.4 스크린 리더 지원

- 스크린 리더, 음성 인식, 저시력/색맹 도구, 대체 키보드, 스위치 장치 지원 목표
- 아이콘/이미지에 대체 텍스트 필수
- `accessibilityLabel`에 표시 텍스트 포함 권장 (음성 인식 명령 매칭)
- 외부 링크에 "(opens a new window)" 자동 안내 패턴

### 5.5 접근성 특화 토큰

- `light-high-contrast` 테마: 고대비 모드 전용 토큰 세트
- Foreground/background 페어링 토큰 (`--p-color-text-*-on-bg-fill`): 대비율 구조적 보장
- `--p-color-border-focus`: 포커스 링 전용 토큰

---

## 6. 동기화 거버넌스

### 6.1 Figma↔Code 동기화 프로세스

| 항목 | 상태 |
|------|------|
| 공식 Figma kit | **미확인** (Tools 페이지에 없음) |
| Figma→Code 자동화 | **없음** (Code-first) |
| Code→Figma 자동화 | **미확인** (GitHub `figma-plugin` 토픽 존재하나 상세 불명) |
| 토큰 동기화 도구 | Style Dictionary, Tokens Studio 등 **미사용** |
| 토큰 소스 | TypeScript 코드 (`polaris-tokens/src/`) |

**판단**: Polaris는 **Code-first 거버넌스** 모델이다. 토큰과 컴포넌트의 권위 있는 소스는 코드이며, Figma는 디자인 탐색/의사소통 도구로 사용되더라도 시스템 of record가 아니다.

### 6.2 릴리스 주기

| 항목 | 내용 |
|------|------|
| 마지막 릴리스 | `@shopify/polaris@13.9.5` (2025-03-26) |
| 릴리스 방식 | **자동화** — `shopify-github-actions-access[bot]` 발행 |
| 동시 발행 | monorepo 내 패키지 동시 patch 릴리스 (2025-03-17: polaris, polaris-tokens, stylelint-polaris, polaris-migrator 동시) |
| 버전 관리 | Changesets (`/.changeset/`) |
| 빌드 도구 | pnpm workspaces + Turborepo |
| 현재 상태 | **Archived** (2026-01-06) — 더 이상 릴리스 없음 |

### 6.3 기여 모델

| 항목 | 내용 |
|------|------|
| 오픈소스 여부 | 소스 공개, 그러나 **Shopify 연동 앱 사용 제한** 라이선스 |
| 기여 수용 | **중단** — "no longer accepting contributions or feature requests" |
| 이슈 | GitHub Issues 읽기 전용 |
| 후속 프로젝트 | Polaris Web Components (shopify.dev) |

### 6.4 Polaris Web Components 전환

| 항목 | 내용 |
|------|------|
| 릴리스일 | 2025-10-01 |
| 아키텍처 | Custom Elements (`<s-button>`, `<s-section>` 등) |
| 프레임워크 | React, Vue, Svelte, vanilla JS 등 **프레임워크 비종속** |
| 토큰 | `@shopify/polaris-tokens` 공유 (동일 `--p-*` 체계) |
| 마이그레이션 | `polaris-migrator` codemod + Shopify AI Toolkit (2026-06-11) |
| 문서 | shopify.dev (URL 구조 확인 중) |

**벤치마크 시사점**: Polaris는 분석 시점(2026-07)에서 **전환기**에 있다. React 구현은 archived, Web Components는 아직 커뮤니티 문서/커버리지가 제한적. Figma kit 존재 여부와 관계없이, 구현체 전환 자체가 Figma↔Code 매핑의 연속성을 단절시키는 요인이다.

---

## 7. 종합 평가

### 강점

| 영역 | 평가 |
|------|------|
| 토큰 설계 | `--p-*` / `--pc-*` 2계층 custom-property state machine은 우아하고 실용적 |
| 시맨틱 토큰 | `bg-surface` vs `bg-fill`, `on-bg-fill` 페어링 등 **도메인 특화 시맨틱**이 정교 |
| 접근성 | WCAG 2.1 AA, props 기반 ARIA 자동화, high-contrast 테마 |
| API 일관성 | configuration(원자) + composition(구조) 분리 원칙이 명확 |
| 디자인 시스템 강제력 | `className`/`style` 탈출구 제거, `stylelint-polaris` lint — **준수를 API 수준에서 강제** |

### 약점 / 한계

| 영역 | 평가 |
|------|------|
| Figma 통합 | 공식 Figma kit 미확인, Figma↔Code 동기화 파이프라인 부재 |
| 커스터마이징 | 의도적 제약이나, 복잡한 커스텀 UI 요구 시 탈출구 없음 |
| 생태계 연속성 | React → Web Components 전환으로 매핑/문서 단절 |
| 라이선스 | Shopify 연동 앱 제한 — 범용 디자인 시스템 벤치마크에 구조적 제약 |
| Headless 부재 | 로직/스타일 분리 없음 — 재사용성 관점에서 한계 |

### 벤치마크 관점 핵심 인사이트

> **Polaris는 "Figma↔Code 매핑 충실도"라는 질문 자체가 성립하기 어려운 시스템이다.**
>
> Code-first 거버넌스, 공식 Figma kit 부재(또는 비공개), 그리고 React→Web Components 전환으로 인해, Figma를 디자인의 single source of truth로 전제하는 벤치마크 프레임워크로는 평가가 제한적이다. Polaris에게 "디자인 시스템의 소스"는 Figma가 아니라 **코드와 토큰**이다.
>
> 이는 Figma 중심 워크플로우를 가진 조직(예: Figma Variables → Style Dictionary → Code 파이프라인)과 근본적으로 다른 철학이다. Polaris 모델에서는 디자이너가 Figma에서 작업하더라도, 최종 권위는 항상 코드 토큰에 있다.
