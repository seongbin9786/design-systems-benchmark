# Shopify Polaris — Design Token 시스템 Deep-Dive

> **패키지**: `@shopify/polaris-tokens` v9.4.2  
> **리포지토리**: github.com/Shopify/polaris (archived)  
> **라이선스**: SEE LICENSE IN LICENSE.md  
> **분석 기준**: 코드 레벨 토큰 아키텍처

---

## 1. Token 정의 (Definition)

### 1.1 소스 구조

```
polaris-tokens/
├── src/
│   ├── colors.ts          # 컬러 프리미티브 (13개 램프 × 16 스텝 + 2개 알파 램프)
│   ├── size.ts            # 사이즈 스케일 (27개 값)
│   ├── index.ts           # 공개 API exports
│   ├── types.ts           # 유틸리티 타입 (Entry, Exact 등)
│   ├── utils.ts           # createVar, createVarName, toRem, toPx 등
│   └── themes/
│       ├── base/          # 11개 토큰 그룹 정의
│       │   ├── index.ts   # metaThemeBase = createMetaThemeBase({border, breakpoints, color, ...})
│       │   ├── border.ts
│       │   ├── breakpoints.ts
│       │   ├── color.ts   # ~39KB, 가장 큰 파일
│       │   ├── font.ts
│       │   ├── height.ts
│       │   ├── motion.ts
│       │   ├── shadow.ts
│       │   ├── space.ts
│       │   ├── text.ts
│       │   ├── width.ts
│       │   └── zIndex.ts
│       ├── constants.ts   # themeNames 정의
│       ├── types.ts       # MetaTokenProperties, MetaThemeShape 등
│       ├── utils.ts       # createMetaTheme, resolveMetaThemeRefs 등
│       ├── light.ts       # 기본 테마 (빈 partial → base 그대로)
│       ├── light-mobile.ts
│       ├── light-high-contrast.ts
│       └── dark.ts
├── scripts/
│   ├── index.ts           # 빌드 오케스트레이션
│   ├── toStyleSheet.ts    # CSS/SCSS 출력
│   ├── toValues.ts        # JS 값 출력 (build/index.ts 생성)
│   └── toMediaConditions.ts
├── rollup.config.mjs
└── package.json
```

### 1.2 11개 토큰 그룹

`polaris-tokens/src/themes/base/index.ts`:

```typescript
export const metaThemeBase = createMetaThemeBase({
  border,       // 15개 토큰
  breakpoints,  // 5개 토큰
  color,        // ~250개 토큰 (가장 큰 그룹)
  font,         // 31개 토큰
  height,       // 20개 토큰
  motion,       // 23개 토큰
  shadow,       // 23개 토큰
  space,        // 22개 토큰
  text,         // 55개 토큰
  width,        // 20개 토큰
  zIndex,       // 13개 토큰
});
// 총 ~477개 토큰
```

### 1.3 네이밍 체계 (Taxonomy)

`polaris-tokens-structure.md`에 문서화된 공식 구조:

```
--p-[token-group-name]-[token-name]
```

그룹별 패턴:

| 그룹 | 패턴 | 예시 |
|------|------|------|
| border | `--p-border-[property]-[alias-or-scale]` | `--p-border-radius-200`, `--p-border-width-050` |
| breakpoints | `--p-breakpoints-[alias]` | `--p-breakpoints-sm`, `--p-breakpoints-md` |
| color | `--p-color-[element]-[role?]-[prominence?]-[state?]` | `--p-color-bg-surface-secondary-hover` |
| font | `--p-font-[property]-[alias-or-scale]` | `--p-font-size-300`, `--p-font-weight-bold` |
| height | `--p-height-[scale]` | `--p-height-800` |
| motion | `--p-motion-[property]-[alias-or-scale]` | `--p-motion-duration-200`, `--p-motion-ease-in` |
| shadow | `--p-shadow-[variant?]-[alias-or-scale]-[state?]` | `--p-shadow-button-primary-inset` |
| space | `--p-space-[alias-or-scale]` | `--p-space-400`, `--p-space-card-padding` |
| text | `--p-text-[variant-size]-[font-property]` | `--p-text-heading-xl-font-size` |
| width | `--p-width-[scale]` | `--p-width-800` |
| z-index | `--p-z-index-[scale]` | `--p-z-index-modal` → 실제: `--p-z-index-1`~`--p-z-index-12` |

### 1.4 컬러 프리미티브 (`src/colors.ts`)

13개 컬러 램프, 각 16 스텝 (1=가장 밝음 → 16=가장 어두움):

```typescript
// src/colors.ts
type ColorScale = '1' | '2' | ... | '16';
type Color = { [Scale in ColorScale]: `rgba(${number}, ${number}, ${number}, 1)` };

export const gray: Color = {
  1: 'rgba(255, 255, 255, 1)',   // 흰색
  2: 'rgba(253, 253, 253, 1)',
  // ...
  15: 'rgba(48, 48, 48, 1)',
  16: 'rgba(26, 26, 26, 1)',     // 거의 검정
};

export const azure: Color = { /* 16 스텝 */ };
export const blue: Color = { /* 16 스텝 */ };
export const cyan: Color = { /* 16 스텝 */ };
export const green: Color = { /* 16 스텝 */ };
export const lime: Color = { /* 16 스텝 */ };
export const magenta: Color = { /* 16 스텝 */ };
export const orange: Color = { /* 16 스텝 */ };
export const purple: Color = { /* 16 스텝 */ };
export const red: Color = { /* 16 스텝 */ };
export const rose: Color = { /* 16 스텝 */ };
export const teal: Color = { /* 16 스텝 */ };
export const yellow: Color = { /* 16 스텝 */ };

// 알파 램프
export const blackAlpha: ColorAlpha = {
  1: 'rgba(0, 0, 0, 0)',
  5: 'rgba(0, 0, 0, 0.05)',
  16: 'rgba(0, 0, 0, 0.90)',
};
export const whiteAlpha: ColorAlpha = { /* 16 스텝 */ };
```

**총 컬러 프리미티브**: 13 × 16 + 2 × 16 = **240개 raw 값**

### 1.5 사이즈 스케일 (`src/size.ts`)

4px 기반 스케일, 27개 값:

```typescript
export const size = {
  '0': '0px',
  '0165': '0.66px',   // 1px border (Retina)
  '025': '1px',
  '050': '2px',
  '100': '4px',       // ← 기준 단위
  '150': '6px',
  '200': '8px',
  '275': '11px',
  '300': '12px',
  '325': '13px',
  '350': '14px',
  '400': '16px',
  '450': '18px',
  '500': '20px',
  '550': '22px',
  '600': '24px',
  '700': '28px',
  '750': '30px',
  '800': '32px',
  '900': '36px',
  '1000': '40px',
  '1200': '48px',
  '1600': '64px',
  '2000': '80px',
  '2400': '96px',
  '2800': '112px',
  '3200': '128px',
} as const;
```

space, height, width, border-radius, font-size, font-line-height 그룹이 이 스케일을 공유.

### 1.6 컬러 토큰 아키텍처: bg-surface vs bg-fill

Polaris의 컬러 시맨틱은 **표면적(surface area)** 에 따라 2축으로 분리:

| 축 | 용도 | 예시 |
|----|------|------|
| `bg-surface-*` | 넓은 표면 (Card, Panel) | `--p-color-bg-surface`, `--p-color-bg-surface-secondary` |
| `bg-fill-*` | 작은 표면 (Button, Badge) | `--p-color-bg-fill`, `--p-color-bg-fill-brand` |

각 축은 **prominence** (secondary, tertiary)와 **state** (hover, active, selected, disabled)로 확장.

실제 토큰 정의 (`src/themes/base/color.ts`):

```typescript
'color-bg-surface': {
  value: colors.gray[1],    // rgba(255, 255, 255, 1)
  description: 'The background color for elements with the highest level of prominence, like a card.',
},
'color-bg-surface-hover': {
  value: colors.gray[4],    // rgba(247, 247, 247, 1)
  description: 'The hover state color for elements with the highest level of prominence.',
},
'color-bg-fill': {
  value: colors.gray[1],    // rgba(255, 255, 255, 1)
  description: 'The background color of contained elements with a smaller surface area, like a button.',
},
'color-bg-fill-brand': {
  value: colors.gray[15],   // rgba(48, 48, 48, 1) — 어두운 색!
  description: 'The background color of main actions, like primary buttons.',
},
```

### 1.7 on-bg-fill 페어링 패턴

텍스트/아이콘 컬러는 배경 위에 올라갈 때 **전용 on-bg-fill 토큰**으로 페어링:

```typescript
// 배경
'color-bg-fill-brand': { value: colors.gray[15] },         // 어두운 배경
'color-bg-fill-brand-hover': { value: colors.gray[16] },

// 이 위에 올리는 텍스트
'color-text-brand-on-bg-fill': {
  value: colors.gray[1],    // 흰색 텍스트
  description: 'Use for text on bg-fill-brand, like primary buttons.',
},
'color-text-brand-on-bg-fill-hover': {
  value: colors.gray[8],
  description: 'The hover state color for text on bg-fill-brand-hover.',
},
'color-text-brand-on-bg-fill-disabled': {
  value: colors.gray[1],
  description: 'The disabled state color for text on bg-fill-brand-disabled.',
},
```

이 패턴은 모든 semantic color에 적용: `text-info-on-bg-fill`, `text-success-on-bg-fill`, `text-critical-on-bg-fill`, `text-warning-on-bg-fill`, `text-emphasis-on-bg-fill`, `text-magic-on-bg-fill`.

### 1.8 Specialty/Component 토큰

글로벌 시맨틱 토큰 외에 **컴포넌트 전용** 컬러 토큰도 존재:

```typescript
// ColorBackgroundAlias 중 specialty 토큰
'avatar-bg-fill' | 'avatar-one-bg-fill' | ... | 'avatar-seven-bg-fill'
'backdrop-bg'
'button-gradient-bg-fill'
'checkbox-bg-surface-disabled'
'input-bg-surface' | 'input-bg-surface-hover' | 'input-bg-surface-active'
'nav-bg' | 'nav-bg-surface' | 'nav-bg-surface-hover' | 'nav-bg-surface-active' | 'nav-bg-surface-selected'
'radio-button-bg-surface-disabled'
'video-thumbnail-play-button-bg-fill' | 'video-thumbnail-play-button-bg-fill-hover'
'scrollbar-thumb-bg' | 'scrollbar-thumb-bg-hover'
'tooltip-tail-down-border' | 'tooltip-tail-up-border'
```

### 1.9 Space 토큰: 스케일 + Alias

```typescript
// src/themes/base/space.ts
'space-0':    { value: size[0] },      // 0px
'space-025':  { value: size['025'] },  // 1px
'space-050':  { value: size['050'] },  // 2px
'space-100':  { value: size[100] },    // 4px  ← 기준
'space-150':  { value: size[150] },    // 6px
'space-200':  { value: size[200] },    // 8px
'space-300':  { value: size[300] },    // 12px
'space-400':  { value: size[400] },    // 16px
'space-500':  { value: size[500] },    // 20px
'space-600':  { value: size[600] },    // 24px
'space-800':  { value: size[800] },    // 32px
'space-1000': { value: size[1000] },   // 40px
'space-1200': { value: size[1200] },   // 48px
'space-1600': { value: size[1600] },   // 64px
'space-2000': { value: size[2000] },   // 80px
'space-2400': { value: size[2400] },   // 96px
'space-2800': { value: size[2800] },   // 112px
'space-3200': { value: size[3200] },   // 128px

// Alias → 스케일 참조
'space-button-group-gap': { value: 'var(--p-space-200)' },  // 8px
'space-card-gap':         { value: 'var(--p-space-400)' },  // 16px
'space-card-padding':     { value: 'var(--p-space-400)' },  // 16px
'space-table-cell-padding': { value: 'var(--p-space-150)' }, // 6px
```

### 1.10 MetaTokenProperties: description 포함

모든 토큰은 `value` + optional `description`을 가짐:

```typescript
// src/themes/types.ts
export interface MetaTokenProperties {
  value: string;
  description?: string;
}
```

실제 활용 예:

```typescript
'color-bg': {
  value: colors.gray[6],
  description: 'The default background color of the admin.',
},
'motion-ease': {
  value: 'cubic-bezier(0.25, 0.1, 0.25, 1)',
  description: 'Responds quickly and finishes with control. A great default for any user interaction.',
},
'breakpoints-sm': {
  value: '490px',
  description: 'Commonly used for sizing containers (e.g. max-width). See below for media query usage.',
},
```

### 1.11 기타 토큰 그룹 실제 값

**Motion** (23개):
```typescript
'motion-duration-0':    { value: '0ms' },
'motion-duration-100':  { value: '100ms' },
'motion-duration-200':  { value: '200ms' },
'motion-duration-500':  { value: '500ms' },
'motion-duration-5000': { value: '5000ms' },
'motion-ease':          { value: 'cubic-bezier(0.25, 0.1, 0.25, 1)' },
'motion-ease-in':       { value: 'cubic-bezier(0.42, 0, 1, 1)' },
'motion-ease-out':      { value: 'cubic-bezier(0.19, 0.91, 0.38, 1)' },
'motion-ease-in-out':   { value: 'cubic-bezier(0.42, 0, 0.58, 1)' },
'motion-linear':        { value: 'cubic-bezier(0, 0, 1, 1)' },
'motion-keyframes-fade-in':  { value: '{ to { opacity: 1 } }' },
'motion-keyframes-spin':     { value: '{ to { transform: rotate(1turn) } }' },
'motion-keyframes-bounce':   { value: '{ from, 65%, 85% { transform: scale(1) } 75% { ... } }' },
'motion-keyframes-pulse':    { value: '{ from, 75% { transform: scale(0.85); ... } }' },
```

**Shadow** (23개):
```typescript
'shadow-0':   { value: 'none' },
'shadow-100': { value: '0px 1px 0px 0px rgba(26, 26, 26, 0.07)' },
'shadow-200': { value: '0px 3px 1px -1px rgba(26, 26, 26, 0.07)' },
'shadow-300': { value: '0px 4px 6px -2px rgba(26, 26, 26, 0.20)' },
'shadow-400': { value: '0px 8px 16px -4px rgba(26, 26, 26, 0.22)' },
'shadow-500': { value: '0px 12px 20px -8px rgba(26, 26, 26, 0.24)' },
'shadow-600': { value: '0px 20px 20px -8px rgba(26, 26, 26, 0.28)' },
'shadow-bevel-100': { value: '1px 0px 0px 0px rgba(0,0,0,0.13) inset, ...' },
'shadow-button': { value: '0px -1px 0px 0px #b5b5b5 inset, ...' },
'shadow-button-primary': { value: '0px -1px 0px 1px rgba(0,0,0,0.8) inset, ...' },
'shadow-button-primary-critical': { value: '...' },
'shadow-button-primary-success': { value: '...' },
```

**Z-Index** (13개):
```typescript
'z-index-0':  { value: 'auto' },
'z-index-1':  { value: '100' },
'z-index-2':  { value: '400' },
'z-index-3':  { value: '510' },
'z-index-4':  { value: '512' },
// ... z-index-12: '520'
```

**Breakpoints** (5개):
```typescript
'breakpoints-xs': { value: '0px' },
'breakpoints-sm': { value: '490px' },
'breakpoints-md': { value: '768px' },
'breakpoints-lg': { value: '1040px' },
'breakpoints-xl': { value: '1440px' },
```

**Font** (31개):
```typescript
'font-family-sans': { value: "'Inter', -apple-system, BlinkMacSystemFont, 'San Francisco', 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif" },
'font-family-mono': { value: "ui-monospace, SFMono-Regular, 'SF Mono', Consolas, 'Liberation Mono', Menlo, monospace" },
'font-size-275': { value: '11px' },   // size[275]
'font-size-300': { value: '12px' },
'font-size-325': { value: '13px' },
'font-size-350': { value: '14px' },
'font-size-400': { value: '16px' },
// ... font-size-1000: '40px'
'font-weight-regular':  { value: '450' },
'font-weight-medium':   { value: '550' },
'font-weight-semibold': { value: '650' },
'font-weight-bold':     { value: '700' },
'font-letter-spacing-densest': { value: '-0.54px' },
'font-letter-spacing-denser':  { value: '-0.3px' },
'font-letter-spacing-dense':   { value: '-0.2px' },
'font-letter-spacing-normal':  { value: '0px' },
```

**Text** (55개 = 11 variants × 5 properties):
```typescript
// 각 variant는 font-family, font-size, font-weight, font-letter-spacing, font-line-height를 가짐
'text-heading-3xl-font-size':   { value: 'var(--p-font-size-900)' },    // 36px
'text-heading-2xl-font-size':   { value: 'var(--p-font-size-750)' },    // 30px
'text-heading-xl-font-size':    { value: 'var(--p-font-size-600)' },    // 24px
'text-heading-lg-font-size':    { value: 'var(--p-font-size-500)' },    // 20px
'text-heading-md-font-size':    { value: 'var(--p-font-size-350)' },    // 14px
'text-heading-sm-font-size':    { value: 'var(--p-font-size-325)' },    // 13px
'text-heading-xs-font-size':    { value: 'var(--p-font-size-300)' },    // 12px
'text-body-lg-font-size':       { value: 'var(--p-font-size-350)' },    // 14px
'text-body-md-font-size':       { value: 'var(--p-font-size-325)' },    // 13px
'text-body-sm-font-size':       { value: 'var(--p-font-size-300)' },    // 12px
'text-body-xs-font-size':       { value: 'var(--p-font-size-275)' },    // 11px
```

---

## 2. Token 소비 (Consumption)

### 2.1 2-Layer 아키텍처: `--p-*` → `--pc-*`

Polaris 토큰 소비의 핵심은 **2층 커스텀 프로퍼티** 구조:

```
Layer 1: --p-*     (글로벌 토큰, 테마가 결정)
Layer 2: --pc-*    (컴포넌트 프라이빗, variant가 결정)
```

- `--p-*`: `polaris-tokens`에서 생성, `:root`에 주입. 테마 변경 시 이 값만 바뀌면 됨
- `--pc-*`: 컴포넌트 CSS Module 내부에서만 정의/사용. 외부에서 접근 불가

### 2.2 Custom-Property State Machine: Button.module.css

`polaris-react/src/components/Button/Button.module.css` — **전체 파일이 이 패턴의 교과서**:

```css
.Button {
  /* === State Machine 초기화 === */
  /* 각 채널(channel)마다 base + 4개 state 변수 선언 */
  --pc-button-bg: transparent;
  --pc-button-bg_hover: var(--pc-button-bg);           /* default: base 상속 */
  --pc-button-bg_active: var(--pc-button-bg);
  --pc-button-bg_pressed: var(--pc-button-bg_active);
  --pc-button-bg_disabled: var(--p-color-bg-fill-disabled);  /* --p-* 참조 */

  --pc-button-color: inherit;
  --pc-button-color_hover: var(--pc-button-color);
  --pc-button-color_active: var(--pc-button-color);
  --pc-button-color_pressed: var(--pc-button-color_active);
  --pc-button-color_disabled: var(--p-color-text-disabled);

  --pc-button-box-shadow: transparent;
  --pc-button-box-shadow_hover: var(--pc-button-box-shadow);
  --pc-button-box-shadow_active: var(--pc-button-box-shadow);
  --pc-button-box-shadow_pressed: var(--pc-button-box-shadow_active);
  --pc-button-box-shadow_disabled: var(--pc-button-box-shadow);

  --pc-button-icon-fill: currentColor;
  --pc-button-icon-fill_hover: var(--pc-button-icon-fill);
  --pc-button-icon-fill_active: var(--pc-button-icon-fill);
  --pc-button-icon-fill_pressed: var(--pc-button-icon-fill_active);
  --pc-button-icon-fill_disabled: var(--p-color-icon-disabled);

  /* === 실제 스타일은 --pc-* 변수만 소비 === */
  background: var(--pc-button-bg);
  color: var(--pc-button-color);
  box-shadow: var(--pc-button-box-shadow);
  border-radius: var(--p-border-radius-200);  /* --p-* 직접 참조도 가능 */
}

/* pseudo-class는 변수 "읽기"만 */
.Button:hover {
  background: var(--pc-button-bg_hover);
  color: var(--pc-button-color_hover);
  box-shadow: var(--pc-button-box-shadow_hover);
}

.Button:active {
  background: var(--pc-button-bg_active);
  color: var(--pc-button-color_active);
}

.Button:disabled {
  background: var(--pc-button-bg_disabled);
  color: var(--pc-button-color_disabled);
}
```

**Variant 클래스는 변수 "재할당"만** — 새로운 CSS 프로퍼티를 쓰지 않음:

```css
.variantPrimary {
  --pc-button-bg: var(--pc-button-bg-gradient), var(--p-color-bg-fill-brand);
  --pc-button-bg_hover: var(--pc-button-bg-gradient), var(--p-color-bg-fill-brand-hover);
  --pc-button-bg_active: var(--pc-button-bg-gradient), var(--p-color-bg-fill-brand-active);
  --pc-button-bg_disabled: var(--p-color-bg-fill-brand-disabled);
  --pc-button-color: var(--p-color-text-brand-on-bg-fill);
  --pc-button-color_disabled: var(--p-color-text-brand-on-bg-fill-disabled);
  --pc-button-box-shadow: var(--p-shadow-button-primary);
  --pc-button-box-shadow_active: var(--p-shadow-button-primary-inset);
  --pc-button-icon-fill: var(--p-color-text-brand-on-bg-fill);
}

.variantSecondary {
  --pc-button-box-shadow: var(--p-shadow-button);
  --pc-button-box-shadow_active: var(--p-shadow-button-inset);
  --pc-button-bg: var(--p-color-bg-fill);
  --pc-button-bg_hover: var(--p-color-bg-fill-hover);
  --pc-button-bg_active: var(--p-color-bg-fill-active);
  --pc-button-bg_pressed: var(--p-color-bg-fill-selected);
  --pc-button-color: var(--p-color-text);
}

.variantTertiary {
  --pc-button-bg_hover: var(--p-color-bg-fill-transparent-hover);
  --pc-button-bg_active: var(--p-color-bg-fill-transparent-active);
  --pc-button-bg_disabled: transparent;
  --pc-button-color: var(--p-color-text);
}

.variantPlain {
  --pc-button-color: var(--p-color-text-link);
  --pc-button-color_hover: var(--p-color-text-link-hover);
  --pc-button-color_active: var(--p-color-text-link-active);
}
```

**Tone 클래스도 동일 패턴**:

```css
.toneSuccess:is(.variantPrimary) {
  --pc-button-bg: var(--p-color-bg-fill-success);
  --pc-button-bg_hover: var(--p-color-bg-fill-success-hover);
  --pc-button-bg_active: var(--p-color-bg-fill-success-active);
  --pc-button-box-shadow: var(--p-shadow-button-primary-success);
}

.toneCritical:is(.variantSecondary, .variantTertiary, .variantPlain) {
  --pc-button-color: var(--p-color-text-critical);
  --pc-button-color_hover: var(--p-color-text-critical-hover);
  --pc-button-icon-fill: currentColor;
}
```

**Size 클래스**:

```css
.sizeMicro {
  --pc-button-padding-block: var(--p-space-100);
  --pc-button-padding-inline: var(--p-space-200);
  min-height: var(--p-height-700);
}
.sizeSlim, .sizeMedium {
  --pc-button-padding-block: var(--p-space-150);
  --pc-button-padding-inline: var(--p-space-300);
  min-height: var(--p-height-800);
}
.sizeLarge {
  --pc-button-padding-block: var(--p-space-150);
  --pc-button-padding-inline: var(--p-space-300);
  min-height: var(--p-height-900);
}
```

### 2.3 이 패턴의 설계 의의

```
┌─────────────────────────────────────────────────┐
│  .Button (base)                                 │
│  --pc-button-bg: transparent                    │  ← default 값
│  --pc-button-bg_hover: var(--pc-button-bg)      │  ← cascade 상속
│  background: var(--pc-button-bg)                │  ← 소비
├─────────────────────────────────────────────────┤
│  .variantPrimary                                │
│  --pc-button-bg: var(--p-color-bg-fill-brand)   │  ← 재할당만
│  (background 프로퍼티는 건드리지 않음)            │
├─────────────────────────────────────────────────┤
│  .toneSuccess:is(.variantPrimary)               │
│  --pc-button-bg: var(--p-color-bg-fill-success) │  ← 재할당만
└─────────────────────────────────────────────────┘
```

- **Variant × Tone × State 조합 폭발**을 O(n+m)으로 해결
- CSS specificity 전쟁 없음
- `className`/`style` prop escape hatch 없음 → 토큰 우회 불가

### 2.4 stylelint-polaris: 토큰 사용 강제

`stylelint-polaris/index.js` — **10개 coverage 카테고리**로 토큰 사용을 lint:

```javascript
const stylelintPolarisCoverageOptions = {
  border: [
    { 'declaration-property-unit-disallowed-list': [
        { 'border-width': disallowedUnits, 'border-radius': disallowedUnits, ... }
    ]},
    { message: 'Please use a Polaris border token' },
  ],
  color: [
    { 'color-named': 'never',
      'color-no-hex': true,
      'function-disallowed-list': ['rgb', 'rgba', 'hsl', 'hsla', ...] },
    { message: 'Please use a Polaris color token' },
  ],
  conventions: {
    // --p-*, --pc-*, --pg-* 이외의 커스텀 프로퍼티 정의만 허용
    'polaris/custom-property-allowed-list': {
      allowedProperties: [/--(?!(p|pc|pg|polaris-version)-).+/],
      allowedValues: {
        '/.+/': [
          ...getThemeVarNames(themeDefault),  // 유효한 --p-* 토큰만 허용
          /--(?!(p|pc|pg)-).+/,              // 그 외 --p-*는 플래그
        ],
      },
    },
  },
  space: [
    { 'declaration-property-unit-disallowed-list': [
        { '/^padding/': disallowedUnits, '/^margin/': disallowedUnits, '/^gap/': disallowedUnits }
    ]},
    { message: 'Please use a Polaris space token' },
  ],
  typography: [
    { 'property-disallowed-list': [['font-size', 'font-weight', 'line-height', ...],
        {severity: 'warning'}] },
    { message: 'Please use the Polaris Text component' },
  ],
  motion: [
    { 'declaration-property-unit-disallowed-list': [
        { '/^animation/': ['ms', 's'], '/^transition/': ['ms', 's'] }
    ]},
    { message: 'Please use a Polaris motion token' },
  ],
  shadow: [ /* box-shadow에 raw 단위 금지 */ ],
  'z-index': [
    { 'declaration-property-value-allowed-list': [
        { 'z-index': Object.keys(themeDefault.zIndex).map(createVar) }
    ]},
    { message: 'Please use a Polaris z-index token' },
  ],
  layout: [ /* position, grid, flex 등에 warning */ ],
  legacy: [ /* 구형 mixin/function 차단 */ ],
  'media-queries': [ /* Polaris breakpoint 토큰 강제 */ ],
};
```

**핵심 규칙 요약**:
- `color-no-hex: true` → 헥스 컬러 직접 사용 금지
- `color-named: never` → `blue`, `red` 등 named color 금지
- 모든 padding/margin/gap에 px/rem/em 단위 금지 → `var(--p-space-*)` 강제
- z-index는 `var(--p-z-index-*)` 값만 허용
- animation/transition에 ms/s 단위 금지 → `var(--p-motion-duration-*)` 강제
- `--p-*` 커스텀 프로퍼티는 유효한 Polaris 토큰 이름만 허용

**7개 커스텀 플러그인**:
1. `coverage` — 카테고리별 동적 규칙 이름 생성
2. `global-disallowed-list` — 레거시 Sass 변수 차단
3. `at-rule-disallowed-list` — 레거시 mixin 차단
4. `custom-property-allowed-list` — `--p-*` 토큰 검증
5. `custom-property-disallowed-list`
6. `media-query-allowed-list` — breakpoint 토큰 강제
7. `declaration-property-value-disallowed-list`

### 2.5 4가지 출력 포맷

`package.json` exports:

```json
{
  "exports": {
    ".": {
      "types": "./dist/types/build/index.d.ts",
      "import": "./dist/esm/build/index.mjs",
      "require": "./dist/cjs/build/index.js"
    },
    "./css/*": "./dist/css/*",
    "./scss/*": "./dist/scss/*"
  }
}
```

빌드 파이프라인 (`scripts/index.ts`):

```typescript
import {toMediaConditions} from './toMediaConditions';
import {toStyleSheet} from './toStyleSheet';
import {toValues} from './toValues';

(async () => {
  await Promise.all([toMediaConditions(), toStyleSheet(), toValues()]);
})();
```

| 포맷 | 출력 경로 | 용도 |
|------|-----------|------|
| **JS (CJS)** | `dist/cjs/build/index.js` | Node.js require |
| **JS (ESM)** | `dist/esm/build/index.mjs` | bundler import |
| **CSS** | `dist/css/styles.css` | `<link>` 또는 CSS import |
| **SCSS** | `dist/scss/styles.scss` | Sass 프로젝트 |

`toValues.ts`가 생성하는 `build/index.ts`:

```typescript
// 자동 생성됨
export * from '../src/index';
export const themes = {
  light: { /* 모든 토큰 값, var() 참조 해결됨 */ },
  'light-mobile': { /* ... */ },
  'light-high-contrast-experimental': { /* ... */ },
  'dark-experimental': { /* ... */ },
} as const;
export const themeDefault = themes['light'];
export const isTokenName = createIsTokenName(themes['light']);
```

`toStyleSheet.ts`가 생성하는 CSS:

```css
/* :root에 기본 테마(light) 전체 토큰 주입 */
:root,.p-theme-light{--p-color-bg:rgba(241,241,241,1);--p-color-bg-surface:rgba(255,255,255,1);...}

/* 다른 테마는 partial만 (base에서 변경된 값만) */
.p-theme-light-mobile{--p-shadow-100:none;--p-shadow-bevel-100:none;...}
.p-theme-light-high-contrast-experimental{--p-color-text:rgba(26,26,26,1);...}
.p-theme-dark-experimental{--p-color-bg:rgba(26,26,26,1);--p-color-bg-surface:rgba(48,48,48,1);...}

/* keyframes */
@keyframes p-motion-keyframes-fade-in{ to { opacity: 1 } }
@keyframes p-motion-keyframes-spin{ to { transform: rotate(1turn) } }
```

### 2.6 테마 시스템: 4개 테마

`src/themes/constants.ts`:

```typescript
export const themeNames = [
  'light',                              // 기본 (base 그대로)
  'light-mobile',                       // 모바일 최적화
  'light-high-contrast-experimental',   // 고대비
  'dark-experimental',                  // 다크 모드
] as const;
```

**테마 합성 메커니즘** (`src/themes/utils.ts`):

```typescript
export function createMetaTheme(metaThemePartial) {
  return deepmerge(metaThemeBase, metaThemePartial);
  // base 전체 + partial 오버라이드 → 완전한 테마
}
```

**light** (기본): 빈 partial → base 그대로 사용

```typescript
export const metaThemeLightPartial = createMetaThemePartial({});
```

**dark-experimental**: color + shadow 오버라이드

```typescript
export const metaThemeDarkPartial = createMetaThemePartial({
  color: {
    'color-scheme': {value: 'dark'},
    'color-bg': {value: colors.gray[16]},           // 어두운 배경
    'color-bg-surface': {value: colors.gray[15]},
    'color-bg-fill': {value: colors.gray[15]},
    'color-text': {value: colors.gray[8]},           // 밝은 텍스트
    'color-text-secondary': {value: colors.gray[11]},
    'color-bg-fill-brand': {value: colors.gray[1]},  // 반전: 밝은 브랜드
    'color-text-brand-on-bg-fill': {value: colors.gray[15]},
    // ... ~40개 오버라이드
  },
  shadow: {
    'shadow-bevel-100': {value: '... rgba(204,204,204,0.08) inset ...'},
  },
});
```

**light-mobile**: shadow 제거 + 타이포그래피 확대

```typescript
export const metaThemeLightMobilePartial = createMetaThemePartial({
  color: {
    'color-button-gradient-bg-fill': {value: 'none'},
  },
  shadow: {
    'shadow-100': {value: 'none'},
    'shadow-bevel-100': {value: 'none'},
    'shadow-button': {value: buttonShadow},  // 단순 inset border로 대체
    'shadow-button-primary': {value: 'none'},
    // ... 모든 button shadow 제거
  },
  space: {
    'space-card-gap': {value: createVar('space-200')},  // 16px → 8px
  },
  text: {
    'text-body-md-font-size': {value: createVar('font-size-400')},  // 13px → 16px
    'text-body-lg-font-size': {value: createVar('font-size-450')},  // 14px → 18px
    // ... 모바일에 맞게 전체 타이포 스케일 업
  },
});
```

**light-high-contrast-experimental**: 대비 강화

```typescript
export const metaThemeLightHighContrastPartial = createMetaThemePartial({
  color: {
    'color-text': {value: colors.gray[16]},           // 가장 어두운 텍스트
    'color-text-secondary': {value: colors.gray[16]}, // secondary도 동일
    'color-border': {value: colors.gray[12]},         // 더 진한 border
    'color-input-border': {value: colors.gray[14]},
  },
  shadow: {
    'shadow-bevel-100': {value: '... 더 강한 inset shadow ...'},
  },
});
```

**테마 적용**: CSS 클래스로 전환

```typescript
export function createThemeClassName(themeName: ThemeName) {
  return `p-theme-${themeName}`;
}
// → .p-theme-light, .p-theme-dark-experimental, etc.
```

### 2.7 className/style Escape Hatch 부재

Polaris React 컴포넌트는 `className`이나 `style` prop을 노출하지 않음.
이는 **토큰 시스템의 무결성**을 보장:

- 개발자가 임의 CSS로 토큰을 우회할 수 없음
- 모든 시각적 변경은 토큰 또는 variant prop을 통해서만 가능
- stylelint-polaris가 내부 코드에서도 이를 강제

---

## 3. Token 거버넌스 (Governance)

### 3.1 빌드 프로세스

```
npm run build
  ├── build:assets  → ts-node scripts/index.ts
  │   ├── toValues()           → build/index.ts (JS 값, var() 해결됨)
  │   ├── toStyleSheet()       → dist/css/styles.css + dist/scss/styles.scss
  │   └── toMediaConditions()  → 미디어 쿼리 유틸리티
  ├── build:js      → rollup -c
  │   ├── dist/cjs/build/index.js   (CommonJS)
  │   └── dist/esm/build/index.mjs  (ESM)
  └── build:types   → tsc -b
      └── dist/types/build/index.d.ts
```

Rollup 설정 (`rollup.config.mjs`):

```javascript
export default {
  input: 'build/index.ts',  // scripts/toValues가 생성한 파일
  output: [
    { format: 'cjs', dir: 'dist/cjs', preserveModules: true },
    { format: 'es',  dir: 'dist/esm', preserveModules: true },
  ],
  plugins: [nodeResolve(), commonjs(), babel()],
  external: ['deepmerge'],  // 유일한 런타임 의존성
};
```

### 3.2 Code-First: TypeScript가 Single Source of Truth

```
TypeScript (src/themes/base/*.ts)
    │
    ├──→ JS 객체 (themes, themeDefault)
    ├──→ CSS 커스텀 프로퍼티 (--p-*)
    ├──→ SCSS 변수
    ├──→ TypeScript 타입 (ColorTokenName, SpaceScale 등)
    └──→ 문서 (polaris.shopify.com/tokens)
```

**Figma가 source of truth가 아님**. 토큰은 TypeScript 코드로 정의되고, Figma는 이를 소비하는 쪽.

함의:
- 토큰 변경 = 코드 변경 → PR 리뷰, CI 테스트, 버전 관리 적용
- Figma ↔ Code 동기화 문제 발생 가능 (양방향 자동 동기화 없음)
- 타입 안전성: 존재하지 않는 토큰 참조 시 컴파일 에러

### 3.3 타입 안전성 메커니즘

```typescript
// 토큰 이름이 리터럴 타입으로 추출됨
export type TokenName = {
  [TokenGroupName in keyof Theme]: {
    [TokenName in keyof Theme[TokenGroupName]]: TokenName;
  }[keyof Theme[TokenGroupName]];
}[keyof Theme];

// createVar는 유효한 토큰 이름만接受
export function createVarName(tokenName: TokenName) {
  return `--p-${tokenName}`;
}

// 런타임 검증도 제공
export const isTokenName = createIsTokenName(themes[themeNameDefault]);
```

`Exact` 타입으로 partial 테마의 오타도 차단:

```typescript
export function createMetaThemePartial<
  T extends Exact<MetaThemePartialShape, T>,
>(metaThemePartial: T) { ... }
// 존재하지 않는 토큰 이름을 쓰면 타입 에러
```

### 3.4 버전 관리 및 Changelog

**현재 버전**: 9.4.2

주요 마일스톤 (CHANGELOG.md에서):

| 버전 | 주요 변경 |
|------|-----------|
| 9.4.2 | Add provenance statement |
| 9.4.0 | tooltip 토큰 정식화, `bg-fill-secondary-selected` 추가, dark 테마 확장 |
| 9.3.0 | green/red 토큰 값 업데이트 |
| 9.2.0 | touch/non-touch 미디어 쿼리 추가 |
| 9.1.0 | scrollbar 토큰 추가, whiteAlpha 램프 업데이트, `sideEffects: false` |
| 9.0.0 | **Breaking**: Node v20.10.0 최소 요구 |
| 8.10.0 | white alpha 램프 추가, dark 테마 토큰 확장 |
| 8.9.0 | `ThemeProvider` 추가, `dark-experimental` 테마 초기화 |
| 8.8.0 | light-mobile 테마에 Button 네이티브 스타일 |
| 8.6.0 | 모바일 타이포그래피 토큰, Button shadow 토큰 |

### 3.5 공개 API

`src/index.ts`에서 export하는 것:

```typescript
// 유틸리티 함수
export { createVar, createVarName, getThemeVarNames, getMediaConditions, toPx, toPxs, toRem } from './utils';

// 테마 데이터
export { metaThemes, metaThemeDefault } from './themes';
export { themeNameDefault, themeNames } from './themes/constants';
export { createThemeClassName } from './themes/utils';

// 타입 (모든 토큰 그룹)
export type { BorderTokenGroup, BorderTokenName, BorderRadiusScale, ... } from './themes/base/border';
export type { ColorTokenGroup, ColorTokenName, ColorBackgroundAlias, ColorBorderAlias, ColorIconAlias, ColorTextAlias } from './themes/base/color';
export type { FontTokenGroup, FontTokenName, FontSizeScale, ... } from './themes/base/font';
export type { SpaceTokenGroup, SpaceTokenName, SpaceScale } from './themes/base/space';
// ... 11개 그룹 전체
```

### 3.6 React → Web Components 마이그레이션과 토큰

Polaris는 React에서 Web Components로 마이그레이션 중.
토큰 관점에서의 영향:

- **`@shopify/polaris-tokens`는 프레임워크 독립적** — CSS custom properties로 출력되므로 Web Components에서도 동일하게 소비 가능
- `--p-*` 토큰은 `:root`에 주입되는 글로벌 값이므로, Shadow DOM 내부에서도 `var(--p-*)`로 접근 가능
- `--pc-*` 컴포넌트 프라이빗 토큰은 Shadow DOM 경계 내에 자연스럽게 격리됨
- 토큰 패키지 자체의 변경 없이 소비층만 교체 가능

### 3.7 의존성

```json
{
  "dependencies": {
    "deepmerge": "^4.3.1"
  }
}
```

**유일한 런타임 의존성 1개**. 테마 합성(`deepmerge(metaThemeBase, partial)`)에 사용.
나머지는 모두 devDependencies (rollup, babel, typescript, jest).

---

## 4. 핵심 설계 패턴 요약

### 4.1 토큰 계층 구조

```
Color Primitives (colors.ts)     ← 240개 raw rgba 값
    ↓ 참조
Semantic Tokens (themes/base/)   ← ~477개 --p-* 토큰
    ↓ var() 참조
Component Tokens (*.module.css)  ← --pc-* 컴포넌트 프라이빗
    ↓ 소비
CSS Properties                   ← background, color, box-shadow 등
```

### 4.2 테마 = Partial Override

```
metaThemeBase (전체 ~477개 토큰)
    + metaThemeLightPartial ({})              → light (기본)
    + metaThemeDarkPartial (~40개 오버라이드)  → dark-experimental
    + metaThemeLightMobilePartial (~30개)     → light-mobile
    + metaThemeLightHighContrastPartial (~8개) → light-high-contrast-experimental
```

### 4.3 빌드 출력 흐름

```
src/themes/base/*.ts  ──→  scripts/toValues.ts  ──→  build/index.ts
                                                         │
                                                    rollup -c
                                                    ┌────┴────┐
                                              dist/cjs    dist/esm

src/themes/*.ts  ──→  scripts/toStyleSheet.ts  ──→  dist/css/styles.css
                                                     dist/scss/styles.scss
```

### 4.4 Polaris 토큰 시스템의 고유 특징

1. **Code-first**: Figma가 아닌 TypeScript가 source of truth
2. **2-layer custom properties**: `--p-*` (global) → `--pc-*` (component) 분리
3. **State machine pattern**: variant 클래스가 CSS 프로퍼티가 아닌 변수만 재할당
4. **stylelint 강제**: 10개 카테고리로 토큰 우회 차단
5. **Escape hatch 없음**: className/style prop 미제공으로 토큰 무결성 보장
6. **Partial 테마 합성**: deepmerge로 base + override, CSS에서는 변경분만 출력
7. **타입 안전성**: TypeScript 리터럴 타입으로 잘못된 토큰 참조 컴파일 타임 차단
8. **최소 의존성**: 런타임 의존성 1개 (deepmerge)
