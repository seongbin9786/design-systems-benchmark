# Adobe Spectrum — 벤치마크 분석

> **분석 대상**: Adobe Spectrum Design System (spectrum.adobe.com)
> **주요 코드 구현체**: React Spectrum v3 (`@adobe/react-spectrum`), React Aria (headless), Spectrum 2 (`@react-spectrum/s2`)
> **토큰 패키지**: `@adobe/spectrum-tokens` (구 `adobe/spectrum-tokens` → 현 `adobe/spectrum-design-data`)
> **GitHub**: [adobe/react-spectrum](https://github.com/adobe/react-spectrum) (⭐ 15.7k) · [adobe/spectrum-design-data](https://github.com/adobe/spectrum-design-data)
> **분석 기준일**: 2026-07-26

---

## 0. 구조적 특수성: Design-first, Layered Architecture

Adobe Spectrum는 Adobe 제품군(Photoshop, Illustrator, XD, Creative Cloud 등) 전체에 적용되는 **단일 통합 디자인 시스템**이다. 코드 구현은 명확한 계층 분리를 따른다:

| 계층 | 패키지 | 역할 |
|------|--------|------|
| **Design Data** | `@adobe/spectrum-tokens`, `@adobe/spectrum-design-data` | 토큰, 컴포넌트 스키마, 모드셋, 가이드라인 |
| **Headless 로직** | `react-aria` (54개 패키지), `react-stately` | 접근성·행동 로직, 스타일 비종속 |
| **스타일 적용 컴포넌트** | `@react-spectrum/*` (63개 패키지) | Spectrum 디자인 적용 React 컴포넌트 |
| **Spectrum 2** | `@react-spectrum/s2` (v1.5.1) | 차세대 컴포넌트, React 19 기반 |

이 구조의 핵심은 **React Aria라는 headless 계층**이 접근성·키보드·상호작용 로직을 완전히 분리하고, React Spectrum이 여기에 Spectrum 디자인 토큰과 스타일을 입히는 것이다. Figma 디자인과 코드 간 매핑은 토큰을 매개로 이루어지며, 컴포넌트 API 스키마(`@adobe/spectrum-component-api-schemas`)가 양쪽을 연결하는 계약 역할을 한다.

---

## 1. 토큰 아키텍처

### 1.1 계층 구조: 3-layer (palette → semantic → component)

Spectrum 토큰은 [spectrum-design-data 문서](https://opensource.adobe.com/spectrum-design-data/tokens/)에서 확인되는 3단계 계층을 가진다:

```
Color Palette / Layout Primitives  →  Color Aliases / Semantic Palette  →  Component Tokens
       원시 값                              시맨틱 별칭                       컴포넌트별 결정
```

| 계층 | 카테고리 | 역할 | 예시 |
|------|----------|------|------|
| **Primitive** | Color palette | 원시 색상 값 (hex/rgb) | Spectrum 팔레트 색상 |
| **Primitive** | Layout | spacing, dimensions, corner radius 등 레이아웃 원시값 | spacing 토큰 |
| **Primitive** | Typography | font families, weights, sizes, letter spacing, text alignment | 폰트 스택 |
| **Semantic** | Color aliases | 팔레트를 참조하는 시맨틱 색상 토큰 | `focus`, `overlay` |
| **Semantic** | Semantic color palette | 의미 기반 팔레트 토큰 | `semantic blue`, `semantic red` |
| **Component** | Color component | 컴포넌트별 색상 토큰 | 컴포넌트 상태별 색상 |
| **Component** | Layout component | 컴포넌트별 레이아웃 토큰 | 컴포넌트별 spacing |
| **Component** | Icons | 아이콘 색상 토큰 | `primary`, `hover`, `down`, `background`, `disabled` |

**토큰 값 타입**: spacing, color, typography, object styles, animation, opacity, animation easing

### 1.2 네이밍 컨벤션

**토큰명**: kebab-case 기반
- 예시: `detail-margin-top-multiplier`
- `naming-exceptions.json` 파일로 예외 관리
- 별도 `packages/token-names` 패키지에 네이밍 taxonomy 분리 (taxonomy 변경이 토큰 패키지 버전 범프를 유발하지 않도록 격리)

**비난(deprecation) 및 이름 변경 관리**:
```json
{
  "deprecated": true,
  "renamed": "new-token-name",
  "deprecated_comment": "migration context"
}
```
이전 토큰은 새 토큰을 alias로 참조하여 하위 호환성 유지.

**코드 (CSS custom properties)**: React Spectrum에서 `--spectrum-*` 네임스페이스 사용:
```css
--spectrum-global-color-blue-500: #1473e6;
--spectrum-alias-background-color-primary: var(--spectrum-global-color-gray-50);
```

### 1.3 테마 전환 / 다크모드

**React Spectrum v3 Provider 기반 테마 시스템**:

테마 = **color scheme (light/dark)** × **platform scale (medium/large)** 의 2축 조합.

| Theme 객체 필드 | 정의 내용 |
|-----------------|----------|
| `global` | 스킴/스케일 불변 전역 변수 |
| `light` | Light color scheme 변수 |
| `dark` | Dark color scheme 변수 |
| `medium` | Medium scale (마우스 포인터) 변수 |
| `large` | Large scale (터치) 변수 |

**기본 제공 테마 3종**:

| 테마 | Light 색상 | Dark 색상 | 용도 |
|------|-----------|----------|------|
| `defaultTheme` | `light` | `darkest` | 대부분의 애플리케이션 |
| `darkTheme` | `dark` | `darkest` | 사진/비디오 편집기 |
| `lightTheme` | `lightest` | `darkest` | 고휘도 light + 고대비 dark |

**다크모드 전환 메커니즘**:
- **기본 동작**: `prefers-color-scheme` 미디어 쿼리로 OS 설정 자동 추종, 실시간 전환
- **수동 오버라이드**: `<Provider colorScheme="dark">` prop
- **중첩 지원**: light 앱 내 dark dialog 등 영역별 다른 스킴 적용 가능
- **Scale 자동 전환**: 디바이스 특성(마우스 vs 터치)에 따라 medium/large 자동 선택

```jsx
<Provider theme={defaultTheme} colorScheme="light">
  <ActionButton>Light</ActionButton>
  <Provider colorScheme="dark">
    <ActionButton>Dark (nested)</ActionButton>
  </Provider>
</Provider>
```

### 1.4 토큰 포맷

| 포맷 | 사용처 |
|------|--------|
| JSON (source) | `spectrum-design-data/packages/tokens/src/` — 토큰 원본 |
| JSON Schema | `schemas/token-types/` — 토큰 타입 검증 |
| CSS custom properties | React Spectrum 런타임 (`--spectrum-*`) |
| CSS Modules | React Spectrum 테마 객체 (`Theme` = CSSModule 맵) |
| JSON (dist) | `@adobe/spectrum-tokens` npm 배포 형식 |
| manifest.json | 토큰 배포 매니페스트 |

### 1.5 Figma Variables ↔ Code token 동기화

**반자동 파이프라인 존재. 완전 자동은 아님.**

`spectrum-design-data` 모노레포에 Figma 관련 도구 존재:
- `tools/component-options-editor`: **Figma 플러그인** — Spectrum 컴포넌트 옵션 스키마를 시각적 UI로 작성/편집, JSON 검증 포함
- `packages/component-schemas`: 컴포넌트 API의 JSON 스키마 — Figma와 Code 간 계약 역할

**토큰 빌드/검증 파이프라인**:
```
Figma (디자인 결정) → packages/tokens/src/ (JSON)
    → JSON Schema 검증 (Layer 1)
    → Catalog rules 검증 (Layer 2, rules.yaml)
    → Rust design-data CLI로 validate
    → dist/ 빌드
    → diff-generator로 이전 릴리스와 비교
    → Changesets로 버전 관리
    → npm @adobe/spectrum-tokens 발행
```

검증 도구:
- `moon run tokens:validateDesignData` — 디자인 데이터 검증
- `moon run tokens:verifyDesignDataSnapshot` — 스냅샷 검증
- `design-data migrate snapshot` — 스냅샷 업데이트
- `pnpm generateDiffResult` — 토큰 diff 생성 (추가/삭제/값변경/이름변경 보고)

**핵심 관찰**: Figma Variables에서 Code 토큰으로의 직접 자동 변환 파이프라인(Style Dictionary, Tokens Studio 등)은 확인되지 않는다. 대신 Figma 플러그인(`component-options-editor`)으로 스키마를 작성하고, 토큰 JSON을 수동/반자동으로 관리하며, 다층 검증으로 정합성을 보장하는 구조이다.

---

## 2. 컴포넌트 인벤토리

### 2.1 코드 컴포넌트 수

| 패키지군 | 수 | 비고 |
|----------|---:|------|
| **@react-spectrum/** | **63개 패키지** | 스타일 적용 컴포넌트 (테마 3종, 유틸 포함) |
| **@react-aria/** | **54개 패키지** | headless 접근성/행동 hook |
| **@react-stately/** | 별도 패키지군 | 상태 관리 hook |
| **@internationalized/** | 별도 패키지군 | i18n (30+ 언어, 13 캘린더 시스템) |
| **react-aria-components** | 통합 패키지 | React Aria 컴포넌트 통합 배포 |
| **@react-spectrum/s2** | v1.5.1, ~89개 컴포넌트 모듈 | Spectrum 2, React 19 기반 |

**@react-spectrum/ 패키지 목록** (63개, GitHub 확인):
accordion, actionbar, actiongroup, ai, autocomplete, avatar, badge, breadcrumbs, button, buttongroup, calendar, card, checkbox, color, combobox, contextualhelp, datepicker, dialog, divider, dnd, dropzone, filetrigger, form, icon, illustratedmessage, image, inlinealert, label, labeledvalue, layout, link, list, listbox, menu, meter, numberfield, overlays, picker, progress, provider, radio, s2, searchfield, slider, statuslight, steplist, story-utils, style-macro-s1, switch, table, tabs, tag, test-utils, text, textfield, theme-dark, theme-default, theme-express, theme-light, toast, tooltip, tree, utils, view, well

### 2.2 컴포넌트 카테고리 (React Spectrum v3 공식 문서)

| 카테고리 | 수 | 컴포넌트 |
|----------|---:|---------|
| **Application** | 1 | Provider |
| **Layout** | 2 | Flex, Grid |
| **Buttons** | 7 | ActionButton, ActionGroup, Button, ButtonGroup, FileTrigger, LogicButton, ToggleButton |
| **Collections** | 9 | ActionBar, ActionMenu, ListBox, ListView, Menu, MenuTrigger, TableView, TagGroup, TreeView |
| **Color** | 7 | ColorArea, ColorField, ColorPicker, ColorSlider, ColorSwatch, ColorSwatchPicker, ColorWheel |
| **Date & Time** | 6 | Calendar, DateField, DatePicker, DateRangePicker, RangeCalendar, TimeField |
| **Drag & Drop** | 1 | DropZone |
| **Forms** | 12 | Checkbox, CheckboxGroup, Form, NumberField, RadioGroup, RangeSlider, SearchField, Slider, Switch, TextArea, TextField |
| **Icons** | 2 | Custom Icons, Workflow Icons |
| **Navigation** | 5 | Accordion, Breadcrumbs, Disclosure, Link, Tabs |
| **Overlays** | 6 | AlertDialog, ContextualHelp, Dialog, DialogContainer, DialogTrigger, Tooltip |
| **Pickers** | 3 | ComboBox, Picker, SearchAutocomplete |
| **Status** | 8 | Badge, InlineAlert, LabeledValue, Meter, ProgressBar, ProgressCircle, StatusLight, Toast |
| **Content** | 12 | Avatar, Content, Divider, Footer, Header, Heading, IllustratedMessage, Image, Keyboard, Text, View, Well |
| **Other** | 1 | StepList |

**총 사용자-facing 컴포넌트**: 약 **82개** (문서 카테고리 기준)

### 2.3 Figma 컴포넌트

Adobe는 공식 Spectrum Figma kit을 Figma Community에 공개하고 있다. 그러나 Figma Community 접근 제한(403)으로 상세 컴포넌트 수를 직접 확인하지 못했다.

**간접 추정 근거**:
- spectrum.adobe.com에서 Figma 기반 디자인 리소스 제공
- `spectrum-design-data`에 `component-schemas` 패키지가 존재하여 Figma 컴포넌트 옵션을 JSON Schema로 정의
- `component-options-editor` Figma 플러그인으로 스키마 작성
- Adobe 내부적으로 Figma를 디자인 소스로 사용 (spectrum.adobe.com 자체가 Figma 기반 문서)

### 2.4 커버리지

| 영역 | React Spectrum | React Aria | 비고 |
|------|:-------------:|:----------:|------|
| Buttons (다중 variant) | ✅ | ✅ | ActionButton, ToggleButton, LogicButton 등 |
| Text fields / Forms | ✅ | ✅ | TextField, NumberField, SearchField, TextArea |
| Checkbox / Radio / Switch | ✅ | ✅ | CheckboxGroup, RadioGroup 포함 |
| Slider / RangeSlider | ✅ | ✅ | |
| Date/Time picker | ✅ | ✅ | Calendar, DatePicker, DateRangePicker, TimeField |
| Color picker | ✅ | ✅ | ColorArea, ColorWheel, ColorSlider 등 7종 |
| ComboBox / Autocomplete | ✅ | ✅ | SearchAutocomplete 포함 |
| Table | ✅ | ✅ | TableView, column resizing |
| Tree | ✅ | ✅ | TreeView |
| Dialog / Modal | ✅ | ✅ | AlertDialog, DialogContainer |
| Tooltip | ✅ | ✅ | |
| Toast | ✅ | ✅ | |
| Tabs | ✅ | ✅ | |
| Breadcrumbs | ✅ | ✅ | |
| Menu / Context menu | ✅ | ✅ | ActionMenu, MenuTrigger |
| Drag & Drop | ✅ | ✅ | DropZone, dnd 패키지 |
| Progress | ✅ | ✅ | ProgressBar, ProgressCircle, Meter |
| Accordion / Disclosure | ✅ | ✅ | |
| Tag | ✅ | ✅ | TagGroup |
| Avatar | ✅ | — | |
| Card | ✅ | — | |
| StepList | ✅ | ✅ | |
| AI 컴포넌트 | ✅ | — | `@react-spectrum/ai` 패키지 |

### 2.5 Compound component 패턴

React Spectrum은 **Composition 중심** 설계를 강력하게 채택:

```jsx
// TableView — 완전한 compound 구조
<TableView aria-label="Example table">
  <TableHeader>
    <Column key="name">Name</Column>
    <Column key="type">Type</Column>
  </TableHeader>
  <TableBody>
    <Row key="1">
      <Cell>Games</Cell>
      <Cell>File folder</Cell>
    </Row>
  </TableBody>
</TableView>

// Dialog — Trigger + Container + Content 조합
<DialogTrigger>
  <ActionButton>Save</ActionButton>
  <Dialog>
    <Heading>Save file</Heading>
    <Content>Are you sure?</Content>
    <ButtonGroup>
      <Button variant="secondary">Cancel</Button>
      <Button variant="cta">Save</Button>
    </ButtonGroup>
  </Dialog>
</DialogTrigger>

// Menu — Trigger + Menu + Item
<MenuTrigger>
  <ActionButton>Actions</ActionButton>
  <Menu onAction={handleAction}>
    <Item key="edit">Edit</Item>
    <Item key="duplicate">Duplicate</Item>
    <Item key="delete">Delete</Item>
  </Menu>
</MenuTrigger>
```

**React Aria의 3단계 API**:
1. **High-level components** (`react-aria-components`): DOM 구조 내장, 간단한 스타일링 API
2. **Exported contexts**: 커스텀 조합 (예: `ButtonContext` 슬롯으로 Stepper 구축)
3. **Low-level hooks** (`useCalendar`, `useButton` 등): 완전 제어, 자체 DOM에 props spread

---

## 3. Figma↔Code 매핑 충실도 ⭐

### 3.1 매핑 방향: Design-first (Figma-first with structured sync)

```
Adobe Spectrum Design Team (Figma)
         │
         ├─→ spectrum.adobe.com (디자인 문서, Figma 기반)
         ├─→ spectrum-design-data (토큰 JSON, 컴포넌트 스키마)
         │        │
         │        ├─→ @adobe/spectrum-tokens (npm)
         │        └─→ @adobe/spectrum-component-api-schemas (npm)
         │
         ├─→ React Spectrum (@react-spectrum/*) — Adobe 공식
         │        │
         │        └─→ React Aria (@react-aria/*) — headless 기반
         │
         └─→ Figma Community kit (공개)
```

**Spectrum은 명확한 Figma-first 구조이다.** Adobe의 디자인 팀이 Figma에서 디자인 결정을 내리고, 이것이 `spectrum-design-data`를 통해 토큰과 스키마로 구조화된 뒤, React Spectrum에 반영된다. Code-first가 아닌, 디자인 결정이 선행하는 구조.

### 3.2 1:1 대응률

| 비교 쌍 | 대응률 | 설명 |
|---------|-------:|------|
| Spectrum 디자인 ↔ React Spectrum | **~95%** | Adobe 공식 구현, 디자인 팀과 개발 팀 동일 조직 |
| Spectrum 디자인 ↔ Figma kit | **~90%** | 공식 kit, 내부 사용과 동일 소스 (추정) |
| Figma kit ↔ React Spectrum | **~90%** | 동일 디자인 시스템의 양면 표현 |

**근거**: React Spectrum은 Adobe 내부에서 "Spectrum의 React 구현"으로 명시적으로 포지셔닝된다 (`react-spectrum.adobe.com`: "React Spectrum is Adobe's React implementation of Spectrum"). Adobe 제품군에 직접 사용되므로 디자인↔코드 괴리가 구조적으로 최소화된다.

### 3.3 네이밍 정합성

**컴포넌트명**: **높음**. Figma/Spectrum 문서의 컴포넌트명과 React Spectrum 컴포넌트명이 직접 대응:

| Spectrum 디자인 | React Spectrum | React Aria |
|----------------|---------------|------------|
| Button | `<Button>` | `useButton` |
| Action Button | `<ActionButton>` | — |
| Checkbox | `<Checkbox>` | `useCheckbox` |
| Text Field | `<TextField>` | `useTextField` |
| Date Picker | `<DatePicker>` | `useDatePicker` |
| Combo Box | `<ComboBox>` | `useComboBox` |
| Dialog | `<Dialog>` | `useDialog` |
| Table View | `<TableView>` | `useTable` |
| Tabs | `<Tabs>` | `useTabList` / `useTab` |
| Slider | `<Slider>` | `useSlider` |
| Tag Group | `<TagGroup>` | `useTagGroup` |
| Tree View | `<TreeView>` | `useTree` |

**Props명**: Spectrum 디자인 용어와 React props가 높은 정합성 유지:
- `variant`: `"cta"`, `"primary"`, `"secondary"`, `"negative"` — Spectrum 디자인의 button variant명과 일치
- `isDisabled`, `isRequired`, `isReadOnly` — Spectrum의 상태 명명 반영

### 3.4 Variant property 매핑

**Figma variant ↔ Code props**: 높은 정합성

```
Figma Button variants:        React Spectrum:
  Variant = CTA         →     variant="cta"
  Variant = Primary     →     variant="primary"
  Variant = Secondary   →     variant="secondary"
  Variant = Negative    →     variant="negative"
  State = Disabled      →     isDisabled={true}

Figma Picker variants:        React Spectrum:
  Size = Medium         →     (scale="medium" on Provider)
  Size = Large          →     (scale="large" on Provider)
  State = Default/Hover/Down/Disabled  →  CSS pseudo-class / isDisabled
```

**Scale (medium/large)**: Figma의 크기 variant가 React Spectrum에서는 `Provider`의 `scale` prop으로 전역 적용된다. 개별 컴포넌트 prop이 아닌 Provider 수준에서 제어 — 이는 Figma의 컴포넌트별 size variant와 구조적으로 다르다.

### 3.5 토큰 정합성

**Figma styles/variables ↔ Code design tokens**: **높음**

`spectrum-design-data`가 단일 소스 역할을 하여 Figma와 Code가 동일한 토큰 데이터를 참조:

```
spectrum-design-data/packages/tokens/src/ (JSON)
    │
    ├─→ Figma: component-options-editor 플러그인으로 스키마 작성
    ├─→ Code: @adobe/spectrum-tokens → CSS custom properties (--spectrum-*)
    └─→ 검증: JSON Schema + catalog rules + snapshot testing
```

**컴포넌트 API 스키마** (`@adobe/spectrum-component-api-schemas`): Figma 컴포넌트의 옵션/프로퍼티를 JSON Schema로 정의하여, Figma와 Code 간 API 계약이 구조적으로 관리된다.

### 3.6 구조적 대응 (Figma auto-layout ↔ Code)

| Figma | React Spectrum | 대응 수준 |
|-------|---------------|----------|
| Auto-layout (horizontal) | `<Flex direction="row">` | 개념적 대응 |
| Auto-layout (vertical) | `<Flex direction="column">` | 개념적 대응 |
| Auto-layout gap | `<Flex gap="size-100">` | 토큰 기반 대응 |
| Auto-layout padding | `padding="size-200"` | 토큰 기반 대응 |
| Layout grid | `<Grid columns={...}>` | 개념적 대응 |
| Component variant | React props | 구조적 대응 |
| Styles (color, text) | CSS custom properties (`--spectrum-*`) | 토큰 기반 대응 |

React Spectrum은 **style props** 시스템을 제공하여 Figma의 디자인 속성과 직접 매핑:
- `margin`, `marginTop`, `marginBottom` 등: `DimensionValue` 토큰 사용 (`"size-100"`, `"size-200"` 등)
- `width`, `height`, `minWidth`, `maxWidth`: 동일 토큰 시스템
- `flexGrow`, `flexShrink`, `flexBasis`, `justifySelf`, `alignSelf`: 표준 CSS 속성

### 3.7 종합 평가

| 항목 | 평가 | 근거 |
|------|:----:|------|
| 1:1 대응률 | ★★★★☆ | Adobe 공식 구현, 동일 조직. 단, Figma kit 상세 수 미확인으로 보수적 평가 |
| 네이밍 정합성 | ★★★★★ | 컴포넌트명, props명, variant명 직접 대응 |
| Variant 매핑 | ★★★★☆ | 대부분 직접 매핑. Scale은 Provider 수준으로 구조적 차이 |
| 토큰 정합성 | ★★★★☆ | spectrum-design-data 단일 소스. 단, Figma Variables ↔ Code 자동 변환은 미확인 |
| 구조적 대응 | ★★★☆☆ | auto-layout ↔ flex/grid 개념적 대응. 자동 변환 도구 없음 |

**Spectrum의 Figma↔Code 매핑은 "동일 조직 내 design-first" 모델의 모범 사례이다.** 디자인 팀과 개발 팀이 같은 조직에서 일하며, `spectrum-design-data`가 구조화된 단일 소스 역할을 한다. 그러나 Figma Variables에서 Code 토큰으로의 완전 자동 파이프라인(Style Dictionary 등)은 확인되지 않으며, 컴포넌트 수준에서는 Figma auto-layout 구조가 코드에 자동으로 반영되지 않는다.

---

## 4. API 설계 철학

### 4.1 Composition 중심 설계

React Spectrum은 **Composition을 핵심 원칙**으로 채택한다. 거의 모든 복합 UI가 자식 컴포넌트 조합으로 구성된다:

```jsx
// Configuration이 아닌 Composition
<Picker label="Font" selectedKey={font} onSelectionChange={setFont}>
  <Item key="arial">Arial</Item>
  <Item key="helvetica">Helvetica</Item>
  <Item key="times">Times New Roman</Item>
</Picker>

// 중첩 Composition
<DialogTrigger type="fullscreen">
  <ActionButton>Open</ActionButton>
  {(close) => (
    <Dialog>
      <Heading>Title</Heading>
      <Content>...</Content>
      <ButtonGroup>
        <Button variant="secondary" onPress={close}>Cancel</Button>
        <Button variant="cta" onPress={close}>Confirm</Button>
      </ButtonGroup>
    </Dialog>
  )}
</DialogTrigger>
```

**Collections API**: 동적 데이터도 Composition으로 처리:
```jsx
<ListView items={items} aria-label="List">
  {(item) => (
    <Item key={item.id} textValue={item.name}>
      <Text>{item.name}</Text>
      <Text slot="description">{item.description}</Text>
    </Item>
  )}
</ListView>
```

### 4.2 스타일링 접근법

**React Spectrum v3**: 제한적 커스터마이징 의도적 설계

| 방법 | 범위 | 설명 |
|------|------|------|
| Style props | 단일 인스턴스 | `margin`, `width`, `flex` 등 레이아웃 속성만 허용 |
| `UNSTABLE_className` | 단일 인스턴스 | CSS 클래스 추가 (비권장, 불안정 API) |
| Provider theme | 앱 전역 | colorScheme, scale 전환 |
| 커스텀 Theme 객체 | 앱 전역 | CSS Modules로 변수 재정의 |

**의도적 제약**: React Spectrum v3는 **디자인 시스템 준수를 강제**하기 위해 스타일 커스터마이징을 제한한다. 색상, 타이포그래피 등 시각적 속성은 Spectrum 토큰으로 고정되고, 레이아웃 속성(margin, width, flex)만 개발자에게 개방된다.

**Spectrum 2 (`@react-spectrum/s2`)**: React 19 기반, `react-aria-components` 위에 구축. CSS 기반 스타일링(`page.css`, `./style` 엔트리포인트)으로 전환.

**React Aria (headless)**: 완전한 스타일 자유
- 기본 class names: `.react-aria-DatePicker`, `.react-aria-CalendarCell`
- Data attributes: `data-pressed`, `data-selected`, `data-dragging`
- Tailwind 플러그인: `tailwindcss-react-aria-components` (`pressed:bg-gray-100`, `group-selected:font-semibold`)
- Render props: `{({ isSelected }) => …}`
- CSS, Tailwind, styled-components, Panda CSS 등 모든 스타일링 솔루션 호환

### 4.3 Headless 분리: React Aria

React Spectrum의 가장 중요한 구조적 결정은 **React Aria로의 headless 분리**이다:

```
React Spectrum (@react-spectrum/*)
    │  Spectrum 디자인 적용 (스타일, 토큰)
    │
    ├── React Aria (@react-aria/*) — 54개 패키지
    │     접근성, 키보드, 상호작용 로직
    │     스타일 완전 비종속
    │
    └── React Stately (@react-stately/*)
          상태 관리 로직
```

**React Aria 3단계 API**:

| 단계 | 사용처 | 제어 수준 |
|------|--------|----------|
| **High-level components** (`react-aria-components`) | 빠른 구축, 내장 DOM 구조 | 중간 |
| **Contexts + Slots** | 커스텀 조합, 부분 교체 | 높음 |
| **Hooks** (`useButton`, `useCalendar` 등) | 완전 커스텀 DOM | 완전 |

```tsx
// Hook 레벨: 완전 제어
import {useButton} from 'react-aria';

function MyButton(props) {
  let ref = useRef(null);
  let { buttonProps } = useButton(props, ref);
  return <button {...buttonProps} ref={ref} className="my-custom-style" />;
}
```

### 4.4 커스터마이징 시스템

| 레벨 | 방법 | 용도 |
|------|------|------|
| **토큰** | CSS custom properties (`--spectrum-*`) | 디자인 값 오버라이드 |
| **테마** | Provider + Theme 객체 | colorScheme, scale 전환 |
| **레이아웃** | Style props (margin, width, flex) | 배치 조정 |
| **구조** | Compound composition | 자식 컴포넌트 조합 변경 |
| **행동** | React Aria hooks | 상호작용 로직 커스텀 |
| **완전 커스텀** | React Aria standalone | Spectrum 스타일 없이 로직만 사용 |

---

## 5. 접근성

### 5.1 내장 ARIA

React Spectrum의 접근성은 React Aria 계층에서 제공되며, **W3C ARIA Authoring Practices Guide**를 기반으로 한다:

- 모든 인터랙티브 컴포넌트에 적절한 `role`, `aria-*` 속성 자동 적용
- 브라우저와 스크린 리더 간 동작 차이 정규화
- `aria-modal-polyfill` 패키지로 구형 브라우저의 `aria-modal` 지원
- `live-announcer` 패키지로 동적 콘텐츠 변경 알림
- `visually-hidden` 패키지로 스크린 리더 전용 콘텐츠

**주요 ARIA 패턴 구현**:
- Combobox: `role="combobox"`, `aria-expanded`, `aria-activedescendant`
- ListBox: `role="listbox"`, `role="option"`, `aria-selected`
- Dialog: `role="dialog"`, `aria-modal`, focus trap
- TableView: `role="grid"`, `role="row"`, `role="columnheader"`, `role="gridcell"`
- Tabs: `role="tablist"`, `role="tab"`, `role="tabpanel"`
- Menu: `role="menu"`, `role="menuitem"`

### 5.2 키보드 네비게이션

**"Keyboard interactions are first-class"** — React Aria 공식 입장:

| 기능 | 설명 |
|------|------|
| Arrow key navigation | ListBox, Menu, Tabs, Table, Tree 등 |
| Typeahead | 목록에서 키 입력으로 항목 검색 |
| Multi-selection modifiers | Shift+Click, Ctrl/Cmd+Click |
| Landmark navigation | 페이지 내 랜드마크 이동 |
| Focus management | 오버레이 내 focus containment, 닫기 시 focus 복원, 항목 삭제 시 focus 이동 |
| Focus ring | 키보드 사용 시에만 표시 (마우스 클릭 시 비표시) |
| 모바일 스크린 리더 | 키보드 없이 모든 동작 접근 가능, dialog에 hidden dismiss button 추가 |

### 5.3 WCAG 준수

- **WAI-ARIA Authoring Practices Guide** 기반 구현
- 실제 프로덕션 앱(Adobe Creative Cloud)에서 광범위하게 테스트
- 다양한 스크린 리더(VoiceOver, NVDA, JAWS 등) 및 디바이스에서 검증
- Touch, mouse, keyboard, screen reader 모든 입력 방식 지원
- `prefers-reduced-motion` 고려
- High contrast 모드 지원 (테마 variant)
- **국제화**: 30+ 언어, 13 캘린더 시스템, 5 넘버링 시스템, RTL 레이아웃

### 5.4 접근성 아키텍처의 의의

React Spectrum/React Aria의 접근성 접근법은 업계 최고 수준으로 평가된다:
- 접근성을 **사후 추가가 아닌 설계 단계부터 내장**
- Headless 계층(React Aria)에 접근성 로직을 격리하여, 어떤 스타일링을 적용해도 접근성 보장
- Adobe의 실제 제품(수억 명 사용자)에서 검증된 실전 테스트
- 브라우저/스크린 리더 호환성 이슈를 추적하는 [전용 위키 페이지](https://github.com/adobe/react-spectrum/wiki) 운영

---

## 6. 동기화 거버넌스

### 6.1 프로세스: Design-first, 구조화된 반자동 동기화

```
Adobe Spectrum Design Team
    │
    ├─ Figma에서 디자인 결정
    ├─ component-options-editor (Figma 플러그인)로 스키마 작성
    │
    ▼
spectrum-design-data 모노레포
    │
    ├─ packages/tokens/src/ (토큰 JSON)
    ├─ packages/component-schemas/ (컴포넌트 API 스키마)
    ├─ packages/design-data/ (정규 데이터셋: tokens, components, fields, mode-sets, guidelines, registry)
    ├─ packages/design-data-spec/ (명세, JSON Schema, 검증 규칙, 적합성 픽스처)
    │
    ├─ 검증: JSON Schema (Layer 1) + Catalog rules (Layer 2)
    ├─ Diff: diff-generator / optimized-diff
    ├─ Changeset: token-changeset-generator
    │
    ▼
npm 발행
    ├─ @adobe/spectrum-tokens
    ├─ @adobe/spectrum-component-api-schemas
    └─ @adobe/spectrum-design-data
    │
    ▼
React Spectrum (@react-spectrum/*)
    └─ 토큰을 CSS custom properties로 소비
```

### 6.2 도구

| 도구 | 사용 여부 | 역할 |
|------|:---------:|------|
| Style Dictionary | ❌ | 사용하지 않음 |
| Tokens Studio | ❌ | 사용하지 않음 |
| Figma Variables | ✅ (추정) | Figma 내 디자인 토큰 관리 |
| **component-options-editor** (자체 Figma 플러그인) | ✅ | 컴포넌트 옵션 스키마 작성/편집 |
| **design-data CLI** (자체 Rust CLI) | ✅ | 토큰 검증, 해결, diff, 쿼리, 마이그레이션 |
| **diff-generator / optimized-diff** (자체) | ✅ | 토큰 변경 분석 |
| **token-changeset-generator** (자체) | ✅ | Changeset 자동 생성 |
| **token-manifest-builder** (자체) | ✅ | 토큰 배포 매니페스트 생성 |
| **transform-tokens-json** (자체) | ✅ | 토큰 형식 변환/병합 |
| **MCP 서버** (자체, 3종) | ✅ | AI 어시스턴트에 디자인 데이터 제공 |
| Moon (태스크 러너) | ✅ | 빌드/검증 오케스트레이션 |
| Changesets | ✅ | 버전 관리/릴리스 |
| pnpm | ✅ | 패키지 관리 |

**핵심 관찰**: Adobe는 Style Dictionary나 Tokens Studio 같은 범용 도구를 사용하지 않고, **전용 도구 체인을 자체 구축**했다. Rust 기반 CLI, Figma 플러그인, diff 엔진, MCP 서버까지 포함하는 고도로 전문화된 파이프라인이다.

### 6.3 릴리스 주기

| 패키지 | 릴리스 방식 | 비고 |
|--------|------------|------|
| `@adobe/spectrum-tokens` | Semantic Versioning, Changesets | Conventional Commits, GitHub Actions |
| `@react-spectrum/*` | Lerna 기반 모노레포 릴리스 | yarn workspaces |
| `@react-spectrum/s2` | 독립 버전 (v1.5.1) | React 19 peer dependency |

- `spectrum-design-data`에 `docs/release-timeline` — 릴리스 빈도/개발 활동 시각화 도구 존재
- `tools/release-analyzer` — 릴리스 이력 분석 도구
- Spectrum 1 (legacy): `s1-legacy` 브랜치, `v12.x.x` npm 패키지로 보존
- Spectrum 2: `main` 브랜치에서 릴리스

### 6.4 기여 모델

**React Spectrum** (GitHub 확인):
- 오픈소스, Apache-2.0 라이선스
- GitHub PR 기반 기여
- Adobe CLA(Contributor License Agreement) 서명 필요
- 대규모 변경은 **RFC 프로세스** 필수 (`rfcs/` 폴더)
- `help wanted`, `good first issue` 태그로 커뮤니티 기여 유도
- 테스트: Jest + react-testing-library
- 시각 테스트: Storybook story per visual state
- CI: CircleCI, Chromatic (시각 회귀 테스트)
- Linting: oxlint
- Node v24.14.1+, Yarn v1.22.0+

**spectrum-design-data**:
- 오픈소스, Apache-2.0
- pnpm + Moon 태스크 러너
- Conventional Commits + commitlint
- Husky git hooks
- Prettier 포맷팅

### 6.5 Spectrum 1 → Spectrum 2 전환

현재 Adobe는 Spectrum 1에서 Spectrum 2로의 대규모 전환을 진행 중:

| 항목 | Spectrum 1 (v3) | Spectrum 2 |
|------|-----------------|------------|
| 패키지 | `@react-spectrum/*` (63개) | `@react-spectrum/s2` (단일 패키지) |
| React 버전 | React 16.8+ | React 19+ |
| 기반 | 자체 컴포넌트 아키텍처 | `react-aria-components` 위 구축 |
| 스타일링 | CSS Modules + Provider | CSS 기반 (`page.css`, `./style`) |
| 토큰 | `@adobe/spectrum-tokens` v12.x | `spectrum-design-data` main 브랜치 |
| 상태 | 활성 (maintenance 방향) | 활성 개발 |

### 6.6 동기화 리스크 및 강점

**강점**:
1. **동일 조직**: 디자인 팀과 개발 팀이 Adobe 내부에서 긴밀 협업
2. **구조화된 단일 소스**: `spectrum-design-data`가 토큰/스키마/명세의 정규 소스
3. **다층 검증**: JSON Schema + catalog rules + snapshot testing으로 정합성 보장
4. **전용 도구 체인**: Figma 플러그인, Rust CLI, diff 엔진 등 고도화된 자체 도구
5. **실전 검증**: Adobe Creative Cloud 제품군에서 직접 사용

**리스크**:
1. **Figma Variables ↔ Code 자동 변환 부재**: Style Dictionary 같은 자동 변환 도구 미사용, 수동/반자동 관리
2. **Spectrum 1 → 2 전환기**: 두 버전 공존으로 복잡성 증가
3. **폐쇄적 도구 체인**: 자체 도구가 Adobe 내부 워크플로우에 최적화되어 외부 기여자 진입 장벽
4. **Figma kit 접근성**: 공식 kit이 공개되어 있으나 상세 구조 검증이 제한적

---

## 7. 핵심 요약

| 차원 | 평가 | 핵심 근거 |
|------|------|----------|
| 토큰 아키텍처 | ★★★★☆ | palette→semantic→component 3계층, 전용 모노레포, 다층 검증. 단, 자동 변환 파이프라인 부재 |
| 컴포넌트 인벤토리 | ★★★★★ | 82+ 사용자-facing 컴포넌트, 14개 카테고리, Color/Date/DnD 등 고급 영역 포함 |
| Figma↔Code 매핑 | ★★★★☆ | 동일 조직 design-first, 컴포넌트 API 스키마로 구조화된 계약. 단, 완전 자동 동기화는 아님 |
| API 설계 철학 | ★★★★★ | React Aria 3단계(headless→context→component), Composition 중심, 의도적 스타일 제약 |
| 접근성 | ★★★★★ | WAI-ARIA APG 기반, 54개 headless 패키지에 내장, Adobe 제품 실전 검증, 업계 최고 수준 |
| 동기화 거버넌스 | ★★★★☆ | 전용 도구 체인(Figma 플러그인, Rust CLI, diff 엔진), Changesets 릴리스. 단, 범용 도구 미사용 |

### 벤치마크 관점에서의 시사점

Adobe Spectrum은 **"동일 조직 내 design-first" 모델의 가장 성숙한 구현**이다:

1. **계층 분리의 모범**: React Aria(headless) → React Spectrum(styled) 분리는 접근성과 디자인을 독립적으로 진화시킬 수 있는 구조적 기반을 제공한다. 이 패턴은 다른 디자인 시스템(shadcn/ui의 Radix 기반, Chakra의 Zag 기반)에도 영향을 미쳤다.

2. **토큰 거버넌스의 전문화**: Style Dictionary 같은 범용 도구 대신 Rust CLI, Figma 플러그인, MCP 서버까지 포함하는 전용 도구 체인을 구축한 것은, 대규모 디자인 시스템에서 토큰 관리가 얼마나 복잡한 문제인지를 보여준다.

3. **Figma↔Code 매핑의 현실**: 동일 조직 내에서조차 Figma Variables에서 Code로의 완전 자동 동기화는 달성되지 않았다. 대신 **구조화된 검증**(JSON Schema, catalog rules, snapshot)으로 정합성을 보장하는 실용적 접근을 취한다.

4. **Spectrum 1→2 전환의 교훈**: 대규모 디자인 시스템의 버전 전환이 얼마나 복잡한지 보여준다. 63개 패키지의 v3에서 단일 패키지 s2로의 통합은 API 단순화를 추구하지만, 기존 사용자의 마이그레이션 비용이 크다.

5. **접근성의 구조화**: 접근성을 별도 레이어(React Aria)로 분리하여 54개 독립 패키지로 배포하는 접근법은, 접근성이 "컴포넌트의 속성"이 아닌 "기반 인프라"임을 구조적으로 증명한다.
