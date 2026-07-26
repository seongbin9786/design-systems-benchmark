# Material Design — 벤치마크 분석

> **분석 대상**: Google Material Design 3 (m3.material.io)
> **주요 코드 구현체**: MUI Material UI (React, `@mui/material`), Material Web Components (`@material/web`)
> **GitHub**: [mui/material-ui](https://github.com/mui/material-ui) (⭐ 98.6k) · [material-components/material-web](https://github.com/material-components/material-web) (⭐ 11.1k)
> **분석 기준일**: 2026-07-26

---

## 0. 구조적 특수성: Spec-first, Multi-implementation

Material Design는 단일 라이브러리가 아니라 **Google이 정의한 디자인 스펙**이다. 이 스펙을 기반으로 여러 플랫폼/프레임워크에서 독립적으로 구현한다:

| 구현체 | 플랫폼 | 상태 |
|--------|--------|------|
| Material Components for Android (MDC-Android) | Android (Jetpack Compose) | Google 공식, 활성 |
| Material for Flutter | Flutter | Google 공식, 활성 |
| Material Web Components (`@material/web`) | Web (Lit/Web Components) | Google 공식, **maintenance mode** |
| MUI Material UI (`@mui/material`) | React | MUI(서드파티) 공식, 활성 — **Material Design 2** 기반 |
| Angular Material | Angular | Angular 팀 공식, 활성 |

이 구조 때문에 Figma↔Code 매핑 충실도 분석이 다른 디자인 시스템(예: Polaris, Carbon)과 근본적으로 다르다. **단일 소스 ↔ 단일 구현**이 아니라 **단일 스펙 ↔ 다수 구현**이며, 각 구현체의 충실도와 커버리지가 상이하다.

---

## 1. 토큰 아키텍처

### 1.1 계층 구조: 3-layer (ref → sys → comp)

Material Design 3는 명확한 **3단계 토큰 계층**을 정의한다. Material Web Components의 `tokens/` 디렉토리에서 이 구조가 직접 확인된다:

```
Reference (ref)  →  System (sys)  →  Component (comp)
  원시 값              시맨틱 별칭        컴포넌트별 결정
```

| 계층 | 접두사 | 파일 수 | 역할 | 예시 |
|------|--------|---------|------|------|
| **Reference** | `md-ref-` | 2 (`palette`, `typeface`) | 원시 색상 팔레트, 폰트 스택 | `md-ref-palette-primary40` |
| **System** | `md-sys-` | 6 (`color`, `elevation`, `motion`, `shape`, `state`, `typescale`) | 크로스-컴포넌트 시맨틱 별칭 | `md-sys-color-primary` |
| **Component** | `md-comp-` | 49 | 개별 컴포넌트 토큰 | `md-comp-filled-button-container-color` |

**토큰 총량**: ref 2 + sys 6 + comp 49 = **57개 SCSS 토큰 파일** (Material Web 기준)

### 1.2 네이밍 컨벤션

**스펙 토큰**: dot notation — `md.sys.color.primary`, `md.sys.typescale.display-large`

**코드 (CSS custom properties)**: kebab-case, 계층 중 `md-` 네임스페이스 유지:
```css
/* System token */
--md-sys-color-primary: #6750A4;
--md-sys-color-on-primary: #FFFFFF;
--md-sys-color-surface-container-high: #ECE6F0;

/* Component token (browser에서는 layer segment 생략) */
--md-filled-button-container-color: var(--md-sys-color-primary);
--md-filled-button-label-text-color: var(--md-sys-color-on-primary);
```

**네이밍 패턴**: `md-{layer}-{scope}-{property}`
```
md-comp-filled-button-container-color
│  │    │             │
│  │    │             └─ 토큰명 (제어 대상)
│  │    └─ 컴포넌트 스코프
│  └─ 계층 (ref / sys / comp)
└─ Material 네임스페이스
```

### 1.3 토큰 카테고리별 상세

#### Color tokens (~30+ roles)

시맨틱 color role 기반. 고정 hex 값이 아닌 **역할(role)** 로 매핑:

| 그룹 | 주요 토큰 | 수 |
|------|----------|-----|
| Primary accent | `primary`, `onPrimary`, `primaryContainer`, `onPrimaryContainer`, `inversePrimary` | 5 |
| Secondary accent | `secondary`, `onSecondary`, `secondaryContainer`, `onSecondaryContainer` | 4 |
| Tertiary accent | `tertiary`, `onTertiary`, `tertiaryContainer`, `onTertiaryContainer` | 4 |
| Error | `error`, `onError`, `errorContainer`, `onErrorContainer` | 4 |
| Fixed (테마 불변) | `primaryFixed`, `primaryFixedDim`, `onPrimaryFixed`, `onPrimaryFixedDim` + secondary/tertiary 동일 패턴 | 12 |
| Surface hierarchy | `surface`, `onSurface`, `surfaceVariant`, `onSurfaceVariant`, `surfaceBright`, `surfaceDim`, `surfaceContainerLowest` ~ `surfaceContainerHighest` (5단계), `inverseSurface`, `onInverseSurface`, `surfaceTint` | ~13 |
| Outline/Shadow/Scrim | `outline`, `outlineVariant`, `shadow`, `scrim` | 4 |
| Background | `background`, `onBackground` | 2 |

**총 color role**: 약 **48개** (fixed variant 포함)

**Dynamic Color**: Android 12+에서 사용자 벽지 색상을 source color로 추출 → 전체 팔레트 자동 생성. `primary`, `secondary`, `tertiary`가 source color로부터 알고리즘적으로 파생.

#### Typography tokens (15 styles)

5 roles × 3 sizes = **15개 typescale 토큰**:

| Role | Large | Medium | Small |
|------|-------|--------|-------|
| Display | `display-large` | `display-medium` | `display-small` |
| Headline | `headline-large` | `headline-medium` | `headline-small` |
| Title | `title-large` | `title-medium` | `title-small` |
| Body | `body-large` | `body-medium` | `body-small` |
| Label | `label-large` | `label-medium` | `label-small` |

각 스타일은 `font`, `weight`, `size`, `line-height`, `tracking` 속성 토큰을 가짐.
Reference 토큰: `md.ref.typeface.brand`, `md.ref.typeface.plain`, `md.ref.typeface.weight-regular/medium/bold`

#### Shape tokens (7 levels)

| 토큰 | Corner radius |
|------|--------------:|
| `none` | 0dp |
| `extra-small` | 4dp |
| `small` | 8dp |
| `medium` | 12dp |
| `large` | 16dp |
| `extra-large` | 28dp |
| `full` | 완전 원형 (pill/circle) |

#### Elevation tokens (6 levels)

| 토큰 | 높이 | Tonal tint opacity |
|------|-----:|-------------------:|
| `level0` | 0dp | 0% |
| `level1` | 1dp | 5% |
| `level2` | 3dp | 8% |
| `level3` | 6dp | 11% |
| `level4` | 8dp | 12% |
| `level5` | 12dp | 14% |

Shadow elevation + tonal elevation(surface tint overlay) 이중 구현.

### 1.4 테마 전환 / 다크모드

**Material Design 스펙 수준**:
- Light/Dark 테마: 동일한 color role에 다른 값 매핑. `primary`가 light에서 `#6750A4`이면 dark에서 `#D0BCFF`로 전환
- High contrast variant 지원
- Fixed role(`primaryFixed` 등)은 light/dark 전환에도 값 불변

**Material Web Components**:
- CSS custom properties 값 교체로 테마 전환
- `data-theme` attribute 또는 미디어 쿼리(`prefers-color-scheme`) 기반

**MUI (React)**:
- `palette.mode: 'light' | 'dark'` — 테마 객체 재생성 방식 (classic)
- `CssVarsProvider` — CSS custom properties(`--mui-palette-primary-main`)로 컴파일, **React re-render 없이** 다크모드 전환
- `useColorScheme()` hook + `InitColorSchemeScript`로 FOUC(flash of unstyled content) 방지
- `defaultMode="system"`으로 OS 설정 자동 감지

### 1.5 토큰 포맷

| 포맷 | 사용처 |
|------|--------|
| SCSS partials (`_md-sys-color.scss`) | Material Web Components 토큰 원본 |
| CSS custom properties (`--md-sys-color-*`) | Material Web 런타임 |
| JS theme object (`createTheme()`) | MUI — palette, typography, spacing, shadows, transitions, zIndex |
| CSS custom properties (`--mui-*`) | MUI CssVarsProvider |
| JSON / Kotlin / Swift / Dart | 각 플랫폼(Android, iOS, Flutter)별 토큰 출력 |

### 1.6 Figma Variables ↔ Code token 동기화

**자동화된 동기화 파이프라인: 없음.**

Material Design는 spec-first 구조로, Google이 스펙(m3.material.io)과 디자인 토큰 값을 문서로 발행하면 각 구현체가 이를 수동으로 반영한다. Figma Variables와 코드 토큰을 연결하는 Style Dictionary, Tokens Studio 등의 자동화 도구는 공식적으로 사용되지 않는다.

- Figma kit의 styles/variables → 코드 토큰: **수동 매핑**
- 스펙 업데이트 → 각 구현체 반영: **구현체별 독립 릴리스 주기**

---

## 2. 컴포넌트 인벤토리

### 2.1 구현체별 컴포넌트 수

| 구현체 | 컴포넌트 수 | 비고 |
|--------|------------:|------|
| **Material Design 3 스펙** | ~30+ | m3.material.io에 정의된 컴포넌트 |
| **MUI Material UI** (React) | **62** | 8개 카테고리, MUI X(Data Grid, Charts 등) 제외 |
| **Material Web Components** | **~21** | 21개 컴포넌트 디렉토리, maintenance mode |
| **Material for Flutter** | ~40+ | Flutter SDK 내장 |
| **Material for Android** (Compose) | ~40+ | Jetpack Compose Material 3 |
| **Figma 공식 kit** | ~30+ | Figma Community 공개 (접근 제한으로 상세 수 미확인) |

### 2.2 MUI 컴포넌트 카테고리 (62개)

| 카테고리 | 수 | 주요 컴포넌트 |
|----------|---:|--------------|
| Inputs | 14 | Autocomplete, Button, Checkbox, Radio, Select, Slider, Switch, Text Field, Number Field, Rating, Transfer List, Toggle Button, FAB, Button Group |
| Data display | 10 | Avatar, Badge, Chip, Divider, Icons, List, Table, Tooltip, Typography, Material Icons |
| Navigation | 10 | Bottom Navigation, Breadcrumbs, Drawer, Link, Menu, Menubar, Pagination, Speed Dial, Stepper, Tabs |
| Feedback | 6 | Alert, Backdrop, Dialog, Progress, Skeleton, Snackbar |
| Layout | 5 | Box, Container, Grid, Stack, Image List |
| Surfaces | 4 | Accordion, App Bar, Card, Paper |
| Utils | 11 | Click-Away Listener, CSS Baseline, Modal, Popover, Popper, Portal, Transitions, useMediaQuery 등 |
| Lab | 2 | Masonry, Timeline |

### 2.3 Material Web Components (~21개)

`button`, `checkbox`, `chips`, `dialog`, `divider`, `elevation`, `fab`, `field`, `focus`, `icon`, `iconbutton`, `list`, `menu`, `progress`, `radio`, `ripple`, `select`, `slider`, `switch`, `tabs`, `textfield`

+ `labs/` 디렉토리에 실험적 컴포넌트 추가

### 2.4 커버리지 비교

| 영역 | M3 스펙 | MUI | Material Web |
|------|:-------:|:---:|:------------:|
| Buttons (5 variants) | ✅ | ✅ | ✅ |
| FAB | ✅ | ✅ | ✅ |
| Icon buttons | ✅ | ✅ | ✅ |
| Segmented buttons | ✅ | ✅ (Toggle Button) | ✅ (labs) |
| Text fields | ✅ | ✅ | ✅ |
| Checkbox / Radio / Switch | ✅ | ✅ | ✅ |
| Slider | ✅ | ✅ | ✅ |
| Date/Time picker | ✅ | ✅ (MUI X) | ❌ |
| Cards (3 types) | ✅ | ✅ | ❌ |
| Chips (4 types) | ✅ | ✅ | ✅ |
| Dialog | ✅ | ✅ | ✅ |
| Bottom sheet / Side sheet | ✅ | ✅ (Drawer) | ❌ |
| Navigation bar/rail/drawer | ✅ | ✅ | ✅ (navigation-bar) |
| Tabs | ✅ | ✅ | ✅ |
| Top app bar | ✅ | ✅ (App Bar) | ❌ |
| Snackbar | ✅ | ✅ | ❌ |
| Tooltip | ✅ | ✅ | ❌ |
| Progress indicators | ✅ | ✅ | ✅ |
| Badge | ✅ | ✅ | ❌ (labs) |
| Carousel | ✅ | ❌ | ❌ |
| Search bar | ✅ | ❌ | ❌ |
| Table / Data Grid | ❌ (스펙 외) | ✅ | ❌ |
| Accordion | ❌ (스펙 외) | ✅ | ❌ |
| Autocomplete | ❌ (스펙 외) | ✅ | ❌ |
| Transfer List | ❌ (스펙 외) | ✅ | ❌ |

**핵심 관찰**: MUI는 Material Design 스펙에 없는 컴포넌트(Table, Accordion, Autocomplete, Transfer List 등)를 추가하여 **스펙 대비 확장된 커버리지**를 제공한다. Material Web은 스펙의 핵심 컴포넌트만 구현하고 maintenance mode에 진입했다.

### 2.5 Compound component 패턴

**MUI**: Configuration 중심이지만 복합 구조에서 compound 패턴 사용:
```jsx
<Card>
  <CardHeader title="..." />
  <CardContent>...</CardContent>
  <CardActions>
    <Button>...</Button>
  </CardActions>
</Card>
```
- `Table` → `TableHead` / `TableBody` / `TableRow` / `TableCell`
- `Tabs` → `Tab`
- `Menu` → `MenuItem`
- `Stepper` → `Step` → `StepLabel` / `StepContent`
- `Select` → `MenuItem` / `ListSubheader`

**Material Web**: Web Components 슬롯 기반:
```html
<md-filled-text-field label="Email" type="email">
  <md-icon slot="leading-icon">email</md-icon>
</md-filled-text-field>
```

---

## 3. Figma↔Code 매핑 충실도 ⭐

### 3.1 매핑 방향: Spec-first (Figma-first도 Code-first도 아님)

```
Material Design Spec (m3.material.io)
         │
         ├──→ Figma kit (Google 발행)
         ├──→ Material Web Components (Google, maintenance)
         ├──→ Material for Android/Flutter (Google)
         ├──→ MUI Material UI (MUI, 서드파티, M2 기반)
         └──→ Angular Material (Angular 팀)
```

**Figma와 Code 사이에 직접적 동기화 관계가 없다.** 양쪽 모두 스펙을 참조하는 병렬 구현이다.

### 3.2 1:1 대응률

| 비교 쌍 | 대응률 | 설명 |
|---------|-------:|------|
| M3 스펙 ↔ Figma kit | **~90%** | 공식 kit이 스펙 컴포넌트 대부분 커버 |
| M3 스펙 ↔ Material Web | **~70%** | 핵심 컴포넌트 구현, cards/sheets/snackbar/tooltip 등 미구현 |
| M3 스펙 ↔ MUI | **~60%** | M2 기반 + MUI 독자 확장 컴포넌트 다수 |
| Figma kit ↔ MUI | **~50%** | 간접 관계. MUI가 M2 기반이고 Figma kit은 M3 |
| Figma kit ↔ Material Web | **~65%** | 둘 다 M3 기반이나 Material Web 커버리지 제한 |

### 3.3 네이밍 정합성

**스펙 ↔ Material Web**: **높음**. 컴포넌트명, variant명, 토큰명이 스펙과 직접 대응:
- 스펙: "Filled Button" → 코드: `<md-filled-button>`, 토큰: `--md-filled-button-*`
- 스펙: "Outlined Text Field" → 코드: `<md-outlined-text-field>`

**스펙 ↔ MUI**: **중간~낮음**. MUI는 React 생태계 관례를 따름:
- 스펙: "Filled Button" → MUI: `<Button variant="contained">` (variant명이 다름)
- 스펙: "Filled Tonal Button" → MUI: `<Button variant="contained" color="secondary">` (근사치)
- 스펙: "Outlined Text Field" → MUI: `<TextField variant="outlined">` (유사)
- 스펙: "Navigation Bar" → MUI: `<BottomNavigation>` (이름 다름)
- 스펙: "Top App Bar" → MUI: `<AppBar>` (이름 다름)

### 3.4 Variant property 매핑

**Material Web**: 스펙 variant가 별도 컴포넌트로 분리:
```
스펙 Button variants: Elevated / Filled / Filled Tonal / Outlined / Text
코드: <md-elevated-button> / <md-filled-button> / <md-filled-tonal-button> / <md-outlined-button> / <md-text-button>
```
→ Figma의 variant property와 1:1 대응

**MUI**: 단일 컴포넌트 + `variant` prop:
```jsx
<Button variant="contained">   // ≈ Filled
<Button variant="outlined">    // ≈ Outlined
<Button variant="text">        // ≈ Text
// Elevated, Filled Tonal은 직접 대응 없음
```
→ Figma variant와 부분 대응. MUI가 M2 기반이라 M3의 5개 button variant 중 3개만 직접 매핑.

### 3.5 토큰 정합성

**Material Web ↔ 스펙**: **높음**. 토큰명이 스펙 정의와 직접 대응:
- 스펙: `md.sys.color.primary` → CSS: `--md-sys-color-primary`
- 스펙: `md.comp.filled-button.container.color` → CSS: `--md-filled-button-container-color`

**MUI ↔ 스펙**: **낮음**. MUI는 자체 테마 구조 사용:
- 스펙: `md.sys.color.primary` → MUI: `theme.palette.primary.main`
- 스펙: `md.sys.color.surface-container-high` → MUI: 직접 대응 없음
- 스펙: `md.sys.typescale.body-large` → MUI: `theme.typography.body1`
- 스펙: `md.sys.shape.medium` (12dp) → MUI: `theme.shape.borderRadius` (4px, 단일 값)

MUI는 Material Design의 시맨틱 토큰 체계를 따르지 않고, **자체 JS 테마 객체**를 사용한다. CssVarsProvider로 CSS variables를 생성하지만 네이밍이 `--mui-palette-primary-main`으로 스펙과 다르다.

### 3.6 구조적 대응 (Figma auto-layout ↔ Code)

Figma kit의 auto-layout 구조와 Material Web의 CSS 구조는 스펙을 공유하므로 개념적으로 대응한다. 그러나:
- Figma의 auto-layout direction/padding/gap ↔ 코드의 flexbox: **개념적 대응, 자동 변환 없음**
- Figma의 component variant ↔ 코드의 prop/attribute: **수동 매핑**
- Figma의 styles/variables ↔ 코드의 design tokens: **이름 다름, 값 동일**

### 3.7 종합 평가

| 항목 | Material Web | MUI |
|------|:-----------:|:---:|
| 1:1 대응률 | ★★★☆ | ★★☆☆ |
| 네이밍 정합성 | ★★★★ | ★★☆☆ |
| Variant 매핑 | ★★★★ | ★★☆☆ |
| 토큰 정합성 | ★★★★ | ★☆☆☆ |
| 구조적 대응 | ★★★☆ | ★★☆☆ |

**Material Design의 Figma↔Code 매핑은 구조적으로 분산되어 있다.** 단일 Figma kit ↔ 단일 Code 라이브러리 관계가 성립하지 않으며, 가장 충실한 구현체인 Material Web조차 maintenance mode로 향후 동기화 보장이 약하다. MUI는 가장 널리 쓰이는 React 구현체이지만 Material Design 2 기반이고 자체 API 관례가 강해 스펙/Figma와의 정합성이 낮다.

---

## 4. API 설계 철학

### 4.1 MUI: Configuration 중심 + 점진적 Composition

**기본 패턴**: Configuration (props 기반)
```jsx
<TextField
  label="Email"
  variant="outlined"
  fullWidth
  required
  error={!!error}
  helperText={error}
/>
```

**복합 구조에서는 Composition**:
```jsx
<Table>
  <TableHead>
    <TableRow>
      <TableCell>Name</TableCell>
    </TableRow>
  </TableHead>
  <TableBody>
    {rows.map(row => (
      <TableRow key={row.id}>
        <TableCell>{row.name}</TableCell>
      </TableRow>
    ))}
  </TableBody>
</Table>
```

### 4.2 스타일링 접근법 (MUI)

4단계 커스터마이징 전략 (좁은 범위 → 넓은 범위):

| 방법 | 범위 | 사용처 |
|------|------|--------|
| `sx` prop | 단일 인스턴스 | 토큰 인식 인라인 스타일: `<Box sx={{ bgcolor: 'primary.main', p: 2 }} />` |
| `styled()` | 재사용 컴포넌트 | 테마 접근 + 동적 props 지원 래퍼 생성 |
| `createTheme({ components })` | 앱 전역 | `styleOverrides`, `defaultProps` 일괄 설정 |
| `<GlobalStyles />` | 전역 CSS | HTML 기본 요소 스타일링 |

**sx prop**은 MUI의 시그니처 API:
- 테마 토큰 직접 참조: `color: 'success.main'`, `typography: 'body2'`
- 반응형: `{ flexDirection: { xs: 'column', md: 'row' } }`
- 중첩 셀렉터: `'& .MuiSlider-thumb': { ... }`
- 상태 클래스: `'&.Mui-disabled': { ... }`

### 4.3 Headless 분리 (MUI)

MUI는 핵심 로직을 **headless hook**으로 분리:

| Hook | 역할 | 크기 |
|------|------|------|
| `useAutocomplete` | Autocomplete 로직 (ARIA, 키보드) | ~4.6 kB gzip |
| `useMediaQuery` | 미디어 쿼리 감지 | — |
| `useScrollTrigger` | 스크롤 기반 elevation | — |
| `useFormControl` | 폼 상태 관리 | — |

`@mui/base` (구 Unstyled) 패키지로 완전 headless 컴포넌트도 제공했으나, 최근에는 MUI Base를 별도 프로젝트로 분리하는 방향.

### 4.4 Material Web: Web Components + CSS Custom Properties

```html
<md-filled-button
  style="--md-filled-button-container-color: #006A6A"
>
  Click me
</md-filled-button>
```

- **프레임워크 비종속**: Lit 기반 Web Components, 모든 프레임워크에서 사용 가능
- **스타일링**: CSS custom properties(`--md-*`)로 토큰 오버라이드
- **Shadow DOM**: 컴포넌트 내부 스타일 격리, `::part()` 또는 CSS custom properties로 커스터마이징
- **Configuration + slot 기반 Composition** 혼용

### 4.5 MUI 테마 시스템 구조

```js
createTheme({
  palette: { mode, primary, secondary, error, warning, info, success, grey, text, background, action },
  typography: { fontFamily, fontSize, fontWeight*, h1~h6, subtitle*, body*, button, caption, overline },
  spacing: (n) => `${8 * n}px`,   // 8px base unit
  shape: { borderRadius: 4 },
  breakpoints: { xs: 0, sm: 600, md: 900, lg: 1200, xl: 1536 },
  shadows: Array(25),              // elevation 0~24 box-shadow
  transitions: { easing, duration },
  zIndex: { appBar: 1100, drawer: 1200, modal: 1300, snackbar: 1400, tooltip: 1500 },
  components: { MuiButton: { defaultProps, styleOverrides } },
})
```

`ThemeProvider` → React Context로 배포, `styled()` / `sx` / `useTheme()`으로 소비.

---

## 5. 접근성

### 5.1 MUI

**내장 ARIA**:
- WAI-ARIA Authoring Practices 패턴 구현 (combobox, listbox, dialog, tab 등)
- `useAutocomplete` 등 headless hook에 ARIA 로직 내장
- 자동 `role`, `aria-*` 속성 적용 (예: Autocomplete의 `aria-owns`, `role="listbox"`)

**키보드 네비게이션**:
- Autocomplete: Enter(선택), Home/End, Escape(초기화), Arrow keys(옵션 이동)
- Dialog: focus trap, Escape로 닫기
- Tabs: Arrow keys로 탭 이동
- Menu: Arrow keys, Enter, Escape
- `defaultMuiPrevented`로 기본 키 핸들러 오버라이드 가능

**WCAG 준수**:
- 기본 contrast ratio: **3:1** (WCAG AA 4.5:1 미달)
- `palette.contrastThreshold`로 조정 가능
- Focus visible 상태 지원
- Touch target 크기 가이드 제공
- **한계**: iOS VoiceOver의 `aria-owns` 지원 문제 (Autocomplete), 커스텀 Listbox에 `role="listbox"` 수동 설정 필요

### 5.2 Material Web Components

- Material Design 3 스펙의 접근성 가이드를 직접 구현
- Focus ring, ripple, state layer 등 접근성 관련 내부 컴포넌트 별도 관리 (`focus/`, `ripple/`)
- Shadow DOM 내 ARIA 속성 자동 적용
- 키보드 네비게이션 내장 (tabs, list, menu 등)

### 5.3 Material Design 스펙 수준의 접근성

- Contrast, focus states, touch targets, interaction guidance 문서화
- High contrast 테마 variant
- Reduced motion 고려
- 상태 레이어(state layer): hover, focus, pressed, disabled, dragged 시각적 피드백

---

## 6. 동기화 거버넌스

### 6.1 프로세스: Spec-first, 분산 구현

```
Google Material Design 팀
    │
    ├─ 스펙 발행 (m3.material.io)
    ├─ 디자인 토큰 값 정의
    ├─ Figma kit 발행 (Figma Community)
    │
    ├──→ Material Web (Google) ──── 스펙 수동 반영, maintenance mode
    ├──→ Material Android/Flutter (Google) ──── 스펙 수동 반영, 활성
    ├──→ MUI (서드파티) ──── M2 기반, 독립 릴리스, 스펙과 간접 관계
    └──→ Angular Material (Angular 팀) ──── 독립 릴리스
```

**자동 동기화 없음**: Figma kit ↔ Code 간 Style Dictionary, Tokens Studio 등의 자동화 파이프라인이 없다. 각 구현체가 스펙 문서를 참조하여 수동으로 토큰/컴포넌트를 업데이트.

### 6.2 릴리스 주기

| 구현체 | 릴리스 패턴 | 비고 |
|--------|------------|------|
| Material Design 스펙 | 수시 업데이트 | m3.material.io 지속 갱신 |
| Material Web | 비정기 | **maintenance mode**, 새 maintainer 모집 중 |
| MUI | 정기 (v9.x) | 활성 개발, 자체 로드맵 |
| Material for Flutter | Flutter SDK 릴리스와 연동 | Google 공식 |
| Material for Android | AndroidX 릴리스와 연동 | Google 공식 |

### 6.3 도구

| 도구 | 사용 여부 |
|------|----------|
| Style Dictionary | ❌ 공식 사용 안 함 |
| Tokens Studio | ❌ 공식 사용 안 함 |
| Figma Variables | Figma kit에서 사용 (추정) |
| SCSS 토큰 파일 | ✅ Material Web (`tokens/*.scss`) |
| 자체 코드 생성 | Material Web: `tokens/` 디렉토리에 generated 파일 |

### 6.4 기여 모델

**MUI**: 오픈소스 (MIT), GitHub PR 기반, 98.6k stars, 32.6k forks, 활성 커뮤니티
**Material Web**: 오픈소스 (Apache-2.0), 11.1k stars, maintenance mode로 기여 제한적

### 6.5 동기화 리스크

1. **Material Web maintenance mode**: Google의 공식 Web 구현체가 유지보수 상태로, 스펙 업데이트 반영이 지연/중단될 수 있음
2. **MUI의 M2 기반**: 가장 인기 있는 React 구현체가 Material Design 2에 머물러 있어 M3 스펙/Figma kit과의 괴리 지속
3. **다중 구현체 분산**: 동일한 스펙을 5개 이상의 구현체가 각각 해석하므로, 크로스 플랫폼 일관성이 각 구현체의 노력에 의존
4. **Figma kit ↔ Code 단절**: 자동 동기화 없이 수동 관리, 버전 드리프트 가능성

---

## 7. 핵심 요약

| 차원 | 평가 | 핵심 근거 |
|------|------|----------|
| 토큰 아키텍처 | ★★★★☆ | ref→sys→comp 3계층, 57개 토큰 파일, 명확한 네이밍. 단, 구현체별 토큰 포맷 상이 |
| 컴포넌트 인벤토리 | ★★★☆☆ | MUI 62개로 풍부하나 M3 스펙과의 정합성 낮음. Material Web은 21개로 제한적 |
| Figma↔Code 매핑 | ★★☆☆☆ | Spec-first + multi-implementation 구조로 1:1 매핑 불가. Material Web이 가장 충실하나 maintenance mode |
| API 설계 철학 | ★★★★☆ | MUI의 sx/styled/theme 4단계 커스터마이징, headless hook 분리. Material Web의 CSS custom properties |
| 접근성 | ★★★☆☆ | WAI-ARIA 패턴 구현, 키보드 네비게이션. 단, 기본 contrast 3:1로 WCAG AA 미달 |
| 동기화 거버넌스 | ★★☆☆☆ | 자동 동기화 없음, 구현체 분산, Material Web maintenance mode, MUI의 M2 잔류 |

### 벤치마크 관점에서의 시사점

Material Design는 **디자인 시스템 스펙으로서의 완성도**는 높으나, **Figma↔Code 매핑 충실도**라는 관점에서는 구조적 한계가 명확하다:

1. **단일 소스-단일 구현 부재**: Figma kit과 1:1로 대응하는 공식 React/Web 라이브러리가 없다
2. **가장 충실한 구현체(Material Web)의 maintenance mode**: 향후 동기화 보장 약화
3. **가장 인기 있는 구현체(MUI)의 M2 잔류**: 시장 점유율과 스펙 충실도의 괴리
4. **토큰 체계의 구현체별 분절**: 스펙 토큰(`md.sys.color.primary`)과 MUI 토큰(`palette.primary.main`)이 이름·구조 모두 다름

이러한 구조는 "디자인 시스템 = 스펙 + 다중 구현" 모델의 장단점을 극명하게 보여준다.
