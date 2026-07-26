# Fluent 2 — 벤치마크 분석

> **분석 대상**: Microsoft Fluent 2 (fluent2.microsoft.design)
> **주요 코드 구현체**: Fluent UI React v9 (`@fluentui/react-components`), Fluent UI Web Components (`@fluentui/web-components`)
> **GitHub**: [microsoft/fluentui](https://github.com/microsoft/fluentui) (⭐ 19k+)
> **Figma**: [Fluent 2 Web UI Kit](https://aka.ms/Fluent2Toolkits/Web/Figma), [Figma Community @microsoft](https://www.figma.com/@microsoft)
> **npm**: `@fluentui/react-components`, `@fluentui/tokens`, `@fluentui/react-icons`
> **분석 기준일**: 2026-07-26

---

## 0. 구조적 특수성: Multi-platform, Multi-implementation

Fluent 2는 Microsoft의 **통합 디자인 시스템**으로, 단일 코드 라이브러리가 아니라 여러 플랫폼·프레임워크에 걸쳐 구현된다:

| 구현체 | 플랫폼 | 상태 |
|--------|--------|------|
| Fluent UI React v9 (`@fluentui/react-components`) | Web (React) | **공식 활성**, 현재 주력 |
| Fluent UI React v8 (`@fluentui/react`) | Web (React) | 레거시, 유지보수 모드 |
| Fluent UI React Northstar (v0) | Web (React, Teams) | **deprecated**, v9로 마이그레이션 중 |
| Fluent UI Web Components (`@fluentui/web-components`) | Web (Framework-agnostic) | 공식 활성 |
| Fluent UI Blazor | .NET/Blazor | 커뮤니티/MS 공식 |
| Fluent UI iOS / Android / Windows | 네이티브 플랫폼 | 각 플랫폼 팀 유지 |

이 구조는 Material Design과 유사한 **스펙 중심 다중 구현** 모델이지만, Material과 달리 **Microsoft 내부 단일 조직(Fluent team)이 디자인과 코드를 함께 소유**한다는 점에서 차이가 있다. Figma 키트와 코드 라이브러리가 같은 조직에서 나오므로, 서드파티 구현체(MUI 등)에서 발생하는 충실도 편차가 상대적으로 적다.

**마이그레이션 지원**: `react-migration-v0-v9`, `react-migration-v8-v9` 패키지를 통해 레거시 → v9 점진적 마이그레이션을 공식 지원한다.

---

## 1. 토큰 아키텍처

### 1.1 계층 구조: 2-layer (Global → Alias)

Fluent 2는 명시적인 **2단계 토큰 시스템**을 사용한다:

```
Global tokens (원시 값, context-agnostic)
        ↓  참조
Alias tokens (시맨틱 의미 부여, 테마별 분기)
        ↓  적용
UI 컴포넌트
```

| 계층 | 코드 위치 | 역할 | 예시 |
|------|----------|------|------|
| **Global** | `@fluentui/tokens` → `src/global/` | 원시 값 저장 (hex, px, ms) | `colorPaletteRedForeground1`, `fontSizeBase300` |
| **Alias** | `@fluentui/tokens` → `src/alias/` | 시맨틱 매핑, 테마별 분기 | `colorNeutralBackground1`, `colorBrandBackground` |

**코드에서 확인되는 Global 토큰 파일** (`packages/tokens/src/global/`):

| 파일 | 내용 |
|------|------|
| `colors.ts` | 기본 색상 원시 값 |
| `colorPalette.ts` | 전체 색상 팔레트 (Red, Green, Blue, etc.) |
| `brandColors.ts` | 브랜드 색상 정의 |
| `fonts.ts` | 폰트 패밀리, 크기, 굵기, 줄 높이 |
| `spacings.ts` | 간격 스케일 |
| `borderRadius.ts` | 보더 반경 값 |
| `strokeWidths.ts` | 스트로크 두께 |
| `durations.ts` | 애니메이션 지속 시간 |
| `curves.ts` | 이징 커브 |
| `typographyStyles.ts` | 타이포그래프리셋 (복합 토큰) |

**Alias 토큰 파일** (`packages/tokens/src/alias/`):

| 파일 | 내용 |
|------|------|
| `lightColor.ts` | Light 테마 시맨틱 색상 |
| `darkColor.ts` | Dark 테마 시맨틱 색상 |
| `highContrastColor.ts` | High Contrast 테마 색상 |
| `lightColorPalette.ts` / `darkColorPalette.ts` / `highContrastColorPalette.ts` | 테마별 팔레트 별칭 |
| `teamsDarkColor.ts` | Teams 전용 Dark 색상 |
| `teamsFontFamilies.ts` | Teams 전용 폰트 |

**테마 정의** (`packages/tokens/src/themes/`): `web/`과 `teams/` 두 제품군별 테마 번들.

> **Material Design 3와의 비교**: MD3는 ref → sys → comp의 3단계이나, Fluent는 comp-level 토큰을 별도 계층으로 분리하지 않고 컴포넌트 스타일 파일(`useButtonStyles.styles.ts` 등)에서 alias 토큰을 직접 참조한다. 이는 토큰 계층은 단순하지만 컴포넌트-토큰 결합이 스타일 코드에 분산되어 있음을 의미한다.

### 1.2 네이밍 컨벤션

**코드 (TypeScript)**: camelCase — `tokens.colorNeutralBackground1`, `tokens.fontSizeBase300`

**런타임 (CSS custom properties)**: `--colorNeutralBackground1`, `--fontSizeBase300` (camelCase 유지)

**네이밍 패턴 분석**:

```
colorNeutralBackground1Hover
│     │       │         │   └─ 상태 (rest/Hover/Pressed/Selected)
│     │       │         └─ 시맨틱 역할
│     │       └─ 카테고리 (Background/Foreground/Stroke)
│     └─ 팔레트 구분 (Neutral/Brand/Subtle/Transparent)
└─ 토큰 타입 (color/font/spacing/borderRadius/strokeWidth/duration/shadow)
```

**주요 토큰 패밀리**:

| 패밀리 | 네이밍 예시 | 수량 규모 |
|--------|-----------|----------|
| Color | `colorNeutralForeground1`, `colorBrandBackground`, `colorSubtleBackgroundHover` | 100+ alias |
| Typography | `fontSizeBase200`~`Base600`, `fontWeightRegular`/`Semibold`/`Bold`, `lineHeightBase300`, `fontFamilyBase` | ~30 |
| Spacing | `spacingHorizontalXS`/`S`/`SNudge`/`M`/`L`/`XL`, `spacingVertical*` | ~20 |
| Border Radius | `borderRadiusNone`/`Small`/`Medium`/`Large`/`Circular` | 5 |
| Stroke Width | `strokeWidthThin`/`Thick`/`Thicker`/`Thickest` | 4 |
| Shadow | `shadow2`/`4`/`8`/`16`/`28`/`64` | 6 |
| Duration | `durationUltraFast`/`Faster`/`Fast`/`Normal`/`Gentle`/`Slow`/`Slower`/`UltraSlow` | 8 |
| Curve | `curveEasyEase`, `curveDecelerate`, `curveAccelerate` | ~5 |

### 1.3 테마 전환 / 다크모드

**메커니즘**: `FluentProvider`에 테마 객체를 주입하면, 해당 테마의 모든 alias 토큰이 CSS custom properties로 DOM에 주입된다.

```tsx
import { FluentProvider, webLightTheme, webDarkTheme, teamsLightTheme } from '@fluentui/react-components';

// Light
<FluentProvider theme={webLightTheme}>...</FluentProvider>

// Dark
<FluentProvider theme={webDarkTheme}>...</FluentProvider>

// Teams 브랜드
<FluentProvider theme={teamsLightTheme}>...</FluentProvider>
```

**제공 테마**: `webLightTheme`, `webDarkTheme`, `webHighContrastTheme`, `teamsLightTheme`, `teamsDarkTheme`, `teamsHighContrastTheme`

**특이사항**:
- **High Contrast 모드**: OS 수준 `forced-colors: active` 미디어 쿼리에 대한 런타임 대응 + 전용 highContrast 테마 객체. 컴포넌트 스타일에 `@media (forced-colors: active)` 블록이 직접 포함되어 Windows High Contrast를 지원
- **Dark mode 색상 시프트**: Dark 모드에서 shared palette 색상이 채도·명도를 조정하여 눈의 피로 감소 (fluent2.microsoft.design/color 문서화)
- **중첩 Provider**: 앱 내에서 `FluentProvider`를 중첩하여 영역별 다른 테마 적용 가능

### 1.4 토큰 포맷

| 포맷 | 사용처 |
|------|--------|
| **TypeScript 객체** | `@fluentui/tokens` — canonical source |
| **CSS custom properties** | 런타임 — `FluentProvider`가 `--tokenName` 형태로 DOM 주입 |
| **Sass variables** | `@fluentui/react-theme-sass` — Sass 프로젝트용 변환 |
| **Figma Variables** | Fluent 2 Design Language 파일 — color, spacing, corner radius, stroke width, size |

### 1.5 Figma Variables ↔ Code 동기화

- Figma 키트의 **Fluent 2 Design Language** 파일에 Figma Variables로 global/alias 토큰이 구현되어 있음
- Light/Dark 모드 토글이 Figma Variables의 mode 전환으로 지원됨
- **그러나 자동 동기화 파이프라인(Style Dictionary, Tokens Studio 등)에 대한 공개 문서는 없음**
- 코드 토큰(`@fluentui/tokens`)과 Figma Variables가 **동일한 네이밍 체계(camelCase)를 공유**하는 것으로 보이나, 공식적인 자동 sync 도구 언급은 부재
- Web Components용 `@fluentui/tokens` 패키지가 별도 존재하여, `setTheme()` API로 CSS variables를 주입

---

## 2. 컴포넌트 인벤토리

### 2.1 총 컴포넌트 수

**Code (React v9, `packages/react-components/`)**:

GitHub 디렉토리 분석 기준, 실제 UI 컴포넌트 패키지:

| 카테고리 | 컴포넌트 | 수 |
|----------|---------|-----|
| **Actions** | Button, Menu, Toolbar | 3 |
| **Form** | Checkbox, Combobox, Input, Radio, Search, Select, Slider, SpinButton, Switch, Textarea, TagPicker, ColorPicker, SwatchPicker, Rating | 14 |
| **Data Display** | Avatar, Badge, Card, Image, List, Persona, Skeleton, Table, Tags, Tree | 10 |
| **Navigation** | Breadcrumb, Nav, Tabs, Link | 4 |
| **Overlay** | Dialog, Drawer, Popover, Tooltip, TeachingPopover, Toast, MessageBar | 7 |
| **Layout** | Accordion, Divider, Carousel, Overflow | 4 |
| **Feedback** | Progress, Spinner | 2 |
| **Typography** | Text, Label, Field, InfoLabel | 4 |
| **Infrastructure** | Provider, Portal | 2 |
| **합계 (stable)** | | **~50** |

**추가 (preview/compat)**:
- Preview: `react-headless-components-preview`, `react-menu-grid-preview`, `react-motion-components-preview`, `component-selector-preview`
- Compat (v8/v0 래퍼): `react-calendar-compat`, `react-datepicker-compat`, `react-timepicker-compat`, `react-colorpicker-compat`, `react-icons-compat`

**Figma (Fluent 2 Web UI Kit)**:
- 공식 문서에서 "code-aligned building blocks"로 표현
- Assets 패널에서 컴포넌트 제공, 대부분 2단계 이하 깊이로 구성
- 정확한 컴포넌트 수는 Figma 파일 내부 확인 필요하나, **코드와 동일한 컴포넌트 셋을 커버**한다고 명시
- 추가: Copilot UI Kit (AI 특화 컴포넌트), Labs UI Kit (실험적)

### 2.2 분류 체계

**코드**: 패키지 단위 1:1 분리 — `react-button`, `react-dialog`, `react-table` 등. 카테고리 디렉토리 없이 flat 구조.

**Figma**: 4-tier 구조:
1. **Fluent 2 Design Language** — 토큰 소스 (color, spacing, radius, stroke, size)
2. **Fluent 2 Core UI Kits** — 코드 정렬 컴포넌트 (Web, iOS, Android)
3. **Copilot UI Kits** — AI/Copilot 특화 컴포넌트
4. **Labs UI Kits** — 실험적/파트너 주도

### 2.3 복합 컴포넌트 (Compound Patterns)

Fluent UI React v9는 **slot-based compound pattern**을 광범위하게 사용:

```tsx
// Menu — compound + context
<Menu>
  <MenuTrigger>
    <Button>Options</Button>
  </MenuTrigger>
  <MenuPopover>
    <MenuList>
      <MenuItem icon={<CutIcon />}>Cut</MenuItem>
      <MenuDivider />
      <MenuItemSubMenu>
        <MenuTrigger><MenuItem>Share</MenuItem></MenuTrigger>
        <MenuPopover><MenuList><MenuItem>Email</MenuItem></MenuList></MenuPopover>
      </MenuItemSubMenu>
    </MenuList>
  </MenuPopover>
</Menu>

// Table — compound
<Table>
  <TableHeader>
    <TableRow><TableHeaderCell>File</TableHeaderCell></TableRow>
  </TableHeader>
  <TableBody>
    <TableRow><TableCell>report.pdf</TableCell></TableRow>
  </TableBody>
</Table>

// Dialog — compound
<Dialog>
  <DialogTrigger><Button>Open</Button></DialogTrigger>
  <DialogSurface>
    <DialogBody>
      <DialogTitle>Title</DialogTitle>
      <DialogContent>Content</DialogContent>
      <DialogActions><Button>OK</Button></DialogActions>
    </DialogBody>
  </DialogSurface>
</Dialog>
```

이외 Accordion, Tree, Tabs, Toolbar, Breadcrumb 등 대부분 컨테이너형 컴포넌트가 compound pattern 사용.

---

## 3. Figma↔Code 매핑 충실도 (핵심)

### 3.1 1:1 대응률

**공식 입장**: Fluent 2 문서는 Figma 키트가 "code-aligned building blocks"이며 "component properties in the UI kits map to code"라고 명시한다.

**실제 대응 분석**:

| 측면 | 대응 수준 | 근거 |
|------|----------|------|
| 컴포넌트 목록 | **높음** (~90%+) | Figma Web Kit이 React v9 컴포넌트와 동일 조직에서 제작, "code-aligned" 명시 |
| 토큰/스타일 | **높음** | Figma Variables와 Code tokens가 동일한 2-layer (global→alias) 구조, camelCase 네이밍 공유 |
| 플랫폼 커버리지 | **차이 존재** | Figma는 Web/iOS/Android 키트 분리, Code는 React v9가 주력 + Web Components 별도 |

**갭 요인**:
- Code에는 `react-headless-components-preview`, `react-motion` 등 Figma에 대응하지 않는 인프라 패키지 존재
- Figma에는 Copilot UI Kit, Labs Kit 등 코드에 1:1 대응하지 않는 실험적 에셋 존재
- Compat 컴포넌트(Calendar, DatePicker, TimePicker)는 Figma Kit 포함 여부가 불확실

### 3.2 네이밍 정합성

| 항목 | Figma | Code | 정합도 |
|------|-------|------|--------|
| 컴포넌트명 | Button, Checkbox, Dialog... | `Button`, `Checkbox`, `Dialog`... | ✅ **높음** — 동일 명명 |
| 패키지명 | N/A | `react-button`, `react-dialog` | `react-` 접두사 외 동일 |
| Props명 | Component properties | TypeScript props | ✅ 매핑 명시 ("properties map to code") |
| 토큰명 | Figma Variables (camelCase 추정) | `tokens.colorNeutralBackground1` | ✅ 동일 네이밍 체계 |

### 3.3 Variant 정합성

**Button 기준 상세 비교**:

| Variant 축 | Figma (Component Properties) | Code (Props) | 매핑 |
|------------|------------------------------|-------------|------|
| Appearance | Primary, Secondary, Outline, Subtle, Transparent | `appearance: 'primary' \| 'secondary' \| 'outline' \| 'subtle' \| 'transparent'` | ✅ 완전 일치 |
| Size | Small, Medium, Large | `size: 'small' \| 'medium' \| 'large'` | ✅ 완전 일치 |
| Shape | Rounded, Circular, Square | `shape: 'rounded' \| 'circular' \| 'square'` | ✅ 완전 일치 |
| Icon Position | Before, After | `iconPosition: 'before' \| 'after'` | ✅ 완전 일치 |
| Disabled | True/False | `disabled: boolean` | ✅ 일치 |
| State | Rest, Hover, Pressed, Disabled | CSS pseudo-classes + tokens | ⚠️ Figma는 variant로, Code는 pseudo-class로 처리 (구조적 차이) |

### 3.4 토큰 정합성

| Figma | Code | 정합도 |
|-------|------|--------|
| Figma Variables (Design Language 파일) | `@fluentui/tokens` TypeScript | ✅ **동일 2-layer 구조** |
| Light/Dark mode (Variables mode) | `webLightTheme` / `webDarkTheme` | ✅ 테마 분기 일치 |
| Color, Spacing, Corner Radius, Stroke Width, Size | color, spacing, borderRadius, strokeWidth, fontSize | ✅ 카테고리 일치 |
| High Contrast | `webHighContrastTheme` + `@media (forced-colors)` | ✅ Code에서 추가 지원 |

**핵심 패턴**: 컴포넌트 스타일에서 상태 변화(hover/press) 시 **CSS property가 아닌 token을 교체**:
```ts
// rest → hover → pressed: 같은 background-color에 다른 token
backgroundColor: tokens.colorNeutralBackground1,        // rest
':hover': { backgroundColor: tokens.colorNeutralBackground1Hover },
':active': { backgroundColor: tokens.colorNeutralBackground1Pressed },
```
이 패턴은 Figma의 state별 variant와 개념적으로 대응한다.

### 3.5 구조적 대응

| Figma | Code | 대응 |
|-------|------|------|
| Auto Layout (horizontal/vertical) | Flexbox (Griffel styles) | ✅ 개념적 일치 |
| Component nesting ≤ 2 levels | Slot-based composition | ✅ 유사 — slot이 Figma의 내부 구조에 대응 |
| Variants + Component Properties | Props + TypeScript union types | ✅ 1:1 매핑 |
| Figma Variables (token) | CSS custom properties (runtime) | ✅ 값 체계 공유 |

### 3.6 매핑 방향

**양방향 (Bi-directional)에 가깝되, 디자인 시스템 팀 주도**:

- Fluent team이 Figma Kit과 Code library를 **동일 조직에서 동시 유지**
- "Component properties in the UI kits map to code" — **디자인 → 코드 정렬**을 명시적 목표로 설정
- 자동 동기화 도구(Style Dictionary, Tokens Studio 등)의 공개 문서 없음 → **수동/반자동 동기화**로 추정
- Code-first 변경도 디자인 팀에 전파되는 구조이나, 공식 프로세스는 비공개

> **평가**: 단일 조직 소유로 인한 **개념적 정합도는 매우 높으나**, 자동화된 sync 파이프라인의 부재로 **기계적 검증 가능성은 제한적**. Material Design(스펙 ↔ 다수 구현, 서드파티 편차)보다는 충실도가 높고, Polaris/Carbon(단일 조직, 단일 구현)과 유사한 수준.

---

## 4. API 설계 철학

### 4.1 패턴: Slot-based Composition

Fluent UI React v9의 핵심 아키텍처는 **3-layer slot composition**:

```
Props (선언적 입력)
  → State (useXxx hook: props를 required로 정규화 + 파생 상태 계산)
    → Render (slots에 스타일/ARIA 적용하여 JSX 생성)
```

**Slot 모델**:
```ts
type ButtonSlots = {
  root: NonNullable<Slot<ARIAButtonSlotProps<'a'>>>;  // <button> 또는 <a>
  icon?: Slot<'span'>;                                 // 아이콘 컨테이너
};
```

- 각 slot은 `Slot<T>` 타입 — shorthand(string/element) 또는 full props 객체 전달 가능
- `root` slot은 `as` prop으로 렌더링 요소 변경 가능 (`<Button as="a" href="...">`)
- Compound 컴포넌트는 context로 parent-child 연결 (`MenuContext`, `AccordionContext` 등)

**Configuration vs Composition**: **Composition 우위**. 단순 컴포넌트(Button, Badge)는 props-based configuration, 복합 컴포넌트(Menu, Table, Tree, Dialog)는 JSX children 기반 composition.

### 4.2 스타일링: Griffel (Atomic CSS-in-JS)

**Griffel** (`@griffel/react`)은 Microsoft가 개발한 CSS-in-JS 라이브러리로, Fluent UI v9의 전용 스타일링 엔진:

| 특성 | 설명 |
|------|------|
| **Atomic CSS** | 개별 CSS declaration 단위로 class 생성, 최대 재사용 |
| **Near-zero runtime** | Webpack loader로 AOT 컴파일 시 런타임 비용 거의 제거 |
| **Type-safe** | `csstype` 기반 — 잘못된 CSS property/value는 컴파일 에러 |
| **SSR 지원** | 서버 사이드 렌더링 시 스타일 하이드레이션 |
| **CSS 추출 (실험)** | Webpack plugin으로 정적 CSS 파일 추출 가능 |

**스타일 작성 패턴**:
```ts
import { makeStyles, makeResetStyles, mergeClasses, shorthands } from '@griffel/react';
import { tokens } from '@fluentui/react-theme';

const useRootBaseClassName = makeResetStyles({
  backgroundColor: tokens.colorNeutralBackground1,
  color: tokens.colorNeutralForeground1,
  fontFamily: tokens.fontFamilyBase,
  borderRadius: tokens.borderRadiusMedium,
  // ...
});

const useRootStyles = makeStyles({
  primary: {
    backgroundColor: tokens.colorBrandBackground,
    color: tokens.colorNeutralForegroundOnBrand,
    ':hover': { backgroundColor: tokens.colorBrandBackgroundHover },
  },
  subtle: {
    backgroundColor: tokens.colorSubtleBackground,
    // ...
  },
  small: { fontSize: tokens.fontSizeBase200, padding: `... ${tokens.spacingHorizontalS}` },
  medium: { /* ... */ },
  large: { /* ... */ },
});

// Hook에서 조건부 합성
state.root.className = mergeClasses(
  rootBaseClassName,
  rootStyles[state.appearance],
  rootStyles[state.size],
  rootStyles[state.shape],
  state.root.className,  // 사용자 override
);
```

**핵심 설계 결정**:
- 스타일이 **컴포넌트 패키지 내부**에 co-locate (`useButtonStyles.styles.ts`)
- Token 참조가 스타일 파일에 직접 분산 — 별도 component-level token 계층 없음
- `mergeClasses()`로 variant 조합을 런타임에 합성

### 4.3 Headless 분리

- `react-headless-components-preview` 패키지가 **preview 상태**로 존재
- 아직 stable이 아니며, 어떤 컴포넌트가 headless로 제공되는지 공식 문서 제한적
- 현재 구조: **스타일과 로직이 완전히 분리되지는 않음** — `useButton()` (state hook) + `useButtonStyles()` (style hook) + `renderButton()` (render)로 파일 수준 분리는 되어 있으나, 동일 패키지 내 결합
- `@fluentui/react-aria` — ARIA 로직을 별도 패키지로 분리 (버튼, 메뉴 등의 키보드/ARIA 동작)
- `@fluentui/react-tabster` — 포커스 관리를 별도 패키지로 분리

> **평가**: Radix/shadcn 수준의 완전한 headless-first 아키텍처는 아니나, hook-level 분리와 ARIA 패키지 분리 headless 방향으로 진화 중.

### 4.4 커스터마이징

| 방법 | 설명 |
|------|------|
| **FluentProvider theme** | 앱 레벨 테마 객체 교체 (전체 토큰 override) |
| **Slot props** | 개별 slot에 style/className 직접 전달 |
| **`as` prop** | root slot의 렌더링 요소 변경 |
| **`mergeClasses`** | 사용자 className이 항상 마지막에 병합 (override 우선) |
| **Theme designer** | `theme-designer` 패키지 — 커스텀 브랜드 테마 생성 도구 |
| **Partial theme** | `createLightTheme()` / `createDarkTheme()` API로 brand color 기반 테마 생성 |

---

## 5. 접근성

### 5.1 내장 ARIA

| 패키지 | 역할 |
|--------|------|
| `@fluentui/react-aria` | ARIA 속성/동작 유틸리티 — `ARIAButtonSlotProps` 등 타입 레벨 ARIA 적용 |
| `@fluentui/react-tabster` | [tabster](https://github.com/microsoft/tabster) 기반 포커스 관리 — 선언적 `data-*` 속성 |

**컴포넌트 내장 ARIA 예시**:
- `Button`: `<button>` / `<a>` 자동 role, `aria-disabled`, `disabledFocusable` (비활성 상태에서도 tab order 유지)
- `Menu`: `role="menu"`, `role="menuitem"`, `aria-expanded`, `aria-haspopup`
- `Dialog`: `role="dialog"`, `aria-modal`, `aria-labelledby`, `aria-describedby`
- `Accordion`: `aria-expanded`, `aria-controls`, `role="region"`
- `Tooltip`: `role="tooltip"`, `aria-describedby`

### 5.2 키보드 네비게이션

- **tabster 라이브러리**: Microsoft가 개발한 포커스 관리 전용 라이브러리. React hook + `data-*` 속성으로 선언적 키보드 네비게이션 구현
- `useArrowNavigationGroup()`: 화살표 키 네비게이션 (메뉴, 탭, 라디오 그룹 등), `circular: true`로 순환 지원
- `useFocusFinders()`: 프로그램적 포커스 탐색
- `useFocusableGroup()`: 포커스 가능 요소 그룹 관리
- **Tab 순서**: 모든 인터랙티브 컴포넌트가 논리적 tab order 보장
- **Escape**: Dialog, Drawer, Popover, Menu, Tooltip — Escape로 닫기
- **Home/End**: Menu, List, Tree 등에서 첫/마지막 항목 이동

### 5.3 WCAG / 표준 준수

| 항목 | 수준 |
|------|------|
| **WCAG** | **2.1 AA** 준수 목표 (Microsoft 전사 접근성 정책) |
| **High Contrast** | Windows High Contrast Mode (`forced-colors: active`) 전용 스타일 블록 포함 |
| **색상 대비** | Fluent 2 Design Language에서 충분한 대비 보장 명시, Figma 플러그인(A11y Color Contrast Checker) 제공 |
| **스크린 리더** | NVDA, JAWS, VoiceOver 테스트 (Microsoft Accessibility Insights 도구 활용) |
| **모션** | `@media (prefers-reduced-motion: reduce)` 지원 |
| **Figma 접근성 도구** | A11y Focus Order 플러그인, A11y Color Contrast Checker 플러그인 공식 제공 |

**특이사항**: Microsoft는 접근성을 **디자인 시스템 수준의 기본 요구사항**으로 취급. fluent2.microsoft.design/accessibility 페이지에서 접근성 원칙, WCAG 체크포인트, 포커스 순서 가이드, 색상 대비 가이드를 포괄적으로 문서화. `disabledFocusable` prop처럼 **비활성 요소의 포커스 가능성**을 명시적으로 설계한 것은 Fluent의 독특한 접근성 패턴.

---

## 6. 동기화 거버넌스

### 6.1 Figma↔Code 동기화 프로세스

| 항목 | 현황 |
|------|------|
| **소유 구조** | Microsoft Fluent team이 Figma Kit + Code library를 **동일 조직에서 소유** |
| **동기화 방식** | 자동화 도구 공개 문서 없음 → **수동/반자동 동기화**로 추정 |
| **정렬 원칙** | "Component properties in the UI kits map to code" — 디자인 → 코드 정렬을 명시적 목표로 선언 |
| **토큰 동기화** | Figma Variables와 Code tokens가 동일한 2-layer 구조·네이밍 공유, 그러나 자동 sync 파이프라인(Style Dictionary 등) 미공개 |

### 6.2 도구 및 인프라

| 도구 | 용도 |
|------|------|
| **Nx** | Monorepo 빌드 오케스트레이션 |
| **Beachball** | 자동 버전 관리 (changelog + semver bump) |
| **Storybook** | 컴포넌트 문서화/개발 (`storybooks.fluentui.dev`) |
| **Verdaccio** | 로컬 npm 레지스트리 (개발/테스트) |
| **Azure Pipelines** | CI/CD |
| **Jest + Playwright** | 테스트 (unit + e2e) |
| **ESLint + Prettier** | 코드 품질 |
| **Griffel DevTools** | 스타일 디버깅 Chrome 확장 |
| **theme-designer** | 커스텀 테마 생성 패키지 |

### 6.3 릴리스 주기

- **독립 패키지 버전 관리**: 각 패키지가 독립 SemVer (`@fluentui/react-button@9.x.x`, `@fluentui/react-dialog@9.x.x`)
- **조정된 배치 릴리스**: 여러 패키지가 동일 타임스탬프로 동시 릴리스 (2026-05-26 기준 다수 패키지 동시 배포 확인)
- **릴리스 빈도**: 수시 (주 단위 이상), 패치/마이너 중심
- **Preview 패키지**: `-preview` 접미사로 unstable API 제공, stable 승격 전 피드백 수렴

### 6.4 기여 모델

- **오픈소스**: MIT 라이선스, GitHub에서 공개 개발
- **기여 가이드**: CONTRIBUTING.md, 개발 환경 설정 문서 제공
- **이슈/PR**: GitHub Issues + Pull Requests로 커뮤니티 기여 수용
- **내부-외부 이중 구조**: Microsoft 내부 팀이 핵심 설계 결정, 커뮤니티는 버그 수정/기능 제안 중심

---

## 7. 종합 평가

### 강점

| 항목 | 평가 |
|------|------|
| **토큰 체계** | 명확한 2-layer (global→alias), 테마별 alias 분기(light/dark/HC), camelCase 네이밍 일관성 |
| **접근성** | 업계 최고 수준 — 전용 ARIA 패키지, tabster 포커스 관리, High Contrast, `disabledFocusable` 같은 고유 패턴 |
| **스타일링** | Griffel atomic CSS-in-JS — near-zero runtime, type-safe, SSR 지원 |
| **복합 컴포넌트** | slot-based composition + compound pattern의 일관된 적용 |
| **조직 정합성** | Figma와 Code를 동일 팀이 소유하여 개념적 매핑 충실도 높음 |
| **마이그레이션** | v0/v8 → v9 공식 마이그레이션 패키지 제공 |

### 약점 / 한계

| 항목 | 평가 |
|------|------|
| **Figma↔Code 자동 동기화** | 공개된 자동 sync 파이프라인 없음 — 수동 정렬에 의존 |
| **Component-level 토큰** | MD3의 `md-comp-*` 같은 컴포넌트 전용 토큰 계층 부재 — 스타일 파일에 분산 |
| **Headless** | preview 단계, stable headless 패키지 미제공 — Radix/shadcn 대비 커스터마이징 자유도 제한 |
| **다중 구현 파편화** | React v8, v0(Northstar), v9, Web Components 공존 — 사용자 혼란, 마이그레이션 부담 |
| **Figma Kit 검증 한계** | Figma 파일 내부의 정확한 컴포넌트/토큰 수를 외부에서 기계적으로 검증하기 어려움 |

### Figma↔Code 매핑 충실도 종합 점수 (추정)

| 차원 | 점수 (5점 만점) | 근거 |
|------|:---:|------|
| 1:1 대응률 | 4.0 | 동일 조직 소유, "code-aligned" 명시, 그러나 preview/compat 갭 존재 |
| 네이밍 정합성 | 4.5 | 컴포넌트명, props명, 토큰명 모두 높은 일치 |
| Variant 정합성 | 4.5 | Button 기준 appearance/size/shape 완전 일치 |
| 토큰 정합성 | 4.0 | 2-layer 구조 공유, camelCase 일치, 그러나 자동 검증 수단 부재 |
| 구조적 대응 | 3.5 | Auto Layout ↔ Flexbox 개념 일치, slot 구조 유사, 그러나 기계적 매핑 아님 |
| 동기화 거버넌스 | 3.0 | 동일 조직 소유이나 자동화 파이프라인 비공개 |
| **종합** | **3.9** | **개념적 정합도는 최상위권, 기계적 검증 가능성은 중간** |
