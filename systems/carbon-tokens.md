# IBM Carbon — 코드 레벨 토큰 심층 분석

> **분석 대상**: `carbon-design-system/carbon` monorepo (main branch)
> **핵심 패키지**: `@carbon/colors`, `@carbon/themes`, `@carbon/styles`
> **분석 기준일**: 2026-07-26
> **초점**: 토큰의 정의·소비·거버넌스 (코드 레벨)

---

## 1. 토큰 정의 (Definition)

### 1.1 3-Layer 아키텍처: 실제 코드

Carbon은 **Primitive → Core/Semantic → Component** 3단계 토큰 구조를 사용한다. 각 계층이 별도 npm 패키지에 물리적으로 분리되어 있다.

```
@carbon/colors          → Primitive (원시 색상 팔레트)
@carbon/themes          → Core/Semantic (시맨틱 역할 매핑, 테마별 값)
@carbon/styles/scss/components/*  → Component (컴포넌트 전용 토큰)
```

#### Layer 1: Primitive — `@carbon/colors`

**파일**: `packages/colors/src/colors.ts`

Swatch(색상군) × Grade(10~100) 매트릭스 구조. 각 grade에 hover 변형도 존재:

```ts
// packages/colors/src/colors.ts (실제 코드)
export const blue10 = '#edf5ff';
export const blue20 = '#d0e2ff';
export const blue30 = '#a6c8ff';
export const blue40 = '#78a9ff';
export const blue50 = '#4589ff';
export const blue60 = '#0f62fe';   // ← Carbon 브랜드 블루
export const blue70 = '#0043ce';
export const blue80 = '#002d9c';
export const blue90 = '#001d6c';
export const blue100 = '#001141';

export const blue = {
  10: blue10, 20: blue20, 30: blue30, 40: blue40, 50: blue50,
  60: blue60, 70: blue70, 80: blue80, 90: blue90, 100: blue100,
};

// hover 변형도 grade별로 존재
export const blue60Hover = '#0050e6';
export const blue70Hover = '#0053ff';
```

**전체 swatch 목록** (14개):

| Swatch | Grade 범위 | 비고 |
|--------|-----------|------|
| `black` | 100만 | `#000000` |
| `white` | 0만 | `#ffffff` |
| `yellow` | 10–100 | |
| `orange` | 10–100 | |
| `red` | 10–100 | |
| `magenta` | 10–100 | |
| `purple` | 10–100 | |
| `blue` | 10–100 | 브랜드 색상 |
| `cyan` | 10–100 | |
| `teal` | 10–100 | |
| `green` | 10–100 | |
| `coolGray` | 10–100 | |
| `gray` | 10–100 | 테마 배경의 기반 |
| `warmGray` | 10–100 | |

**Primitive 총량**: 14 swatch × 10 grade = **~140 base 색상** + **~140 hover 변형** + black/white = **~282개**

Sass에서는 `@carbon/colors`에서 `$blue-60`, `$gray-10` 형태로 소비:

```scss
@use '@carbon/colors';
colors.$blue-60;      // #0f62fe
colors.$cool-gray-10; // #f2f4f8
colors.$black-100;    // #000000
```

#### Layer 2: Core/Semantic — `@carbon/themes`

**파일 구조**: `packages/themes/scss/`

```
packages/themes/scss/
├── _themes.scss          → @forward 'generated/themes' (테마 맵)
├── _tokens.scss          → @forward 'generated/tokens' (토큰 변수)
├── _theme.scss           → theme() mixin, get() function
├── _component-tokens.scss → 컴포넌트 토큰 배럴
├── _config.scss          → $prefix 설정
├── _utilities.scss
└── compat/               → v10 호환 레이어
```

테마 값은 `generated/` 디렉토리에 **빌드 타임에 생성**된다. Source of Truth는 TypeScript(`packages/themes/src/tokens/`)이고, 여기서 Sass와 DTCG JSON이 모두 생성된다.

**4개 내장 테마** (Sass map):

```scss
// 사용 방식
@use '@carbon/themes/scss/themes';

themes.$white   // White 테마 (기본값, light)
themes.$g10     // Gray 10 테마 (light)
themes.$g90     // Gray 90 테마 (dark)
themes.$g100    // Gray 100 테마 (dark)
```

각 테마는 **token-name → value**의 Sass map이다. White 테마 기준 실제 값:

| Token | White 테마 값 | 역할 |
|-------|-------------|------|
| `$background` | `#ffffff` | 페이지 배경 |
| `$layer-01` | `#f4f4f4` | background 위 컨테이너 |
| `$layer-02` | `#ffffff` | layer-01 위 컨테이너 |
| `$layer-03` | `#f4f4f4` | layer-02 위 컨테이너 |
| `$text-primary` | `#161616` | 본문 텍스트 |
| `$text-secondary` | `#525252` | 보조 텍스트 |
| `$link-primary` | `#0f62fe` | 링크 (= `$blue-60`) |
| `$interactive` | `#0f62fe` | 인터랙티브 요소 |
| `$support-error` | `#da1e28` | 에러 (= `$red-60`) |
| `$support-success` | `#24a148` | 성공 (= `$green-50`) |
| `$focus` | `#0f62fe` | 포커스 표시 |
| `$border-subtle-00` | `#e0e0e0` | 미묘한 보더 |
| `$field-01` | `#f4f4f4` | 입력 필드 배경 |

**Core 토큰 카테고리별 수량** (v11TokenGroup.ts 기준):

| 카테고리 | 토큰 수 | 대표 토큰 |
|----------|---------|----------|
| Background | 9 | `$background`, `$background-hover`, `$background-inverse` |
| Layer | 30 | `$layer-01`~`$layer-accent-active-03`, `$layer-selected-inverse` |
| Field | 6 | `$field-01`~`$field-hover-03` |
| Border | 16 | `$border-subtle-00`~`$border-disabled` |
| Text | 9 | `$text-primary`~`$text-disabled` |
| Link | 8 | `$link-primary`~`$link-inverse-visited` |
| Icon | 7 | `$icon-primary`~`$icon-interactive` |
| Support | 11 | `$support-error`~`$support-caution-undefined` |
| Focus | 3 | `$focus`, `$focus-inset`, `$focus-inverse` |
| Skeleton | 2 | `$skeleton-background`, `$skeleton-element` |
| Syntax Highlighting | ~80 | `$syntax-keyword`~`$syntax-deleted` |
| AI | ~42 | `$ai-popover-background`~`$chat-button-text-selected` |
| Contextual (별칭) | 14 | `$layer`, `$field`, `$border-subtle` (레이어 맥락에 따라 값 변경) |
| Misc | 6 | `$interactive`, `$highlight`, `$overlay`, `$toggle-off`, `$shadow`, `$color-scheme` |

**Core 토큰 총량**: **~243개** (syntax, AI 포함)

#### Layer 3: Component — `@carbon/styles/scss/components/`

**파일**: `packages/themes/src/tokens/components.ts` (Source of Truth)

5개 컴포넌트에 전용 토큰이 정의되어 있다:

```ts
// packages/themes/src/tokens/components.ts (실제 코드)
export const button = TokenGroup.create({
  name: 'Button',
  tokens: [
    'button-separator',
    'button-primary',
    'button-secondary',
    'button-tertiary',
    'button-danger-primary',
    'button-danger-secondary',
    'button-danger-active',
    'button-primary-active',
    'button-secondary-active',
    'button-tertiary-active',
    'button-danger-hover',
    'button-primary-hover',
    'button-secondary-hover',
    'button-tertiary-hover',
    'button-disabled',
  ],
});

export const notification = TokenGroup.create({
  name: 'Notification',
  tokens: [
    'notification-background-error',
    'notification-background-success',
    'notification-background-info',
    'notification-background-warning',
    'notification-action-hover',
    'notification-action-tertiary-inverse',
    'notification-action-tertiary-inverse-active',
    'notification-action-tertiary-inverse-hover',
    'notification-action-tertiary-inverse-text',
    'notification-action-tertiary-inverse-text-on-color-disabled',
  ],
});

export const tag = TokenGroup.create({
  name: 'Tag',
  tokens: [
    'tag-background-red', 'tag-color-red', 'tag-hover-red',
    'tag-background-magenta', 'tag-color-magenta', 'tag-hover-magenta',
    // ... 10개 색상군 × 3 (background, color, hover) + border 변형
    'tag-border-red', 'tag-border-blue', /* ... */
  ],  // 총 40개
});

export const status = TokenGroup.create({
  name: 'Status',
  tokens: [
    'status-red', 'status-orange', 'status-orange-outline',
    'status-yellow', 'status-yellow-outline', 'status-purple',
    'status-green', 'status-blue', 'status-gray',
  ],  // 총 9개
});

export const contentSwitcher = TokenGroup.create({
  name: 'Content Switcher',
  tokens: [
    'content-switcher-selected',
    'content-switcher-background',
    'content-switcher-background-hover',
  ],  // 총 3개
});
```

**Component 토큰 총량**: Button 15 + Notification 10 + Tag 40 + Status 9 + Content Switcher 3 = **77개**

Sass 배럴 파일에서 이 5개를 모두 forward:

```scss
// packages/themes/scss/_component-tokens.scss (실제 코드)
@forward 'generated/button-tokens';
@forward 'generated/tag-tokens';
@forward 'generated/notification-tokens';
@forward 'generated/status-tokens';
@forward 'generated/content-switcher-tokens';
```

### 1.2 Layer Level System (01/02/03)

Carbon의 가장 독특한 토큰 패턴. UI 중첩 깊이에 따라 **동일 역할의 토큰이 3단계로 분기**한다.

**원리**: `$background` → `$layer-01` → `$layer-02` → `$layer-03`으로 중첩되며, 각 레벨에서 field, border, accent 토큰이 **맥락에 맞게 자동 전환**된다.

```
$background (#ffffff, White 테마)
  └─ $layer-01 (#f4f4f4)        ← field-01, border-subtle-01이 이 레벨에 쌍
       └─ $layer-02 (#ffffff)    ← field-02, border-subtle-02가 이 레벨에 쌍
            └─ $layer-03 (#f4f4f4) ← field-03, border-subtle-03이 이 레벨에 쌍
```

**실제 토큰 매핑** (White 테마):

| 레벨 | layer | field | border-subtle | border-strong | layer-accent |
|------|-------|-------|---------------|---------------|--------------|
| 01 | `#f4f4f4` | `#f4f4f4` | `#c6c6c6` | `#8d8d8d` | `#e0e0e0` |
| 02 | `#ffffff` | `#ffffff` | `#e0e0e0` | `#8d8d8d` | `#e0e0e0` |
| 03 | `#f4f4f4` | `#f4f4f4` | `#c6c6c6` | `#8d8d8d` | `#e0e0e0` |

각 레벨에 상태 변형(hover, active, selected, selected-hover)이 존재하므로, layer 카테고리だけで 30개 토큰이 생성된다.

**코드 구현** — `packages/styles/scss/layer/_layer-sets.scss`:

```scss
// packages/styles/scss/layer/_layer-sets.scss (실제 코드)
$-default-layer-sets: (
  layer: (
    theme.$layer-01,    // 레벨 1
    theme.$layer-02,    // 레벨 2
    theme.$layer-03,    // 레벨 3
  ),
  layer-active: (
    theme.$layer-active-01,
    theme.$layer-active-02,
    theme.$layer-active-03,
  ),
  field: (
    theme.$field-01,
    theme.$field-02,
    theme.$field-03,
  ),
  border-subtle: (
    theme.$border-subtle-00,   // ← 4개 (00, 01, 02, 03)
    theme.$border-subtle-01,
    theme.$border-subtle-02,
    theme.$border-subtle-03,
  ),
  border-strong: (
    theme.$border-strong-01,
    theme.$border-strong-02,
    theme.$border-strong-03,
  ),
  // ... 총 15개 layer set
);
```

**Contextual 토큰**: 레벨 번호 없는 `$layer`, `$field`, `$border-subtle` 등은 **현재 맥락의 레이어 레벨에 따라 값이 자동 변경**되는 별칭 토큰이다. CSS custom property로 구현:

```scss
// packages/styles/scss/theme/_theme.scss (실제 코드)
$layer: custom-property.get-var('layer');
// → var(--cds-layer)

$field: custom-property.get-var('field');
// → var(--cds-field)

$border-subtle: custom-property.get-var('border-subtle');
// → var(--cds-border-subtle)
```

### 1.3 네이밍 Taxonomy

**규칙**: `$` + kebab-case

```
$border-subtle-selected-01
│      │      │         └─ 레이어 레벨 (01, 02, 03)
│      │      └─ 상태 (hover, active, selected, disabled, inverse, visited)
│      └─ 시맨틱 역할 (subtle, strong, interactive, primary, secondary)
└─ 카테고리 (background, layer, field, border, text, link, icon, support, focus)
```

**컴포넌트 토큰**: `{component}-{role}[-{state}]`

```
$button-primary-hover
│      │        └─ 상태
│      └─ 역할 (primary, secondary, tertiary, danger-*)
└─ 컴포넌트 (button, notification, tag, status, content-switcher)
```

**태그 토큰의 특수 패턴**: `{component}-{property}-{color}`

```
$tag-background-red, $tag-color-red, $tag-hover-red
$tag-border-cool-gray, $tag-background-warm-gray
```

### 1.4 Source of Truth와 생성 파이프라인

```
packages/themes/src/tokens/     ← TypeScript Source of Truth
├── v11TokenGroup.ts            ← 시맨틱 토큰 그룹 정의
├── v11TokenSet.ts              ← 레이어 세트 구성
├── components.ts               ← 컴포넌트 토큰 정의
├── v10.ts                      ← v10 레거시 토큰 (호환용)
├── Token.ts, TokenGroup.ts, TokenSet.ts  ← 토큰 모델 클래스
└── index.ts

        ↓ 빌드 (tasks/)

packages/themes/scss/generated/  ← 생성된 Sass 파일
├── themes.scss                  ← 4개 테마 맵
├── tokens.scss                  ← 토큰 변수
├── button-tokens.scss           ← 컴포넌트별 생성
├── tag-tokens.scss
├── notification-tokens.scss
├── status-tokens.scss
└── content-switcher-tokens.scss

packages/themes/src/dtcg/        ← 생성된 DTCG JSON
├── white.json, g10.json, g90.json, g100.json
└── components/
    ├── button.json, tag.json, notification.json
    ├── status.json, content-switcher.json
```

### 1.5 토큰 총량 요약

| 계층 | 수량 | 비고 |
|------|------|------|
| Primitive (`@carbon/colors`) | ~282 | 14 swatch × 10 grade + hover |
| Core/Semantic (`@carbon/themes`) | ~243 | background, layer, field, border, text, link, icon, support, focus, syntax, AI, misc |
| Component | 77 | button 15, notification 10, tag 40, status 9, content-switcher 3 |
| **합계** | **~602** | |

> 참고: spacing(`$spacing-01`~`$spacing-13`), layout, motion, type 토큰은 별도 패키지(`@carbon/layout`, `@carbon/motion`, `@carbon/type`)에 정의되며, 위 수치에는 미포함.

---

## 2. 토큰 소비 (Consumption)

### 2.1 핵심 발견: CSS Custom Properties 기반 소비

**중요 수정**: 기존 분석에서 "Carbon은 CSS custom properties를 기본 출력 포맷으로 사용하지 않는다"고 기술했으나, **코드 확인 결과 이는 부정확하다**. Carbon v11은 `theme()` mixin을 통해 **모든 토큰을 CSS custom property로 출력**하며, 컴포넌트는 `var(--cds-*)` 형태로 토큰을 소비한다.

**theme() mixin** — `packages/themes/scss/_theme.scss`:

```scss
// packages/themes/scss/_theme.scss (실제 코드)
@mixin theme($active-theme: $theme, $component-tokens...) {
  // 모든 토큰을 CSS custom property로 출력
  @each $token, $value in $active-theme {
    @include -custom-property($token, $value);
  }

  // 컴포넌트 토큰도 출력
  @each $group in $component-tokens {
    @each $token, $value in $group {
      @include -custom-property($token, $value);
    }
  }
}

// 실제 CSS custom property 생성
@mixin -custom-property($name, $value) {
  @if meta.type-of($value) == map {
    @each $property, $property-value in $value {
      @if meta.type-of($property-value) != map {
        @include -custom-property('#{$name}-#{$property}', $property-value);
      }
    }
  } @else {
    --#{config.$prefix}-#{$name}: #{$value};
    // 예: --cds-background: #ffffff;
    // 예: --cds-text-primary: #161616;
  }
}
```

**custom-property 유틸리티** — `packages/styles/scss/utilities/_custom-property.scss`:

```scss
// packages/styles/scss/utilities/_custom-property.scss (실제 코드)
@function get-name($name) {
  @return --#{config.$prefix}-#{$name};
  // → --cds-background
}

@function get-var($name, $fallback: false) {
  @if $fallback {
    @return var(--#{config.$prefix}-#{$name}, #{$fallback});
    // → var(--cds-button-primary, #0f62fe)
  }
  @return var(--#{config.$prefix}-#{$name});
  // → var(--cds-layer)
}

@mixin declaration($name, $value) {
  #{get-name($name)}: #{$value};
  // → --cds-layer: #f4f4f4;
}
```

**출력 결과** (개념적):

```css
:root {
  --cds-background: #ffffff;
  --cds-layer-01: #f4f4f4;
  --cds-text-primary: #161616;
  --cds-link-primary: #0f62fe;
  --cds-focus: #0f62fe;
  /* ... ~243개 토큰 */
}
```

### 2.2 컴포넌트 SCSS의 토큰 소비 패턴

**Button 컴포넌트** — `packages/styles/scss/components/button/_button.scss`:

```scss
// packages/styles/scss/components/button/_button.scss (실제 코드, 발췌)
@use 'tokens' as *;          // ← 컴포넌트 토큰 ($button-primary 등)
@use 'vars' as *;
@use 'mixins' as *;
@use '../../config' as *;    // ← $prefix
@use '../../spacing' as *;   // ← $spacing-05 등
@use '../../theme' as *;     // ← $text-on-color, $text-inverse 등
@use '../../type' as *;
@use '../../layer' as *;     // ← 레이어 시스템

// Primary Button
.#{$prefix}--btn--primary {
  @include button-theme(
    $button-primary,           // 배경: var(--cds-button-primary, #0f62fe)
    transparent,               // 보더
    $text-on-color,            // 텍스트: var(--cds-text-on-color, #ffffff)
    $button-primary-hover,     // hover 배경
    currentColor,              // hover 보더
    $button-primary-active     // active 배경
  );
}

// Tertiary Button
.#{$prefix}--btn--tertiary {
  @include button-theme(
    transparent,
    $button-tertiary,          // 보더 색상
    $button-tertiary,          // 텍스트 색상
    $button-tertiary-hover,
    currentColor,
    $button-tertiary-active
  );
}
```

**컴포넌트 토큰의 테마 분기 구조** — `packages/styles/scss/components/button/_tokens.scss`:

```scss
// packages/styles/scss/components/button/_tokens.scss (실제 코드, 발췌)
@use '@carbon/themes/scss/component-tokens' as button;

$button-primary: (
  fallback: map.get(button.$button-primary, white-theme),
  values: (
    (theme: themes.$white, value: map.get(button.$button-primary, white-theme)),
    (theme: themes.$g10,   value: map.get(button.$button-primary, g-10)),
    (theme: themes.$g90,   value: map.get(button.$button-primary, g-90)),
    (theme: themes.$g100,  value: map.get(button.$button-primary, g-100)),
  ),
) !default;
```

이 구조는 **컴포넌트 토큰이 테마별로 다른 값을 가질 수 있음**을 의미한다. `component-tokens.get-var()`가 현재 테마에 맞는 값을 `var()` fallback과 함께 반환:

```scss
// packages/styles/scss/utilities/_component-tokens.scss (실제 코드)
@function get-var($token-map, $name) {
  @if meta.type-of($token-map) == map {
    $fallback: map.get($token-map, fallback);
    $theme-values: map.get($token-map, values);

    @each $theme-value in $theme-values {
      $theme: map.get($theme-value, theme);
      $value: map.get($theme-value, value);

      @if theme.matches($theme, theme.$theme) {
        @return custom-property.get-var($name, $value);
        // → var(--cds-button-primary, #0f62fe)
      }
    }
    @return custom-property.get-var($name, $fallback);
  }
  @return custom-property.get-var($name, $token-map);
}
```

### 2.3 `@use` 모듈 패턴

Carbon v11은 Sass Modules (`@use`/`@forward`)를 전면 채택. `@import` 미사용.

```scss
// 전체 스타일 로드
@use '@carbon/styles';

// 컴포넌트 선택 로드
@use '@carbon/styles/scss/components/button';
@use '@carbon/styles/scss/components/data-table';

// 테마 설정
@use '@carbon/styles/scss/themes';
@use '@carbon/styles/scss/theme' with (
  $theme: themes.$g100
);

// 토큰 직접 참조
@use '@carbon/styles/scss/theme';
.my-element {
  background: theme.$background;   // → var(--cds-background)
  color: theme.$text-primary;      // → var(--cds-text-primary)
}
```

### 2.4 Theme Mixin의 동작 원리

**글로벌 테마 설정**:

```scss
@use '@carbon/styles/scss/themes';
@use '@carbon/styles/scss/theme' with (
  $theme: themes.$g100
);
// → :root에 --cds-* custom properties가 g100 값으로 출력
```

**인라인 테마 스코핑**:

```scss
@use '@carbon/themes/scss/theme';

.my-dark-section {
  @include theme.theme(themes.$g90);
  // → 이 셀렉터 내부에서 --cds-* 값이 g90으로 오버라이드
}
```

**theme() mixin 내부 동작**:

1. `$active-theme` map의 모든 key-value를 순회
2. 각 토큰을 `--cds-{name}: {value}` CSS custom property로 출력
3. 컴포넌트 토큰도 동일하게 출력
4. `color-scheme` custom property 설정
5. High Contrast Mode (`forced-colors`) 대응 오버라이드
6. Layer 토큰을 레벨 1로 재출력 (CSS cascade 문제 해결)

```scss
// packages/styles/scss/_theme.scss (실제 코드, 발췌)
@mixin theme($args...) {
  @include theme.theme($args...);
  color-scheme: custom-property.get-var('color-scheme', light);

  @media screen and (forced-colors: active) {
    @include custom-property.declaration('icon-primary', ButtonText);
    @include custom-property.declaration('focus', Highlight);
    // ... 시스템 색상으로 오버라이드
  }

  // Layer 토큰 재출력 (cascade 문제 해결)
  @include layer-tokens.emit-layer-tokens(1);
}
```

### 2.5 Layer 컴포넌트의 토큰 전환 메커니즘

`<Layer>` React 컴포넌트는 CSS 클래스를 통해 **contextual 토큰 값을 전환**한다.

**SCSS 구현** — `packages/styles/scss/_layer.scss`:

```scss
// packages/styles/scss/_layer.scss (실제 코드)
:root {
  @include layer-tokens.emit-layer-tokens(1);
  // → --cds-layer: var(--cds-layer-01);
  // → --cds-field: var(--cds-field-01);
  // → --cds-border-subtle: var(--cds-border-subtle-01);
}

.#{$prefix}--layer-one {
  @include layer-tokens.emit-layer-tokens(1);
}

.#{$prefix}--layer-two {
  @include layer-tokens.emit-layer-tokens(2);
  // → --cds-layer: var(--cds-layer-02);
  // → --cds-field: var(--cds-field-02);
  // → --cds-border-subtle: var(--cds-border-subtle-02);
}

.#{$prefix}--layer-three {
  @include layer-tokens.emit-layer-tokens(3);
  // → --cds-layer: var(--cds-layer-03);
  // → --cds-field: var(--cds-field-03);
}
```

**emit-layer-tokens mixin**:

```scss
// packages/styles/scss/layer/_layer-tokens.scss (실제 코드)
@mixin emit-layer-tokens($level) {
  @each $key, $layer-set in $layer-sets {
    $value: list.nth($layer-set, $level);
    @include custom-property.declaration($key, $value);
  }
}
```

**결과**: `<Layer level={2}>` 내부의 모든 컴포넌트는 `var(--cds-field)`가 `var(--cds-field-02)`로 자동 전환되어, **컴포넌트 코드 변경 없이 맥락적 색상 계층이 적용**된다.

### 2.6 사용자 토큰 오버라이드

**방법 1: 테마 map 오버라이드**

```scss
@use '@carbon/styles/scss/theme' with (
  $theme: (
    background: #e2e2e2,
    text-primary: #ffffff,
  )
);
```

**방법 2: 기존 테마 확장**

```scss
@use '@carbon/styles/scss/themes';
@use '@carbon/styles/scss/theme' with (
  $fallback: themes.$g100,
  $theme: (
    custom-token-01: #000000,
  )
);
```

**방법 3: 컴포넌트 토큰 오버라이드** (`!default` 플래그 활용)

```scss
// button _tokens.scss의 모든 토큰이 !default로 선언되어 있으므로:
@use '@carbon/styles/scss/components/button/tokens' with (
  $button-primary: (
    fallback: #custom,
    values: (/* ... */)
  )
);
```

**방법 4: Layer set 확장**

```scss
// packages/styles/scss/layer/_layer-sets.scss
$layer-sets: () !default;
$layer-sets: map.deep-merge($-default-layer-sets, $layer-sets);
// → 사용자가 $layer-sets에 커스텀 세트를 추가하면 deep-merge됨
```

---

## 3. 토큰 거버넌스 (Governance)

### 3.1 `@carbon/themes` 패키지 Export

**Sass**:
- `scss/themes` → 4개 테마 Sass map (`$white`, `$g10`, `$g90`, `$g100`)
- `scss/theme` → `theme()` mixin, `get()` function, `matches()` function
- `scss/tokens` → 개별 토큰 Sass 변수
- `scss/component-tokens` → 5개 컴포넌트 토큰 그룹
- `scss/compat/` → v10 호환 테마/토큰

**JavaScript**:

```js
import {
  themes,          // { white: {...}, g10: {...}, g90: {...}, g100: {...} }
  white, g10, g90, g100,  // 개별 테마 객체
  interactive01,   // v10 호환 개별 토큰 값
} from '@carbon/themes';
```

**DTCG JSON** (`packages/themes/src/dtcg/`):

```json
// packages/themes/src/dtcg/white.json (실제 코드, 발췌)
{
  "$schema": "https://tr.designtokens.org/format/",
  "$description": "White theme - Light theme with high contrast",
  "$extensions": {
    "org.carbon": { "color-scheme": "light" }
  },
  "background": {
    "$type": "color",
    "$value": "{white.default}",
    "$description": "Default page background color."
  },
  "background-hover": {
    "$type": "color",
    "$value": "{gray.50}",
    "$extensions": {
      "org.carbon": { "alphaModifier": 0.12 }
    }
  },
  "layer": {
    "01": {
      "$type": "color",
      "$value": "{gray.10}"
    }
  }
}
```

DTCG 포맷은 **W3C Design Tokens Community Group 표준**(`$schema: https://tr.designtokens.org/format/`)을 따르며, 테마별 4개 파일 + 컴포넌트별 5개 파일이 제공된다.

### 3.2 v10 → v11 토큰 마이그레이션

#### v10 토큰 체계 (레거시)

`packages/themes/src/tokens/v10.ts`에 v10 토큰 전체 목록이 보존되어 있다:

```ts
// v10 color 토큰 (실제 코드)
'interactive-01', 'interactive-02', 'interactive-03', 'interactive-04',
'ui-background', 'ui-01', 'ui-02', 'ui-03', 'ui-04', 'ui-05',
'text-01', 'text-02', 'text-03', 'text-04', 'text-05', 'text-error',
'icon-01', 'icon-02', 'icon-03',
'link-01', 'link-02', 'inverse-link',
'field-01', 'field-02',
'support-01', 'support-02', 'support-03', 'support-04',
'danger-01', 'danger-02',
'hover-primary', 'active-primary', 'hover-secondary', 'active-secondary',
'disabled-01', 'disabled-02', 'disabled-03',
// ... 총 ~70개 color 토큰
```

#### 주요 이름 변경 매핑

| v10 토큰 | v11 토큰 | 변경 유형 |
|----------|---------|----------|
| `$ui-background` | `$background` | 이름 변경 |
| `$ui-01` | `$layer-01` | 이름 변경 + 레이어 시스템 도입 |
| `$ui-02` | `$layer-02` | 이름 변경 |
| `$ui-03` | `$layer-accent-01` | 이름 변경 |
| `$ui-04` | `$border-strong-01` | 이름 변경 |
| `$ui-05` | `$border-inverse` | 이름 변경 |
| `$text-01` | `$text-primary` | 번호 → 시맨틱 이름 |
| `$text-02` | `$text-secondary` | 번호 → 시맨틱 이름 |
| `$text-03` | `$text-placeholder` | 번호 → 시맨틱 이름 |
| `$text-04` | `$text-on-color` | 번호 → 시맨틱 이름 |
| `$text-05` | `$text-inverse` | 번호 → 시맨틱 이름 |
| `$icon-01` | `$icon-primary` | 번호 → 시맨틱 이름 |
| `$icon-02` | `$icon-secondary` | 번호 → 시맨틱 이름 |
| `$icon-03` | `$icon-on-color` | 번호 → 시맨틱 이름 |
| `$link-01` | `$link-primary` | 번호 → 시맨틱 이름 |
| `$link-02` | `$link-secondary` | 번호 → 시맨틱 이름 |
| `$interactive-01` | `$interactive` / `$background-brand` | 분리 |
| `$support-01` | `$support-error` | 번호 → 시맨틱 이름 |
| `$support-02` | `$support-success` | 번호 → 시맨틱 이름 |
| `$support-03` | `$support-warning` | 번호 → 시맨틱 이름 |
| `$support-04` | `$support-info` | 번호 → 시맨틱 이름 |
| `$danger-01` | `$support-error` | 통합 |
| `$hover-ui` | `$layer-hover-01` | 레이어 시스템 편입 |
| `$active-ui` | `$layer-active-01` | 레이어 시스템 편입 |
| `$selected-ui` | `$layer-selected-01` | 레이어 시스템 편입 |
| `$disabled-01` | `$text-disabled` / `$icon-disabled` | 역할별 분리 |
| `$inverse-01` | `$background-inverse` | 이름 변경 |
| `$inverse-02` | `$text-inverse` | 이름 변경 |
| `$overlay-01` | `$overlay` | 번호 제거 |
| `$skeleton-01` | `$skeleton-element` | 번호 → 시맨틱 |
| `$skeleton-02` | `$skeleton-background` | 번호 → 시맨틱 |

**v10의 핵심 문제**: 번호 기반 네이밍(`$ui-01`, `$text-01`, `$icon-01`)이 **역할을 직관적으로 전달하지 못함**. v11에서 시맨틱 이름으로 전면 개편.

#### 호환 레이어 (Compat)

`packages/styles/scss/compat/_themes.scss`:

```scss
// packages/styles/scss/compat/_themes.scss (실제 코드)
// v10 + v11 테마를 병합하여 호환 테마 생성
$white: map.merge(themes.$white, compat.$white);
$g10: map.merge(themes.$g10, compat.$g10);
$g90: map.merge(themes.$g90, compat.$g90);
$g100: map.merge(themes.$g100, compat.$g100);
```

이 호환 테마는 **v10 토큰명과 v11 토큰명을 모두 포함**하므로, 마이그레이션 중에도 v10 토큰 참조가 작동한다.

#### Codemod (`@carbon/upgrade`)

`packages/upgrade/transforms/`에 **24개 codemod**이 존재하나, v10→v11 토큰 이름 변경 전용 codemod은 현재 목록에 없다. 대신:

- `refactor-light-to-layer.js` — `light` prop → `<Layer>` 컴포넌트 전환
- `size-prop-update.js` — size prop 표준화
- `update-carbon-components-react-import-to-scoped.js` — import 경로 변경

v10→v11 토큰 마이그레이션은 주로 **문서 기반 수동 전환** + **compat 테마를 통한 점진적 전환** 방식으로 처리되었다.

### 3.3 토큰 Deprecation

v10 토큰 중 일부는 v10 시점에서도 deprecated로 마크되어 있었다:

```ts
// packages/themes/src/tokens/v10.ts (실제 코드)
// deprecated
'brand-01',
'brand-02',
'brand-03',
'active-01',
'hover-field',
'danger',
```

v11에서는 이러한 토큰이 완전히 제거되었고, compat 레이어를 통해서만 접근 가능하다.

### 3.4 Figma Variables ↔ Sass 토큰 매핑

| 측면 | Figma | Code (Sass) | 정합도 |
|------|-------|-------------|--------|
| Color tokens | Figma Variables (color) | `$background`, `$text-primary` 등 | **높음** — 동일 시맨틱 네이밍 |
| 테마 modes | 4개 Variables mode | `$white`, `$g10`, `$g90`, `$g100` | **높음** — 1:1 대응 |
| Component tokens | 컴포넌트 내부 Variables | `$button-primary` 등 | **중간** — Figma에서 별도 Variable 여부 불확실 |
| Spacing | auto-layout 값 | `$spacing-01`~`$spacing-13` | **낮음** — Figma에서 토큰명 참조 안 함 |
| Typography | Text styles | `@carbon/type` mixins | **중간** — 구조 대응, 포맷 상이 |

**자동 동기화 파이프라인 부재**: 코드 토큰(TypeScript → Sass 생성)과 Figma Variables 간 자동 sync 도구(Style Dictionary, Tokens Studio 등)는 공개되어 있지 않다. 단, DTCG JSON export가 존재하므로 **향후 Figma ↔ Code 동기화의 기반**은 마련되어 있다.

### 3.5 DTCG 표준 준수

Carbon은 **W3C DTCG (Design Tokens Community Group) 포맷**으로 토큰을 export한다:

```
packages/themes/src/dtcg/
├── white.json      ← White 테마 전체 토큰
├── g10.json        ← Gray 10 테마
├── g90.json        ← Gray 90 테마
├── g100.json       ← Gray 100 테마
└── components/
    ├── button.json
    ├── content-switcher.json
    ├── notification.json
    ├── status.json
    └── tag.json
```

DTCG JSON의 특징:
- `$schema: "https://tr.designtokens.org/format/"` — W3C 표준 스키마
- `$value`에 **alias 참조** 사용: `"{white.default}"`, `"{gray.50}"`, `"{blue.60}"`
- `$extensions.org.carbon.alphaModifier` — Carbon 고유 확장 (alpha 적용)
- `$extensions.org.carbon.color-scheme` — light/dark 메타데이터

### 3.6 Stylelint / Lint 설정

Carbon monorepo는 **Stylelint**를 사용하나, 토큰 사용 강제 전용 rule의 공개 문서는 제한적이다. 대신:

- **Sass 컴파일 타임 검증**: `theme.get($token)`에서 미존재 토큰 참조 시 `@error` 발생

```scss
// packages/themes/scss/_theme.scss (실제 코드)
@function get($token) {
  @if map.has-key($theme, $token) {
    @return map.get($theme, $token);
  }
  @error "Unable to find token: #{$token} in current $theme";
}
```

- **컴포넌트 토큰 `!default` 패턴**: 모든 컴포넌트 토큰이 `!default`로 선언되어, 오버라이드되지 않으면 기본값 사용
- **테스트**: `packages/themes/__tests__/`, `packages/styles/scss/__tests__/`에서 Sass 컴파일 스냅샷 테스트

---

## 4. 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                    Source of Truth (TypeScript)                  │
│  packages/themes/src/tokens/                                    │
│  ├── v11TokenGroup.ts  (시맨틱 토큰 그룹)                        │
│  ├── components.ts     (컴포넌트 토큰)                           │
│  └── v10.ts            (레거시 호환)                             │
└───────────┬─────────────────────┬───────────────────────────────┘
            │ 빌드                │ 빌드
            ▼                     ▼
┌───────────────────┐  ┌─────────────────────┐
│  Sass (generated) │  │  DTCG JSON          │
│  scss/generated/  │  │  src/dtcg/          │
│  ├── themes.scss  │  │  ├── white.json     │
│  ├── tokens.scss  │  │  ├── g10.json       │
│  └── *-tokens.scss│  │  └── components/    │
└───────┬───────────┘  └─────────────────────┘
        │ @use
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  @carbon/styles/scss/                                           │
│  ├── _theme.scss      → theme() mixin → CSS custom properties   │
│  ├── _layer.scss      → Layer 레벨 시스템                        │
│  ├── theme/_theme.scss → contextual 토큰 var() 바인딩            │
│  └── components/                                                │
│      └── button/                                                │
│          ├── _tokens.scss  → $button-primary 등 (!default)       │
│          └── _button.scss  → @use '../../theme' as *             │
│                              → var(--cds-button-primary)         │
└─────────────────────────────────────────────────────────────────┘
        │ CSS 출력
        ▼
┌─────────────────────────────────────────────────────────────────┐
│  :root {                                                        │
│    --cds-background: #ffffff;                                   │
│    --cds-text-primary: #161616;                                 │
│    --cds-button-primary: #0f62fe;                               │
│    --cds-layer: var(--cds-layer-01);                            │
│    --cds-field: var(--cds-field-01);                            │
│  }                                                              │
│  .cds--layer-two {                                              │
│    --cds-layer: var(--cds-layer-02);                            │
│    --cds-field: var(--cds-field-02);                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. 핵심 발견 요약

### 발견 1: CSS Custom Properties가 실제 소비 메커니즘

기존 문서/분석과 달리, Carbon v11은 **모든 토큰을 `--cds-*` CSS custom property로 출력**하고, 컴포넌트는 `var(--cds-*)`로 소비한다. Sass 변수는 **빌드 타임 접근 인터페이스**이고, 런타임 값은 CSS custom property가 담당한다. 이는 Fluent 2, Material Design 3와 동일한 런타임 메커니즘이다.

### 발견 2: Layer Level System은 CSS Cascade 기반

`<Layer>` 컴포넌트는 JavaScript 로직 없이 **순수 CSS custom property cascade**로 동작한다. `.cds--layer-two` 클래스가 `--cds-field`의 값을 `var(--cds-field-02)`로 재정의하면, 내부 모든 컴포넌트의 `var(--cds-field)`가 자동 전환된다.

### 발견 3: TypeScript가 단일 Source of Truth

Sass, JavaScript, DTCG JSON 모두 TypeScript 정의에서 **빌드 타임에 생성**된다. `generated/` 디렉토리의 Sass 파일은 손으로 편집하지 않는다.

### 발견 4: 컴포넌트 토큰은 5개 컴포넌트에만 존재

Button, Tag, Notification, Status, Content Switcher만 전용 토큰을 가지며, 나머지 ~95개 컴포넌트는 Core/Semantic 토큰을 직접 소비한다.

### 발견 5: v10→v11은 번호 체계에서 시맨틱 체계로의 전환

`$ui-01` → `$layer-01`, `$text-01` → `$text-primary` 등 **번호 기반 → 역할 기반** 네이밍으로 전면 개편. Compat 레이어로 하위 호환을 유지하면서, 전용 codemod보다는 문서 기반 수동 마이그레이션을 권장.

### 발견 6: DTCG 표준 선제 채택

W3C DTCG 포맷의 JSON export를 이미 제공하며, alias 참조(`{blue.60}`)와 Carbon 고유 확장(`alphaModifier`)을 포함한다. 이는 Figma Variables, Style Dictionary 등 외부 도구와의 상호운용성 기반이 된다.
