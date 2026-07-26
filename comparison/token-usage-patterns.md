# 디자인 토큰 사용 패턴 레퍼런스

> 7개 디자인 시스템의 실제 코드에서 추출한 토큰 정의·소비 패턴 총집계
> 분석 기준일: 2026-07-26

---

## 1. 토큰 계층별 정의 패턴

### 1.1 Color — Primitive (원시 팔레트)

각 시스템이 원시 색상 팔레트를 어떻게 정의하는가:

#### Spectrum (JSON, sets 기반 테마)

```json
// packages/tokens/src/color-palette.json
{
  "blue-100": {
    "private": true,
    "sets": {
      "light": { "value": "rgb(245, 249, 255)" },
      "dark":  { "value": "rgb(14, 23, 63)" },
      "wireframe": { "value": "rgb(246, 248, 252)" }
    }
  },
  "blue-900": {
    "private": true,
    "sets": {
      "light": { "value": "rgb(39, 77, 234)" },
      "dark":  { "value": "rgb(150, 185, 255)" }
    }
  }
}
```

**특징**: 하나의 token name이 `sets` 안에 light/dark/wireframe 값을 보유. `private: true`로 직접 사용 금지.

#### Material Web (SCSS, codegen 자동 생성)

```scss
// tokens/versions/v0_192/_md-ref-palette.scss (자동 생성)
@function values($exclude-hardcoded-values: false) {
  @return (
    'primary0': #000,
    'primary10': #21005d,
    'primary20': #381e72,
    'primary30': #4f378b,
    'primary40': #6750a4,    // ← Light theme "primary"
    'primary50': #7f67be,
    'primary60': #9a82db,
    'primary70': #b69df8,
    'primary80': #d0bcff,    // ← Dark theme "primary"
    'primary90': #eaddff,
    'primary95': #f6edff,
    'primary99': #fffbfe,
    'primary100': #fff,
    // secondary, tertiary, error, neutral, neutral-variant 동일 구조
    // 총 89개
  );
}
```

**특징**: Tonal palette — hue별로 13개 tone stop. Light=40, Dark=80 역전 규칙.

#### Fluent 2 (TypeScript, 자동 생성)

```ts
// packages/tokens/src/global/colors.ts (자동 생성)
export const grey: Record<Greys, string> = {
  '2': '#050505', '4': '#0a0a0a', /* ...50단계... */ '98': '#fafafa',
};

export const darkRed: ColorVariants = {
  shade50: '#130204', shade40: '#230308', shade30: '#420610',
  shade20: '#590815', shade10: '#690a19', primary: '#750b1c',
  tint10: '#861b2c', tint20: '#962f3f', tint30: '#ac4f5e',
  tint40: '#d69ca5', tint50: '#e9c7cd', tint60: '#f9f0f2',
};
// 44개 팔레트 × 12 variants = ~600개 원시 값
```

**특징**: shade50~primary~tint60 구조. 44개 팔레트.

#### Carbon (TypeScript → Sass 빌드)

```ts
// packages/colors/src/colors.ts
export const blue10 = '#edf5ff';
export const blue20 = '#d0e2ff';
export const blue60 = '#0f62fe';   // ← Carbon 브랜드 블루
export const blue70 = '#0043ce';
export const blue100 = '#001141';

export const blue60Hover = '#0050e6';  // hover 변형도 grade별로 존재
```

**특징**: 14 swatch × 10 grade + hover 변형 = ~282개.

#### Polaris (TypeScript)

```ts
// polaris-tokens/src/colors.ts
export const gray: Color = {
  1: 'rgba(255, 255, 255, 1)',   // 흰색
  2: 'rgba(253, 253, 253, 1)',
  // ...16 스텝...
  16: 'rgba(26, 26, 26, 1)',     // 거의 검정
};
// 13개 램프 × 16 스텝 + 2개 알파 램프 = 240개
```

**특징**: 1~16 숫자 스케일. rgba 포맷.

#### shadcn/ui — Primitive 계층 없음

```css
/* globals.css — semantic이 곧 raw 값 */
:root {
  --primary: oklch(0.205 0 0);           /* primitive 없이 직접 값 */
  --destructive: oklch(0.577 0.245 27.325);
}
```

**특징**: 32개 semantic 변수가 raw 값을 직접 보유. primitive 계층이 구조적으로 없음.

#### Ant Design (TypeScript, 알고리즘 파생)

```ts
// @ant-design/colors — HSB 알고리즘으로 10단계 팔레트 자동 생성
// hueStep=2, saturationStep=0.16, brightnessStep=0.16
generate('#1677ff')
// → ['#E6F4FF', '#BAE0FF', '#91CAFF', '#69B1FF', '#4096FF',
//    '#1677FF', '#0958D9', '#003EB3', '#002C8C', '#001D66']
```

**특징**: Seed 색상 하나 → HSB 알고리즘 → 10단계 자동 파생.

---

### 1.2 Color — Semantic (의미 기반 매핑)

Primitive를 시맨틱 역할에 매핑하는 패턴:

#### Spectrum (JSON alias, `{curly-brace}` 참조)

```json
// packages/tokens/src/color-aliases.json
{
  "accent-background-color-default": {
    "sets": {
      "light": { "value": "{accent-color-900}" },
      "dark":  { "value": "{accent-color-800}" }
    }
  },
  "accent-background-color-hover": {
    "sets": {
      "light": { "value": "{accent-color-1000}" },
      "dark":  { "value": "{accent-color-700}" }
    }
  }
}
```

#### Material Web (SCSS, map.get 참조)

```scss
// tokens/versions/v0_192/_md-sys-color.scss
@function values-light($deps) {
  @return (
    'primary': map.get($deps, 'md-ref-palette', 'primary40'),     // #6750a4
    'on-primary': map.get($deps, 'md-ref-palette', 'primary100'), // #fff
    'primary-container': map.get($deps, 'md-ref-palette', 'primary90'),
    'surface': map.get($deps, 'md-ref-palette', 'neutral98'),
    'on-surface': map.get($deps, 'md-ref-palette', 'neutral10'),
    // 총 49개
  );
}
@function values-dark($deps) {
  @return (
    'primary': map.get($deps, 'md-ref-palette', 'primary80'),     // #d0bcff (역전)
    'on-primary': map.get($deps, 'md-ref-palette', 'primary20'),
    // ...
  );
}
```

**Light ↔ Dark tone 역전 규칙**: primary 40↔80, on-primary 100↔20, surface 98↔6

#### Fluent 2 (TypeScript, 직접 참조)

```ts
// packages/tokens/src/alias/lightColor.ts
export const generateColorTokens = (brand: BrandVariants): ColorTokens => ({
  colorNeutralForeground1: grey[14],           // #242424
  colorNeutralBackground1: white,              // #ffffff
  colorNeutralBackground1Hover: grey[96],      // #f5f5f5
  colorBrandBackground: brand[80],             // #0f6cbd
  colorBrandBackgroundHover: brand[70],        // #115ea3
  // 총 184개 alias
});
```

#### Carbon (Sass map, 테마별 값)

```scss
// @carbon/themes — White 테마 기준
$background: #ffffff;
$layer-01: #f4f4f4;         // background 위 컨테이너
$layer-02: #ffffff;         // layer-01 위 컨테이너
$text-primary: #161616;
$text-secondary: #525252;
$link-primary: #0f62fe;     // = $blue-60
$interactive: #0f62fe;
$support-error: #da1e28;    // = $red-60
$focus: #0f62fe;
// 총 ~243개
```

**Layer Level System**: `$layer-01` → `$layer-02` → `$layer-03` — UI 중첩 깊이별 색상 계층.

#### Polaris (TypeScript, description 포함)

```ts
// polaris-tokens/src/themes/base/color.ts
'color-bg-surface': {
  value: colors.gray[1],    // rgba(255, 255, 255, 1)
  description: 'The background color for elements with the highest level of prominence, like a card.',
},
'color-bg-fill-brand': {
  value: colors.azure[13],
  description: 'The background color of contained elements with a smaller surface area, like a button.',
},
'color-text-brand-on-bg-fill': {
  value: colors.white,
  description: '텍스트-배경 페어링: 대비율 구조적 보장',
},
// 총 ~250개
```

**bg-surface vs bg-fill**: 넓은 표면(Card) vs 작은 표면(Button) 이분 구조.
**on-bg-fill 페어링**: 배경 위 전경색을 토큰 수준에서 쌍으로 정의.

#### shadcn/ui (CSS, foreground/background 쌍)

```css
:root {
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);    /* 쌍 구조 */
  --secondary: oklch(0.97 0 0);
  --secondary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.97 0 0);                  /* secondary와 동일 값 */
  --muted-foreground: oklch(0.556 0 0);
  --accent: oklch(0.97 0 0);                 /* secondary와 동일 값 */
  --accent-foreground: oklch(0.205 0 0);
}
```

**특징**: `--X` / `--X-foreground` 쌍. secondary/muted/accent가 light에서 동일 값.

#### Ant Design (TypeScript, 알고리즘 파생)

```ts
// genColorMapToken — Seed → Map 자동 파생
return {
  colorPrimaryBg: primaryColors[1],        // 가장 밝은 배경
  colorPrimaryBgHover: primaryColors[2],
  colorPrimaryBorder: primaryColors[3],
  colorPrimaryHover: primaryColors[5],     // hover
  colorPrimary: primaryColors[6],          // 기본 (= Seed)
  colorPrimaryActive: primaryColors[7],    // active
  colorPrimaryTextHover: primaryColors[5],
  colorPrimaryText: primaryColors[6],
  colorPrimaryTextActive: primaryColors[7],
  // success, warning, error, info도 동일 패턴
};
```

**특징**: Seed `colorPrimary: '#1677ff'` 하나 → 10단계 팔레트 → 시맨틱 매핑 전부 자동.

---

### 1.3 Typography

| 시스템 | 정의 방식 | 스케일 | 예시 |
|--------|----------|--------|------|
| Spectrum | JSON (`typography.json`, 96KB) | font-size-50~1300 | `"font-size-100": { "value": "17px" }` |
| Material Web | SCSS (`_md-sys-typescale.scss`) | 5 roles × 3 sizes = 15 | `body-large-size: 1rem`, `body-large-line-height: 1.5rem` |
| MUI | JS (`createTypography.js`) | h1~h6, subtitle, body, button, caption, overline = 13 | `body1: { fontSize: '1rem', lineHeight: 1.5 }` |
| Fluent 2 | TS (`fonts.ts`) | fontSizeBase100~Hero1000 = 10 | `fontSizeBase300: '14px'` (기본 본문) |
| Carbon | TS → Sass (`@carbon/type`) | IBM Plex 기반, productive/expressive | `@include type.type-style('body-01')` |
| Polaris | TS (`font.ts`, `text.ts`) | font-size-75~500, text-heading-xl~body-sm | `--p-font-size-300: 1rem` |
| shadcn/ui | Tailwind 기본 + `text-sm` 등 | Tailwind 스케일 재사용 | `text-sm font-medium` (클래스) |
| Ant Design | TS (`genFontMapToken`) | fontSizeSM~fontSizeHeading5 | `fontSize: 14`, `fontSizeSM: 12`, `fontSizeLG: 16` |

---

### 1.4 Spacing

| 시스템 | 스케일 | 기본 단위 | 예시 |
|--------|--------|----------|------|
| Spectrum | `size-10`~`size-6000` | 4px | `"size-100": { "value": "8px" }` |
| Material Web | 별도 spacing 토큰 없음 | — | 컴포넌트 토큰에 인코딩 |
| MUI | `spacing(n) = 8*n px` | 8px | `spacing: 8` → `theme.spacing(2) = '16px'` |
| Fluent 2 | `spacingHorizontalXS~XXXL` + `Nudge` | 4px | `spacingHorizontalM: '16px'`, `spacingHorizontalSNudge: '6px'` |
| Carbon | `$spacing-01`~`$spacing-13` | 8px | `$spacing-05: 1rem (16px)` |
| Polaris | `--p-space-0`~`--p-space-3200` | 4px | `--p-space-400: 16px` (27개 값) |
| shadcn/ui | Tailwind 스케일 | 4px | `px-4`, `gap-2` (유틸리티) |
| Ant Design | `paddingXXS~paddingXL`, `marginXXS~marginXXL` | 4px | `padding: 16`, `marginLG: 24` |

---

### 1.5 Border Radius / Shape

| 시스템 | 스케일 | 예시 |
|--------|--------|------|
| Spectrum | `corner-radius-*` | JSON token |
| Material Web | 7 levels | `corner-none: 0`, `corner-extra-small: 4px`, `corner-small: 8px`, `corner-medium: 12px`, `corner-large: 16px`, `corner-extra-large: 28px`, `corner-full: 9999px` |
| MUI | 단일 값 | `shape.borderRadius: 4` |
| Fluent 2 | 11 levels | `borderRadiusNone: 0`, `borderRadiusSmall: 2px`, `borderRadiusMedium: 4px`, `borderRadiusLarge: 6px`, `borderRadiusXLarge: 8px`, `borderRadiusCircular: 10000px` |
| Carbon | Sass 변수 | `$border-radius: 4px` |
| Polaris | `--p-border-radius-*` | `--p-border-radius-100: 2px`, `--p-border-radius-200: 4px`, `--p-border-radius-300: 8px` |
| shadcn/ui | `--radius` + 파생 | `--radius: 0.625rem` → `--radius-sm: calc(var(--radius) * 0.6)` ~ `--radius-4xl: calc(var(--radius) * 2.6)` |
| Ant Design | Seed → 파생 | `borderRadius: 6` → `borderRadiusSM: 4`, `borderRadiusLG: 8` |

---

### 1.6 Shadow / Elevation

| 시스템 | 체계 | 예시 |
|--------|------|------|
| Spectrum | `drop-shadow-*` JSON token | component별 shadow |
| Material Web | 6 levels | `elevation-level0: 0` ~ `elevation-level5: 5` + tonal tint |
| MUI | 25 levels | `shadows: Array(25)` — `shadows[2]` = contained button |
| Fluent 2 | 6 + 6 brand | `shadow2`, `shadow4`, `shadow8`, `shadow16`, `shadow28`, `shadow64` |
| Carbon | `$shadow` 단일 | 복합 box-shadow 값 |
| Polaris | `--p-shadow-*` | `--p-shadow-300`, `--p-shadow-button-primary`, `--p-shadow-button-primary-inset` |
| shadcn/ui | Tailwind `shadow-xs` | 토큰 없음, 유틸리티 |
| Ant Design | `boxShadow`, `boxShadowSecondary`, `boxShadowTertiary` | AliasToken에 3단계 |

---

### 1.7 Motion / Animation

| 시스템 | 체계 | 예시 |
|--------|------|------|
| Spectrum | JSON token | duration, easing |
| Material Web | 27개 토큰 | `duration-short1: 50ms` ~ `duration-long4: 700ms`, easing curves |
| Fluent 2 | 8 duration + 9 curve | `durationUltraFast: 50ms` ~ `durationUltraSlow: 500ms`, `curveEasyEase`, `curveDecelerate` |
| Carbon | `@carbon/motion` | productive/expressive 커브, `$duration-fast-01: 70ms` |
| Polaris | `--p-motion-*` | `--p-motion-duration-100: 50ms` ~ `--p-motion-duration-500: 500ms`, `--p-motion-ease-in` |
| shadcn/ui | `transition-all` 클래스 | 토큰 없음 |
| Ant Design | Seed에 8개 easing | `motionEaseInOut: 'cubic-bezier(0.645, 0.045, 0.355, 1)'` |

---

## 2. 컴포넌트별 토큰 소비 사례

### 2.1 Button — 전체 시스템 비교

**Button은 모든 시스템에서 토큰 소비 패턴이 가장 잘 드러나는 컴포넌트이다.**

#### Spectrum — 3단계 CSS fallback + component-local variable

```css
/* 1. 사이즈: global token → component-local variable */
.spectrum-Button {
  --spectrum-button-sized-height: var(--spectrum-component-height-100);
  --spectrum-button-sized-font-size: var(--spectrum-font-size-100);
}
.spectrum-Button--sizeS {
  --spectrum-button-sized-height: var(--spectrum-component-height-75);
  --spectrum-button-sized-font-size: var(--spectrum-font-size-75);
}

/* 2. Variant: semantic token → component-local variable */
.spectrum-Button--accent {
  --spectrum-button-background-color-default: var(--spectrum-accent-background-color-default);
  --spectrum-button-background-color-hover: var(--spectrum-accent-background-color-hover);
  --spectrum-button-background-color-down: var(--spectrum-accent-background-color-down);
  --spectrum-button-content-color-default: var(--spectrum-white);
}
.spectrum-Button--negative {
  --spectrum-button-background-color-default: var(--spectrum-negative-background-color-default);
  --spectrum-button-background-color-hover: var(--spectrum-negative-background-color-hover);
}

/* 3. 최종 적용: 3단계 fallback (highcontrast > mod > spectrum) */
.spectrum-Button {
  background-color: var(
    --highcontrast-button-background-color-default,
    var(--mod-button-background-color-default,
      var(--spectrum-button-background-color-default)
    )
  );
}
```

**패턴**: global semantic → component-local 변수 매핑 → 3단계 fallback으로 override hook 제공.

#### Material Web — 3단계 CSS custom property 체인

```scss
// tokens/versions/v0_192/_md-comp-filled-button.scss (자동 생성)
@function values($deps) {
  @return (
    'container-color': map.get($deps, 'md-sys-color', 'primary'),
    'container-shape': map.get($deps, 'md-sys-shape', 'corner-full'),
    'label-text-color': map.get($deps, 'md-sys-color', 'on-primary'),
    'label-text-font': map.get($deps, 'md-sys-typescale', 'label-large-font'),
    'label-text-size': map.get($deps, 'md-sys-typescale', 'label-large-size'),
    // 총 42개 토큰
  );
}
```

```css
/* 컴포넌트 내부 — 3단계 var() 체인 */
md-filled-button {
  --_container-color: var(
    --md-filled-button-container-color,     /* 사용자 override */
    var(--md-sys-color-primary, #6750a4)    /* sys token → ref fallback */
  );
  background-color: var(--_container-color);
}
```

**패턴**: ref → sys → comp 3단계 참조. comp token이 sys를, sys가 ref를 var()로 체이닝.

#### MUI — JS theme 객체 + CSS vars 이중 모드

```js
// packages/mui-material/src/Button/Button.js
const ButtonRoot = styled(ButtonBase)(({ theme }) => ({
  ...theme.typography.button,                    // typography 토큰
  borderRadius: (theme.vars || theme).shape.borderRadius,  // shape 토큰

  variants: [{
    props: { variant: 'contained' },
    style: {
      color: 'var(--variant-containedColor)',
      backgroundColor: 'var(--variant-containedBg)',
      boxShadow: (theme.vars || theme).shadows[2],  // elevation 토큰
    },
  }],

  // palette 색상 동적 매핑
  ...Object.entries(theme.palette)
    .filter(createSimplePaletteValueFilter())
    .map(([color]) => ({
      props: { color },
      style: {
        '--variant-containedBg': (theme.vars || theme).palette[color].main,
        '--variant-containedColor': (theme.vars || theme).palette[color].contrastText,
        '&:hover': {
          '--variant-containedBg': (theme.vars || theme).palette[color].dark,
        },
      },
    })),
}));
```

**패턴**: `(theme.vars || theme)` — CSS vars 모드와 JS 객체 모드 이중 지원. palette[color].main/dark/contrastText.

#### Fluent 2 — Griffel atomic CSS-in-JS + tokens 객체

```ts
// useButtonStyles.styles.ts (16.9KB)
const useRootBaseClassName = makeResetStyles({
  backgroundColor: tokens.colorNeutralBackground1,     // alias token
  color: tokens.colorNeutralForeground1,
  fontFamily: tokens.fontFamilyBase,
  fontSize: tokens.fontSizeBase300,
  borderRadius: tokens.borderRadiusMedium,
  padding: `${tokens.spacingVerticalS} ${tokens.spacingHorizontalM}`,
});

const useRootStyles = makeStyles({
  primary: {
    backgroundColor: tokens.colorBrandBackground,
    color: tokens.colorNeutralForegroundOnBrand,
    ':hover': { backgroundColor: tokens.colorBrandBackgroundHover },
    ':active': { backgroundColor: tokens.colorBrandBackgroundPressed },
  },
  subtle: {
    backgroundColor: tokens.colorSubtleBackground,
    color: tokens.colorNeutralForeground2,
    ':hover': { backgroundColor: tokens.colorSubtleBackgroundHover },
  },
  // appearance × size 매트릭스
  small: { fontSize: tokens.fontSizeBase200, padding: `... ${tokens.spacingHorizontalS}` },
  large: { fontSize: tokens.fontSizeBase500, padding: `... ${tokens.spacingHorizontalXL}` },
});

// 조건부 합성
state.root.className = mergeClasses(
  rootBaseClassName,
  rootStyles[state.appearance],
  rootStyles[state.size],
  state.root.className,  // 사용자 override (항상 마지막)
);
```

**패턴**: `tokens.colorBrandBackground` = `var(--colorBrandBackground)`. Griffel이 atomic class로 분해. `mergeClasses()`로 variant 합성.

#### Carbon — Sass mixin + component token + CSS vars

```scss
// packages/styles/scss/components/button/_button.scss
@use 'tokens' as *;    // $button-primary 등 component token
@use '../../theme' as *;

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

// component token의 테마 분기
$button-primary: (
  fallback: #0f62fe,
  values: (
    (theme: themes.$white, value: #0f62fe),
    (theme: themes.$g10,   value: #0f62fe),
    (theme: themes.$g90,   value: #78a9ff),   // dark에서는 밝은 파랑
    (theme: themes.$g100,  value: #78a9ff),
  ),
);
```

**패턴**: component token이 테마별 값을 보유. `var(--cds-button-primary, fallback)` 출력.

#### Polaris — Custom Property State Machine

```css
/* Button.module.css */

/* 1. State Machine 초기화 — base + 4개 state 변수 */
.Button {
  --pc-button-bg: transparent;
  --pc-button-bg_hover: var(--pc-button-bg);
  --pc-button-bg_active: var(--pc-button-bg);
  --pc-button-bg_disabled: var(--p-color-bg-fill-disabled);

  --pc-button-color: inherit;
  --pc-button-color_hover: var(--pc-button-color);
  --pc-button-color_disabled: var(--p-color-text-disabled);

  /* 실제 스타일은 변수 소비만 */
  background: var(--pc-button-bg);
  color: var(--pc-button-color);
  border-radius: var(--p-border-radius-200);
}

/* 2. Variant — 변수 재할당만, CSS 프로퍼티 없음 */
.variantPrimary {
  --pc-button-bg: var(--p-color-bg-fill-brand);
  --pc-button-bg_hover: var(--p-color-bg-fill-brand-hover);
  --pc-button-bg_active: var(--p-color-bg-fill-brand-active);
  --pc-button-color: var(--p-color-text-brand-on-bg-fill);
  --pc-button-box-shadow: var(--p-shadow-button-primary);
}
.variantSecondary {
  --pc-button-bg: var(--p-color-bg-fill);
  --pc-button-bg_hover: var(--p-color-bg-fill-hover);
  --pc-button-color: var(--p-color-text);
}
.variantTertiary {
  --pc-button-bg_hover: var(--p-color-bg-fill-transparent-hover);
  --pc-button-color: var(--p-color-text);
}

/* 3. Tone — variant와 조합 */
.toneSuccess:is(.variantPrimary) {
  --pc-button-bg: var(--p-color-bg-fill-success);
  --pc-button-bg_hover: var(--p-color-bg-fill-success-hover);
}
.toneCritical:is(.variantSecondary, .variantTertiary) {
  --pc-button-color: var(--p-color-text-critical);
}

/* 4. Size — spacing/height 토큰 */
.sizeMicro {
  --pc-button-padding-block: var(--p-space-100);
  --pc-button-padding-inline: var(--p-space-200);
  min-height: var(--p-height-700);
}
.sizeLarge {
  --pc-button-padding-block: var(--p-space-150);
  --pc-button-padding-inline: var(--p-space-300);
  min-height: var(--p-height-900);
}

/* 5. Pseudo-class — 변수 읽기만 */
.Button:hover { background: var(--pc-button-bg_hover); }
.Button:active { background: var(--pc-button-bg_active); }
.Button:disabled { background: var(--pc-button-bg_disabled); }
```

**패턴**: Variant × Tone × State 조합 폭발을 O(n+m)으로 해결. CSS specificity 전쟁 없음.

#### shadcn/ui — CVA + Tailwind 유틸리티

```tsx
const buttonVariants = cva(
  // Base: 모든 variant 공통
  "inline-flex shrink-0 items-center justify-center gap-2 rounded-md text-sm font-medium whitespace-nowrap transition-all outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-white hover:bg-destructive/90",
        outline: "border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground dark:border-input dark:bg-input/30",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 gap-1.5 rounded-md px-3",
        lg: "h-10 rounded-md px-6",
        icon: "size-9",
      },
    },
  }
);
```

**패턴**: 토큰을 CSS var로 직접 참조하지 않고 Tailwind 유틸리티(`bg-primary`)로 소비. 상태 토큰 없이 opacity modifier(`hover:bg-primary/90`)로 대체.

#### Ant Design — CSS-in-JS genStyleHooks + ComponentToken

```ts
// components/button/style/index.ts
export default genStyleHooks('Button', (token) => {
  const buttonToken = prepareToken(token);
  return [
    genSharedButtonStyle(buttonToken),
    genVariantStyle(buttonToken),
    // ...
  ];
}, prepareComponentToken);

// components/button/style/token.ts
export const prepareComponentToken = (token) => ({
  fontWeight: 400,
  defaultColor: token.colorText,                    // AliasToken 참조
  defaultBg: token.colorBgContainer,
  defaultBorderColor: token.colorBorder,
  defaultHoverColor: token.colorPrimaryHover,       // MapToken 참조
  defaultHoverBorderColor: token.colorPrimaryHover,
  defaultActiveColor: token.colorPrimaryActive,
  primaryColor: token.colorTextLightSolid,          // #fff
  dangerColor: token.colorTextLightSolid,
  paddingInline: token.paddingContentHorizontal - token.lineWidth,
  contentFontSize: token.fontSize,
});

// 스타일 생성기 내부
const genVariantStyle = (token) => ({
  [`${componentCls}-primary`]: {
    backgroundColor: token.colorPrimary,
    color: token.primaryColor,
    boxShadow: token.primaryShadow,
    '&:hover': {
      backgroundColor: token.colorPrimaryHover,
    },
    '&:active': {
      backgroundColor: token.colorPrimaryActive,
    },
  },
});
```

**패턴**: `genStyleHooks`가 ComponentToken 등록 → 스타일 생성기가 token 참조 → CSS-in-JS 런타임 주입. v6에서 `--ant-*` CSS vars 출력.

---

### 2.2 Button 토큰 소비 패턴 요약

| 시스템 | 소비 메커니즘 | 상태 처리 | Override 방법 |
|--------|-------------|----------|-------------|
| Spectrum | CSS vars 3단계 fallback | component-local 변수 | `--mod-*`, `--highcontrast-*` |
| Material Web | CSS vars 3단계 체인 | comp token에 상태 포함 | `--md-filled-button-*` 직접 설정 |
| MUI | JS theme + CSS vars 이중 | palette[color].dark | `sx` prop, `styled()` |
| Fluent 2 | Griffel + `tokens.*` var() | `:hover`에 별도 alias token | `mergeClasses` 마지막 인자 |
| Carbon | Sass mixin + `var(--cds-*)` | component token 테마 분기 | Sass `!default` 오버라이드 |
| Polaris | `--pc-*` state machine | 변수 재할당 (CSS 프로퍼티 없음) | 불가 (의도적 제약) |
| shadcn/ui | Tailwind 유틸리티 클래스 | opacity modifier (`/90`) | `className` (tailwind-merge) |
| Ant Design | CSS-in-JS token 참조 | `:hover`에 MapToken 참조 | `theme.components.Button` |

---

### 2.3 Card / Surface

| 시스템 | 배경 토큰 | 보더 토큰 | 그림자 토큰 | 패턴 |
|--------|----------|----------|-----------|------|
| Spectrum | `--spectrum-gray-25` (component token) | `--spectrum-gray-200` | component별 | JSON component token |
| Material Web | `--md-sys-color-surface` | `--md-sys-color-outline-variant` | `--md-sys-elevation-level1` | sys token 직접 |
| MUI | `theme.palette.background.paper` | `theme.palette.divider` | `theme.shadows[1]` | JS theme |
| Fluent 2 | `tokens.colorNeutralBackground1` | `tokens.colorNeutralStroke2` | `tokens.shadow4` | alias token |
| Carbon | `var(--cds-layer-01)` | `var(--cds-border-subtle-01)` | — | Layer Level System |
| Polaris | `var(--p-color-bg-surface)` | `var(--p-color-border)` | `var(--p-shadow-300)` | global token |
| shadcn/ui | `bg-card` | `ring-foreground/10` | `shadow-xs` | 유틸리티 + 쌍 구조 |
| Ant Design | `token.colorBgContainer` | `token.colorBorderSecondary` | `token.boxShadowCard` | AliasToken |

---

### 2.4 Input / TextField

| 시스템 | 배경 | 보더 | 포커스 | 텍스트 |
|--------|------|------|--------|--------|
| Spectrum | `--spectrum-gray-25` | `--spectrum-gray-400` | `--spectrum-blue-800` | `--spectrum-gray-900` |
| Material Web | `--md-sys-color-surface-container-highest` | `--md-sys-color-outline` | `--md-sys-color-primary` | `--md-sys-color-on-surface` |
| MUI | `transparent` | `palette.action.active` | `palette.primary.main` | `palette.text.primary` |
| Fluent 2 | `colorNeutralBackground1` | `colorNeutralStrokeAccessible` | `colorStrokeFocus2` | `colorNeutralForeground1` |
| Carbon | `var(--cds-field-01)` | `var(--cds-border-strong-01)` | `var(--cds-focus)` | `var(--cds-text-primary)` |
| Polaris | `var(--p-color-bg-fill)` | `var(--p-color-border)` | `var(--p-color-border-focus)` | `var(--p-color-text)` |
| shadcn/ui | `bg-background` / `bg-transparent` | `border-input` | `ring-ring` | `text-foreground` |
| Ant Design | `colorBgContainer` | `colorBorder` | `colorPrimary` + `controlOutline` | `colorText` |

---

### 2.5 Notification / Alert

| 시스템 | Error 배경 | Success 배경 | Warning 배경 | Info 배경 |
|--------|----------|------------|------------|---------|
| Spectrum | `--spectrum-negative-background-color-default` | `--spectrum-positive-*` | `--spectrum-notice-*` | `--spectrum-informative-*` |
| Material Web | `--md-sys-color-error-container` | — (스펙 외) | — | — |
| MUI | `palette.error.light` + alpha | `palette.success.light` | `palette.warning.light` | `palette.info.light` |
| Fluent 2 | `colorPaletteRedBackground1` | `colorPaletteGreenBackground1` | `colorPaletteYellowBackground1` | `colorPaletteBlueBackground1` |
| Carbon | `var(--cds-notification-background-error)` | `-success` | `-warning` | `-info` |
| Polaris | `var(--p-color-bg-fill-critical)` | `-success` | `-caution` | `-info` |
| shadcn/ui | `bg-destructive` (CVA variant) | 별도 토큰 없음 | — | — |
| Ant Design | `colorErrorBg` | `colorSuccessBg` | `colorWarningBg` | `colorInfoBg` |

---

## 3. 토큰 소비 아키텍처 패턴 분류

### 패턴 A: CSS Custom Property 체인 (Spectrum, Material Web, Carbon)

```
[primitive] → var() 참조 → [semantic] → var() 참조 → [component-local] → 최종 CSS 속성
```

- 런타임 테마 전환 가능 (CSS cascade)
- Override hook 제공 (`--mod-*`, 직접 var 설정)
- 빌드 타임에 CSS 생성

### 패턴 B: JS Theme 객체 + CSS vars 이중 (MUI, Fluent 2, Ant Design)

```
[TS/JS theme 객체] → Provider가 CSS vars 주입 → 컴포넌트는 var() 또는 theme.* 참조
```

- 런타임 테마 전환 가능 (Provider re-render 또는 CSS vars swap)
- 타입 안전 (TS 자동완성)
- CSS-in-JS 런타임 오버헤드 (Ant: v6에서 CSS vars 기본화로 해결)

### 패턴 C: CSS Custom Property State Machine (Polaris)

```
[--p-* global] → [--pc-* component 변수 재할당] → pseudo-class가 변수 읽기
```

- Variant × State 조합 폭발을 O(n+m)으로 해결
- CSS specificity 전쟁 없음
- 가장 우아한 패턴이나 학습 곡선 존재

### 패턴 D: Tailwind 유틸리티 (shadcn/ui)

```
[CSS vars] → @theme inline → [Tailwind 유틸리티 생성] → className 문자열
```

- 토큰을 직접 참조하지 않고 유틸리티 클래스로 간접 소비
- 상태 토큰 없이 opacity modifier로 대체
- 타입 안전성 없음 (문자열)

### 패턴 E: Sass 모듈 + 테마 mixin (Carbon)

```
[TS source] → 빌드 → [Sass variables] → theme() mixin → [--cds-* CSS vars 출력]
```

- Sass `@use` 모듈 시스템
- `!default` 플래그로 오버라이드
- Layer Level System으로 맥락적 색상 전환
