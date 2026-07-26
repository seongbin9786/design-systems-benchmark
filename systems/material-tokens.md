# Material Design — 코드 수준 토큰 심층 분석

> **분석 대상**: Material Web Components (`material-components/material-web`) 토큰 시스템 + MUI (`mui/material-ui`) 테마 시스템
> **분석 기준일**: 2026-07-26
> **목적**: 토큰의 정의(Definition) → 소비(Consumption) → 거버넌스(Governance) 전 과정을 실제 코드로 추적

---

## 1. Token Definition (정의)

### 1.1 Material Web: tokens/ 디렉토리 구조

`github.com/material-components/material-web/tree/main/tokens` 기준, 총 **57개 SCSS 파일**:

| 구분 | 파일 수 | 네이밍 패턴 | 예시 |
|------|---------|-------------|------|
| **ref** (Reference) | 2 | `_md-ref-*.scss` | `_md-ref-palette.scss`, `_md-ref-typeface.scss` |
| **sys** (System) | 6 | `_md-sys-*.scss` | `_md-sys-color.scss`, `_md-sys-typescale.scss`, `_md-sys-shape.scss`, `_md-sys-elevation.scss`, `_md-sys-motion.scss`, `_md-sys-state.scss` |
| **comp** (Component) | 47 | `_md-comp-*.scss` | `_md-comp-filled-button.scss`, `_md-comp-dialog.scss` 등 |
| 기타 | 2 | `_index.scss`, internal/ | 유틸리티 |

버전 관리: `tokens/versions/v0_192/` 하위에 **자동 생성된** 실제 값 파일들이 위치. 헤더에 명시:

```scss
// !!! THIS FILE WAS AUTOMATICALLY GENERATED !!!
// !!! DO NOT MODIFY IT BY HAND !!!
// Design system display name: Google Material 3
// Design system version: v0.192
// User-configured context group "Audience": "3P"
// User-configured context group "Platform": "Web"
// User-configured context group "Scheme": "Dynamic"
```

→ 토큰 값이 **수동이 아닌 코드 생성(codegen) 파이프라인**에서 나옴을 확인.

### 1.2 네이밍 컨벤션: `md-{layer}-{scope}-{property}`

실제 토큰 이름 예시:

```
md-ref-palette-primary40          → ref 계층, palette 범위, primary40 속성
md-sys-color-primary                → sys 계층, color 범위, primary 속성
md-sys-typescale-body-large-size    → sys 계층, typescale 범위, body-large-size 속성
md-comp-filled-button-container-color → comp 계층, filled-button 범위, container-color 속성
```

CSS custom property로 변환 시: `--md-{layer}-{scope}-{property}`

```css
--md-sys-color-primary: #6750a4;
--md-sys-typescale-body-large-size: 1rem;
--md-filled-button-container-color: var(--md-sys-color-primary);
```

### 1.3 ref → sys → comp 계층: 실제 코드 추적

#### Level 1: Reference (`_md-ref-palette.scss`)

**역할**: 원시 색상 값(raw hex). 디자인 스펙의 "Tonal Palette"를 직접 인코딩.

`tokens/versions/v0_192/_md-ref-palette.scss` (자동 생성, 실제 값):

```scss
@function values($exclude-hardcoded-values: false) {
  @return (
    'black': if($exclude-hardcoded-values, null, #000),
    'white': if($exclude-hardcoded-values, null, #fff),
    // Primary tonal palette (13 stops)
    'primary0': if($exclude-hardcoded-values, null, #000),
    'primary10': if($exclude-hardcoded-values, null, #21005d),
    'primary20': if($exclude-hardcoded-values, null, #381e72),
    'primary30': if($exclude-hardcoded-values, null, #4f378b),
    'primary40': if($exclude-hardcoded-values, null, #6750a4),  // ← Light theme "primary"
    'primary50': if($exclude-hardcoded-values, null, #7f67be),
    'primary60': if($exclude-hardcoded-values, null, #9a82db),
    'primary70': if($exclude-hardcoded-values, null, #b69df8),
    'primary80': if($exclude-hardcoded-values, null, #d0bcff),  // ← Dark theme "primary"
    'primary90': if($exclude-hardcoded-values, null, #eaddff),
    'primary95': if($exclude-hardcoded-values, null, #f6edff),
    'primary99': if($exclude-hardcoded-values, null, #fffbfe),
    'primary100': if($exclude-hardcoded-values, null, #fff),
    // Secondary, Tertiary, Error, Neutral, Neutral-variant도 동일 구조
    'secondary40': if($exclude-hardcoded-values, null, #625b71),
    'tertiary40': if($exclude-hardcoded-values, null, #7d5260),
    'error40': if($exclude-hardcoded-values, null, #b3261e),
    'neutral40': if($exclude-hardcoded-values, null, #605d64),
    // ...총 89개 토큰
  );
}
```

**토큰 수**: primary 13 + secondary 13 + tertiary 13 + error 13 + neutral 21 (추가 stops: 4, 6, 12, 17, 22, 24, 87, 92, 94, 96, 98) + neutral-variant 13 + black/white 2 = **89개**

`$exclude-hardcoded-values` 파라미터: `true` 시 모든 값을 `null`로 반환 → CSS custom property fallback 없이 변수만 선언하는 모드.

#### Level 1b: Reference Typeface (`_md-ref-typeface.scss`)

```scss
@function values($exclude-hardcoded-values: false) {
  @return (
    'brand': if($exclude-hardcoded-values, null, (Roboto)),
    'plain': if($exclude-hardcoded-values, null, (Roboto)),
    'weight-bold': if($exclude-hardcoded-values, null, 700),
    'weight-medium': if($exclude-hardcoded-values, null, 500),
    'weight-regular': if($exclude-hardcoded-values, null, 400)
  );
}
```

→ 총 **5개** 토큰. `brand`와 `plain`이 둘 다 `Roboto`로 기본값 동일.

#### Level 2: System Color (`_md-sys-color.scss`)

**역할**: ref palette의 특정 tone을 **의미 있는 역할(role)** 에 매핑. Light/Dark 이중 정의.

`tokens/versions/v0_192/_md-sys-color.scss` (자동 생성):

```scss
@function values-light($deps: $_default-light) {
  @return (
    'primary': map.get($deps, 'md-ref-palette', 'primary40'),         // #6750a4
    'on-primary': map.get($deps, 'md-ref-palette', 'primary100'),     // #fff
    'primary-container': map.get($deps, 'md-ref-palette', 'primary90'), // #eaddff
    'on-primary-container': map.get($deps, 'md-ref-palette', 'primary10'), // #21005d
    'surface': map.get($deps, 'md-ref-palette', 'neutral98'),         // #fef7ff
    'on-surface': map.get($deps, 'md-ref-palette', 'neutral10'),      // #1d1b20
    'surface-container': map.get($deps, 'md-ref-palette', 'neutral94'), // #f3edf7
    'surface-container-high': map.get($deps, 'md-ref-palette', 'neutral92'),
    'surface-container-highest': map.get($deps, 'md-ref-palette', 'neutral90'),
    'surface-container-low': map.get($deps, 'md-ref-palette', 'neutral96'),
    'surface-container-lowest': map.get($deps, 'md-ref-palette', 'neutral100'),
    'outline': map.get($deps, 'md-ref-palette', 'neutral-variant50'),
    'error': map.get($deps, 'md-ref-palette', 'error40'),             // #b3261e
    // ...총 49개 토큰
  );
}

@function values-dark($deps: $_default-dark) {
  @return (
    'primary': map.get($deps, 'md-ref-palette', 'primary80'),         // #d0bcff
    'on-primary': map.get($deps, 'md-ref-palette', 'primary20'),      // #381e72
    'primary-container': map.get($deps, 'md-ref-palette', 'primary30'), // #4f378b
    'on-primary-container': map.get($deps, 'md-ref-palette', 'primary90'), // #eaddff
    'surface': map.get($deps, 'md-ref-palette', 'neutral6'),          // #141218
    'on-surface': map.get($deps, 'md-ref-palette', 'neutral90'),      // #e6e0e9
    'surface-container': map.get($deps, 'md-ref-palette', 'neutral12'),
    'surface-container-high': map.get($deps, 'md-ref-palette', 'neutral17'),
    'surface-container-highest': map.get($deps, 'md-ref-palette', 'neutral22'),
    'surface-container-low': map.get($deps, 'md-ref-palette', 'neutral10'),
    'surface-container-lowest': map.get($deps, 'md-ref-palette', 'neutral4'),
    'outline': map.get($deps, 'md-ref-palette', 'neutral-variant60'),
    'error': map.get($deps, 'md-ref-palette', 'error80'),             // #f2b8b5
    // ...총 49개 토큰 (light와 동일 키, 다른 tone 매핑)
  );
}
```

**Light ↔ Dark tone 매핑 규칙** (실제 코드에서 추출):

| Color Role | Light tone | Dark tone |
|-----------|-----------|----------|
| `primary` | 40 | 80 |
| `on-primary` | 100 | 20 |
| `primary-container` | 90 | 30 |
| `on-primary-container` | 10 | 90 |
| `surface` | 98 | 6 |
| `on-surface` | 10 | 90 |
| `outline` | neutral-variant 50 | neutral-variant 60 |
| `error` | 40 | 80 |

→ **역전(inversion) 패턴**: Light에서 낮은 tone(40)이 Dark에서 높은 tone(80)으로, 그 반대도 동일.

**sys-color 총 토큰 수**: 49개 (light/dark 각각)

#### Level 2b: System Shape / Elevation / Motion / State

**Shape** (`_md-sys-shape.scss`, 7개 supported + 5개 composite):

```scss
// 실제 값 (versions/v0_192/_md-sys-shape.scss)
'corner-none': 0px,
'corner-extra-small': 4px,
'corner-small': 8px,
'corner-medium': 12px,
'corner-large': 16px,
'corner-extra-large': 28px,
'corner-full': 9999px,
```

**Elevation** (`_md-sys-elevation.scss`, 6개):

```scss
'level0': 0, 'level1': 1, 'level2': 2, 'level3': 3, 'level4': 4, 'level5': 5
// 주석: "Elevation levels on web should use the level number, not the dp value."
```

**Motion** (`_md-sys-motion.scss`, 27개):

```scss
// Duration (16개)
'duration-short1': 50ms,  'duration-short2': 100ms,
'duration-short3': 150ms, 'duration-short4': 200ms,
'duration-medium1': 250ms, 'duration-medium2': 300ms,
'duration-medium3': 350ms, 'duration-medium4': 400ms,
'duration-long1': 450ms,  'duration-long2': 500ms,
'duration-long3': 550ms,  'duration-long4': 600ms,
'duration-extra-long1': 700ms, 'duration-extra-long2': 800ms,
'duration-extra-long3': 900ms, 'duration-extra-long4': 1000ms,

// Easing (10개)
'easing-emphasized': cubic-bezier(0.2, 0, 0, 1),
'easing-emphasized-accelerate': cubic-bezier(0.3, 0, 0.8, 0.15),
'easing-emphasized-decelerate': cubic-bezier(0.05, 0.7, 0.1, 1),
'easing-standard': cubic-bezier(0.2, 0, 0, 1),
'easing-standard-accelerate': cubic-bezier(0.3, 0, 1, 1),
'easing-standard-decelerate': cubic-bezier(0, 0, 0, 1),
'easing-legacy': cubic-bezier(0.4, 0, 0.2, 1),
'easing-legacy-accelerate': cubic-bezier(0.4, 0, 1, 1),
'easing-legacy-decelerate': cubic-bezier(0, 0, 0.2, 1),
'easing-linear': cubic-bezier(0, 0, 1, 1),
```

**State** (`_md-sys-state.scss`, 4개):

```scss
'hover-state-layer-opacity': 0.08,
'focus-state-layer-opacity': 0.12,
'pressed-state-layer-opacity': 0.12,
'dragged-state-layer-opacity': 0.16,
```

**Typescale** (`_md-sys-typescale.scss`, 61개 supported + 30개 unsupported):

5개 role(display, headline, title, body, label) × 3개 size(large, medium, small) × 4개 속성(font, line-height, size, weight) = 60 + weight-prominent 2개 = **62개**

실제 값 예시:

```scss
'body-large-font': Roboto,        // md-ref-typeface.plain
'body-large-line-height': 1.5rem, // 24px
'body-large-size': 1rem,          // 16px
'body-large-weight': 400,         // md-ref-typeface.weight-regular
'body-large-tracking': 0.03125rem,// 0.5px (unsupported token)

'label-large-size': 0.875rem,     // 14px
'label-large-weight': 500,        // weight-medium

'display-large-size': 3.5625rem,  // 57px
'display-large-line-height': 4rem, // 64px
```

#### Level 3: Component (`_md-comp-filled-button.scss`)

**역할**: sys 토큰을 컴포넌트 특정 속성에 매핑.

`tokens/versions/v0_192/_md-comp-filled-button.scss` (자동 생성):

```scss
@function values($deps: $_default, $exclude-hardcoded-values: false) {
  @return (
    // sys-color → comp 매핑
    'container-color': map.get($deps, 'md-sys-color', 'primary'),
    'label-text-color': map.get($deps, 'md-sys-color', 'on-primary'),
    'disabled-container-color': map.get($deps, 'md-sys-color', 'on-surface'),
    'hover-state-layer-color': map.get($deps, 'md-sys-color', 'on-primary'),
    'pressed-state-layer-color': map.get($deps, 'md-sys-color', 'on-primary'),
    'container-shadow-color': map.get($deps, 'md-sys-color', 'shadow'),

    // sys-shape → comp 매핑
    'container-shape': map.get($deps, 'md-sys-shape', 'corner-full'),  // 9999px (pill)

    // sys-elevation → comp 매핑
    'container-elevation': map.get($deps, 'md-sys-elevation', 'level0'),
    'hover-container-elevation': map.get($deps, 'md-sys-elevation', 'level1'),
    'pressed-container-elevation': map.get($deps, 'md-sys-elevation', 'level0'),

    // sys-typescale → comp 매핑
    'label-text-font': map.get($deps, 'md-sys-typescale', 'label-large-font'),
    'label-text-size': map.get($deps, 'md-sys-typescale', 'label-large-size'),
    'label-text-weight': map.get($deps, 'md-sys-typescale', 'label-large-weight'),
    'label-text-line-height': map.get($deps, 'md-sys-typescale', 'label-large-line-height'),

    // sys-state → comp 매핑
    'hover-state-layer-opacity': map.get($deps, 'md-sys-state', 'hover-state-layer-opacity'),
    'pressed-state-layer-opacity': map.get($deps, 'md-sys-state', 'pressed-state-layer-opacity'),

    // Hardcoded 값 (sys에 없는 컴포넌트 고유 값)
    'container-height': 40px,
    'disabled-container-opacity': 0.12,
    'disabled-label-text-opacity': 0.38,
    'with-icon-icon-size': 18px,
  );
}
```

**Filled Button comp 토큰 수**: 42개 supported + 4개 unsupported = **46개**

전체 comp 파일 47개 × 평균 ~30개 토큰 = **약 1,400개 comp 토큰** 추정.

### 1.4 전체 토큰 수 합산 (Material Web)

| 계층 | 카테고리 | 토큰 수 |
|------|----------|---------|
| ref | palette | 89 |
| ref | typeface | 5 |
| sys | color | 49 × 2 (light/dark) |
| sys | typescale | 62 (+30 unsupported) |
| sys | shape | 7 (+5 composite) |
| sys | elevation | 6 |
| sys | motion | 27 |
| sys | state | 4 |
| comp | 47개 컴포넌트 | ~1,400 (추정) |
| **합계** | | **~1,700+** |

### 1.5 MUI: 완전히 다른 토큰 시스템

MUI는 Material Design 스펙의 토큰 계층을 사용하지 않는다. **JavaScript 객체 기반 테마** 시스템:

#### `createPalette.js` — 색상 정의

```js
// packages/mui-material/src/styles/createPalette.js

// Light 모드 기본값
function getLight() {
  return {
    text: {
      primary: 'rgba(0, 0, 0, 0.87)',
      secondary: 'rgba(0, 0, 0, 0.6)',
      disabled: 'rgba(0, 0, 0, 0.38)',
    },
    divider: 'rgba(0, 0, 0, 0.12)',
    background: {
      paper: common.white,
      default: common.white,
    },
    action: {
      active: 'rgba(0, 0, 0, 0.54)',
      hover: 'rgba(0, 0, 0, 0.04)',
      hoverOpacity: 0.04,
      selected: 'rgba(0, 0, 0, 0.08)',
      disabled: 'rgba(0, 0, 0, 0.26)',
      disabledBackground: 'rgba(0, 0, 0, 0.12)',
      focus: 'rgba(0, 0, 0, 0.12)',
    },
  };
}

// Dark 모드 기본값
function getDark() {
  return {
    text: {
      primary: common.white,
      secondary: 'rgba(255, 255, 255, 0.7)',
      disabled: 'rgba(255, 255, 255, 0.5)',
    },
    divider: 'rgba(255, 255, 255, 0.12)',
    background: {
      paper: '#121212',
      default: '#121212',
    },
    action: {
      active: common.white,
      hover: 'rgba(255, 255, 255, 0.08)',
      selected: 'rgba(255, 255, 255, 0.16)',
      disabled: 'rgba(255, 255, 255, 0.3)',
      disabledBackground: 'rgba(255, 255, 255, 0.12)',
    },
  };
}
```

**Color intent 구조** — M3의 tonal palette 대신 `main/light/dark/contrastText` 4속성:

```js
// 기본 primary (light 모드)
{ main: blue[700], light: blue[400], dark: blue[800] }
// 기본 secondary (light 모드)
{ main: purple[500], light: purple[300], dark: purple[700] }
// 기본 error (light 모드)
{ main: red[700], light: red[400], dark: red[800] }

// augmentColor()가 자동 생성:
// - light/dark 미지정 시 tonalOffset(0.2) 기반 lighten/darken
// - contrastText 미지정 시 contrastThreshold(3) 기반 자동 선택
```

→ M3의 89개 ref palette + 49개 sys color = **138개** vs MUI의 6개 intent × 4속성 + text/divider/background/action ≈ **~40개**. **토큰 밀도 자체가 근본적으로 다름.**

#### `createTypography.js` — 타이포그래피 정의

```js
// packages/mui-material/src/styles/createTypography.js

const defaultFontFamily = '"Roboto", "Helvetica", "Arial", sans-serif';

// M3의 5 role × 3 size = 15 variant 대신, MUI는 13 variant:
const variants = {
  h1: buildVariant(fontWeightLight, 96, 1.167, -1.5),
  h2: buildVariant(fontWeightLight, 60, 1.2, -0.5),
  h3: buildVariant(fontWeightRegular, 48, 1.167, 0),
  h4: buildVariant(fontWeightRegular, 34, 1.235, 0.25),
  h5: buildVariant(fontWeightRegular, 24, 1.334, 0),
  h6: buildVariant(fontWeightMedium, 20, 1.6, 0.15),
  subtitle1: buildVariant(fontWeightRegular, 16, 1.75, 0.15),
  subtitle2: buildVariant(fontWeightMedium, 14, 1.57, 0.1),
  body1: buildVariant(fontWeightRegular, 16, 1.5, 0.15),
  body2: buildVariant(fontWeightRegular, 14, 1.43, 0.15),
  button: buildVariant(fontWeightMedium, 14, 1.75, 0.4, caseAllCaps),
  caption: buildVariant(fontWeightRegular, 12, 1.66, 0.4),
  overline: buildVariant(fontWeightRegular, 12, 2.66, 1, caseAllCaps),
};

// buildVariant 출력 구조:
// { fontFamily, fontWeight, fontSize: pxToRem(size), lineHeight, letterSpacing }
```

→ M3 typescale: `display/headline/title/body/label` × `large/medium/small` = **15 roles**
→ MUI typography: `h1~h6, subtitle1~2, body1~2, button, caption, overline` = **13 variants** (M2 기반)
→ **네이밍이 완전히 다르고, M3의 display/headline/title/label 역할이 MUI에 없음**

#### `createTheme.ts` — 테마 조합

```ts
// packages/mui-material/src/styles/createTheme.ts

export default function createTheme(options: ThemeOptions = {}, ...args: object[]): Theme {
  const {
    palette,
    cssVariables = false,
    colorSchemes: initialColorSchemes = !palette ? { light: true } : undefined,
    defaultColorScheme: initialDefaultColorScheme = palette?.mode,
    ...other
  } = options;

  if (cssVariables === false) {
    // v5 호환 모드: CSS 변수 없이 JS 객체만
    return createThemeNoVars(options, ...args);
  }

  // CSS 변수 모드: --mui-* custom properties 생성
  return createThemeWithVars({
    ...other,
    colorSchemes: colorSchemesInput,
    defaultColorScheme: defaultColorSchemeInput,
  }, ...args);
}
```

### 1.6 Material Web vs MUI 토큰 시스템 비교

| 차원 | Material Web | MUI |
|------|-------------|-----|
| **정의 언어** | SCSS (`.scss` 함수) | JavaScript/TypeScript (객체) |
| **계층 구조** | ref → sys → comp (3층) | palette/typography/shape/spacing (병렬) |
| **색상 모델** | Tonal palette (13 tone stops) | main/light/dark/contrastText |
| **색상 토큰 수** | ~138개 (ref 89 + sys 49) | ~40개 |
| **타이포그래피** | 15 roles × 4속성 = 62개 | 13 variants × 5속성 = 65개 |
| **코드 생성** | 자동 생성 (codegen) | 수동 작성 |
| **CSS 출력** | `--md-sys-color-primary` | `--mui-palette-primary-main` |
| **Dark mode** | `values-light()` / `values-dark()` 이중 함수 | `palette.mode: 'dark'` 또는 `colorSchemes` |
| **버전 관리** | `versions/v0_192/` 디렉토리 | 패키지 시맨틱 버저닝 |

---

## 2. Token Consumption (소비)

### 2.1 Material Web: SCSS mixin 기반 소비

컴포넌트는 **두 개의 mixin**으로 토큰을 소비:

`button/internal/_filled-button.scss`:

```scss
@use '../../tokens';

// 1. theme mixin: 사용자가 CSS custom property를 오버라이드하는 인터페이스
@mixin theme($tokens) {
  $supported-tokens: tokens.$md-comp-filled-button-supported-tokens;
  @each $token, $value in $tokens {
    @if list.index($supported-tokens, $token) == null {
      @error 'Token `#{$token}` is not a supported token.';
    }
    @if $value {
      --md-filled-button-#{$token}: #{$value};  // ← public custom property
    }
  }
}

// 2. styles mixin: 컴포넌트 내부 스타일에 토큰 값을 주입
@mixin styles() {
  $tokens: tokens.md-comp-filled-button-values();

  :host {
    $tokens: map.remove($tokens, 'container-shape');
    @each $token, $value in $tokens {
      --_#{$token}: #{$value};  // ← private custom property (내부용)
    }
  }
}
```

**소비 흐름**:

```
[ref palette: #6750a4]
    ↓ map.get($deps, 'md-ref-palette', 'primary40')
[sys color: primary = var(--md-sys-color-primary, #6750a4)]
    ↓ map.get($deps, 'md-sys-color', 'primary')
[comp filled-button: container-color = var(--md-filled-button-container-color, ...)]
    ↓ @each $token, $value in $tokens
[컴포넌트 :host: --_container-color: var(--md-filled-button-container-color, ...)]
    ↓ 컴포넌트 내부 CSS
[실제 렌더링: background-color: var(--_container-color)]
```

**3단계 CSS custom property 체인**:

```css
/* 사용자가 설정 가능 */
--md-sys-color-primary: #6750a4;
--md-filled-button-container-color: var(--md-sys-color-primary);

/* 컴포넌트 내부 (private) */
--_container-color: var(--md-filled-button-container-color, var(--md-sys-color-primary, #6750a4));
```

### 2.2 MUI: styled() + theme 객체 기반 소비

`packages/mui-material/src/Button/Button.js`:

```js
const ButtonRoot = styled(ButtonBase, {
  name: 'MuiButton',
  slot: 'Root',
})(
  memoTheme(({ theme }) => {
    return {
      // typography 토큰 소비
      ...theme.typography.button,  // { fontFamily, fontWeight: 500, fontSize: '0.875rem', ... }

      // shape 토큰 소비
      borderRadius: (theme.vars || theme).shape.borderRadius,

      // palette 토큰 소비 (disabled 상태)
      [`&.${buttonClasses.disabled}`]: {
        color: (theme.vars || theme).palette.action.disabled,
      },

      // variant별 색상 소비
      variants: [
        {
          props: { variant: 'contained' },
          style: {
            color: `var(--variant-containedColor)`,
            backgroundColor: `var(--variant-containedBg)`,
            boxShadow: (theme.vars || theme).shadows[2],
          },
        },
        // ...
        // palette 색상 동적 매핑
        ...Object.entries(theme.palette)
          .filter(createSimplePaletteValueFilter())
          .map(([color]) => ({
            props: { color },
            style: {
              '--variant-textColor': (theme.vars || theme).palette[color].main,
              '--variant-containedColor': (theme.vars || theme).palette[color].contrastText,
              '--variant-containedBg': (theme.vars || theme).palette[color].main,
              '@media (hover: hover)': {
                '&:hover': {
                  '--variant-containedBg': (theme.vars || theme).palette[color].dark,
                },
              },
            },
          })),
      ],
    };
  }),
);
```

**`(theme.vars || theme)` 패턴**: CSS 변수 모드(`cssVariables: true`)에서는 `theme.vars.palette.primary.main` → `var(--mui-palette-primary-main)`, 비활성 시 `theme.palette.primary.main` → `#1976d2` 직접 값.

### 2.3 CSS Custom Properties 출력 비교

**Material Web** (SCSS 컴파일 결과):

```css
:root {
  --md-sys-color-primary: #6750a4;
  --md-sys-color-on-primary: #fff;
  --md-sys-color-primary-container: #eaddff;
  --md-sys-color-surface: #fef7ff;
  --md-sys-color-on-surface: #1d1b20;
  --md-sys-typescale-body-large-size: 1rem;
  --md-sys-typescale-body-large-line-height: 1.5rem;
  --md-sys-shape-corner-full: 9999px;
  --md-sys-shape-corner-large: 16px;
  --md-ref-typeface-brand: Roboto;
  --md-ref-typeface-plain: Roboto;
}

md-filled-button {
  --md-filled-button-container-color: var(--md-sys-color-primary);
  --md-filled-button-container-shape: var(--md-sys-shape-corner-full);
  --md-filled-button-label-text-color: var(--md-sys-color-on-primary);
}
```

**MUI** (`cssVariables: true` 시):

```css
:root {
  --mui-palette-primary-main: #1976d2;
  --mui-palette-primary-light: #42a5f5;
  --mui-palette-primary-dark: #1565c0;
  --mui-palette-primary-contrastText: #fff;
  --mui-palette-secondary-main: #9c27b0;
  --mui-palette-error-main: #d32f2f;
  --mui-palette-text-primary: rgba(0, 0, 0, 0.87);
  --mui-palette-background-default: #fff;
  --mui-shadows-2: 0px 3px 1px -2px rgba(0,0,0,0.2), ...;
  --mui-shape-borderRadius: 4px;
}
```

### 2.4 Dark Mode: 토큰 수준 메커니즘

#### Material Web

SCSS 함수 수준에서 light/dark이 **완전히 분리**:

```scss
// tokens/_md-sys-color.scss

@function values-dark($deps: $_default-dark, $exclude-custom-properties: false) {
  $tokens: md-sys-color.values-dark($deps);  // ← dark 전용 매핑
  @if not $exclude-custom-properties {
    @each $token, $value in $tokens {
      @if $value != null {
        $tokens: map.set($tokens, $token,
          var(--md-sys-color-#{$token}, #{$value}));
      }
    }
  }
  @return validate.values($tokens, $supported-tokens: $supported-tokens);
}

@function values-light($deps: $_default-light, $exclude-custom-properties: false) {
  $tokens: md-sys-color.values-light($deps);  // ← light 전용 매핑
  // ...동일 로직
}
```

→ 컴포넌트는 `values-light()` 또는 `values-dark()`을 선택 호출. 런타임 전환은 CSS custom property 오버라이드로 처리:

```css
/* Dark mode: 사용자가 :root 변수를 오버라이드 */
:root[data-theme="dark"] {
  --md-sys-color-primary: #d0bcff;      /* primary80 */
  --md-sys-color-on-primary: #381e72;   /* primary20 */
  --md-sys-color-surface: #141218;      /* neutral6 */
  --md-sys-color-on-surface: #e6e0e9;   /* neutral90 */
}
```

#### MUI

**방법 1**: `palette.mode` (전통적)

```js
const theme = createTheme({ palette: { mode: 'dark' } });
// → getDark() 호출: background.default = '#121212', text.primary = '#fff'
```

**방법 2**: `colorSchemes` + CSS 변수 (v5+)

```js
const theme = createTheme({
  cssVariables: true,
  colorSchemes: { light: true, dark: true },
});
```

```css
/* 생성 결과 */
:root {
  --mui-palette-primary-main: #1976d2;
  --mui-palette-background-default: #fff;
}
[data-mui-color-scheme="dark"] {
  --mui-palette-primary-main: #90caf9;
  --mui-palette-background-default: #121212;
}
```

→ MUI는 `color-scheme` CSS 속성 또는 `data-mui-color-scheme` attribute로 전환. **JS 재실행 없이 CSS 변수 스왑**.

### 2.5 Dynamic Color (Android): 알고리즘적 팔레트 생성

Material Design 3의 핵심 차별점. `material-foundation/material-color-utilities` 라이브러리(npm: `@material/material-color-utilities`)가 구현.

**HCT 색상 공간**: Hue(색상), Chroma(채도), Tone(명도) 기반. 기존 HSL/HSV와 달리 **인간 지각 균일성(perceptual uniformity)** 을 보장.

**알고리즘 흐름**:

```
1. Source Color 추출 (예: 사용자 벽지 색상 #6750a4)
       ↓
2. HCT 변환: H=271.6, C=36.8, T=40.0
       ↓
3. Tonal Palette 생성: 각 key color(primary, secondary, tertiary, neutral, neutral-variant, error)마다
   13개 tone stop 생성: 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100
       ↓
4. Scheme 매핑: Light scheme → tone 40/100/90/10, Dark scheme → tone 80/20/30/90
       ↓
5. Color Roles 할당: primary, on-primary, primary-container, on-primary-container 등 49개 역할
```

**실제 ref-palette 값으로 확인하는 tonal palette**:

```
primary0:  #000000  (tone 0)
primary10: #21005d  (tone 10)  ← dark on-primary-container
primary20: #381e72  (tone 20)  ← dark on-primary
primary30: #4f378b  (tone 30)  ← dark primary-container
primary40: #6750a4  (tone 40)  ← light primary (기본 소스 색상)
primary50: #7f67be  (tone 50)
primary60: #9a82db  (tone 60)
primary70: #b69df8  (tone 70)
primary80: #d0bcff  (tone 80)  ← dark primary
primary90: #eaddff  (tone 90)  ← light primary-container
primary95: #f6edff  (tone 95)
primary99: #fffbfe  (tone 99)
primary100:#ffffff  (tone 100) ← light on-primary
```

→ `#6750a4`(source)의 HCT hue/chroma를 유지하면서 tone만 변화시켜 13개 stop 생성. secondary/tertiary는 hue를 일정 각도 회전(약 60°)하여 생성.

**Web에서의 Dynamic Color**: Material Web의 ref-palette는 **정적 기본값**(source color = `#6750a4`, M3 default purple). Dynamic Color는 주로 Android 12+에서 벽지 기반 실시간 생성에 사용. Web에서는 `--md-ref-palette-primary40` 등을 오버라이드하여 동일한 효과 구현 가능.

---

## 3. Token Governance (거버넌스)

### 3.1 Spec → Code 전파 파이프라인

Material Web의 `versions/v0_192/` 파일 헤더가 파이프라인을 증명:

```scss
// !!! THIS FILE WAS AUTOMATICALLY GENERATED !!!
// Design system display name: Google Material 3
// Design system version: v0.192
// User-configured context group "Audience": "3P"
// User-configured context group "Platform": "Web"
// User-configured context group "Scheme": "Dynamic"
```

**추정 파이프라인**:

```
[Material Design Spec (Google 내부)]
    ↓ (코드 생성 도구, 비공개)
[tokens/versions/v0_192/*.scss] — 자동 생성, 수동 수정 금지
    ↓ (래퍼 파일, 수동 관리)
[tokens/_md-sys-color.scss 등] — supported/unsupported 토큰 목록, validation
    ↓ (SCSS 컴파일)
[컴포넌트 SCSS] — mixin으로 소비
    ↓ (npm 빌드)
[@material/web 패키지]
```

**Context group** 시스템: `"Audience": "3P"` (third-party), `"Platform": "Web"`, `"Scheme": "Dynamic"` → 동일 스펙에서 플랫폼/대상별 다른 토큰 세트 생성 가능.

### 3.2 Material Web Maintenance Mode: 토큰 관점 영향

`README.md`:

> **Note:** MWC is in maintenance mode pending new maintainers.

`discussions/5642` 핵심 내용:

| 항목 | 상태 |
|------|------|
| 신규 토큰/컴포넌트 | ❌ 계획 없음 |
| Material 3 Expressive 토큰 | ❌ MWC에 미적용 |
| 기존 토큰 수정 | ⚠️ critical bug fix만 |
| PR 수용 | ❌ 원칙적으로 불가, 소규모만 case-by-case |
| 토큰 codegen 파이프라인 | ⚠️ Google 내부(Wiz)에서 계속 사용, MWC 갱신은 어려움 |
| 대안 | Angular Material(별도 프로젝트), 커뮤니티 포크(mdui, M3E 등) |

**토큰 관점 핵심 리스크**:
- `v0_192`에서 토큰 버전 **동결**. M3 Expressive의 신규 토큰(예: 새로운 surface 역할, 확장된 motion)이 반영되지 않음
- Google 내부 Wiz 프레임워크는 동일 토큰을 계속 사용하나, MWC로의 역전파(backport)는 인력 문제
- Figma Material 3 Kit이 업데이트되어도 MWC 코드에 자동 반영되지 않음

### 3.3 MUI 토큰 비호환성(Breaking Changes) 관리

MUI는 시맨틱 버저닝 + codemod 기반:

```js
// v4 → v5: palette.type → palette.mode (renamed)
// codemod: npx @mui/codemod v5.0.0/preset-safe

// v5 → v6: 일부 theme 키 구조 변경
// v6 → v7: cssVariables 기본값 변경 가능성

// 토큰 비호환 시:
// 1. @mui/codemod 자동 변환 스크립트 제공
// 2. console.warn으로 런타임 비호환 경고
// 3. TypeScript 타입에서 deprecated 마킹
```

**MUI의 토큰 비호환 예시** (실제 코드에서 확인):

```js
// createTypography.js 내부 주석:
// TODO v6: Remove handling of 'inherit' variant from the theme
// as it is already handled in Material UI's Typography component.
```

→ `inherit` variant가 v6에서 제거 예정. 코드에 TODO로 명시.

### 3.4 Figma ↔ Code 토큰 동기화

**Material Web**:
- `versions/v0_192/` 파일의 `"Design system version": "v0.192"` → Figma Material 3 Kit의 특정 버전과 대응
- 그러나 **자동 동기화 메커니즘은 비공개**. Google 내부 도구로 추정
- 공개 repo에서는 Figma 파일 → SCSS 변환 도구가 보이지 않음
- Maintenance mode로 인해 Figma Kit 최신 버전과 코드 간 **괴리 발생 중**

**MUI**:
- 공식 Figma 키트가 존재하나 (`mui.com/store/items/figma-react/`), **유료**
- Figma ↔ Code 자동 동기화 없음
- MUI 테마 객체는 JS이므로 Figma Variables와 구조적 매핑이 어려움
- 커뮤니티 도구(예: Figma Tokens plugin)로 수동 동기화 가능

### 3.5 Token Validation 메커니즘

Material Web의 `internal/validate` 모듈:

```scss
// tokens/_md-sys-color.scss에서 사용
@use 'internal/validate';

@return validate.values(
  $tokens,
  $supported-tokens: $supported-tokens,
  $unsupported-tokens: $unsupported-tokens,  // tracking 등 웹 미지원 토큰
  $new-tokens: $new-tokens,                  // 수동 추가 토큰
  $renamed-tokens: (                         // 이름 변경 매핑
    'with-icon-disabled-icon-color': 'disabled-icon-color',
    'with-icon-icon-size': 'icon-size',
  )
);
```

→ **빌드 타임 validation**: 지원되지 않는 토큰 사용 시 SCSS 컴파일 에러. `$renamed-tokens`로 비호환 이름 변경 관리.

---

## 4. 핵심 발견 요약

### 4.1 토큰 아키텍처 성숙도

| 평가 항목 | Material Web | MUI |
|-----------|-------------|-----|
| 계층적 토큰 구조 | ✅ ref→sys→comp 3층, 명확 | ❌ 병렬 구조, 계층 없음 |
| 토큰 코드 생성 | ✅ 자동 생성 (codegen) | ❌ 수동 작성 |
| 토큰 수 | ~1,700+ | ~200 (추정) |
| CSS custom properties | ✅ `--md-*` 네이티브 | ⚠️ opt-in (`cssVariables: true`) |
| Dark mode 토큰 | ✅ 함수 수준 분리 | ✅ mode/colorSchemes |
| Dynamic Color | ✅ tonal palette 기반 | ❌ lighten/darken 단순 변환 |
| 빌드 타임 validation | ✅ supported/unsupported 체크 | ⚠️ TypeScript 타입 체크 |
| 토큰 버전 관리 | ✅ `versions/v0_192/` | ❌ 패키지 버전에 포함 |

### 4.2 Figma↔Code 매핑 관점

**Material Web**:
- **강점**: 3층 계층이 Figma Variables의 mode/collection 구조와 1:1 대응 가능. codegen 파이프라인이 존재하므로 Figma → Code 자동화 이론적 가능
- **약점**: Maintenance mode로 파이프라인 동결. Figma Kit 최신 버전과 코드 간 괴리
- **매핑 충실도**: 높음 — 토큰 이름이 Figma Variables 이름과 동일한 네이밍 컨벤션 사용

**MUI**:
- **강점**: 활성 개발, React 생태계 통합, CSS 변수 모드 점진적 도입
- **약점**: Material Design 2 기반 토큰 구조. M3의 tonal palette/color roles와 구조적 불일치. Figma Variables와 JS 객체 간 자동 매핑 어려움
- **매핑 충실도**: 낮음 — M3 Figma Kit의 `primary/40` → MUI의 `palette.primary.main`은 이름도 구조도 다름

### 4.3 "동일한 Material Design"이지만 다른 토큰 시스템

```
Material Design 3 Spec
    ├── Material Web: md-sys-color-primary = ref-palette.primary40 = #6750a4
    │   └── 3층 계층, 89개 ref palette, SCSS codegen
    │
    ├── MUI: theme.palette.primary.main = blue[700] = #1976d2
    │   └── 병렬 구조, main/light/dark, JS 객체
    │
    └── Android Compose: MaterialTheme.colorScheme.primary = Color(0xFF6750A4)
        └── Kotlin, Dynamic Color 런타임 생성
```

→ **동일 스펙, 완전히 다른 토큰 구현**. "Material Design 토큰"은 단일 실체가 아니라 스펙 수준의 추상화이며, 각 구현체가 독립적으로 인코딩.
