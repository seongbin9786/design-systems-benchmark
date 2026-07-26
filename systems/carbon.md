# Carbon Design System — 벤치마크 분석

> **분석 대상**: IBM Carbon Design System v11 (carbondesignsystem.com)
> **주요 코드 구현체**: `@carbon/react` (React), `@carbon/web-components` (Web Components)
> **GitHub**: [carbon-design-system/carbon](https://github.com/carbon-design-system/carbon) (⭐ 8k+)
> **Figma**: (v11) Carbon Design System — Figma Community 공개 키트
> **npm**: `@carbon/react`, `@carbon/styles`, `@carbon/themes`, `@carbon/colors`, `@carbon/elements`
> **분석 기준일**: 2026-07-26

---

## 0. 구조적 특수성: IBM Design Language 위의 제품 레벨 시스템

Carbon은 IBM의 **제품·경험을 위한 오픈소스 디자인 시스템**으로, IBM Design Language를 기반으로 구축된다. 단일 코드 라이브러리가 아니라 **디자인 언어 → 엘리먼트 → 컴포넌트**의 계층적 구조를 가진다:

| 구현체 | 플랫폼 | 상태 |
|--------|--------|------|
| `@carbon/react` | Web (React) | **공식 활성**, 현재 주력 |
| `@carbon/web-components` | Web (Framework-agnostic) | 공식 활성 |
| Carbon for Angular | Web (Angular) | 커뮤니티 유지 |
| Carbon for Svelte | Web (Svelte) | 커뮤니티 유지 |
| Carbon for Vue | Web (Vue) | 커뮤니티 유지 |

**핵심 구조**: Carbon monorepo는 컴포넌트뿐 아니라 **디자인 엘리먼트 패키지**를 별도로 분리하여, 토큰·아이콘·픽토그램·그리드·모션·타이포그래피를 독립적으로 소비할 수 있게 한다:

| 패키지 | 역할 |
|--------|------|
| `@carbon/colors` | 색상 스케일 및 유틸리티 |
| `@carbon/themes` | 테마별 색상 토큰 (white, g10, g90, g100) |
| `@carbon/layout` | 레이아웃 단위, spacing 스케일 토큰 |
| `@carbon/motion` | productive/expressive 모션 커브 |
| `@carbon/type` | IBM Plex 기반 타이포그래피 토큰 |
| `@carbon/grid` | 2x Grid 시스템 (16-column CSS Grid) |
| `@carbon/icons` / `@carbon/pictograms` | 아이콘·픽토그램 에셋 |
| `@carbon/elements` | IBM Design Language 파운데이션 통합 |
| `@carbon/styles` | Sass 스타일 (컴포넌트 SCSS) |
| `@carbon/react` | React 컴포넌트 + 스타일 + 아이콘 번들 |

이 구조는 **토큰과 컴포넌트의 분리**가 매우 철저하며, 프레임워크에 의존하지 않고 디자인 엘리먼트만 사용할 수 있다는 점에서 Material Design의 토큰 패키지와 유사하다. 그러나 Material과 달리 **Figma와 코드가 동일 조직(IBM)에서 동시에 관리**되며, Figma 키트가 코드 릴리스와 함께 업데이트된다.

---

## 1. 토큰 아키텍처

### 1.1 계층 구조: 3-layer (Primitive → Core/Semantic → Component)

Carbon은 명시적인 **3단계 토큰 시스템**을 사용한다:

```
Primitive values (IBM Color Palette — hex 원시 값)
        ↓  참조
Core tokens (시맨틱 역할 — $background, $text-primary, $border-subtle-01)
        ↓  적용
Component tokens (컴포넌트 전용 — $button-*, $notification-*, $tag-*)
```

| 계층 | 코드 위치 | 역할 | 예시 |
|------|----------|------|------|
| **Primitive** | `@carbon/colors` | 원시 색상 값 (hex) | `$blue-60: #0f62fe`, `$gray-10: #f4f4f4` |
| **Core (Semantic)** | `@carbon/themes` → `scss/_theme.scss` | 시맨틱 역할 매핑, 테마별 분기 | `$background`, `$text-primary`, `$interactive` |
| **Component** | `@carbon/styles/scss/components/*` | 컴포넌트 전용 토큰 | `$button-primary`, `$notification-background-info` |

**Core 토큰 카테고리** (carbondesignsystem.com/elements/color/tokens 기준):

| 카테고리 | 토큰 수 (대략) | 대표 토큰 |
|----------|--------------|----------|
| Background | ~10 | `$background`, `$background-hover`, `$background-inverse` |
| Layer | ~20 | `$layer-01`~`$layer-03`, `$layer-hover-*`, `$layer-selected-*` |
| Layer accent | ~9 | `$layer-accent-01`~`$layer-accent-active-03` |
| Field | ~6 | `$field-01`~`$field-hover-03` |
| Border | ~16 | `$border-subtle-*`, `$border-strong-*`, `$border-inverse` |
| Text | ~9 | `$text-primary`, `$text-secondary`, `$text-error` |
| Link | ~8 | `$link-primary`, `$link-visited`, `$link-inverse` |
| Icon | ~7 | `$icon-primary`, `$icon-on-color`, `$icon-disabled` |
| Support | ~11 | `$support-error`, `$support-success`, `$support-caution-*` |
| Focus | 3 | `$focus`, `$focus-inset`, `$focus-inverse` |
| Syntax | ~80+ | 코드 에디터용 세분화 토큰 (`$syntax-keyword`, `$syntax-string` 등) |
| Miscellaneous | ~6 | `$interactive`, `$highlight`, `$overlay`, `$skeleton-*` |

**Component 토큰 카테고리**: Button, Content Switcher, Tag, Notification 등 컴포넌트별 전용 토큰이 `@carbon/styles/scss/components/` 하위에 분산 정의된다.

**AI 토큰**: v11 후기에 추가된 AI 전용 토큰 카테고리 (General AI, Chat, Chat Button) — AI UI 컴포넌트 전용.

> **Fluent 2와의 비교**: Fluent는 Global → Alias의 2단계이고 component-level 토큰을 별도 계층으로 분리하지 않는 반면, Carbon은 component 토큰을 SCSS 파일 단위로 명시적으로 분리하여 **토큰의 소유권이 컴포넌트에 귀속**되는 구조를 취한다.

### 1.2 네이밍 컨벤션

**Sass 변수**: `$` 접두사 + kebab-case — `$text-primary`, `$border-subtle-01`, `$layer-accent-hover-02`

**네이밍 패턴 분석**:

```
$border-subtle-selected-01
│      │      │         └─ 레이어 레벨 (01, 02, 03)
│      │      └─ 상태/변형 (hover, active, selected, disabled, inverse)
│      └─ 시맨틱 역할 (subtle, strong, interactive)
└─ 카테고리 (background, layer, field, border, text, link, icon, support, focus)
```

**레이어 레벨 시스템**: Carbon의 독특한 패턴으로, UI의 중첩 깊이에 따라 `01` → `02` → `03` 접미사가 부여된다:
- `$layer-01`: `$background` 위에 위치
- `$layer-02`: `$layer-01` 위에 위치
- `$layer-03`: `$layer-02` 위에 위치

이 패턴은 `$field-*`, `$border-subtle-*`, `$border-strong-*`에도 동일하게 적용되어, **맥락적 색상 계층**을 토큰 이름만으로 표현한다.

**Inverse 토큰**: 고대비 상황을 위한 `*-inverse` 변형이 여러 카테고리에 걸쳐 존재 (`$background-inverse`, `$text-inverse`, `$icon-inverse`, `$focus-inverse`, `$support-error-inverse` 등).

### 1.3 테마 전환 / 다크모드

**메커니즘**: `@carbon/themes`가 4개의 내장 테마를 제공하며, Sass mixin으로 적용한다.

| 테마 | 변수 | 모드 |
|------|------|------|
| White | `themes.$white` | Light (기본값) |
| Gray 10 | `themes.$g10` | Light |
| Gray 90 | `themes.$g90` | Dark |
| Gray 100 | `themes.$g100` | Dark |

**적용 방식** (3가지):

```scss
// 1. 기본 (white 테마 자동 초기화)
@use '@carbon/themes/scss/themes';

// 2. 글로벌 오버라이드
@use '@carbon/themes' with ($theme: $g100);

// 3. 인라인 스코핑 (서브트리별 테마)
@use '@carbon/themes/scss/theme';
.my-dark-section {
  @include theme.theme(themes.$g90);
}
```

**특이사항**:
- **혼합 모드 UI**: `theme()` mixin을 셀렉터 단위로 적용하여, Light 앱 내에 Dark 영역을 혼재 가능
- **JavaScript 접근**: `@carbon/themes`에서 테마 객체와 개별 토큰 값을 직접 import 가능
- **Figma**: 4개 테마가 Figma Variables의 mode로 구현되어, 키트 내에서 테마 전환 가능

### 1.4 토큰 포맷

| 포맷 | 사용처 |
|------|--------|
| **Sass variables** | `@carbon/themes`, `@carbon/styles` — canonical source |
| **Sass maps** | 테마 정의 (`$white`, `$g10`, `$g90`, `$g100`) |
| **JavaScript 객체** | `@carbon/themes` JS export — 런타임 접근 |
| **Figma Variables** | Carbon Figma 키트 — color tokens를 Variables로 구현 |

**중요**: Carbon v11은 **CSS custom properties를 기본 출력 포맷으로 사용하지 않는다**. 토큰의 canonical source는 Sass 변수이며, CSS custom properties로의 변환은 공식적으로 문서화되지 않았다. 이는 Fluent 2(`FluentProvider`가 CSS custom properties를 DOM에 주입)나 Material Design 3(`--md-sys-color-*`)와 구별되는 핵심 차이점이다.

### 1.5 Figma Variables ↔ Code 동기화

- Figma 키트에서 **color tokens가 Figma Variables로 구현**되어 있음 (fill, stroke, text layer에 적용)
- 4개 테마가 Variables의 mode로 매핑됨
- Typography tokens는 `(v11) Carbon Type Sets` 라이브러리의 **Text styles**로 제공
- **자동 동기화 파이프라인(Style Dictionary, Tokens Studio 등)에 대한 공개 문서는 없음**
- Figma 키트 피드백은 별도 GitHub repo(`carbon-design-kit`)에서 관리
- 코드 토큰(Sass)과 Figma Variables가 **동일한 시맨틱 네이밍을 공유**하는 것으로 보이나, 공식 자동 sync 도구는 부재

---

## 2. 컴포넌트 인벤토리

### 2.1 총 컴포넌트 수

**Code (React, `packages/react/src/components/`)**:

GitHub API 기준 **100개 이상의 컴포넌트 디렉토리** 확인. 주요 카테고리별:

| 카테고리 | 컴포넌트 (대표) | 수 (대략) |
|----------|---------------|----------|
| **Actions** | Button, ButtonSet, IconButton, ComboButton, ChatButton, CopyButton | ~8 |
| **Form** | Checkbox, CheckboxGroup, ComboBox, DatePicker, Dropdown, FileUploader, FluidForm, Form, FormGroup, FormItem, FormLabel, MultiSelect, NumberInput, PasswordInput, RadioButton, RadioButtonGroup, Search, Select, Slider, TextArea, TextInput, TimePicker, Toggle | ~25+ |
| **Fluid Form** | FluidComboBox, FluidDatePicker, FluidDropdown, FluidMultiSelect, FluidNumberInput, FluidSearch, FluidSelect, FluidTextArea, FluidTextInput, FluidTimePicker | ~12 |
| **Data Display** | ContainedList, DataTable, DataTableSkeleton, ListItem, OrderedList, Pagination, PaginationNav, ProgressBar, ProgressIndicator, StructuredList | ~10 |
| **Navigation** | Breadcrumb, BreadcrumbItem, Link, Tabs, TabList, Tab, TabPanels, TabPanel | ~8 |
| **Overlay** | ComposedModal, Modal, Dialog, Popover, Tooltip, Toggletip, OverflowMenu, Menu, MenuButton, ContextMenu | ~10 |
| **Layout** | AspectRatio, FlexGrid, Grid, Column, Layer, Layout, Stack | ~7 |
| **Feedback** | InlineLoading, Loading, Notification, ActionableNotification, InlineNotification, ToastNotification, Skeleton | ~7 |
| **Content** | Accordion, AccordionItem, CodeSnippet, ContentSwitcher, Tag, Tile, Heading, Plex | ~10 |
| **AI** | AILabel, AISkeleton | 2 |
| **Infrastructure** | ErrorBoundary, FeatureFlags, Portal, ClassPrefix, IdPrefix | ~5 |

**총 Code 컴포넌트**: **~100+ 디렉토리** (하위 컴포넌트·헬퍼 포함)

**Figma ((v11) Carbon Design System 키트)**:
- "all of the Carbon components and their variants"를 포함한다고 명시
- 정확한 수치 미공개이나, 코드 컴포넌트 셋을 커버하는 것을 목표로 함
- 별도 라이브러리: IBM Pictogram Library, IBM UI Icon Library, IBM Color Library, Carbon Type Sets

### 2.2 분류 체계

**코드**: `packages/react/src/components/` 하위에 **flat 디렉토리 구조** — 카테고리 디렉토리 없이 컴포넌트명 알파벳 순. 각 컴포넌트는 자체 디렉토리에 `ComponentName.tsx`, `ComponentName-test.tsx`, `index.ts` 포함.

**Figma**: Assets 패널에서 컴포넌트 제공. variant가 있는 컴포넌트는 프로퍼티 컨트롤로 설정. Screens 에셋으로 5개 2x Grid 브레이크포인트 캔버스 제공.

### 2.3 커버리지

| 영역 | 커버 여부 | 비고 |
|------|----------|------|
| Form / Input | ✅ 광범위 | Fluid 변형까지 포함 |
| Navigation | ✅ | Breadcrumb, Tabs, Link |
| Data Display | ✅ | DataTable (정렬, 확장, 선택), Pagination |
| Overlay / Modal | ✅ | Modal, Dialog, Popover, Tooltip, Toggletip |
| Feedback | ✅ | Notification (3종), Loading, Skeleton, ProgressBar |
| Layout | ✅ | CSS Grid 기반 16-column, FlexGrid (레거시), Stack |
| AI | ✅ | AILabel, AISkeleton, ChatButton, AI 토큰 |
| Motion | ✅ | `@carbon/motion` — productive/expressive 커브 |
| Icon | ✅ | `@carbon/icons` — 2,000+ 아이콘, 프레임워크별 패키지 |

### 2.4 복합 컴포넌트 (Compound Patterns)

Carbon v11은 **compound component 패턴**을 주요 컴포넌트에 적용:

```tsx
// Tabs — v11에서 compound로 재설계
<Tabs>
  <TabList>
    <Tab>Tab 1</Tab>
    <Tab>Tab 2</Tab>
  </TabList>
  <TabPanels>
    <TabPanel>Content 1</TabPanel>
    <TabPanel>Content 2</TabPanel>
  </TabPanels>
</Tabs>

// DataTable — compound + render props
<DataTable rows={rows} headers={headers}>
  {({ rows, headers, getTableProps, getHeaderProps, getRowProps }) => (
    <Table {...getTableProps()}>
      <TableHead>
        <TableRow>
          {headers.map(header => (
            <TableHeader {...getHeaderProps({ header })} />
          ))}
        </TableRow>
      </TableHead>
      <TableBody>
        {rows.map(row => (
          <TableRow {...getRowProps({ row })} />
        ))}
      </TableBody>
    </Table>
  )}
</DataTable>

// Breadcrumb — compound
<Breadcrumb>
  <BreadcrumbItem href="/">Home</BreadcrumbItem>
  <BreadcrumbItem href="/page">Page</BreadcrumbItem>
</Breadcrumb>
```

**v10 → v11 전환**: 많은 컴포넌트가 class component에서 functional component로 전환되면서 compound 패턴이 강화되었다 (Tabs, Notification, Toggle 등).

---

## 3. Figma↔Code 매핑 충실도 (핵심)

### 3.1 1:1 대응률

| 측면 | 평가 | 근거 |
|------|------|------|
| 컴포넌트 대응 | **높음** | Figma 키트가 "all Carbon components and their variants"를 포함한다고 명시. 코드 ~100+ 컴포넌트 디렉토리와 대응 |
| 누락 가능성 | **중간** | Fluid* 변형, AI 컴포넌트, Infrastructure 컴포넌트(ErrorBoundary, FeatureFlags)의 Figma 존재 여부 불확실 |
| Figma 전용 | **낮음** | Screens(그리드 캔버스), Wireframe 키트 등 Figma 전용 에셋 존재하나 컴포넌트 레벨은 아님 |

### 3.2 네이밍 정합성

| 항목 | Figma | Code | 정합도 |
|------|-------|------|--------|
| 컴포넌트명 | Button, Checkbox, DataTable, Tabs | `Button`, `Checkbox`, `DataTable`, `Tabs` | **높음** — PascalCase 일치 |
| Variant명 (kind) | Primary, Secondary, Tertiary, Ghost, Danger | `'primary'`, `'secondary'`, `'tertiary'`, `'ghost'`, `'danger'` | **높음** — 대소문자 차이만 |
| Size | sm, md, lg, xl, 2xl | `'sm'`, `'md'`, `'lg'`, `'xl'`, `'2xl'` | **높음** — v11에서 표준화됨 |
| Props명 | Figma properties | React props | **중간** — Figma property명과 React prop명이 항상 1:1이지는 않음 |

**v11 size 표준화**: v10의 `small`, `default`, `field`, `compact`, `short`, `normal`, `tall` 등 비표준 값이 v11에서 `sm`/`md`/`lg`/`xl`/`2xl`로 통일되어, Figma↔Code size 매핑이 크게 개선됨.

### 3.3 Variant 정합성

**Button 예시**:

| Figma Variant Property | Code Prop | 값 |
|----------------------|-----------|-----|
| Kind | `kind` | primary, secondary, tertiary, ghost, danger, danger--primary, danger--ghost, danger--tertiary |
| Size | `size` | xs, sm, md, lg, xl, 2xl |
| Icon | `renderIcon` / `hasIconOnly` | Figma에서 icon 포함 여부 토글 |
| Disabled | `disabled` | boolean |

**정합도**: **높음**. Figma variant properties와 Code props가 구조적으로 대응. 단, Code의 `hasIconOnly`는 Figma에서 별도 아이콘 버튼 컴포넌트로 분리될 수 있음.

### 3.4 토큰 정합성

| 측면 | 평가 | 근거 |
|------|------|------|
| Color tokens | **높음** | Figma Variables와 Sass 토큰이 동일한 시맨틱 네이밍 공유 (`$background` ↔ Figma Variable `background`) |
| Theme modes | **높음** | Figma 4개 테마 mode ↔ Code 4개 테마 변수 (white, g10, g90, g100) |
| Typography | **중간** | Figma: Text styles / Code: `@carbon/type` Sass mixins — 구조는 대응하나 포맷 다름 |
| Spacing | **중간** | Figma: auto-layout padding 값 / Code: `$spacing-01`~`$spacing-13` — 값은 대응하나 Figma에서 토큰명 참조 여부 불확실 |

### 3.5 구조적 대응

| Figma | Code | 정합도 |
|-------|------|--------|
| Auto Layout (horizontal/vertical) | Flexbox (일부 컴포넌트) | **중간** |
| Auto Layout | CSS Grid (Grid, DataTable) | **중간** |
| Constraints | Responsive breakpoints (`@carbon/grid`) | **중간** |
| Component variants | React props / compound components | **높음** |

### 3.6 매핑 방향

**Code-first with parallel Figma**: Carbon은 코드와 Figma가 **동시에 개발**되는 모델이다:
- 코드 변경은 `carbon` monorepo에서, Figma 키트 변경은 `carbon-design-kit` repo에서 관리
- 두 repo가 분리되어 있으나, 동일 조직(IBM Carbon team)에서 소유
- Figma 키트 사용자가 "automatically receive updates made to the Carbon libraries"라고 명시
- **자동화된 양방향 sync 파이프라인은 부재** — 수동/반자동 동기화로 추정

---

## 4. API 설계 철학

### 4.1 Composition vs Configuration

Carbon은 **Configuration 중심 + 점진적 Composition** 모델을 취한다:

**Configuration (주류)**:
```tsx
// 대부분의 컴포넌트는 props 기반 설정
<Button kind="primary" size="lg" renderIcon={Add} disabled>
  Create
</Button>

<Notification
  kind="error"
  title="Error"
  subtitle="Something went wrong"
  lowContrast
/>
```

**Composition (복합 컴포넌트)**:
```tsx
// Tabs, DataTable, Breadcrumb 등은 compound pattern
<Tabs selectedIndex={0}>
  <TabList>
    <Tab>Tab 1</Tab>
  </TabList>
  <TabPanels>
    <TabPanel>Content</TabPanel>
  </TabPanels>
</Tabs>
```

**Polymorphic rendering**: Button은 `as` prop과 `href` prop으로 `<button>`, `<a>` 등 다양한 요소로 렌더링 가능. `PolymorphicComponentPropWithRef<T>` 타입으로 타입 안전성 확보.

### 4.2 스타일링 접근법

**SCSS Modules (Sass `@use`)** — Carbon의 핵심 스타일링 방식:

```scss
// 전체 스타일
@use '@carbon/react';

// 컴포넌트 단위
@use '@carbon/react/scss/components/button';
@use '@carbon/react/scss/components/data-table';
@use '@carbon/react/scss/components/data-table/sort';

// 테마 접근
@use '@carbon/styles/scss/theme';
.example {
  background: theme.$background;
  color: theme.$text-primary;
}
```

**특징**:
- **CSS-in-JS 미사용**: 런타임 스타일 주입 없음, 빌드 타임 Sass 컴파일
- **Dart Sass 필수**: `node-sass` 지원 중단
- **컴포넌트별 SCSS 분리**: tree-shaking 가능한 스타일 구조
- **CSS custom properties 비기본**: 토큰은 Sass 변수로 소비, CSS variables 출력은 공식 지원 안 함
- **Prefix 설정**: `@use '@carbon/styles' with ($prefix: 'cds')` — 클래스명 접두사 커스텀

### 4.3 Headless 분리

**Headless 아님**: Carbon은 스타일과 로직이 결합된 **opinionated 컴포넌트 라이브러리**이다. Headless 컴포넌트 레이어가 없으며, `@carbon/react`는 스타일 적용된 완성 컴포넌트를 제공한다.

단, `@carbon/web-components`는 프레임워크 독립적 Web Components로, 스타일 커스텀의 여지가 상대적으로 크다.

### 4.4 커스터마이징

| 방법 | 메커니즘 |
|------|---------|
| **테마 오버라이드** | Sass map으로 커스텀 테마 정의: `@use '@carbon/themes' with ($theme: (...))` |
| **컴포넌트 토큰** | 컴포넌트 SCSS에서 `$button-*` 등 변수 오버라이드 |
| **Prefix 변경** | `$prefix` 설정으로 CSS 클래스명 변경 |
| **Layer 시스템** | `<Layer>` 컴포넌트로 맥락적 색상 계층 제어 |
| **className** | 모든 컴포넌트에 `className` 전달 (v11에서 최상위 요소에 적용되도록 수정) |
| **Feature Flags** | `<FeatureFlags>` 컴포넌트로 실험적 기능 토글 |

---

## 5. 접근성

### 5.1 표준 준수

| 항목 | 내용 |
|------|------|
| **WCAG 레벨** | **WCAG 2.1 AA** 준수 목표 |
| **IBM 표준** | IBM Accessibility Checklist 기반 (WCAG AA + Section 508 + 유럽 표준) |
| **색상 대비** | Carbon 테마가 WCAG 2.1 AA 대비 가이드라인 준수 |
| **테스트 도구** | IBM Equal Access Toolkit, High Contrast Chrome plugin, Stark Figma plugin |

### 5.2 내장 ARIA

Carbon 컴포넌트는 **내장 ARIA 속성**을 제공:

- **Button**: `React.ButtonHTMLAttributes<HTMLButtonElement>` 상속으로 네이티브 ARIA 전달. `iconDescription`으로 icon-only 버튼의 accessible name 강제 (미제공 시 console.error + PropTypes validation error)
- **Notification**: `role="status"` (기본), `role="log"`, `role="alert"` 선택. `ActionableNotification`은 `role="alertdialog"` + 자동 포커스
- **Toggle**: `<button role="switch">` 사용 (v11에서 `<input type="checkbox">`에서 변경)
- **Modal**: 포커스 트랩 기본 활성화 (`focusTrap` prop 제거, 항상 활성화)
- **Tooltip**: interactive content 금지, `label`/`description`으로 콘텐츠 지정

### 5.3 키보드 네비게이션

| 패턴 | 구현 |
|------|------|
| **Tab 순서** | DOM 순서 기반 논리적 탭 흐름 |
| **포커스 표시** | 모든 인터랙티브 요소에 visible focus indicator (`$focus` 토큰) |
| **활성화** | `Enter` / `Spacebar`로 포커스 요소 활성화 |
| **Escape** | Notification `closeOnEscape` prop, Modal 기본 Escape 닫기 |
| **포커스 관리** | Modal 열림 시 자동 포커스, `selectorPrimaryFocus`로 초기 포커스 대상 지정 |
| **High Contrast** | Windows High Contrast 모드 (`forced-colors`) 대응 유틸리티 (`scss/utilities/_high-contrast-mode.scss`) |

### 5.4 접근성 설계 원칙

Carbon은 **inclusive design** 원칙을 명시:
- 시각 장애, 저시력, 색맹, 청각 장애, 신체적·인지적 접근성 모두 고려
- 시맨틱 HTML 우선, ARIA는 보강용으로만 사용
- HTML5 landmark label로 스크린 리더 점프 네비게이션 지원
- Figma에 **IBM Accessibility Design Kit** 별도 제공

---

## 6. 동기화 거버넌스

### 6.1 Monorepo 구조

| 도구 | 역할 |
|------|------|
| **Lerna** | 패키지 버전 관리, 릴리스 오케스트레이션 |
| **Nx** | 빌드 캐싱, 태스크 실행 |
| **Yarn (Berry)** | 패키지 매니저 (`.yarnrc.yml`) |
| **Husky** | Git hooks |
| **ESLint + Prettier + Stylelint** | 코드 품질 |
| **Jest + Playwright** | 단위 + E2E 테스트 |
| **GitHub Actions** | CI/CD |
| **Netlify** | 문서 사이트 배포 |

### 6.2 릴리스 주기

| 항목 | 내용 |
|------|------|
| **현재 버전** | v11.112.0 (2026-07-15) |
| **릴리스 주기** | **약 2주 간격** minor 릴리스 |
| **RC 프로세스** | stable 릴리스 ~2일 전 release candidate 발행 |
| **패치** | 필요 시 수시 (예: v11.111.1) |
| **릴리스 예시** | v11.109.0 (06-03) → v11.110.0 (06-17) → v11.111.0 (07-01) → v11.112.0 (07-15) |

### 6.3 Figma↔Code 동기화 프로세스

| 측면 | 내용 |
|------|------|
| **코드 repo** | `carbon-design-system/carbon` |
| **Figma 키트 repo** | `carbon-design-kit` (별도 GitHub repo) |
| **소유 조직** | 동일 (IBM Carbon team) |
| **동기화 방식** | **수동/반자동** — 자동 파이프라인(Style Dictionary, Tokens Studio) 공개 문서 없음 |
| **Figma 업데이트** | Figma 라이브러리 퍼블리싱으로 자동 전파 ("automatically receive updates") |
| **피드백 채널** | `carbon-design-kit` GitHub issues, GitHub Discussions, Discord |

### 6.4 기여 모델

- **오픈소스**: Apache-2.0 라이선스
- **기여 가이드**: `.github/CONTRIBUTING.md`
- **커뮤니티**: GitHub Discussions, Discord 서버
- **프레임워크 포트**: Angular, Svelte, Vue는 커뮤니티 유지 (별도 repo)

---

## 7. 종합 평가

### 강점

| 항목 | 평가 |
|------|------|
| **토큰 체계 완성도** | ★★★★★ — 3단계 계층, 레이어 레벨 시스템, inverse 토큰, AI 토큰까지 포괄 |
| **컴포넌트 커버리지** | ★★★★★ — 100+ 컴포넌트, Fluid 변형, AI 컴포넌트, DataTable 고급 기능 |
| **접근성** | ★★★★★ — WCAG 2.1 AA, IBM Accessibility Checklist, 내장 ARIA, 포커스 관리 |
| **테마 시스템** | ★★★★☆ — 4테마 + 인라인 스코핑, 혼합 모드 지원. 단 CSS custom properties 미기본 |
| **v11 표준화** | ★★★★☆ — size/kind 표준화, compound 패턴, Sass Modules 전환으로 일관성 대폭 향상 |

### 약점 / 한계

| 항목 | 평가 |
|------|------|
| **Figma↔Code 자동 sync** | ★★☆☆☆ — 자동 파이프라인 부재, 별도 repo 관리, 수동 동기화 추정 |
| **CSS custom properties** | ★★☆☆☆ — Sass-first 아키텍처로 런타임 테마 전환이 제한적 |
| **Headless 미지원** | ★★☆☆☆ — 스타일·로직 결합, 디자인 커스텀 자유도 제한 |
| **Figma Variables 범위** | ★★★☆☆ — Color는 Variables이나, spacing/typography는 Text styles/auto-layout 값으로만 |
| **프레임워크 다양성** | ★★★☆☆ — React/Web Components만 공식, Angular/Svelte/Vue는 커뮤니티 |

### Figma↔Code 매핑 충실도 총평

Carbon은 **동일 조직이 Figma와 Code를 동시에 소유**하는 구조로, 네이밍·variant·토큰 수준에서 **높은 정합성**을 보인다. v11의 size/kind 표준화가 Figma↔Code 매핑을 크게 개선했다. 그러나 **자동화된 동기화 파이프라인이 부재**하고, Figma Variables가 color에 한정되며, spacing/typography는 Figma 고유 기능(Text styles, auto-layout)으로 표현되어 **토큰 포맷 수준의 완전한 1:1 대응에는 미치지 못한다**. 매핑 방향은 Code-first에 가깝되 Figma가 병행 업데이트되는 모델이다.
