# IBM Carbon Design System — 컴포넌트 레벨 Token 종속성 감사 (Audit)

> **감사 기준**: `github.com/carbon-design-system/carbon` `main` 브랜치
> **대상 경로**: `packages/styles/scss/components/`
> **감사 날짜**: 2026-07-26
> **방법론**: 각 컴포넌트의 실제 SCSS 소스를 1차로 읽어서 token 참조, hardcoded 값, variant 축, override 메커니즘을 정밀 집계

---

## 0. Carbon Token 아키텍처 개요

Carbon은 **3계층 token 구조**를 사용한다:

| 계층 | 설명 | 예시 |
|------|------|------|
| **Global token** | `@carbon/themes`에서 정의, 모든 컴포넌트가 공유 | `$text-primary`, `$layer`, `$spacing-05`, `$focus` |
| **Component token** | 컴포넌트 전용 `_tokens.scss`에서 정의, `!default`로 override 가능 | `$button-primary`, `$tag-background-red`, `$notification-background-error` |
| **Layout token** | `layout.use()` / `layout.size()` / `layout.density()` 유틸리티 경유 | `layout.size('height')`, `layout.density('padding-inline')` |

**핵심 메커니즘**:
- `component-tokens.get-var()` → Sass map을 CSS custom property(`var(--cds-*)`)로 변환
- 모든 component token은 `!default` flag → Sass map override 가능
- `layout.use('size', $min, $default, $max)` → size variant를 CSS custom property 기반으로 동적 처리
- `@include type-style('body-compact-01')` → typography token을 mixin으로 주입

---

## 1. 컴포넌트별 상세 감사

### 1.1 Button (`button/_button.scss` + `_mixins.scss` + `_tokens.scss`)

**파일 크기**: _button.scss 13,184B / _mixins.scss 4,103B / _tokens.scss 10,224B

#### Token 참조

| 분류 | Token | 사용 횟수 |
|------|-------|-----------|
| Component token | `$button-primary`, `$button-primary-hover`, `$button-primary-active` | 3 |
| Component token | `$button-secondary`, `$button-secondary-hover`, `$button-secondary-active` | 3 |
| Component token | `$button-tertiary`, `$button-tertiary-hover`, `$button-tertiary-active` | 3 |
| Component token | `$button-danger-primary`, `$button-danger-secondary`, `$button-danger-hover`, `$button-danger-active` | 4 |
| Component token | `$button-separator` | 3 |
| Component token | `$button-disabled` | 1 (mixins) |
| Component token | `$button-focus-color`, `$button-outline-width`, `$button-border-width`, `$button-border-radius` | 4 (vars/mixins) |
| Global theme | `$text-on-color`, `$text-inverse`, `$text-disabled`, `$text-on-color-disabled` | 12 |
| Global theme | `$link-primary`, `$link-primary-hover` | 3 |
| Global theme | `$background`, `$background-hover`, `$background-active`, `$background-selected` | 6 |
| Global theme | `$icon-primary`, `$icon-on-color-disabled` | 4 |
| Global theme | `$focus` | 2 |
| Global theme | `$layer-selected-disabled` | 1 |
| Spacing | `$spacing-02`, `$spacing-03`, `$spacing-05`, `$spacing-07`, `$spacing-10` | 7 |
| Motion | `$duration-fast-01` | 4 (mixins) |
| Layout | `layout.size('height')`, `layout.density('padding-inline')` | 8 |

**Token 참조 총계**: ~68회

#### Hardcoded 값

| 값 | 용도 | 발생 횟수 |
|----|------|-----------|
| `convert.to-rem(1px)` | border 보정 (-1px) | 8 |
| `convert.to-rem(16px)` | icon 최소 크기 | 2 |
| `convert.to-rem(20px)` | expressive icon 크기 | 2 |
| `convert.to-rem(176px)` | fluid 최소 버튼 크기 | 1 |
| `convert.to-rem(232px)` | fluid 최대 버튼 크기 | 1 |
| `convert.to-rem(320px)` | max-inline-size | 2 |
| `convert.to-rem(196px)` | button-set max-width | 1 |
| `convert.to-rem(150px)` | skeleton width | 1 |
| `1.5px` | xs padding-block-start | 1 |
| `12px 13px` | expressive icon-only padding | 1 |
| `0`, `100%`, `50%`, `25%` | layout reset/flex | ~15 |

**Hardcoded 총계**: ~35개 선언

#### Variant 축

| 축 | 값 | 메커니즘 |
|----|-----|----------|
| **kind** | `primary`, `secondary`, `tertiary`, `ghost`, `danger`, `danger--tertiary`, `danger--ghost` | className |
| **size** | `xs`, `sm`, `md`, `lg`(default), `xl`, `2xl` | `layout.use('size')` |
| **density** | `normal`(default) | `layout.use('density')` |
| **state** | `disabled`, `expressive`, `icon-only`, `selected`, `skeleton`, `loading` | className |
| **set** | `stacked`, `fluid` | className |

#### Override hooks

- `!default` on 15개 component token (`$button-primary` 등)
- `$button-tokens` Sass map → 일괄 override
- `layout.redefine-tokens()` 가능
- className 기반 variant override

---

### 1.2 TextInput (`text-input/_text-input.scss`)

**파일 크기**: 14,383B

#### Token 참조

| 분류 | Token | 사용 횟수 |
|------|-------|-----------|
| Global theme | `$field`, `$field-02` | 4 |
| Global theme | `$border-strong`, `$border-subtle` | 4 |
| Global theme | `$text-primary`, `$text-disabled`, `$text-error` | 5 |
| Global theme | `$support-error`, `$support-warning` | 2 |
| Global theme | `$icon-primary`, `$icon-disabled` | 5 |
| Global theme | `$black-100` | 1 |
| Spacing | `$spacing-02`, `$spacing-03`, `$spacing-05`, `$spacing-08`, `$spacing-10` | 10 |
| Motion | `$duration-fast-01` | 4 |
| Layout | `layout.size('height')`, `layout.density('padding-inline')` | 6 |

**Token 참조 총계**: ~41회

#### Hardcoded 값

| 값 | 용도 | 발생 횟수 |
|----|------|-----------|
| `1px solid` | border-block-end | 3 |
| `100%` | inline-size | 4 |
| `50%` | translateY | 2 |
| `convert.to-rem(16px)` | fluid label height | 1 |
| `convert.to-rem(13px)` | fluid label top / padding | 2 |
| `convert.to-rem(32px)` | fluid padding-top | 1 |
| `convert.to-rem(64px)` | fluid min-height | 1 |
| `convert.to-rem(80px)` | fluid invalid icon top | 1 |
| `convert.to-rem(142px)` | label helper max-width | 1 |
| `convert.to-rem(2px)` | helper margin | 1 |
| `convert.to-rem(200px)` | form-requirement max-height | 1 |
| `1.5rem` | password padding calc | 1 |
| `1rem` | decorator height | 1 |
| `400` | font-weight | 1 |
| `-1px` | margin (visually hidden) | 1 |
| `0` | reset | ~10 |

**Hardcoded 총계**: ~31개 선언

#### Variant 축

| 축 | 값 | 메커니즘 |
|----|-----|----------|
| **size** | `xs`, `sm`, `md`(default), `lg` | `layout.use('size')` |
| **density** | `normal`(default) | `layout.use('density')` |
| **state** | `invalid`, `warning`, `disabled`, `light`, `readonly`, `skeleton` | className |
| **layout** | `fluid`, `inline` | className |
| **decorator** | `ai-label`, `slug` | className + `:has()` |

#### Override hooks

- `layout.use()` / `layout.redefine-tokens()`
- className 기반
- `@include focus-outline()` mixin parameter
- `@include placeholder-colors` mixin

---

### 1.3 Tile (`tile/_tile.scss`)

**파일 크기**: 18,691B

#### Token 참조

| 분류 | Token | 사용 횟수 |
|------|-------|-----------|
| Global theme | `$layer`, `$layer-02`, `$layer-hover`, `$layer-selected-inverse` | 10 |
| Global theme | `$text-primary`, `$text-disabled` | 5 |
| Global theme | `$border-tile`, `$border-disabled`, `$border-inverse` | 6 |
| Global theme | `$icon-primary`, `$icon-secondary`, `$icon-interactive`, `$icon-disabled` | 6 |
| Global theme | `$focus` | 2 |
| Global theme | `$ai-inner-shadow`, `$ai-drop-shadow` | 6 |
| Spacing | `$spacing-03`, `$spacing-05`, `$spacing-08` | 6 |
| Motion | `$duration-fast-02`, `$duration-moderate-01` | 10 |
| Layout | `layout.density('padding-inline')` | 5 |

**Token 참조 총계**: ~56회

#### Hardcoded 값

| 값 | 용도 | 발생 횟수 |
|----|------|-----------|
| `4rem` | min-block-size | 1 |
| `8rem` | min-inline-size | 1 |
| `2px solid transparent` | outline | 1 |
| `-2px` | outline-offset | 1 |
| `1px solid` | border | 5 |
| `convert.to-rem(20px)` | icon size | 2 |
| `convert.to-rem(12px)` | icon position | 2 |
| `1rem` | checkmark size | 1 |
| `50%` | border-radius | 1 |
| `180deg` | chevron rotation | 1 |
| `100%` | width/height | 3 |
| `-1px` | outline-offset | 1 |
| `0` | reset | ~8 |

**Hardcoded 총계**: ~28개 선언

#### Variant 축

| 축 | 값 | 메커니즘 |
|----|-----|----------|
| **type** | `default`, `clickable`, `selectable`, `expandable` | className |
| **state** | `selected`, `disabled`, `expanded`, `light` | className |
| **density** | `normal`(default) | `layout.use('density')` |
| **decorator** | `ai-label`, `slug`, `rounded` | className + `:has()` |
| **feature flag** | `enable-experimental-tile-contrast`, `enable-tile-contrast`, `enable-v12-tile-radio-icons` | mixin parameter + `enabled()` |

#### Override hooks

- mixin parameter (`$enable-experimental-tile-contrast` 등)
- `enabled()` feature flag 함수
- className 기반
- `layout.use('density')`

---

### 1.4 Modal (`modal/_modal.scss`)

**파일 크기**: 16,807B

#### Token 참조

| 분류 | Token | 사용 횟수 |
|------|-------|-----------|
| Global theme | `$overlay` | 1 |
| Global theme | `$layer`, `$layer-hover` | 8 |
| Global theme | `$border-subtle-01` | 1 |
| Global theme | `$text-primary`, `$text-secondary` | 4 |
| Global theme | `$focus` | 2 |
| Global theme | `$icon-primary` | 1 |
| Global theme | `$ai-overlay`, `$ai-inner-shadow`, `$ai-drop-shadow` | 6 |
| Spacing | `$spacing-02`~`$spacing-09` | 12 |
| Motion | `$duration-fast-02`, `$duration-moderate-02` | 10 |
| Z-index | `z('modal')` | 2 |
| Breakpoint | `breakpoint(md)`, `breakpoint(lg)`, `breakpoint(xlg)` | 12 |

**Token 참조 총계**: ~59회

#### Hardcoded 값

| 값 | 용도 | 발생 횟수 |
|----|------|-----------|
| `100vh`, `100vw` | 전체 viewport | 2 |
| `1px solid` | container border | 1 |
| `3px solid transparent` | outline (HCM) | 1 |
| `-3px` | outline-offset | 1 |
| `84%`, `60%`, `48%` | breakpoint widths | 3 |
| `90%`, `84%` | max-block-size | 2 |
| `32%`, `24%`, `42%`, `72%`, `96%`, `36%` | size variant widths | 8 |
| `convert.to-rem(64px)` | footer height | 2 |
| `convert.to-rem(12px)` | close padding | 1 |
| `3rem` | close button size | 2 |
| `convert.to-rem(20px)` | close icon size | 2 |
| `convert.to-rem(10px)`, `convert.to-rem(48px)` | decorator position | 2 |
| `1rem`, `1.475rem` | decorator inset | 2 |
| `50vh` | header max-height | 1 |
| `20%` | padding-inline-end calc | 2 |
| `80px`, `48px`, `16px`, `2px` | mask gradient stops | 4 |
| `-24px` | translate3d offset | 2 |
| `2px solid transparent` | scroll border | 1 |
| `0` | reset | ~8 |

**Hardcoded 총계**: ~47개 선언

#### Variant 축

| 축 | 값 | 메커니즘 |
|----|-----|----------|
| **size** | `xs`, `sm`, default, `lg` | className (`--modal-container--xs` 등) |
| **state** | `visible`, `slug`, `decorator` | className + `:has()` |
| **feature flag** | `enable-experimental-focus-wrap-without-sentinels`, `enable-focus-wrap-without-sentinels`, `enable-dialog-element`, `enable-presence` | mixin parameter |

#### Override hooks

- mixin parameter (4개 feature flag)
- `enabled()` feature flag
- `@include breakpoint()` mixin
- `z()` z-index 유틸리티
- className 기반

---

### 1.5 Checkbox (`checkbox/_checkbox.scss`)

**파일 크기**: 15,165B

#### Token 참조

| 분류 | Token | 사용 횟수 |
|------|-------|-----------|
| Global theme | `$icon-primary`, `$icon-inverse`, `$icon-disabled` | 8 |
| Global theme | `$text-primary`, `$text-disabled`, `$text-error` | 4 |
| Global theme | `$focus` | 2 |
| Global theme | `$support-error`, `$support-warning` | 3 |
| Spacing | `$spacing-01`, `$spacing-02`, `$spacing-03`, `$spacing-05` | 6 |
| Skeleton | `$skeleton-background` (via mixin) | 1 |

**Token 참조 총계**: ~24회

#### Hardcoded 값

| 값 | 용도 | 발생 횟수 |
|----|------|-----------|
| `convert.to-rem(6px)` | wrapper margin | 1 |
| `convert.to-rem(3px)` | wrapper last margin | 1 |
| `convert.to-rem(20px)` | label min-height, padding | 2 |
| `convert.to-rem(1px)` | padding | 2 |
| `convert.to-rem(10px)` | label-text padding | 1 |
| `convert.to-rem(16px)` | checkbox box size | 2 |
| `convert.to-rem(2px)` | position, focus | 3 |
| `convert.to-rem(5px)` | check height | 1 |
| `1.5px solid` | checkmark border | 2 |
| `convert.to-rem(9px)` | check width | 1 |
| `convert.to-rem(6.5px)` | check top | 1 |
| `convert.to-rem(7px)` | check left | 1 |
| `convert.to-rem(-3px)` | check margin | 1 |
| `2px solid` | focus outline | 1 |
| `1px` | outline-offset | 1 |
| `convert.to-rem(8px)` | indeterminate width | 1 |
| `convert.to-rem(11px)` | indeterminate top | 1 |
| `2px solid` | indeterminate border | 1 |
| `#000000` | warning icon path fill | 1 |
| `convert.to-rem(100px)` | skeleton width | 1 |
| `convert.to-rem(-1px)` | RTL margin | 1 |
| `1.25rem`, `0.7rem` | hidden input position | 2 |
| `convert.to-rem(-1px)` | decorator margin | 1 |
| `0` | reset | ~5 |

**Hardcoded 총계**: ~36개 선언

#### Variant 축

| 축 | 값 | 메커니즘 |
|----|-----|----------|
| **state** | `checked`, `indeterminate`, `disabled`, `invalid`, `warning`, `readonly`, `skeleton` | className + pseudo-class |
| **layout** | `horizontal`, `inline` | className |
| **decorator** | `ai-label`, `slug` | className |

#### Override hooks

- className 기반
- `@include high-contrast-mode` mixin (Windows HCM)
- `@include visually-hidden` mixin
- `@include skeleton` mixin
- RTL `[dir='rtl']` override

---

### 1.6 Tag (`tag/_tag.scss` + `_tokens.scss`)

**파일 크기**: _tag.scss 11,158B / _tokens.scss 25,200B

#### Token 참조

| 분류 | Token | 사용 횟수 |
|------|-------|-----------|
| **Component token** (40개 정의) | `$tag-background-{color}` ×10 | 10 |
| Component token | `$tag-color-{color}` ×10 | 10 |
| Component token | `$tag-hover-{color}` ×10 | 10 |
| Component token | `$tag-border-{color}` ×10 | 10 |
| Global theme | `$focus`, `$focus-inverse` | 4 |
| Global theme | `$border-inverse`, `$border-disabled` | 3 |
| Global theme | `$layer`, `$layer-hover`, `$layer-selected-inverse` | 5 |
| Global theme | `$text-primary`, `$text-inverse`, `$text-disabled` | 5 |
| Global theme | `$background`, `$background-inverse`, `$background-inverse-hover` | 4 |
| Global theme | `$icon-disabled` | 1 |
| Spacing | `$spacing-02`, `$spacing-03`, `$spacing-04` | 7 |
| Motion | `$duration-fast-01` | 3 |
| Skeleton | `$skeleton-background` | 1 |
| Layout | `layout.size('height')` | 3 |

**Token 참조 총계**: ~76회 (component token 40개 정의 포함)

#### Hardcoded 값

| 값 | 용도 | 발생 횟수 |
|----|------|-----------|
| `convert.to-rem(18px)` | xs/sm height | 2 |
| `convert.to-rem(24px)` | md height | 1 |
| `convert.to-rem(32px)` | lg height / min-width | 2 |
| `convert.to-rem(16px)` | border-radius / icon size | 3 |
| `convert.to-rem(208px)` | max-inline-size | 1 |
| `convert.to-rem(2px)` | close margin | 1 |
| `convert.to-rem(5px)` | sm close margin | 1 |
| `convert.to-rem(60px)` | skeleton width | 1 |
| `convert.to-rem(1px)` | ai-label margin | 1 |
| `convert.to-rem(32.14px)` | decorator min-width | 1 |
| `1rem` | decorator height | 1 |
| `50%` | border-radius | 2 |
| `1px solid` | border | 2 |
| `2px solid` | outline | 1 |
| `1px` | outline-offset | 2 |
| `99999` | z-index (close focus) | 1 |
| `convert.to-rem(176px)`~`convert.to-rem(200px)` | tooltip max-widths | 5 |
| `0` | reset | ~8 |

**Hardcoded 총계**: ~36개 선언

#### Variant 축

| 축 | 값 | 메커니즘 |
|----|-----|----------|
| **color** | `red`, `magenta`, `purple`, `blue`, `cyan`, `teal`, `green`, `gray`, `cool-gray`, `warm-gray`, `high-contrast` | className + `@include tag-theme()` |
| **size** | `sm`, `md`(default), `lg` | `layout.use('size')` + `layout.redefine-tokens()` |
| **type** | `filter`, `selectable`, `operational`, `interactive`, `outline`, `disabled` | className |
| **decorator** | `ai-label`, `slug` | className |

#### Override hooks

- `!default` on 40개 component token
- `$tag-tokens` Sass map
- `@include tag-theme()` mixin (bg, text, hover, border)
- `layout.redefine-tokens()` → size별 height 재정의
- `@include high-contrast-mode()` mixin

---

### 1.7 InlineNotification (`notification/_inline-notification.scss` + `_tokens.scss`)

**파일 크기**: _inline-notification.scss 10,102B / _tokens.scss 9,632B

#### Token 참조

| 분류 | Token | 사용 횟수 |
|------|-------|-----------|
| **Component token** (10개 정의) | `$notification-background-{error,success,info,warning}` | 4 |
| Component token | `$notification-action-hover` | 1 |
| Component token | `$notification-action-tertiary-inverse*` (5개) | 5 (tokens file) |
| Global theme | `$text-inverse`, `$text-primary` | 3 |
| Global theme | `$support-error`, `$support-success`, `$support-info`, `$support-warning` | 4 |
| Global theme | `$support-error-inverse`, `$support-success-inverse`, `$support-info-inverse`, `$support-warning-inverse` | 4 |
| Global theme | `$background-inverse`, `$background-inverse-hover` | 4 |
| Global theme | `$link-inverse` | 3 |
| Global theme | `$icon-primary`, `$icon-inverse` | 3 |
| Global theme | `$focus`, `$focus-inverse` | 4 |
| Global theme | `$black-100` | 1 |
| Spacing | `$spacing-02`, `$spacing-03`, `$spacing-05`, `$spacing-08`, `$spacing-09` | 7 |
| Motion | `$duration-fast-02` | 2 |

**Token 참조 총계**: ~45회

#### Hardcoded 값

| 값 | 용도 | 발생 횟수 |
|----|------|-----------|
| `convert.to-rem(288px)` | max/min-inline-size | 2 |
| `convert.to-rem(48px)` | min-height, close button | 3 |
| `convert.to-rem(608px)` | md max-width | 1 |
| `convert.to-rem(736px)` | lg max-width | 1 |
| `convert.to-rem(832px)` | max max-width | 1 |
| `1px` | border-width | 1 |
| `0.4` | filter opacity | 1 |
| `convert.to-rem(13px)` | details margin | 2 |
| `convert.to-rem(14px)` | icon margin | 1 |
| `convert.to-rem(15px)` | text-wrapper padding | 1 |
| `convert.to-rem(32px)` | action button height | 1 |
| `2px solid` | focus outline | 2 |
| `-2px` | outline-offset | 2 |
| `1px solid` | link focus outline | 1 |
| `0` | reset | ~8 |

**Hardcoded 총계**: ~28개 선언

#### Variant 축

| 축 | 값 | 메커니즘 |
|----|-----|----------|
| **kind** | `error`, `success`, `info`, `info-square`, `warning`, `warning-alt` | className + `@include notification--experimental()` |
| **contrast** | default, `low-contrast` | className |
| **state** | `hide-close-button` | className |

#### Override hooks

- `!default` on 10개 component token
- `$notification-tokens` Sass map
- `@include notification--experimental()` mixin
- `@include breakpoint()` mixin
- `@include high-contrast-mode()` mixin

---

### 1.8 Tabs (`tabs/_tabs.scss`)

**파일 크기**: 23,129B

#### Token 참조

| 분류 | Token | 사용 횟수 |
|------|-------|-----------|
| Global theme | `$text-primary`, `$text-secondary`, `$text-on-color-disabled` | 8 |
| Global theme | `$layer`, `$layer-01`, `$layer-hover`, `$layer-accent`, `$layer-accent-hover`, `$layer-accent-active` | 14 |
| Global theme | `$background`, `$background-hover`, `$background-active` | 5 |
| Global theme | `$border-subtle`, `$border-strong`, `$border-interactive` | 10 |
| Global theme | `$icon-primary`, `$icon-disabled` | 5 |
| Global theme | `$focus` | 2 |
| Component var | `$tab-underline-color`, `$tab-underline-color-hover`, `$tab-text-disabled` (from `vars`) | 5 |
| Cross-component | `button.$button-disabled` | 1 |
| Spacing | `$spacing-02`~`$spacing-10` | 12 |
| Motion | `$duration-fast-01` | 8 |
| Skeleton | `$skeleton-element` | 1 |
| Layout | `layout.size('height')`, `layout.density('padding-inline')` | 8 |
| Custom prop | `custom-property.get-var('layout-size-height-xl')` | 1 |

**Token 참조 총계**: ~80회

#### Hardcoded 값

| 값 | 용도 | 발생 횟수 |
|----|------|-----------|
| `convert.to-rem(1px)` | margin, border | 5 |
| `convert.to-rem(3px)` | overflow indicator width | 2 |
| `convert.to-rem(24px)` | close icon size | 2 |
| `convert.to-rem(16px)` | close icon svg | 2 |
| `convert.to-rem(14px)` | skeleton height | 1 |
| `convert.to-rem(48px)` | contained line-height calc | 2 |
| `2px solid` | selected border | 3 |
| `1px solid` | various borders | 4 |
| `3px 0 0 0` | vertical box-shadow | 3 |
| `rgba(255, 255, 255, 0)` | gradient transparent | 6 |
| `10rem` | skeleton width | 1 |
| `100%` | widths | 4 |
| `-2px` | icon margin | 1 |
| `0` | reset | ~10 |

**Hardcoded 총계**: ~46개 선언

#### Variant 축

| 축 | 값 | 메커니즘 |
|----|-----|----------|
| **type** | default, `contained`, `vertical` | className |
| **size** | `sm`, `md`(default), `lg`, `xl` | `layout.use('size')` |
| **density** | `normal`(default) | `layout.use('density')` |
| **state** | `selected`, `disabled`, `dismissable`, `full-width` | className |
| **icon** | `icon-only`, `icon-left` | className |

#### Override hooks

- `layout.use('size')` / `layout.use('density')`
- `custom-property.get-var()` → CSS custom property 직접 참조
- `$tab-underline-color` 등 vars 파일 변수
- `@include high-contrast-mode()` mixin
- className 기반

---

### 1.9 DataTable (`data-table/_data-table.scss`)

**파일 크기**: 36,892B (10개 컴포넌트 중 최대)

#### Token 참조

| 분류 | Token | 사용 횟수 |
|------|-------|-----------|
| Global theme | `$layer`, `$layer-accent`, `$layer-hover`, `$layer-active`, `$layer-selected`, `$layer-selected-hover` | 22 |
| Global theme | `$border-subtle-01`, `$border-subtle-02`, `$border-subtle-03`, `$border-subtle-selected`, `$border-subtle` | 10 |
| Global theme | `$text-primary`, `$text-secondary`, `$text-disabled` | 6 |
| Global theme | `$link-secondary` | 2 |
| Global theme | `$field-02` | 1 |
| Component token | `$data-table-column-hover` | 3 |
| AI token | `$ai-border-end`, `$ai-border-start`, `$ai-border-strong` | 3 |
| AI token | `$ai-aura-start-sm`, `$ai-aura-end` | 1 |
| Spacing | `$spacing-01`, `$spacing-03`, `$spacing-04`, `$spacing-05`, `$spacing-06`, `$spacing-09` | 14 |
| Motion | `$duration-fast-01` | 4 |
| Skeleton | `$skeleton-element` (via mixin) | 1 |

**Token 참조 총계**: ~67회

#### Hardcoded 값

| 값 | 용도 | 발생 횟수 |
|----|------|-----------|
| `1px` | AI container padding | 1 |
| `100%` | widths | 5 |
| `50ch`, `80ch` | description max-width | 2 |
| `convert.to-rem(24px)` | xs row height | 3 |
| `convert.to-rem(32px)` | sm row height / expand | 5 |
| `convert.to-rem(40px)` | md row height | 2 |
| `convert.to-rem(64px)` | xl row height | 3 |
| `convert.to-rem(2px)`~`convert.to-rem(7px)` | size별 padding | 12 |
| `convert.to-rem(13px)` | checkbox padding | 2 |
| `convert.to-rem(4px)`~`convert.to-rem(8px)` | expand padding | 4 |
| `convert.to-rem(10px)`, `convert.to-rem(22px)` | xl expand padding | 2 |
| `convert.to-rem(36px)` | sticky checkbox | 2 |
| `convert.to-rem(48px)` | sticky expand / radio | 3 |
| `convert.to-rem(14px)` | sticky padding | 1 |
| `convert.to-rem(15px)` | sticky header label | 1 |
| `convert.to-rem(-2px)` | radio margin | 1 |
| `convert.to-rem(-3px)` | checkbox margin | 1 |
| `48px` | radio column width | 1 |
| `2.5rem` | min-inline-size | 1 |
| `1rem`, `0.5rem` | padding | 4 |
| `2.25rem` | max-inline-size | 1 |
| `3rem` | min-block-size | 2 |
| `1px solid` | borders | 12 |
| `0` | reset | ~10 |

**Hardcoded 총계**: ~84개 선언 (10개 중 최다)

#### Variant 축

| 축 | 값 | 메커니즘 |
|----|-----|----------|
| **size** | `xs`, `sm`, `md`(default), `lg`, `xl` | className |
| **style** | `zebra`, `static`, `sticky-header` | className |
| **state** | `selected`, `expandable`, `ai-enabled` | className + data attribute |
| **alignment** | `top-aligned-body`, `top-aligned-header` | className |
| **column type** | `checkbox`, `radio`, `menu`, `expand`, `slug/decorator` | className |

#### Override hooks

- `$data-table-column-hover` component token (`!default`)
- `@include sticky-header($max-width)` mixin parameter
- `@include ai-table-gradient()` mixin
- `@include breakpoint()` mixin
- `@include high-contrast-mode()` mixin
- className + `[data-child-row]` data attribute

---

### 1.10 Select (`select/_select.scss`)

**파일 크기**: 12,027B

#### Token 참조

| 분류 | Token | 사용 횟수 |
|------|-------|-----------|
| Global theme | `$field`, `$field-02`, `$field-hover` | 7 |
| Global theme | `$border-strong`, `$border-subtle`, `$border-subtle-01` | 5 |
| Global theme | `$text-primary`, `$text-disabled` | 7 |
| Global theme | `$icon-primary`, `$icon-disabled` | 4 |
| Global theme | `$support-error`, `$support-warning` | 3 |
| Global theme | `$background` | 3 |
| Global theme | `$layer-hover` | 1 |
| Global theme | `$black-100` | 1 |
| Spacing | `$spacing-03`~`$spacing-12` | 14 |
| Motion | `$duration-fast-01` | 1 |
| Layout | `layout.size('height')`, `layout.density('padding-inline')` | 3 |

**Token 참조 총계**: ~49회

#### Hardcoded 값

| 값 | 용도 | 발생 횟수 |
|----|------|-----------|
| `1px solid` | border | 2 |
| `100%` | widths | 3 |
| `convert.to-rem(56px)` | inline invalid padding | 1 |
| `convert.to-rem(16px)` | divider height | 1 |
| `convert.to-rem(1px)` | divider width | 1 |
| `convert.to-rem(0.5px)` | margin | 1 |
| `convert.to-rem(41px)` | revert position | 1 |
| `convert.to-rem(8px)` | revert after | 1 |
| `8px` | calc spacing | 1 |
| `2.5rem` | skeleton height | 1 |
| `0.5rem` | revert before | 1 |
| `#000000` | Firefox text-shadow | 1 |
| `1px` | `$divider-width` variable | 1 |
| `0` | reset | ~10 |

**Hardcoded 총계**: ~26개 선언

#### Variant 축

| 축 | 값 | 메커니즘 |
|----|-----|----------|
| **size** | `xs`, `sm`, `md`(default), `lg` | `layout.use('size')` |
| **density** | `normal`(default) | `layout.use('density')` |
| **state** | `invalid`, `warning`, `disabled`, `light`, `readonly`, `skeleton` | className |
| **layout** | `inline` | className |
| **decorator** | `ai-label`, `slug` | className + `:has()` |

#### Override hooks

- `layout.use()` / `layout.redefine-tokens()`
- `@include focus-outline()` mixin
- `@include ai-gradient` mixin
- `@include skeleton` mixin
- className 기반
- `@-moz-document url-prefix()` Firefox 전용 override

---

## 2. 종합 요약 테이블

| Component | 파일 크기 | CSS 선언(추정) | Token 참조 | Hardcoded 값 | Token 의존율 | Variant 축 수 | Override hooks |
|-----------|-----------|----------------|------------|--------------|-------------|---------------|----------------|
| **Button** | 27.5KB (3파일) | ~120 | ~68 | ~35 | **66%** | 5 (kind/size/density/state/set) | `!default`×15, Sass map, layout.use |
| **TextInput** | 14.4KB | ~95 | ~41 | ~31 | **57%** | 5 (size/density/state/layout/decorator) | layout.use, focus-outline mixin |
| **Tile** | 18.7KB | ~110 | ~56 | ~28 | **67%** | 5 (type/state/density/decorator/flag) | mixin param×3, enabled(), layout.use |
| **Modal** | 16.8KB | ~105 | ~59 | ~47 | **56%** | 3 (size/state/flag) | mixin param×4, breakpoint(), z() |
| **Checkbox** | 15.2KB | ~85 | ~24 | ~36 | **40%** | 3 (state/layout/decorator) | HCM mixin, visually-hidden, RTL |
| **Tag** | 36.4KB (2파일) | ~100 | ~76 | ~36 | **68%** | 4 (color/size/type/decorator) | `!default`×40, Sass map, tag-theme() |
| **Notification** | 19.7KB (2파일) | ~75 | ~45 | ~28 | **62%** | 3 (kind/contrast/state) | `!default`×10, Sass map, breakpoint() |
| **Tabs** | 23.1KB | ~130 | ~80 | ~46 | **63%** | 5 (type/size/density/state/icon) | layout.use, custom-property, vars |
| **DataTable** | 36.9KB | ~190 | ~67 | ~84 | **44%** | 5 (size/style/state/align/column) | sticky-header(), ai-table-gradient() |
| **Select** | 12.0KB | ~80 | ~49 | ~26 | **65%** | 5 (size/density/state/layout/decorator) | layout.use, focus-outline, ai-gradient |

### 핵심 발견

1. **Token 의존율 범위**: 40%(Checkbox) ~ 68%(Tag, Tile)
2. **Checkbox이 가장 낮은 token 의존율**: pseudo-element(`::before`, `::after`)로 체크박스를 직접 그리기 때문에 `convert.to-rem()` hardcoded 값이 불가피
3. **DataTable이 가장 많은 hardcoded 값**: 5개 size variant × row height/padding 조합이 모두 개별 선언
4. **Tag가 가장 많은 component token**: 40개 (10색상 × 4속성)
5. **Button이 가장 구조화된 override 체계**: 15개 component token 모두 `!default` + Sass map

---

## 3. View 1: Component → Token 매핑

### 3.1 Button → Token

```
Button
├── Component tokens (15)
│   ├── $button-primary / -hover / -active
│   ├── $button-secondary / -hover / -active
│   ├── $button-tertiary / -hover / -active
│   ├── $button-danger-primary / -secondary / -hover / -active
│   ├── $button-separator
│   ├── $button-disabled
│   └── $button-focus-color / -outline-width / -border-width / -border-radius
├── Global theme tokens
│   ├── $text-on-color, $text-inverse, $text-disabled, $text-on-color-disabled
│   ├── $link-primary, $link-primary-hover
│   ├── $background, $background-hover, $background-active, $background-selected
│   ├── $icon-primary, $icon-on-color-disabled
│   ├── $focus
│   └── $layer-selected-disabled
├── Spacing: $spacing-02, 03, 05, 07, 10
├── Motion: $duration-fast-01
└── Layout: layout.size('height'), layout.density('padding-inline')
```

### 3.2 TextInput → Token

```
TextInput
├── Global theme tokens
│   ├── $field, $field-02
│   ├── $border-strong, $border-subtle
│   ├── $text-primary, $text-disabled, $text-error
│   ├── $support-error, $support-warning
│   ├── $icon-primary, $icon-disabled
│   └── $black-100
├── Spacing: $spacing-02, 03, 05, 08, 10
├── Motion: $duration-fast-01
└── Layout: layout.size('height'), layout.density('padding-inline')
```

### 3.3 Tile → Token

```
Tile
├── Global theme tokens
│   ├── $layer, $layer-02, $layer-hover, $layer-selected-inverse
│   ├── $text-primary, $text-disabled
│   ├── $border-tile, $border-disabled, $border-inverse
│   ├── $icon-primary, $icon-secondary, $icon-interactive, $icon-disabled
│   ├── $focus
│   └── $ai-inner-shadow, $ai-drop-shadow
├── Spacing: $spacing-03, 05, 08
├── Motion: $duration-fast-02, $duration-moderate-01
└── Layout: layout.density('padding-inline')
```

### 3.4 Modal → Token

```
Modal
├── Global theme tokens
│   ├── $overlay, $layer, $layer-hover
│   ├── $border-subtle-01
│   ├── $text-primary, $text-secondary
│   ├── $focus, $icon-primary
│   └── $ai-overlay, $ai-inner-shadow, $ai-drop-shadow
├── Spacing: $spacing-02 ~ $spacing-09
├── Motion: $duration-fast-02, $duration-moderate-02
├── Z-index: z('modal')
└── Breakpoint: breakpoint(md/lg/xlg)
```

### 3.5 Checkbox → Token

```
Checkbox
├── Global theme tokens
│   ├── $icon-primary, $icon-inverse, $icon-disabled
│   ├── $text-primary, $text-disabled, $text-error
│   ├── $focus
│   └── $support-error, $support-warning
├── Spacing: $spacing-01, 02, 03, 05
└── Skeleton: $skeleton-background (via mixin)
```

### 3.6 Tag → Token

```
Tag
├── Component tokens (40)
│   ├── $tag-background-{red,magenta,purple,blue,cyan,teal,green,gray,cool-gray,warm-gray}
│   ├── $tag-color-{...} ×10
│   ├── $tag-hover-{...} ×10
│   └── $tag-border-{...} ×10
├── Global theme tokens
│   ├── $focus, $focus-inverse
│   ├── $border-inverse, $border-disabled
│   ├── $layer, $layer-hover, $layer-selected-inverse
│   ├── $text-primary, $text-inverse, $text-disabled
│   ├── $background, $background-inverse, $background-inverse-hover
│   └── $icon-disabled
├── Spacing: $spacing-02, 03, 04
├── Motion: $duration-fast-01
├── Skeleton: $skeleton-background
└── Layout: layout.size('height')
```

### 3.7 InlineNotification → Token

```
InlineNotification
├── Component tokens (10)
│   ├── $notification-background-{error,success,info,warning}
│   ├── $notification-action-hover
│   └── $notification-action-tertiary-inverse{,-active,-hover,-text,-text-on-color-disabled}
├── Global theme tokens
│   ├── $text-inverse, $text-primary
│   ├── $support-{error,success,info,warning}{,-inverse}
│   ├── $background-inverse, $background-inverse-hover
│   ├── $link-inverse
│   ├── $icon-primary, $icon-inverse
│   ├── $focus, $focus-inverse
│   └── $black-100
├── Spacing: $spacing-02, 03, 05, 08, 09
└── Motion: $duration-fast-02
```

### 3.8 Tabs → Token

```
Tabs
├── Global theme tokens
│   ├── $text-primary, $text-secondary, $text-on-color-disabled
│   ├── $layer, $layer-01, $layer-hover, $layer-accent{,-hover,-active}
│   ├── $background, $background-hover, $background-active
│   ├── $border-subtle, $border-strong, $border-interactive
│   ├── $icon-primary, $icon-disabled
│   └── $focus
├── Component vars: $tab-underline-color, $tab-underline-color-hover, $tab-text-disabled
├── Cross-component: button.$button-disabled
├── Spacing: $spacing-02 ~ $spacing-10
├── Motion: $duration-fast-01
├── Skeleton: $skeleton-element
├── Layout: layout.size('height'), layout.density('padding-inline')
└── Custom property: custom-property.get-var('layout-size-height-xl')
```

### 3.9 DataTable → Token

```
DataTable
├── Global theme tokens
│   ├── $layer, $layer-accent, $layer-hover, $layer-active, $layer-selected{,-hover}
│   ├── $border-subtle-01, -02, -03, $border-subtle-selected, $border-subtle
│   ├── $text-primary, $text-secondary, $text-disabled
│   ├── $link-secondary
│   └── $field-02
├── Component token: $data-table-column-hover
├── AI tokens: $ai-border-{end,start,strong}, $ai-aura-{start-sm,end}
├── Spacing: $spacing-01, 03, 04, 05, 06, 09
├── Motion: $duration-fast-01
└── Skeleton: $skeleton-element
```

### 3.10 Select → Token

```
Select
├── Global theme tokens
│   ├── $field, $field-02, $field-hover
│   ├── $border-strong, $border-subtle, $border-subtle-01
│   ├── $text-primary, $text-disabled
│   ├── $icon-primary, $icon-disabled
│   ├── $support-error, $support-warning
│   ├── $background, $layer-hover
│   └── $black-100
├── Spacing: $spacing-03 ~ $spacing-12
├── Motion: $duration-fast-01
└── Layout: layout.size('height'), layout.density('padding-inline')
```

---

## 4. View 2: Token → Component 매핑

### 4.1 Global Theme Token 사용처

| Token | 사용 컴포넌트 |
|-------|--------------|
| `$text-primary` | Button, TextInput, Tile, Modal, Checkbox, Tag, Tabs, DataTable, Select **(9/10)** |
| `$text-disabled` | Button, TextInput, Tile, Checkbox, Tag, DataTable, Select **(7/10)** |
| `$text-secondary` | Modal, Tabs, DataTable **(3/10)** |
| `$text-inverse` | Button, Tag, Notification **(3/10)** |
| `$text-on-color` | Button **(1/10)** |
| `$text-on-color-disabled` | Button **(1/10)** |
| `$text-error` | TextInput, Checkbox **(2/10)** |
| `$layer` | Tile, Modal, Tag, Tabs, DataTable, Select **(6/10)** |
| `$layer-hover` | Tile, Modal, Tag, Tabs, DataTable, Select **(6/10)** |
| `$layer-accent` | Tabs, DataTable **(2/10)** |
| `$layer-selected` | DataTable **(1/10)** |
| `$layer-01` | Tabs **(1/10)** |
| `$layer-02` | Tile **(1/10)** |
| `$field` | TextInput, Select **(2/10)** |
| `$field-02` | TextInput, DataTable, Select **(3/10)** |
| `$field-hover` | Select **(1/10)** |
| `$background` | Button, Tabs, Select **(3/10)** |
| `$background-hover` | Button, Tabs **(2/10)** |
| `$background-active` | Button, Tabs **(2/10)** |
| `$background-inverse` | Tag, Notification **(2/10)** |
| `$overlay` | Modal **(1/10)** |
| `$focus` | Button, Tile, Modal, Checkbox, Tag, Notification, Tabs **(7/10)** |
| `$focus-inverse` | Tag, Notification **(2/10)** |
| `$border-strong` | TextInput, Tabs, Select **(3/10)** |
| `$border-subtle` | TextInput, Modal, Tabs, DataTable, Select **(5/10)** |
| `$border-subtle-01` | Modal, DataTable, Select **(3/10)** |
| `$border-interactive` | Tabs **(1/10)** |
| `$border-inverse` | Tag **(1/10)** |
| `$border-disabled` | Tile, Tag **(2/10)** |
| `$border-tile` | Tile **(1/10)** |
| `$icon-primary` | Button, TextInput, Tile, Modal, Checkbox, Tabs, Select **(7/10)** |
| `$icon-disabled` | TextInput, Tile, Checkbox, Tag, Tabs, Select **(6/10)** |
| `$icon-inverse` | Checkbox, Notification **(2/10)** |
| `$icon-secondary` | Tile **(1/10)** |
| `$icon-interactive` | Tile **(1/10)** |
| `$icon-on-color-disabled` | Button **(1/10)** |
| `$support-error` | TextInput, Checkbox, Notification, Select **(4/10)** |
| `$support-warning` | TextInput, Checkbox, Notification, Select **(4/10)** |
| `$support-success` | Notification **(1/10)** |
| `$support-info` | Notification **(1/10)** |
| `$link-primary` | Button **(1/10)** |
| `$link-primary-hover` | Button **(1/10)** |
| `$link-inverse` | Notification **(1/10)** |
| `$link-secondary` | DataTable **(1/10)** |
| `$black-100` | TextInput, Checkbox, Notification, Select **(4/10)** |

### 4.2 Spacing Token 사용처

| Token | 사용 컴포넌트 |
|-------|--------------|
| `$spacing-01` | Checkbox, DataTable **(2/10)** |
| `$spacing-02` | Button, TextInput, Tag, Notification, Tabs, Checkbox **(6/10)** |
| `$spacing-03` | Button, TextInput, Tile, Tag, Checkbox, Notification, Tabs, DataTable, Select **(9/10)** |
| `$spacing-04` | Tag, DataTable **(2/10)** |
| `$spacing-05` | Button, TextInput, Tile, Modal, Checkbox, Notification, Tabs, DataTable, Select **(9/10)** |
| `$spacing-06` | Modal, DataTable **(2/10)** |
| `$spacing-07` | Button, Modal **(2/10)** |
| `$spacing-08` | TextInput, Tile, Tag, Notification, Tabs, Select **(6/10)** |
| `$spacing-09` | Modal, Notification, Tabs, DataTable **(4/10)** |
| `$spacing-10` | TextInput, Button, Select **(3/10)** |
| `$spacing-11` | Select **(1/10)** |
| `$spacing-12` | Select **(1/10)** |

### 4.3 Motion Token 사용처

| Token | 사용 컴포넌트 |
|-------|--------------|
| `$duration-fast-01` | Button, TextInput, Tabs, DataTable, Select, Tag **(6/10)** |
| `$duration-fast-02` | Tile, Modal, Notification **(3/10)** |
| `$duration-moderate-01` | Tile **(1/10)** |
| `$duration-moderate-02` | Modal **(1/10)** |

### 4.4 Layout Token 사용처

| Token/함수 | 사용 컴포넌트 |
|------------|--------------|
| `layout.use('size')` | Button, TextInput, Tag, Tabs, Select **(5/10)** |
| `layout.use('density')` | Button, TextInput, Tile, Tabs, Select **(5/10)** |
| `layout.size('height')` | Button, TextInput, Tag, Tabs, Select **(5/10)** |
| `layout.density('padding-inline')` | Button, TextInput, Tile, Tabs, Select **(5/10)** |
| `layout.redefine-tokens()` | Tag **(1/10)** |

### 4.5 Component Token 보유 현황

| Component | Component Token 수 | `!default` 여부 | Sass Map |
|-----------|-------------------|-----------------|----------|
| Button | 15 | ✅ 전부 | `$button-tokens` |
| Tag | 40 | ✅ 전부 | `$tag-tokens` |
| Notification | 10 | ✅ 전부 | `$notification-tokens` |
| DataTable | 1 (`$data-table-column-hover`) | ✅ | — |
| TextInput | 0 | — | — |
| Tile | 0 | — | — |
| Modal | 0 | — | — |
| Checkbox | 0 | — | — |
| Tabs | 0 (vars 파일에 3개) | — | — |
| Select | 0 | — | — |

---

## 5. Hardcoded 값 인벤토리

### 5.1 카테고리별 분류

#### A. `convert.to-rem()` 래핑된 px 값 (의도적 디자인 결정)

이 값들은 Carbon의 `convert.to-rem()` 유틸리티를 통해 rem으로 변환되지만, **token을 경유하지 않는 raw px 값**이다.

| 컴포넌트 | 주요 hardcoded px 값 | 용도 |
|----------|---------------------|------|
| Button | 176px, 232px, 196px, 320px, 150px, 16px, 20px, 1px | fluid layout, icon, skeleton |
| TextInput | 16px, 13px, 32px, 64px, 80px, 142px, 200px, 2px | fluid layout, positioning |
| Tile | 20px, 12px | icon size/position |
| Modal | 64px, 12px, 20px, 10px, 48px | footer, close button, decorator |
| Checkbox | 6px, 3px, 20px, 16px, 10px, 5px, 9px, 6.5px, 7px, 8px, 11px, 100px, 1px, 2px | 체크박스 geometry 전체 |
| Tag | 18px, 24px, 32px, 16px, 208px, 2px, 5px, 60px, 1px, 32.14px, 176px~200px | size, icon, skeleton, tooltip |
| Notification | 288px, 48px, 608px, 736px, 832px, 13px, 14px, 15px, 32px | responsive width, spacing |
| Tabs | 1px, 3px, 24px, 16px, 14px, 48px | border, icon, skeleton |
| DataTable | 24px, 32px, 40px, 64px, 2px~15px, 36px, 48px, 13px, 14px, 22px, 10px | size별 row height/padding |
| Select | 56px, 16px, 1px, 0.5px, 41px, 8px | divider, decorator position |

#### B. Raw 단위 값 (rem, %, vh/vw, deg)

| 값 | 컴포넌트 | 용도 |
|----|----------|------|
| `4rem`, `8rem` | Tile | min size |
| `3rem` | Modal, DataTable | close button, min height |
| `2.5rem` | Select, DataTable | skeleton, min-width |
| `1.5rem` | TextInput | password padding |
| `1.475rem` | Modal | decorator position |
| `1.25rem`, `0.7rem` | Checkbox | hidden input position |
| `1rem` | Tile, Tag, Modal, DataTable | various |
| `0.5rem` | DataTable, Select | padding |
| `100vh`, `100vw` | Modal | viewport overlay |
| `50vh` | Modal | header max-height |
| `180deg` | Tile | chevron rotation |
| `100%` | 모든 컴포넌트 | width/height |
| `50%` | Button, TextInput | flex-basis, translateY |
| `84%`, `60%`, `48%`, `32%`, `24%`, `42%`, `72%`, `96%`, `36%` | Modal | breakpoint별 width |
| `20%` | Modal | padding calc |
| `25%` | Button | flex |
| `50ch`, `80ch` | DataTable | description max-width |
| `10rem` | Tabs | skeleton width |

#### C. Raw 숫자 값

| 값 | 컴포넌트 | 용도 |
|----|----------|------|
| `0` | 모든 컴포넌트 | reset (margin, padding, border) |
| `1` | 여러 컴포넌트 | opacity, z-index, flex |
| `2` | Checkbox, Tag, Tabs | outline width, z-index |
| `-1px`, `-2px`, `-3px` | 여러 컴포넌트 | outline-offset, margin 보정 |
| `400` | TextInput | font-weight |
| `99999` | Tag | z-index (close focus) |
| `0.4` | Notification | filter opacity |

#### D. Raw 색상 값

| 값 | 컴포넌트 | 용도 |
|----|----------|------|
| `#000000` | Checkbox, Select | warning icon path, Firefox text-shadow |
| `rgba(255, 255, 255, 0)` | Tabs | gradient transparent stop |
| `transparent` | 모든 컴포넌트 | border, background, outline |
| `currentColor` | Button, Tag | icon fill |
| `ButtonText`, `SelectedItem`, `SelectedItemText`, `ButtonBorder`, `GrayText` | Checkbox, Tabs, Select | Windows HCM system color |

### 5.2 Hardcoded 값 심각도 평가

| 심각도 | 설명 | 해당 항목 |
|--------|------|-----------|
| 🔴 **높음** | Token으로 대체 가능하지만 raw 값 사용 | Checkbox geometry (16px, 9px, 5px 등), Modal breakpoint widths (84%, 60% 등), DataTable size별 row heights |
| 🟡 **중간** | 디자인 시스템 차원의 결정이나 token화되지 않음 | Button fluid layout (176px, 232px), Notification responsive widths (288px~832px), Tag max-widths |
| 🟢 **낮음** | 기술적으로 불가피하거나 관례적 | `0` reset, `100%` width, `transparent`, `currentColor`, HCM system colors, `convert.to-rem(1px)` border 보정 |

---

## 6. Override 메커니즘 종합

### 6.1 Override 경로별 분류

| Override 경로 | 사용 컴포넌트 | 설명 |
|--------------|--------------|------|
| **`!default` component token** | Button(15), Tag(40), Notification(10), DataTable(1) | Sass `@use ... with ()` 구문으로 override |
| **Sass map 일괄 override** | Button, Tag, Notification | `$button-tokens`, `$tag-tokens`, `$notification-tokens` |
| **`layout.use()` / `layout.redefine-tokens()`** | Button, TextInput, Tile, Tag, Tabs, Select | CSS custom property 기반 동적 size/density |
| **mixin parameter** | Tile(3), Modal(4), DataTable(1) | `@include tile($enable-experimental-tile-contrast: true)` |
| **`enabled()` feature flag** | Tile, Modal | 런타임 feature flag 체크 |
| **className override** | 모든 컴포넌트 | `.cds--btn--primary` 등 BEM 스타일 |
| **`@include breakpoint()`** | Modal, Notification, DataTable, Tabs | 반응형 breakpoint |
| **`@include high-contrast-mode()`** | Button, Checkbox, Tag, Notification, Tabs, DataTable | Windows HCM 대응 |
| **`[dir='rtl']` selector** | Button, Checkbox | RTL 레이아웃 override |
| **`@-moz-document url-prefix()`** | Select, DataTable | Firefox 전용 override |
| **`@supports` query** | Tile, Tabs, DataTable | Safari/FF 전용 override |
| **CSS custom property 직접 참조** | Tabs | `custom-property.get-var('layout-size-height-xl')` |
| **cross-component token 참조** | Tabs | `button.$button-disabled` |

### 6.2 Token override 용이성 평가

| 등급 | 컴포넌트 | 이유 |
|------|----------|------|
| ⭐⭐⭐ **최상** | Button, Tag | 모든 색상 token이 `!default` + Sass map, `layout.use()`로 size도 동적 |
| ⭐⭐ **양호** | Notification, Select, TextInput | component token 또는 `layout.use()` 보유 |
| ⭐ **보통** | Tile, Modal, Tabs | mixin parameter/feature flag 있으나 색상 token override 제한적 |
| ☆ **제한적** | Checkbox, DataTable | component token 거의 없음, hardcoded geometry 다수 |

---

## 7. Figma↔Code 매핑 관점에서의 시사점

### 7.1 Carbon의 강점

1. **Component token 체계**: Button(15개), Tag(40개), Notification(10개)은 Figma의 component-level token과 1:1 매핑 가능
2. **`layout.use()` 추상화**: size/density가 CSS custom property로 동작 → Figma의 variant property와 구조적 유사
3. **`!default` + Sass map**: 테마 레벨에서 일괄 override 가능 → Figma의 theme switching과 대응
4. **BEM className**: `.cds--btn--primary` 등 명확한 naming → Figma component name과 매핑 용이

### 7.2 Carbon의 약점

1. **Checkbox의 pseudo-element geometry**: 16px, 9px, 5px, 6.5px 등 Figma에서 추출 가능한 값이 token 없이 SCSS에 직접 기술
2. **DataTable의 size variant**: 5개 size × row height/padding이 모두 개별 `convert.to-rem()` 선언 → Figma의 size variant와 1:1 매핑은 가능하나 token 경유 아님
3. **Modal의 responsive width**: `84%`, `60%`, `48%` 등 breakpoint별 width가 hardcoded → Figma에는 없는 CSS 전용 값
4. **Windows HCM system colors**: `ButtonText`, `SelectedItem` 등 플랫폼 전용 값 → Figma 매핑 불가
5. **`convert.to-rem(1px)` border 보정**: -1px 보정이 여러 컴포넌트에 산재 → Figma에서는 표현되지 않는 구현 디테일

### 7.3 Token 의존율 해석

| 의존율 범위 | 해석 | 해당 컴포넌트 |
|------------|------|--------------|
| 65%~68% | **높은 token화** — 대부분의 시각적 속성이 token 경유 | Tag(68%), Tile(67%), Button(66%), Select(65%) |
| 56%~63% | **중간 token화** — 색상은 token, geometry는 hardcoded 혼재 | Tabs(63%), Notification(62%), TextInput(57%), Modal(56%) |
| 40%~44% | **낮은 token화** — 구조적 geometry가 hardcoded | DataTable(44%), Checkbox(40%) |

---

## 8. 부록: 감사 방법론

### 데이터 소스

| 파일 | GitHub 경로 | 크기 |
|------|------------|------|
| button/_button.scss | `packages/styles/scss/components/button/_button.scss` | 13,184B |
| button/_mixins.scss | `packages/styles/scss/components/button/_mixins.scss` | 4,103B |
| button/_tokens.scss | `packages/styles/scss/components/button/_tokens.scss` | 10,224B |
| text-input/_text-input.scss | `packages/styles/scss/components/text-input/_text-input.scss` | 14,383B |
| tile/_tile.scss | `packages/styles/scss/components/tile/_tile.scss` | 18,691B |
| modal/_modal.scss | `packages/styles/scss/components/modal/_modal.scss` | 16,807B |
| checkbox/_checkbox.scss | `packages/styles/scss/components/checkbox/_checkbox.scss` | 15,165B |
| tag/_tag.scss | `packages/styles/scss/components/tag/_tag.scss` | 11,158B |
| tag/_tokens.scss | `packages/styles/scss/components/tag/_tokens.scss` | 25,200B |
| notification/_inline-notification.scss | `packages/styles/scss/components/notification/_inline-notification.scss` | 10,102B |
| notification/_tokens.scss | `packages/styles/scss/components/notification/_tokens.scss` | 9,632B |
| tabs/_tabs.scss | `packages/styles/scss/components/tabs/_tabs.scss` | 23,129B |
| data-table/_data-table.scss | `packages/styles/scss/components/data-table/_data-table.scss` | 36,892B |
| select/_select.scss | `packages/styles/scss/components/select/_select.scss` | 12,027B |

### 집계 기준

- **Token 참조**: `$variable-name` 형태의 Sass 변수 또는 `layout.size()` / `layout.density()` / `custom-property.get-var()` / `z()` 함수 호출을 통한 token 참조
- **Hardcoded 값**: token 변수를 경유하지 않는 raw px, rem, %, vh/vw, deg, hex, rgb, 숫자 값
- **CSS 선언 수**: 셀렉터 블록 내 property: value 쌍의 추정치 (mixin include, 중첩 셀렉터 포함)
- **Token 의존율**: Token 참조 / (Token 참조 + Hardcoded 값) × 100

> ⚠️ **한계**: mixin 내부(`@include type-style()`, `@include focus-outline()`, `@include skeleton` 등)에서 발생하는 token 참조는 해당 mixin의 구현체에 따라 추가될 수 있으나, 본 감사에서는 컴포넌트 SCSS 파일에 직접 나타난 참조만 집계함.
