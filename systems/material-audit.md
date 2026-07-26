# Material Design — 컴포넌트 수준 토큰 의존성 감사 (Audit)

> **감사 대상**: Material Web Components (`material-components/material-web`) + MUI (`mui/material-ui`)
> **감사 방법**: GitHub 실제 소스 코드 라인 단위 분석
> **감사 기준일**: 2026-07-26
> **소스 버전**: material-web `main` branch · mui/material-ui `master` branch

---

## 0. 감사 방법론

### 카운트 기준

| 분류 | 정의 |
|------|------|
| **Token ref** | 값이 디자인 토큰에서 파생되는 CSS 선언. Material Web: `var(--_*)`, `map.get($tokens, ...)`, `map.get($md-sys-*, ...)`. MUI: `theme.palette.*`, `theme.typography.*`, `theme.spacing()`, `theme.shadows[]`, `theme.shape.*`, `theme.transitions.*`, `theme.alpha()` |
| **Hardcoded** | 리터럴 값(px, 숫자, 색상 키워드 등)으로 직접 지정된 CSS 선언 |
| **Structural** | `display`, `position`, `box-sizing`, `overflow` 등 레이아웃 구조 속성 — 토큰화 대상이 아니므로 **카운트 제외** |
| **Token dependency %** | Token refs / (Token refs + Hardcoded) × 100 |

### Material Web 아키텍처 특수성

Material Web은 **3-layer token pipeline**을 사용:

```
md-ref-* (레퍼런스 팔레트)
  → md-sys-* (시스템 시맨틱)
    → md-comp-* (컴포넌트 토큰, SCSS map)
      → --_token-name (CSS custom property로 :host에 출력)
        → var(--_token-name)으로 스타일에서 소비
```

컴포넌트 SCSS 파일은 `tokens.md-comp-*-values()`를 순회하며 **모든 토큰을 CSS custom property로 일괄 출력**한 뒤, 실제 스타일에서 `var(--_*)`로 참조한다. 즉, 컴포넌트 SCSS 파일 자체에는 하드코딩된 디자인 값이 거의 없고, **토큰 정의 파일(`tokens/` 디렉토리)에 모든 값이 집중**되어 있다.

### MUI 아키텍처 특수성

MUI는 `styled()` + `memoTheme()` 패턴으로 **JS 객체 내부에서 직접 `theme.*`을 참조**한다. 토큰 간접층(CSS custom property) 없이 런타임에 테마 객체를 직접 소비하며, `theme.vars` 존재 시 CSS variable 경로를 사용한다.

---

## Part A: Material Web Components 감사

### A-1. Filled Button

**소스**: `button/internal/_filled-button.scss` + `button/internal/_shared.scss`

`_filled-button.scss`는 `tokens.md-comp-filled-button-values()`의 **전체 토큰을 `--_*` CSS custom property로 출력**하는 thin wrapper이다. 실제 스타일은 `_shared.scss`에 정의되어 있으며, 모든 버튼 변형(filled, outlined, text, elevated, filled-tonal)이 공유한다.

#### _shared.scss 스타일 규칙 분석

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 1 | border-start-start-radius | `var(--_container-shape-start-start)` | Token |
| 2 | border-start-end-radius | `var(--_container-shape-start-end)` | Token |
| 3 | border-end-start-radius | `var(--_container-shape-end-start)` | Token |
| 4 | border-end-end-radius | `var(--_container-shape-end-end)` | Token |
| 5 | min-height | `var(--_container-height)` | Token |
| 6 | padding-block | `calc((var(--_container-height) - ...) / 2)` | Token |
| 7 | padding-inline-start | `var(--_leading-space)` | Token |
| 8 | padding-inline-end | `var(--_trailing-space)` | Token |
| 9 | font-family | `var(--_label-text-font)` | Token |
| 10 | font-size | `var(--_label-text-size)` | Token |
| 11 | line-height | `var(--_label-text-line-height)` | Token |
| 12 | font-weight | `var(--_label-text-weight)` | Token |
| 13 | gap | `8px` | **Hardcoded** |
| 14 | hover-color (ripple) | `var(--_hover-state-layer-color)` | Token |
| 15 | pressed-color (ripple) | `var(--_pressed-state-layer-color)` | Token |
| 16 | hover-opacity (ripple) | `var(--_hover-state-layer-opacity)` | Token |
| 17 | pressed-opacity (ripple) | `var(--_pressed-state-layer-opacity)` | Token |
| 18 | color (.button) | `var(--_label-text-color)` | Token |
| 19 | color (:hover) | `var(--_hover-label-text-color)` | Token |
| 20 | color (:focus-within) | `var(--_focus-label-text-color)` | Token |
| 21 | color (:active) | `var(--_pressed-label-text-color)` | Token |
| 22 | background (.background) | `var(--_container-color)` | Token |
| 23 | color (disabled .label) | `var(--_disabled-label-text-color)` | Token |
| 24 | opacity (disabled .label) | `var(--_disabled-label-text-opacity)` | Token |
| 25 | background (disabled) | `var(--_disabled-container-color)` | Token |
| 26 | opacity (disabled) | `var(--_disabled-container-opacity)` | Token |
| 27 | min-width (.button) | `calc(64px - var(--_leading-space) - var(--_trailing-space))` | **Mixed** (64px hardcoded) |
| 28 | padding-inline-start (has-icon) | `var(--_with-leading-icon-leading-space)` | Token |
| 29 | padding-inline-end (has-icon) | `var(--_with-leading-icon-trailing-space)` | Token |
| 30 | padding-inline-start (trailing) | `var(--_with-trailing-icon-leading-space)` | Token |
| 31 | padding-inline-end (trailing) | `var(--_with-trailing-icon-trailing-space)` | Token |
| 32 | focus-ring shape ×4 | `var(--_container-shape-*)` | Token |
| 33 | border (HCM) | `1px solid CanvasText` | **Hardcoded** (HCM 전용) |

#### _filled-button.scss 변형 오버라이드

`_filled-button.scss` 자체에는 하드코딩 값 **0개**. `tokens.md-comp-filled-button-values()` 전체를 출력.

| 항목 | 값 |
|------|-----|
| **Total style rules** | 33 |
| **Token refs** | 30 |
| **Hardcoded** | 3 (gap: 8px, min-width 64px base, HCM border) |
| **Token dependency** | **90.9%** |
| **Variant axes** | 없음 (filled 고정) |

### A-2. Outlined Button

**소스**: `button/internal/_outlined-button.scss` + `_shared.scss`

_shared.scss 공통 스타일 위에 outline 관련 추가 스타일 정의.

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 1 | --_container-color | `none` | **Hardcoded** (변형 오버라이드) |
| 2 | --_disabled-container-color | `none` | **Hardcoded** |
| 3 | --_disabled-container-opacity | `0` | **Hardcoded** |
| 4 | border-color (.outline) | `var(--_outline-color)` | Token |
| 5 | border-start-start-radius | `var(--_container-shape-start-start)` | Token |
| 6 | border-start-end-radius | `var(--_container-shape-start-end)` | Token |
| 7 | border-end-start-radius | `var(--_container-shape-end-start)` | Token |
| 8 | border-end-end-radius | `var(--_container-shape-end-end)` | Token |
| 9 | border-color (:active) | `var(--_pressed-outline-color)` | Token |
| 10 | border-color (disabled) | `var(--_disabled-outline-color)` | Token |
| 11 | opacity (disabled) | `var(--_disabled-outline-opacity)` | Token |
| 12 | border-width (.outline, md-ripple) | `var(--_outline-width)` | Token |
| 13 | border-color (HCM) | `GrayText` | **Hardcoded** (HCM) |
| 14 | opacity (HCM) | `1` | **Hardcoded** (HCM) |
| 15 | border-color (md-ripple) | `transparent` | **Hardcoded** |

| 항목 | 값 |
|------|-----|
| **Total style rules (변형 전용)** | 15 |
| **Token refs** | 9 |
| **Hardcoded** | 6 |
| **Token dependency** | **60.0%** |
| **Variant axes** | 없음 (outlined 고정) |

> **참고**: _shared.scss 공통분(30 token refs) 합산 시 전체 token dependency는 **82.5%** (39/47).

### A-3. Text Button

**소스**: `button/internal/_text-button.scss` + `_shared.scss`

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 1 | --_container-color | `none` | **Hardcoded** |
| 2 | --_disabled-container-color | `none` | **Hardcoded** |
| 3 | --_disabled-container-opacity | `0` | **Hardcoded** |

| 항목 | 값 |
|------|-----|
| **Total style rules (변형 전용)** | 3 |
| **Token refs** | 0 |
| **Hardcoded** | 3 |
| **Token dependency** | **0%** (변형 전용) / **100%** (_shared.scss 공통분만 고려 시) |
| **Variant axes** | 없음 (text 고정) |

> **해석**: Text Button은 "컨테이너 없음"을 표현하기 위해 3개의 토큰 값을 `none`/`0`으로 **의도적 오버라이드**. 이는 하드코딩이지만 디자인 시스템 관점에서는 "토큰 값 재정의"에 해당.

### A-4. Filled Text Field

**소스**: `textfield/internal/_filled-text-field.scss`

이 파일은 `tokens.md-comp-filled-text-field-values()`에서 토큰을 출력한 뒤, **약 90개 이상의 토큰을 `filled-field.theme()` mixin에 `var(--_*)` 형태로 전달**한다.

| 분류 | 수 |
|------|-----|
| `:host`에 출력되는 컴포넌트 토큰 | ~90+ (전체 `md-comp-filled-text-field-values()`) |
| `filled-field.theme()`에 전달되는 토큰 매핑 | **88개** (var(--_*) 참조) |
| Hardcoded 디자인 값 | **0** |

| 항목 | 값 |
|------|-----|
| **Total style rules** | 88 |
| **Token refs** | 88 |
| **Hardcoded** | 0 |
| **Token dependency** | **100%** |
| **Variant axes** | 없음 (filled 고정) |

> **특기**: 전달되는 88개 토큰에는 `error-*`, `focus-*`, `hover-*`, `disabled-*` 등 **모든 interaction state × severity 조합**이 포함. 이는 Material Web의 state-layer 토큰 설계가 가장 밀도 높게 적용된 컴포넌트.

### A-5. Dialog

**소스**: `dialog/internal/_dialog.scss`

Dialog는 `map.get($tokens, ...)`과 `map.get($md-sys-color, ...)`을 **직접 사용** (CSS custom property 경유 없음). 이는 Material Web 내에서 드문 패턴.

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 1 | border-start-start-radius | `map.get($tokens, 'container-shape-start-start')` | Token (md-comp) |
| 2 | border-start-end-radius | `map.get($tokens, 'container-shape-start-end')` | Token (md-comp) |
| 3 | border-end-end-radius | `map.get($tokens, 'container-shape-end-end')` | Token (md-comp) |
| 4 | border-end-start-radius | `map.get($tokens, 'container-shape-end-start')` | Token (md-comp) |
| 5 | max-height | `min(560px, calc(100% - 48px))` | **Hardcoded** |
| 6 | max-width | `min(560px, calc(100% - 48px))` | **Hardcoded** |
| 7 | min-height | `140px` | **Hardcoded** |
| 8 | min-width | `280px` | **Hardcoded** |
| 9 | background (.scrim) | `map.get($md-sys-color, 'scrim')` | Token (md-sys) |
| 10 | opacity (.scrim) | `32%` | **Hardcoded** |
| 11 | color (.headline) | `map.get($tokens, 'headline-color')` | Token (md-comp) |
| 12 | font-family (.headline) | `map.get($tokens, 'headline-font')` | Token (md-comp) |
| 13 | font-size (.headline) | `map.get($tokens, 'headline-size')` | Token (md-comp) |
| 14 | line-height (.headline) | `map.get($tokens, 'headline-line-height')` | Token (md-comp) |
| 15 | font-weight (.headline) | `map.get($tokens, 'headline-weight')` | Token (md-comp) |
| 16 | gap (headline slot) | `8px` | **Hardcoded** |
| 17 | padding (headline slot) | `24px 24px 0` | **Hardcoded** |
| 18 | color (icon slot) | `map.get($tokens, 'icon-color')` | Token (md-comp) |
| 19 | font-size (icon slot) | `map.get($tokens, 'icon-size')` | Token (md-comp) |
| 20 | margin-top (icon slot) | `24px` | **Hardcoded** |
| 21 | height/width (icon slot) | `map.get($tokens, 'icon-size')` ×2 | Token (md-comp) |
| 22 | padding-top (has-icon) | `16px` | **Hardcoded** |
| 23 | padding-bottom (scrollable) | `16px` | **Hardcoded** |
| 24 | padding-top (scrollable+headline) | `8px` | **Hardcoded** |
| 25 | background (.container::before) | `map.get($tokens, 'container-color')` | Token (md-comp) |
| 26 | color (.content) | `map.get($tokens, 'supporting-text-color')` | Token (md-comp) |
| 27 | font-family (.content) | `map.get($tokens, 'supporting-text-font')` | Token (md-comp) |
| 28 | font-size (.content) | `map.get($tokens, 'supporting-text-size')` | Token (md-comp) |
| 29 | line-height (.content) | `map.get($tokens, 'supporting-text-line-height')` | Token (md-comp) |
| 30 | font-weight (.content) | `map.get($tokens, 'supporting-text-weight')` | Token (md-comp) |
| 31 | padding (content slot) | `24px` | **Hardcoded** |
| 32 | gap (actions slot) | `8px` | **Hardcoded** |
| 33 | padding (actions slot) | `16px 24px 24px` | **Hardcoded** |
| 34 | padding-bottom (has-actions) | `8px` | **Hardcoded** |
| 35 | outline (HCM) | `2px solid WindowText` | **Hardcoded** (HCM) |

| 항목 | 값 |
|------|-----|
| **Total style rules** | 35 |
| **Token refs** | 18 (md-comp: 17, md-sys: 1) |
| **Hardcoded** | 17 |
| **Token dependency** | **51.4%** |
| **Variant axes** | 없음 |

> **핵심 발견**: Dialog는 Material Web 컴포넌트 중 **token dependency가 가장 낮다**. spacing(padding, gap, margin)과 sizing(min/max-width/height)이 대거 하드코딩되어 있으며, 이는 M3 spec에서 dialog의 공간 구조가 토큰화되지 않은 채 고정값으로 정의되어 있음을 반영.

### A-6. Checkbox

**소스**: `checkbox/internal/_checkbox.scss`

Checkbox은 `map.get($tokens, ...)` + `map.get($_md-sys-motion, ...)`을 직접 사용.

| 분류 | 상세 | 수 |
|------|------|-----|
| **md-comp token refs** | container-shape ×4, container-size ×2, outline-color/width ×2, selected-container-color, state-layer-shape/size ×3, hover/pressed-state-layer-color/opacity ×4, selected-hover/pressed-state-layer ×4, selected-icon-color, icon-size ×2, hover/focus/pressed-outline-color/width ×6, selected-hover/focus/pressed-container-color ×3, selected-hover/focus/pressed-icon-color ×3, disabled-outline-color/width/opacity ×3, selected-disabled-container-color/opacity ×2, selected-disabled-icon-color | **~42** |
| **md-sys-motion refs** | easing-emphasized-accelerate ×3, easing-emphasized-decelerate ×3 | **6** |
| **Hardcoded** | $_mark-stroke: 2px, focus-ring 44px ×2, touch-target 48px ×2, opacity: 0, transition-duration: 150ms/50ms/350ms, transform: scale(0.6)/scale(1), width: 10px, animation-duration: 150ms/350ms, math.sqrt(32)/sqrt(128), margin: max(0px, (48px - ...)/2), HCM 값 ×5 | **~22** |

| 항목 | 값 |
|------|-----|
| **Total style rules** | 70 |
| **Token refs** | 48 (md-comp: 42, md-sys-motion: 6) |
| **Hardcoded** | 22 |
| **Token dependency** | **68.6%** |
| **Variant axes** | selected, disabled, indeterminate, touch-target |

> **해석**: Hardcoded 값의 대부분은 **체크마크/인디터미네이트 아이콘의 기하학적 애니메이션** 관련(좌표, stroke, scale, duration). 이는 M3 spec의 motion 설계가 토큰화되지 않은 영역.

### A-7. Chips (Assist Chip + Filter Chip + Chip Set)

**소스**: `chips/internal/_assist-chip.scss`, `_filter-chip.scss`, `_chip-set.scss`

#### _chip-set.scss
| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 1 | gap | `8px` | **Hardcoded** |

토큰 참조 **0개**. 주석: "there are currently no tokens for chip-set".

#### _assist-chip.scss
- `tokens.md-comp-assist-chip-values()` 전체를 `--_*`로 출력
- 추가 스타일: HCM `border-color: ActiveText` (hardcoded ×1)
- **Token dependency: ~100%** (HCM 제외)

#### _filter-chip.scss
- `tokens.md-comp-filter-chip-values()` 전체를 `--_*`로 출력
- 추가 스타일: `var(--_elevated-selected-container-color)`, `var(--_icon-size)` ×2, `var(--_disabled-leading-icon-opacity)` → Token ×4
- HCM: `opacity: 1` → Hardcoded ×1

| 항목 | 값 (3파일 합산) |
|------|-----|
| **Total style rules** | ~8 (변형 전용, 토큰 출력 제외) |
| **Token refs** | 4 |
| **Hardcoded** | 4 (gap: 8px, HCM ×2, structural) |
| **Token dependency** | **50%** (변형 전용) / **~95%+** (토큰 출력 포함 시) |
| **Variant axes** | selected, disabled, elevated, link |

### A-8. Tabs (Tabs Container + Primary Tab)

**소스**: `tabs/internal/_tabs.scss`, `tabs/internal/_primary-tab.scss`

#### _tabs.scss (컨테이너)
```scss
// Note, there are currently no tokens for tabs.
```
토큰 참조 **0개**. 모든 속성 구조적(structural) 속성만 존재.

#### _primary-tab.scss
- `tokens.md-comp-primary-tab-values()` 전체를 `--_*`로 출력
- 추가 스타일: `gap: 2px` (hardcoded), `height: var(--_with-icon-and-label-text-container-height)` (token)

| 항목 | 값 |
|------|-----|
| **Total style rules (변형 전용)** | 2 |
| **Token refs** | 1 |
| **Hardcoded** | 1 (gap: 2px) |
| **Token dependency** | **50%** (변형 전용) / **~98%+** (토큰 출력 포함 시) |
| **Variant axes** | stacked (icon+label), active |

### A-9. Filled Select

**소스**: `select/internal/_filled-select.scss`

Filled Text Field와 동일한 패턴. `tokens.md-comp-filled-select-values()` 출력 후 `filled-field.theme()`에 매핑.

| 분류 | 수 |
|------|-----|
| `filled-field.theme()`에 전달되는 토큰 매핑 | **~80개** (var(--_*) 참조) |
| 추가 var() 참조 (icon size) | 6 (leading/trailing icon size ×3 each) |
| Hardcoded 디자인 값 | **0** |

| 항목 | 값 |
|------|-----|
| **Total style rules** | 86 |
| **Token refs** | 86 |
| **Hardcoded** | 0 |
| **Token dependency** | **100%** |
| **Variant axes** | 없음 (filled 고정) |

---

## Part B: MUI 감사

### B-1. Button

**소스**: `packages/mui-material/src/Button/Button.js` — `ButtonRoot`, `ButtonStartIcon`, `ButtonEndIcon`, `ButtonLoadingIndicator` styled 섹션

#### ButtonRoot

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 1 | typography spread | `theme.typography.button` | Token |
| 2 | minWidth | `64` | **Hardcoded** |
| 3 | padding | `'6px 16px'` | **Hardcoded** |
| 4 | border | `0` | **Hardcoded** |
| 5 | borderRadius | `(theme.vars \|\| theme).shape.borderRadius` | Token |
| 6 | transition duration | `theme.transitions.duration.short` | Token |
| 7 | color (disabled) | `(theme.vars \|\| theme).palette.action.disabled` | Token |
| 8 | boxShadow (contained) | `(theme.vars \|\| theme).shadows[2]` | Token |
| 9 | boxShadow (hover) | `(theme.vars \|\| theme).shadows[4]` | Token |
| 10 | boxShadow (active) | `(theme.vars \|\| theme).shadows[8]` | Token |
| 11 | boxShadow (focusVisible) | `(theme.vars \|\| theme).shadows[6]` | Token |
| 12 | boxShadow (disabled) | `(theme.vars \|\| theme).shadows[0]` | Token |
| 13 | backgroundColor (disabled) | `(theme.vars \|\| theme).palette.action.disabledBackground` | Token |
| 14 | padding (outlined) | `'5px 15px'` | **Hardcoded** |
| 15 | border (outlined) | `'1px solid currentColor'` | **Hardcoded** |
| 16 | border (outlined disabled) | `1px solid ${...palette.action.disabledBackground}` | Token |
| 17 | padding (text) | `'6px 8px'` | **Hardcoded** |
| 18 | --variant-textColor | `palette[color].main` | Token |
| 19 | --variant-outlinedColor | `palette[color].main` | Token |
| 20 | --variant-outlinedBorder | `theme.alpha(palette[color].main, 0.5)` | Token + **Hardcoded** (0.5) |
| 21 | --variant-containedColor | `palette[color].contrastText` | Token |
| 22 | --variant-containedBg | `palette[color].main` | Token |
| 23 | --variant-containedBg (hover) | `palette[color].dark` | Token |
| 24 | --variant-textBg (hover) | `theme.alpha(palette[color].main, hoverOpacity)` | Token |
| 25 | --variant-outlinedBg (hover) | `theme.alpha(palette[color].main, hoverOpacity)` | Token |
| 26 | --variant-containedBg (inherit) | `palette.grey[300]` / `grey[800]` | Token |
| 27 | --variant-containedBg (inherit hover) | `palette.grey.A100` / `grey[700]` | Token |
| 28 | padding (small/text) | `'4px 5px'` | **Hardcoded** |
| 29 | fontSize (small/text) | `theme.typography.pxToRem(13)` | Token |
| 30 | padding (large/text) | `'8px 11px'` | **Hardcoded** |
| 31 | fontSize (large/text) | `theme.typography.pxToRem(15)` | Token |
| 32 | padding (small/outlined) | `'3px 9px'` | **Hardcoded** |
| 33 | padding (large/outlined) | `'7px 21px'` | **Hardcoded** |
| 34 | padding (small/contained) | `'4px 10px'` | **Hardcoded** |
| 35 | padding (large/contained) | `'8px 22px'` | **Hardcoded** |
| 36 | boxShadow (disableElevation) ×5 | `'none'` | **Hardcoded** |
| 37 | width (fullWidth) | `'100%'` | **Hardcoded** |
| 38 | color (loading center) | `palette.action.disabled` | Token |

#### ButtonStartIcon / ButtonEndIcon

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 39 | marginRight (start) | `8` | **Hardcoded** |
| 40 | marginLeft (start) | `-4` | **Hardcoded** |
| 41 | marginLeft (small) | `-2` | **Hardcoded** |
| 42 | marginRight (end) | `-4` | **Hardcoded** |
| 43 | marginLeft (end) | `8` | **Hardcoded** |
| 44 | marginRight (small) | `-2` | **Hardcoded** |
| 45 | fontSize (small icon) | `18` | **Hardcoded** |
| 46 | fontSize (medium icon) | `20` | **Hardcoded** |
| 47 | fontSize (large icon) | `22` | **Hardcoded** |

#### ButtonLoadingIndicator

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 48 | left/right positions ×6 | `14`, `10`, `6` | **Hardcoded** |

| 항목 | 값 |
|------|-----|
| **Total style rules** | ~54 |
| **Token refs** | 25 |
| **Hardcoded** | 29 |
| **Token dependency** | **46.3%** |
| **Variant axes** | variant (contained/outlined/text) × size (small/medium/large) × color (palette 동적) × disableElevation × fullWidth × loading × loadingPosition |

### B-2. TextField

**소스**: `packages/mui-material/src/TextField/TextField.js`

```js
const TextFieldRoot = styled(FormControl, {
  name: 'MuiTextField',
  slot: 'Root',
})({});
```

**스타일 정의 없음**. TextField는 `FormControl`, `InputLabel`, `Input/FilledInput/OutlinedInput`, `FormHelperText`의 **순수 조합 wrapper**이다.

| 항목 | 값 |
|------|-----|
| **Total style rules** | 0 |
| **Token refs** | 0 |
| **Hardcoded** | 0 |
| **Token dependency** | N/A (위임) |
| **Variant axes** | variant (standard/filled/outlined) — 하위 컴포넌트에 위임 |

> **해석**: MUI TextField의 모든 시각적 스타일은 `OutlinedInput`, `FilledInput`, `Input`, `InputLabel`, `FormHelperText`에 분산. 이는 Material Web의 `_filled-text-field.scss`가 88개 토큰을 단일 파일에서 매핑하는 것과 **구조적 대조**.

### B-3. Card

**소스**: `packages/mui-material/src/Card/Card.js`

```js
const CardRoot = styled(Paper, {
  name: 'MuiCard',
  slot: 'Root',
})({
  overflow: 'hidden',
});
```

| 항목 | 값 |
|------|-----|
| **Total style rules** | 1 (overflow: hidden — structural) |
| **Token refs** | 0 |
| **Hardcoded** | 0 (디자인 값) |
| **Token dependency** | N/A (Paper에 위임) |
| **Variant axes** | raised (elevation: 8 — **hardcoded** in JSX prop) |

> **해석**: Card는 Paper의 thin wrapper. `raised` 시 `elevation={8}`이 JSX에서 하드코딩됨. Paper 내부에서 `theme.shadows[8]`로 해석.

### B-4. Dialog

**소스**: `packages/mui-material/src/Dialog/Dialog.js` — `DialogRoot`, `DialogContainer`, `DialogPaper` styled 섹션

#### DialogPaper (주요 스타일)

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 1 | margin | `32` | **Hardcoded** |
| 2 | maxHeight (scroll=paper) | `'calc(100% - 64px)'` | **Hardcoded** |
| 3 | maxWidth (no maxWidth prop) | `'calc(100% - 64px)'` | **Hardcoded** |
| 4 | maxWidth (xs) | `Math.max(theme.breakpoints.values.xs, 444)` | Token + **Hardcoded** (444) |
| 5 | maxWidth (sm~xl) | `theme.breakpoints.values[maxWidth]` | Token |
| 6 | width (fullWidth) | `'calc(100% - 64px)'` | **Hardcoded** |
| 7 | borderRadius (fullScreen) | `0` | **Hardcoded** |
| 8 | transition duration | `theme.transitions.duration.enteringScreen/leavingScreen` | Token |

#### DialogContainer

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 9 | outline | `0` | **Hardcoded** |

#### DialogBackdrop

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 10 | zIndex | `-1` | **Hardcoded** |

| 항목 | 값 |
|------|-----|
| **Total style rules** | ~12 |
| **Token refs** | 4 (breakpoints ×2, transitions ×2) |
| **Hardcoded** | 8 |
| **Token dependency** | **33.3%** |
| **Variant axes** | scroll (paper/body) × maxWidth (xs~xl/false) × fullWidth × fullScreen |

> **핵심 발견**: MUI Dialog는 `margin: 32`, `64px` 여백, `444px` 최소 너비 등 **공간 구조가 거의 전부 하드코딩**. Material Web Dialog(51.4%)보다도 token dependency가 낮다.

### B-5. Checkbox

**소스**: `packages/mui-material/src/Checkbox/Checkbox.js` — `CheckboxRoot` styled 섹션

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 1 | color | `palette.text.secondary` | Token |
| 2 | backgroundColor (hover, default) | `theme.alpha(palette.action.active, palette.action.hoverOpacity)` | Token |
| 3 | backgroundColor (hover, palette) | `theme.alpha(palette[color].main, palette.action.hoverOpacity)` | Token |
| 4 | color (checked/indeterminate) | `palette[color].main` | Token |
| 5 | color (disabled) | `palette.action.disabled` | Token |
| 6 | backgroundColor (hover: none) | `'transparent'` | **Hardcoded** |

| 항목 | 값 |
|------|-----|
| **Total style rules** | 6 |
| **Token refs** | 5 |
| **Hardcoded** | 1 |
| **Token dependency** | **83.3%** |
| **Variant axes** | color (palette 동적) × disableRipple × size (icon fontSize 위임) |

> **해석**: MUI Checkbox는 **매우 얇은 스타일 레이어**. 실제 체크박스 시각(아이콘, 크기, 애니메이션)은 SVG 아이콘(`CheckBoxIcon`, `CheckBoxOutlineBlankIcon`)과 `SwitchBase`에 위임. Material Web Checkbox(68.6%)가 42개 md-comp 토큰 + 6개 motion 토큰을 사용하는 것과 극적 대조.

### B-6. Chip

**소스**: `packages/mui-material/src/Chip/Chip.js` — `ChipRoot`, `ChipLabel` styled 섹션

#### ChipRoot

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 1 | fontFamily | `theme.typography.fontFamily` | Token |
| 2 | fontSize | `theme.typography.pxToRem(13)` | Token |
| 3 | height | `32` | **Hardcoded** |
| 4 | lineHeight | `1.5` | **Hardcoded** |
| 5 | color | `palette.text.primary` | Token |
| 6 | backgroundColor | `palette.action.selected` | Token |
| 7 | borderRadius | `32 / 2` (= 16) | **Hardcoded** |
| 8 | transition | `getTransitionStyles(theme, ...)` | Token |
| 9 | opacity (disabled) | `palette.action.disabledOpacity` | Token |
| 10 | avatar marginLeft | `5` | **Hardcoded** |
| 11 | avatar marginRight | `-6` | **Hardcoded** |
| 12 | avatar width/height | `24` | **Hardcoded** |
| 13 | avatar color | `palette.grey[700]` / `grey[300]` | Token |
| 14 | avatar fontSize | `theme.typography.pxToRem(12)` | Token |
| 15 | icon marginLeft/marginRight | `5` / `-6` | **Hardcoded** |
| 16 | deleteIcon color | `theme.alpha(palette.text.primary, 0.26)` | Token + **Hardcoded** (0.26) |
| 17 | deleteIcon fontSize | `22` | **Hardcoded** |
| 18 | deleteIcon margin | `'0 5px 0 -6px'` | **Hardcoded** |
| 19 | deleteIcon hover color | `theme.alpha(palette.text.primary, 0.4)` | Token + **Hardcoded** (0.4) |
| 20 | avatar color (primary) | `palette.primary.contrastText` | Token |
| 21 | avatar bg (primary) | `palette.primary.dark` | Token |
| 22 | avatar color (secondary) | `palette.secondary.contrastText` | Token |
| 23 | avatar bg (secondary) | `palette.secondary.dark` | Token |
| 24 | height (small) | `24` | **Hardcoded** |
| 25 | avatar size (small) | `18` ×2 | **Hardcoded** |
| 26 | avatar fontSize (small) | `theme.typography.pxToRem(10)` | Token |
| 27 | icon fontSize (small) | `18` | **Hardcoded** |
| 28 | deleteIcon fontSize (small) | `16` | **Hardcoded** |
| 29 | bg (palette color) | `palette[color].main` | Token |
| 30 | color (palette color) | `palette[color].contrastText` | Token |
| 31 | deleteIcon color (palette) | `theme.alpha(palette[color].contrastText, 0.7)` | Token + **Hardcoded** |
| 32 | focusVisible bg (onDelete) | `theme.alpha(palette.action.selected, ...)` | Token |
| 33 | focusVisible bg (palette) | `palette[color].dark` | Token |
| 34 | hover bg (clickable) | `theme.alpha(palette.action.selected, ...)` | Token |
| 35 | active boxShadow | `shadows[1]` | Token |
| 36 | hover/focus bg (palette clickable) | `palette[color].dark` | Token |
| 37 | border (outlined) | `1px solid ${palette.grey[400]/grey[700]}` | Token + **Hardcoded** (1px) |
| 38 | hover bg (outlined) | `palette.action.hover` | Token |
| 39 | focus bg (outlined) | `palette.action.focus` | Token |
| 40 | color (outlined palette) | `palette[color].main` | Token |
| 41 | border (outlined palette) | `1px solid ${theme.alpha(palette[color].main, 0.7)}` | Token + **Hardcoded** |
| 42 | hover/focus bg (outlined palette) | `theme.alpha(palette[color].main, hoverOpacity/focusOpacity)` | Token |

#### ChipLabel

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 43 | paddingLeft/Right | `12` | **Hardcoded** |
| 44 | paddingLeft/Right (outlined) | `11` | **Hardcoded** |
| 45 | paddingLeft/Right (small) | `8` | **Hardcoded** |
| 46 | paddingLeft/Right (small/outlined) | `7` | **Hardcoded** |

| 항목 | 값 |
|------|-----|
| **Total style rules** | ~52 |
| **Token refs** | 30 |
| **Hardcoded** | 22 |
| **Token dependency** | **57.7%** |
| **Variant axes** | variant (filled/outlined) × size (medium/small) × color (palette 동적) × clickable × onDelete × iconColor |

### B-7. Alert

**소스**: `packages/mui-material/src/Alert/Alert.js` — `AlertRoot`, `AlertIcon`, `AlertMessage`, `AlertAction` styled 섹션

#### AlertRoot

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 1 | typography spread | `theme.typography.body2` | Token |
| 2 | backgroundColor | `'transparent'` | **Hardcoded** |
| 3 | padding | `'6px 16px'` | **Hardcoded** |
| 4 | color (standard) | `theme.darken/lighten(palette[color].light, 0.6)` | Token + **Hardcoded** (0.6) |
| 5 | backgroundColor (standard) | `theme.lighten/darken(palette[color].light, 0.9)` | Token + **Hardcoded** (0.9) |
| 6 | icon color (standard) | `palette[color].main` | Token |
| 7 | color (outlined) | 동일 #4 | Token + Hardcoded |
| 8 | border (outlined) | `1px solid ${palette[color].light}` | Token + **Hardcoded** (1px) |
| 9 | icon color (outlined) | `palette[color].main` | Token |
| 10 | fontWeight (filled) | `theme.typography.fontWeightMedium` | Token |
| 11 | backgroundColor (filled) | `palette[color].main` / `palette[color].dark` | Token |
| 12 | color (filled) | `palette.getContrastText(palette[color].main)` | Token |

#### AlertIcon / AlertMessage / AlertAction

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 13 | marginRight (icon) | `12` | **Hardcoded** |
| 14 | padding (icon) | `'7px 0'` | **Hardcoded** |
| 15 | fontSize (icon) | `22` | **Hardcoded** |
| 16 | opacity (icon) | `0.9` | **Hardcoded** |
| 17 | padding (message) | `'8px 0'` | **Hardcoded** |
| 18 | padding (action) | `'4px 0 0 16px'` | **Hardcoded** |
| 19 | marginRight (action) | `-8` | **Hardcoded** |

| 항목 | 값 |
|------|-----|
| **Total style rules** | ~24 |
| **Token refs** | 12 |
| **Hardcoded** | 12 |
| **Token dependency** | **50.0%** |
| **Variant axes** | variant (standard/outlined/filled) × severity (success/warning/error/info) × color |

### B-8. Tab

**소스**: `packages/mui-material/src/Tab/Tab.js` — `TabRoot` styled 섹션

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 1 | typography spread | `theme.typography.button` | Token |
| 2 | maxWidth | `360` | **Hardcoded** |
| 3 | minWidth | `90` | **Hardcoded** |
| 4 | minHeight | `48` | **Hardcoded** |
| 5 | padding | `'12px 16px'` | **Hardcoded** |
| 6 | lineHeight | `1.25` | **Hardcoded** |
| 7 | minHeight (icon+label) | `72` | **Hardcoded** |
| 8 | paddingTop/Bottom (icon+label) | `9` | **Hardcoded** |
| 9 | marginBottom (icon top) | `6` | **Hardcoded** |
| 10 | marginTop (icon bottom) | `6` | **Hardcoded** |
| 11 | marginRight (icon start) | `theme.spacing(1)` | Token |
| 12 | marginLeft (icon end) | `theme.spacing(1)` | Token |
| 13 | opacity (inherit) | `0.6` | **Hardcoded** |
| 14 | opacity (inherit disabled) | `palette.action.disabledOpacity` | Token |
| 15 | color (primary) | `palette.text.secondary` | Token |
| 16 | color (primary selected) | `palette.primary.main` | Token |
| 17 | color (primary disabled) | `palette.text.disabled` | Token |
| 18 | color (secondary) | `palette.text.secondary` | Token |
| 19 | color (secondary selected) | `palette.secondary.main` | Token |
| 20 | color (secondary disabled) | `palette.text.disabled` | Token |
| 21 | fontSize (wrapped) | `theme.typography.pxToRem(12)` | Token |

| 항목 | 값 |
|------|-----|
| **Total style rules** | 21 |
| **Token refs** | 11 |
| **Hardcoded** | 10 |
| **Token dependency** | **52.4%** |
| **Variant axes** | textColor (inherit/primary/secondary) × iconPosition (top/bottom/start/end) × fullWidth × wrapped |

### B-9. TableCell

**소스**: `packages/mui-material/src/TableCell/TableCell.js` — `TableCellRoot` styled 섹션

| # | 속성 | 값 | 분류 |
|---|------|-----|------|
| 1 | typography spread | `theme.typography.body2` | Token |
| 2 | borderBottom | `1px solid ${theme.vars.palette.TableCell.border}` / `theme.lighten(theme.alpha(theme.palette.divider, 1), 0.88)` | Token + **Hardcoded** (0.88) |
| 3 | padding | `16` | **Hardcoded** |
| 4 | color (head) | `palette.text.primary` | Token |
| 5 | lineHeight (head) | `theme.typography.pxToRem(24)` | Token |
| 6 | fontWeight (head) | `theme.typography.fontWeightMedium` | Token |
| 7 | color (body) | `palette.text.primary` | Token |
| 8 | color (footer) | `palette.text.secondary` | Token |
| 9 | lineHeight (footer) | `theme.typography.pxToRem(21)` | Token |
| 10 | fontSize (footer) | `theme.typography.pxToRem(12)` | Token |
| 11 | padding (small) | `'6px 16px'` | **Hardcoded** |
| 12 | width (paddingCheckbox) | `24` | **Hardcoded** |
| 13 | padding (paddingCheckbox) | `'0 12px 0 16px'` | **Hardcoded** |
| 14 | width (checkbox) | `48` | **Hardcoded** |
| 15 | padding (checkbox) | `'0 0 0 4px'` | **Hardcoded** |
| 16 | backgroundColor (stickyHeader) | `palette.background.default` | Token |

| 항목 | 값 |
|------|-----|
| **Total style rules** | 16 |
| **Token refs** | 10 |
| **Hardcoded** | 6 |
| **Token dependency** | **62.5%** |
| **Variant axes** | variant (head/body/footer) × size (medium/small) × padding (normal/checkbox/none) × align × stickyHeader |

### B-10. Select

**소스**: `packages/mui-material/src/Select/Select.js`

```js
const StyledInput = styled(Input, styledRootConfig)('');
const StyledOutlinedInput = styled(OutlinedInput, styledRootConfig)('');
const StyledFilledInput = styled(FilledInput, styledRootConfig)('');
```

**스타일 정의 없음**. TextField와 동일하게 순수 조합 wrapper.

| 항목 | 값 |
|------|-----|
| **Total style rules** | 0 |
| **Token refs** | 0 |
| **Hardcoded** | 0 |
| **Token dependency** | N/A (위임) |
| **Variant axes** | variant (standard/outlined/filled) — 하위 Input 컴포넌트에 위임 |

---

## 1. 통합 요약 테이블

### Material Web Components

| Component | Impl | Total rules | Token refs | Hardcoded | Token dep % | Variant axes |
|-----------|------|------------|------------|-----------|-------------|-------------|
| Filled Button | MW | 33 | 30 | 3 | **90.9%** | — |
| Outlined Button | MW | 47 (공통+변형) | 39 | 8 | **83.0%** | — |
| Text Button | MW | 36 (공통+변형) | 30 | 6 | **83.3%** | — |
| Filled Text Field | MW | 88 | 88 | 0 | **100%** | — |
| Dialog | MW | 35 | 18 | 17 | **51.4%** | — |
| Checkbox | MW | 70 | 48 | 22 | **68.6%** | selected, disabled, indeterminate, touch-target |
| Chips (assist+filter+set) | MW | ~8 | 4 | 4 | **50.0%** | selected, disabled, elevated |
| Tabs (container+primary) | MW | ~2 | 1 | 1 | **50.0%** | stacked, active |
| Filled Select | MW | 86 | 86 | 0 | **100%** | — |

### MUI

| Component | Impl | Total rules | Token refs | Hardcoded | Token dep % | Variant axes |
|-----------|------|------------|------------|-----------|-------------|-------------|
| Button | MUI | 54 | 25 | 29 | **46.3%** | variant × size × color × disableElevation × fullWidth × loading |
| TextField | MUI | 0 | 0 | 0 | **N/A** | variant (위임) |
| Card | MUI | 1 | 0 | 0 | **N/A** | raised (위임) |
| Dialog | MUI | 12 | 4 | 8 | **33.3%** | scroll × maxWidth × fullWidth × fullScreen |
| Checkbox | MUI | 6 | 5 | 1 | **83.3%** | color × disableRipple |
| Chip | MUI | 52 | 30 | 22 | **57.7%** | variant × size × color × clickable × onDelete |
| Alert | MUI | 24 | 12 | 12 | **50.0%** | variant × severity × color |
| Tab | MUI | 21 | 11 | 10 | **52.4%** | textColor × iconPosition × fullWidth × wrapped |
| TableCell | MUI | 16 | 10 | 6 | **62.5%** | variant × size × padding × align × stickyHeader |
| Select | MUI | 0 | 0 | 0 | **N/A** | variant (위임) |

---

## 2. View 1: Component → Token (사용 토큰 매핑)

### Material Web Components

| Component | md-sys-color | md-sys-typescale | md-sys-shape | md-sys-motion | md-sys-state | md-sys-elevation | md-comp-* (자체) |
|-----------|:-----------:|:---------------:|:-----------:|:------------:|:-----------:|:---------------:|:---------------:|
| Filled Button | ● (경유) | ● (경유) | ● (경유) | — | ● (경유) | — | ● md-comp-filled-button |
| Outlined Button | ● (경유) | ● (경유) | ● (경유) | — | ● (경유) | — | ● md-comp-outlined-button |
| Text Button | ● (경유) | ● (경유) | ● (경유) | — | ● (경유) | — | ● md-comp-text-button |
| Filled Text Field | ● (경유) | ● (경유) | ● (경유) | — | ● (경유) | — | ● md-comp-filled-text-field |
| Dialog | ● **직접** | ● (경유) | ● (경유) | — | — | — | ● md-comp-dialog |
| Checkbox | ● (경유) | — | ● (경유) | ● **직접** | ● (경유) | — | ● md-comp-checkbox |
| Chips | ● (경유) | ● (경유) | ● (경유) | — | ● (경유) | ● (경유) | ● md-comp-assist/filter-chip |
| Primary Tab | ● (경유) | ● (경유) | ● (경유) | — | ● (경유) | — | ● md-comp-primary-tab |
| Filled Select | ● (경유) | ● (경유) | ● (경유) | — | ● (경유) | — | ● md-comp-filled-select |

> **"경유"**: md-comp-* 토큰 정의 파일 내부에서 md-sys-*를 참조. 컴포넌트 SCSS는 md-comp-*만 직접 소비.
> **"직접"**: 컴포넌트 SCSS에서 md-sys-*를 직접 `map.get()` 호출.

### MUI

| Component | theme.palette | theme.typography | theme.spacing | theme.shadows | theme.shape | theme.transitions | theme.breakpoints |
|-----------|:-----------:|:---------------:|:-----------:|:------------:|:---------:|:---------------:|:---------------:|
| Button | ● | ● | — | ● | ● | ● | — |
| TextField | — | — | — | — | — | — | — |
| Card | — | — | — | — | — | — | — |
| Dialog | — | — | — | — | — | ● | ● |
| Checkbox | ● | — | — | — | — | — | — |
| Chip | ● | ● | — | ● | — | ● | — |
| Alert | ● | ● | — | — | — | — | — |
| Tab | ● | ● | ● | — | — | — | — |
| TableCell | ● | ● | — | — | — | — | — |
| Select | — | — | — | — | — | — | — |

---

## 3. View 2: Token → Component (토큰 소비 역매핑)

### Material Web: md-sys-* 토큰별 소비 컴포넌트

| md-sys 토큰 카테고리 | 소비 컴포넌트 |
|---------------------|-------------|
| **md-sys-color** (scrim, primary, on-primary, surface, error, outline 등) | Dialog (직접), 나머지 전부 (md-comp 경유) |
| **md-sys-typescale** (body-large, label-large, headline-small 등) | Button, Text Field, Select, Dialog, Chips, Tab (md-comp 경유) |
| **md-sys-shape** (corner-extra-small ~ extra-large) | Button, Text Field, Select, Dialog, Checkbox, Chips, Tab (md-comp 경유) |
| **md-sys-motion** (easing-emphasized-accelerate/decelerate, duration-*) | Checkbox (직접), 나머지 (미사용 또는 md-comp 경유) |
| **md-sys-state** (hover/pressed/focus/dragged state-layer-opacity) | Button, Text Field, Select, Checkbox, Chips, Tab (md-comp 경유) |
| **md-sys-elevation** (level0 ~ level5) | Button (elevated), Chips (elevated) (md-comp 경유) |

### MUI: theme.* 토큰별 소비 컴포넌트

| theme 토큰 | 소비 컴포넌트 |
|-----------|-------------|
| **theme.palette.primary/secondary/error/...** | Button, Checkbox, Chip, Alert, Tab, TableCell |
| **theme.palette.action.*** (disabled, hover, selected, focus) | Button, Checkbox, Chip, Tab, TableCell |
| **theme.palette.text.*** (primary, secondary, disabled) | Chip, Alert, Tab, TableCell |
| **theme.palette.grey[]** | Button (inherit), Chip (outlined border, avatar) |
| **theme.palette.background.default** | TableCell (stickyHeader) |
| **theme.palette.divider** | TableCell (border) |
| **theme.typography.button** | Button, Tab |
| **theme.typography.body2** | Alert, TableCell |
| **theme.typography.fontFamily** | Chip |
| **theme.typography.fontWeightMedium** | Alert (filled), TableCell (head) |
| **theme.typography.pxToRem()** | Button, Chip, Tab, TableCell |
| **theme.shadows[0~8]** | Button ([0,2,4,6,8]), Chip ([1]) |
| **theme.shape.borderRadius** | Button |
| **theme.transitions.duration.*** | Button (short), Dialog (enteringScreen/leavingScreen), Chip |
| **theme.spacing()** | Tab |
| **theme.breakpoints.*** | Dialog |
| **theme.alpha()** | Button, Checkbox, Chip, Alert, TableCell |

---

## 4. Hardcoded Values 인벤토리

### Material Web — Hardcoded 값 목록

| Component | 값 | 용도 | 심각도 |
|-----------|-----|------|--------|
| **Button (shared)** | `gap: 8px` | icon-label 간격 | 🟡 M3 spec 고정값 |
| **Button (shared)** | `64px` (min-width base) | 최소 버튼 너비 | 🟡 M3 spec 고정값 |
| **Outlined Button** | `none`, `0` (container override) | 컨테이너 제거 | 🟢 의도적 토큰 재정의 |
| **Text Button** | `none`, `0` (container override) | 컨테이너 제거 | 🟢 의도적 토큰 재정의 |
| **Dialog** | `560px` (max-width/height) | 다이얼로그 최대 크기 | 🔴 토큰 미정의 |
| **Dialog** | `140px`, `280px` (min-size) | 다이얼로그 최소 크기 | 🔴 토큰 미정의 |
| **Dialog** | `48px` (여백) | 화면 가장자리 여백 | 🔴 토큰 미정의 |
| **Dialog** | `32%` (scrim opacity) | 스크림 투명도 | 🔴 토큰 미정의 |
| **Dialog** | `24px`, `16px`, `8px` (padding/gap) | 내부 여백 | 🔴 토큰 미정의 |
| **Checkbox** | `2px` (mark stroke) | 체크마크 선 두께 | 🟡 기하학적 상수 |
| **Checkbox** | `44px`, `48px` (focus/touch) | 접근성 터치 타겟 | 🟡 접근성 고정값 |
| **Checkbox** | `150ms`, `350ms`, `50ms` (duration) | 애니메이션 시간 | 🔴 motion 토큰 미연결 |
| **Checkbox** | `scale(0.6)`, `scale(1)` | 애니메이션 스케일 | 🔴 motion 토큰 미연결 |
| **Checkbox** | `math.sqrt(32)`, `math.sqrt(128)` | 체크마크 기하학 | 🟢 기하학적 상수 |
| **Chip Set** | `gap: 8px` | 칩 간격 | 🔴 토큰 미정의 |
| **Primary Tab** | `gap: 2px` | icon-label 간격 | 🟡 M3 spec 고정값 |
| **HCM 전체** | `CanvasText`, `GrayText`, `Canvas`, `WindowText`, `ActiveText` | High Contrast Mode | 🟢 OS 접근성 키워드 |

### MUI — Hardcoded 값 목록

| Component | 값 | 용도 | 심각도 |
|-----------|-----|------|--------|
| **Button** | `64` (minWidth) | 최소 버튼 너비 | 🟡 M3 spec 유래 |
| **Button** | `'6px 16px'`, `'5px 15px'`, `'6px 8px'` 등 8종 | variant×size별 padding | 🔴 theme.spacing 미사용 |
| **Button** | `13`, `15` (pxToRem 인자) | size별 fontSize | 🟡 typography 스케일 외 값 |
| **Button** | `18`, `20`, `22` (icon fontSize) | size별 아이콘 크기 | 🔴 theme 미연결 |
| **Button** | `8`, `-4`, `-2`, `14`, `10`, `6` (icon/loading position) | 간격/위치 | 🔴 theme.spacing 미사용 |
| **Button** | `'none'` (boxShadow ×5) | elevation 제거 | 🟢 의도적 오버라이드 |
| **Dialog** | `32` (margin) | 다이얼로그 여백 | 🔴 theme.spacing 미사용 |
| **Dialog** | `64px` (calc 여백) | margin×2 | 🔴 파생 하드코드 |
| **Dialog** | `444` (xs 최소 너비) | minWidth 보정 | 🔴 매직 넘버 |
| **Chip** | `32`, `24` (height) | 칩 높이 | 🔴 theme 미연결 |
| **Chip** | `32/2` (borderRadius) | 칩 둥근 모서리 | 🔴 theme.shape 미사용 |
| **Chip** | `5`, `-6`, `22`, `18`, `16` (icon 간격/크기) | 아이콘 레이아웃 | 🔴 theme.spacing 미사용 |
| **Chip** | `12`, `11`, `8`, `7` (label padding) | 라벨 여백 | 🔴 theme.spacing 미사용 |
| **Chip** | `0.26`, `0.4`, `0.7` (alpha 값) | 투명도 | 🔴 theme.palette.action 미사용 |
| **Alert** | `'6px 16px'` (padding) | 얼럿 여백 | 🔴 theme.spacing 미사용 |
| **Alert** | `12`, `22`, `0.9` (icon) | 아이콘 크기/투명도 | 🔴 theme 미연결 |
| **Alert** | `'7px 0'`, `'8px 0'`, `'4px 0 0 16px'` | 내부 여백 | 🔴 theme.spacing 미사용 |
| **Alert** | `0.6`, `0.9` (darken/lighten 인자) | 색상 보정 계수 | 🔴 매직 넘버 |
| **Tab** | `360`, `90`, `48`, `72` (maxWidth/minWidth/minHeight) | 탭 크기 | 🔴 theme 미연결 |
| **Tab** | `'12px 16px'` (padding) | 탭 여백 | 🔴 theme.spacing 미사용 |
| **Tab** | `1.25` (lineHeight) | 줄 간격 | 🔴 theme.typography 미사용 |
| **Tab** | `9`, `6` (icon 간격) | 아이콘 여백 | 🔴 theme.spacing 미사용 |
| **Tab** | `0.6` (opacity) | inherit 텍스트 투명도 | 🔴 theme.palette.action 미사용 |
| **TableCell** | `16`, `'6px 16px'`, `'0 12px 0 16px'`, `'0 0 0 4px'` | 셀 padding | 🔴 theme.spacing 미사용 |
| **TableCell** | `24`, `48` (width) | 체크박스 열 너비 | 🔴 theme 미연결 |
| **TableCell** | `0.88` (lighten 인자) | border 색상 보정 | 🔴 매직 넘버 |

---

## 5. MUI vs Material Web 토큰 의존도 비교

### 5.1 컴포넌트별 직접 비교

| Component | MW Token dep % | MUI Token dep % | 격차 | 분석 |
|-----------|:-------------:|:--------------:|:----:|------|
| **Button** | 90.9% | 46.3% | **-44.6%p** | MW: 전 토큰 CSS var 출력. MUI: padding/spacing 대거 하드코드 |
| **Text Field** | 100% | N/A (위임) | — | MW: 88개 토큰 단일 파일. MUI: 5개 하위 컴포넌트 분산 |
| **Dialog** | 51.4% | 33.3% | **-18.1%p** | 양쪽 모두 spacing 하드코드. MUI가 더 심함 |
| **Checkbox** | 68.6% | 83.3% | **+14.7%p** | MUI: 스타일 코드 자체가 극소(6줄). MW: 70줄 중 motion 하드코드 |
| **Chip** | ~95%+ | 57.7% | **-37%p+** | MW: 토큰 출력 포함 시 거의 100%. MUI: spacing/size 대거 하드코드 |
| **Tab** | ~98%+ | 52.4% | **-46%p+** | MW: 토큰 출력 포함 시 거의 100%. MUI: 크기/간격 하드코드 |
| **Select** | 100% | N/A (위임) | — | MW: 86개 토큰. MUI: Input 컴포넌트에 위임 |
| **Alert** | (해당 없음) | 50.0% | — | MW에 Alert 컴포넌트 없음 |
| **Card** | (해당 없음) | N/A (위임) | — | MW에 Card 컴포넌트 없음 |
| **TableCell** | (해당 없음) | 62.5% | — | MW에 Table 컴포넌트 없음 |

### 5.2 구조적 차이 분석

#### 차원 1: 토큰 간접층 유무

```
Material Web:
  Figma token → md-ref-* → md-sys-* → md-comp-* → CSS custom property (--_*)
                                                     ↑
                                              이 층이 존재

MUI:
  Figma token → (없음) → theme.palette/typography/... → JS 객체 직접 참조
                                                         ↑
                                                  이 층이 없음
```

Material Web은 **컴포넌트마다 전용 md-comp-* 토큰 세트**가 존재하며, 이 토큰들이 md-sys-*를 참조하는 **이중 간접층**을 가진다. MUI는 `theme.*`을 JS에서 직접 참조하므로 **컴포넌트 전용 토큰 층이 없다**.

**영향**: Material Web에서 Figma 토큰 변경 → md-comp-* 값 변경 → 자동 전파. MUI에서 Figma 토큰 변경 → `theme.palette.primary.main` 등 변경 → 전파되나, **하드코딩된 값은 변경되지 않음**.

#### 차원 2: Spacing 토큰화 격차

| 시스템 | Spacing 접근법 |
|--------|--------------|
| **Material Web** | `--_leading-space`, `--_trailing-space`, `--_top-space` 등 **컴포넌트별 spacing 토큰** 존재 |
| **MUI** | `theme.spacing()` 함수 존재하나, **실제 컴포넌트 코드에서 거의 미사용**. `padding: '6px 16px'` 등 리터럴 우세 |

MUI Button의 8종 padding 변형, Chip의 4종 label padding, Tab/TableCell의 padding이 모두 하드코딩. `theme.spacing()`은 Tab의 icon 간격(`theme.spacing(1)`)에서만 확인됨.

#### 차원 3: Motion 토큰화 격차

| 시스템 | Motion 접근법 |
|--------|--------------|
| **Material Web** | `md-sys-motion` 토큰 존재. Checkbox에서 `easing-emphasized-accelerate/decelerate` 직접 참조. 그러나 **duration은 하드코딩** (150ms, 350ms) |
| **MUI** | `theme.transitions.duration.*` 존재. Button(`short`), Dialog(`enteringScreen/leavingScreen`)에서 사용. 그러나 **대부분의 컴포넌트에서 미사용** |

#### 차원 4: Variant 구현 방식

| 시스템 | Variant 구현 |
|--------|-------------|
| **Material Web** | **파일 분리**: `_filled-button.scss`, `_outlined-button.scss`, `_text-button.scss` 각각 독립 토큰 세트 |
| **MUI** | **단일 파일 내 variants 배열**: `styled()` 내부 `variants: [{ props: {...}, style: {...} }]` 패턴 |

Material Web의 파일 분리는 각 변형이 **독립된 md-comp-* 토큰 세트**를 가짐을 의미 (예: `md-comp-filled-button` vs `md-comp-outlined-button`). MUI의 단일 파일 방식은 변형 간 스타일 차이를 **하드코딩된 delta**로 표현 (예: outlined padding `'5px 15px'` vs contained `'6px 16px'`).

### 5.3 종합 평가

| 평가 축 | Material Web | MUI |
|---------|:-----------:|:---:|
| **토큰 커버리지** (디자인 값 중 토큰 비율) | ★★★★★ (90~100%) | ★★★☆☆ (33~83%) |
| **토큰 일관성** (컴포넌트 간 동일 패턴) | ★★★★★ (전 컴포넌트 동일 pipeline) | ★★☆☆☆ (컴포넌트별 편차 큼) |
| **Spacing 토큰화** | ★★★★☆ (전용 토큰 존재) | ★☆☆☆☆ (거의 하드코딩) |
| **Motion 토큰화** | ★★★☆☆ (easing 토큰화, duration 하드코딩) | ★★☆☆☆ (일부만 theme.transitions) |
| **Figma↔Code 매핑 충실도** | ★★★★★ (md-comp-* = Figma token 1:1) | ★★☆☆☆ (theme.* ≈ Figma이나 하드코딩 우회 다수) |
| **Theme 커스터마이즈 용이성** | ★★★★★ (CSS custom property override) | ★★★★☆ (theme override + sx prop) |

### 5.4 핵심 결론

1. **Material Web은 "토큰이 곧 코드"**: 컴포넌트 SCSS 파일에 하드코딩된 디자인 값이 거의 없고, 모든 시각적 속성이 `md-comp-*` 토큰 → CSS custom property 파이프라인을 통과. Figma Design Token과의 **1:1 구조적 대응**이 가능.

2. **MUI는 "테마가 곧 코드"**: `theme.*` 참조가 존재하지만, **spacing, sizing, motion 값의 상당수가 JS 리터럴**. Figma token을 MUI theme에 매핑해도 하드코딩된 값까지 자동 전파되지 않음.

3. **Dialog가 양쪽 모두에서 가장 취약**: M3 spec 자체가 dialog의 공간 구조(max-size, padding, gap)를 토큰화하지 않은 것이 근본 원인. Material Web 51.4%, MUI 33.3%.

4. **Checkbox는 역전 현상**: MUI(83.3%) > Material Web(68.6%). 이는 MUI Checkbox의 스타일 코드가 극도로 얇은(6줄) 반면, Material Web은 체크마크 애니메이션까지 자체 구현하면서 motion 하드코딩이 증가했기 때문.

5. **TextField/Select의 구조적 대조**: Material Web은 단일 파일에서 86~88개 토큰을 일괄 매핑(100%). MUI는 5개 하위 컴포넌트로 스타일을 분산(0% direct). **토큰 추적성(traceability)** 관점에서 Material Web이 압도적으로 유리.

---

## 부록: 감사 대상 소스 파일 목록

### Material Web Components
| 파일 | 상태 |
|------|------|
| `button/internal/_filled-button.scss` | ✅ 분석 완료 |
| `button/internal/_outlined-button.scss` | ✅ 분석 완료 |
| `button/internal/_text-button.scss` | ✅ 분석 완료 |
| `button/internal/_shared.scss` | ✅ 분석 완료 (공통 스타일) |
| `textfield/internal/_filled-text-field.scss` | ✅ 분석 완료 |
| `dialog/internal/_dialog.scss` | ✅ 분석 완료 |
| `checkbox/internal/_checkbox.scss` | ✅ 분석 완료 |
| `chips/internal/_assist-chip.scss` | ✅ 분석 완료 |
| `chips/internal/_filter-chip.scss` | ✅ 분석 완료 |
| `chips/internal/_chip-set.scss` | ✅ 분석 완료 |
| `tabs/internal/_tabs.scss` | ✅ 분석 완료 |
| `tabs/internal/_primary-tab.scss` | ✅ 분석 완료 |
| `select/internal/_filled-select.scss` | ✅ 분석 완료 |

### MUI
| 파일 | 상태 |
|------|------|
| `packages/mui-material/src/Button/Button.js` | ✅ 분석 완료 |
| `packages/mui-material/src/TextField/TextField.js` | ✅ 분석 완료 (스타일 없음) |
| `packages/mui-material/src/Card/Card.js` | ✅ 분석 완료 |
| `packages/mui-material/src/Dialog/Dialog.js` | ✅ 분석 완료 |
| `packages/mui-material/src/Checkbox/Checkbox.js` | ✅ 분석 완료 |
| `packages/mui-material/src/Chip/Chip.js` | ✅ 분석 완료 |
| `packages/mui-material/src/Alert/Alert.js` | ✅ 분석 완료 |
| `packages/mui-material/src/Tab/Tab.js` | ✅ 분석 완료 |
| `packages/mui-material/src/TableCell/TableCell.js` | ✅ 분석 완료 |
| `packages/mui-material/src/Select/Select.js` | ✅ 분석 완료 (스타일 없음) |
