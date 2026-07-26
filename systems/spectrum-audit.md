# Adobe Spectrum CSS — 컴포넌트 레벨 토큰 의존성 감사 보고서

> **소스**: [github.com/adobe/spectrum-css](https://github.com/adobe/spectrum-css) `main` 브랜치
> **감사 일자**: 2026-07-26
> **분석 방법**: 각 컴포넌트의 `index.css` 원본 파일을 다운로드하여 정규식 기반 자동 카운트 수행
> **대상 컴포넌트**: button, textfield, card, dialog, checkbox, tag, inlinealert, tabs, table, picker (총 10개)

---

## 1. 종합 요약 테이블

| Component | CSS 선언 수 | Token 참조 (`var(--spectrum-*)`) | 고유 토큰 수 | Hardcoded 값 | Token 의존율 | `--mod-*` 훅 (고유) | `--highcontrast-*` 훅 (고유) | 파일 크기 |
|-----------|----------:|------:|------:|------:|------:|------:|------:|------:|
| **button** | 96 | 236 | 142 | 4 | 98.3% | 44 | 15 | 30.4 KB |
| **textfield** | 172 | 210 | 154 | 0 | 100.0% | 66 | 16 | 32.0 KB |
| **card** | 200 | 153 | 75 | 5 | 96.8% | 59 | 0 | 18.1 KB |
| **dialog** | 106 | 63 | 25 | 3 | 95.5% | 27 | 0 | 14.4 KB |
| **checkbox** | 123 | 120 | 80 | 0 | 100.0% | 39 | 14 | 22.5 KB |
| **tag** | 113 | 196 | 140 | 0 | 100.0% | 76 | 51 | 27.5 KB |
| **inlinealert** | 51 | 60 | 50 | 0 | 100.0% | 26 | 4 | 8.4 KB |
| **tabs** | 97 | 129 | 103 | 0 | 100.0% | 41 | 9 | 17.1 KB |
| **table** | 175 | 323 | 206 | 6 | 98.2% | 95 | 18 | 48.3 KB |
| **picker** | 127 | 190 | 146 | 1 | 99.5% | 63 | 7 | 25.8 KB |
| **합계/평균** | **1,260** | **1,680** | **1,121** | **19** | **98.9%** | **536** | **134** | **244.5 KB** |

### 핵심 발견

- **평균 Token 의존율 98.9%**: 10개 컴포넌트 중 6개(textfield, checkbox, tag, inlinealert, tabs, picker는 99.5%+)가 hardcoded 값 없이 100% 토큰 기반
- **3-layer override 아키텍처**: `var(--highcontrast-*, var(--mod-*, var(--spectrum-*)))` 패턴으로 시스템 토큰 → 사용자 override → high contrast override의 3단계 폴백 체인 사용
- **table이 최대 규모**: 206개 고유 토큰, 323회 참조, 48.3 KB로 가장 복잡한 컴포넌트
- **dialog가 최소 토큰 사용**: 25개 고유 토큰만 참조 — 대부분의 값을 자체 컴포넌트 토큰으로 추상화

---

## 2. Variant Axes 분석

| Component | Size | State | Variant/Style | Severity | 총 Variant 축 |
|-----------|------|-------|---------------|----------|:---:|
| **button** | S, L, XL | is-disabled, is-focused, is-pending, is-selected | emphasized, quiet | negative | 4 |
| **textfield** | S, L, XL | is-disabled, is-focused, is-invalid, is-keyboardFocused, is-readOnly, is-valid | quiet, sideLabel | — | 3 |
| **card** | — | is-drop-target, is-focused, is-selected | gallery, horizontal, quiet | — | 2 |
| **dialog** | S, L | — | dismissable, fullscreen, noDivider | — | 2 |
| **checkbox** | S, M, L, XL | is-indeterminate, is-invalid, is-readOnly | emphasized | — | 3 |
| **tag** | S, M, L | is-disabled, is-emphasized, is-focused, is-invalid, is-selected | — | — | 2 |
| **inlinealert** | — | — | — | info, notice, positive, negative | 1 |
| **tabs** | S, L, XL | is-disabled, is-selected | compact, emphasized, horizontal, quiet, vertical | — | 3 |
| **table** | S, M, L, XL | is-drop-target, is-focused, is-keyboardFocused, is-last-tier, is-selected, is-sortable, is-sorted-asc, is-sorted-desc | compact, emphasized, quiet | — | 3 |
| **picker** | S, L, XL | is-disabled, is-invalid, is-keyboardFocused, is-loading, is-open, is-placeholder | quiet, sideLabel | — | 3 |

### Variant 패턴 관찰

- **T-shirt sizing (S/M/L/XL)**: 8/10 컴포넌트가 size variant 보유. card와 inlinealert만 size variant 없음
- **table이 가장 많은 state**: 8개 state class (sort, drop-target, keyboard focus 등)
- **강제 색상 모드 (forced-colors)**: checkbox, tag, inlinealert, tabs, table, picker, button, textfield 등 8개 컴포넌트가 `@media (forced-colors: active)` 블록에서 `--highcontrast-*` 토큰 정의

---

## 3. Override Hooks 분석

### 3.1 `--mod-*` 패턴 (Consumer Override)

모든 컴포넌트가 `var(--mod-{component}-{property}, var(--spectrum-{component}-{property}))` 패턴을 사용.
소비자가 CSS custom property로 컴포넌트 스타일을 override할 수 있는 공식 API.

| Component | 고유 `--mod-*` 수 | 대표 예시 |
|-----------|:---:|------|
| table | 95 | `--mod-table-row-background-color`, `--mod-table-header-font-weight` |
| tag | 76 | `--mod-tag-border-color`, `--mod-tag-content-color-hover` |
| textfield | 66 | `--mod-textfield-border-color`, `--mod-textfield-height` |
| picker | 63 | `--mod-picker-block-size`, `--mod-picker-font-color-default` |
| card | 59 | `--mod-card-background-color`, `--mod-card-corner-radius` |
| button | 44 | `--mod-button-background-color`, `--mod-button-border-width` |
| tabs | 41 | `--mod-tabs-color`, `--mod-tabs-divider-size` |
| checkbox | 39 | `--mod-checkbox-control-size`, `--mod-checkbox-border-width` |
| dialog | 27 | `--mod-dialog-width`, `--mod-dialog-confirm-title-text-size` |
| inlinealert | 26 | `--mod-inlinealert-border-width`, `--mod-inlinealert-header-color` |

### 3.2 `--highcontrast-*` 패턴 (Windows High Contrast Mode)

`@media (forced-colors: active)` 내에서 시스템 색상 키워드(`CanvasText`, `Highlight`, `ButtonFace`, `GrayText` 등)로 재정의.

| Component | 고유 `--highcontrast-*` 수 | WHCM 지원 |
|-----------|:---:|:---:|
| tag | 51 | ✅ |
| table | 18 | ✅ |
| textfield | 16 | ✅ |
| button | 15 | ✅ |
| checkbox | 14 | ✅ |
| tabs | 9 | ✅ |
| picker | 7 | ✅ |
| inlinealert | 4 | ✅ |
| card | 0 | ❌ |
| dialog | 0 | ❌ |

> **특이사항**: card와 dialog는 `--highcontrast-*` override가 없음. card는 `forced-colors` 미디어 쿼리 자체가 없고, dialog는 `border: solid`만 추가.

---

## 4. Hardcoded 값 인벤토리

총 19개의 hardcoded 값 발견. 대부분 `var()` 폴백 체인 내부의 fallback 값이거나, 토큰이 아직 존재하지 않는 속성.

### 4.1 button (4개)

| 속성 | 값 | 맥락 | 비고 |
|------|-----|------|------|
| `margin-block-start` | `0px` | var() fallback | ButtonGroup 내 간격 초기화 (4회 반복) |

### 4.2 card (5개)

| 속성 | 값 | 맥락 | 비고 |
|------|-----|------|------|
| `background-color` | `rgb(var(...))` | 직접 | RGB 채널 분리 사용 — `--spectrum-card-selected-background-color-rgb` 토큰의 RGB 값에 opacity 결합 |
| `box-shadow` | `1px` | 직접 | `0 0 0 1px` drop-target outline — 토큰 없음 |
| `background-color` | `rgb(var(...))` | 직접 | quickActions 배경 — RGB + opacity 조합 |
| `box-shadow` | `1px` | 직접 | quiet card drop-target focus ring |
| `background-color` | `rgb(var(...))` | 직접 | quiet card selected overlay |

> **주석**: card 소스에 `/* TODO update to --spectrum-card-selection-background-color token once an RGB stripped value is available */` 라는 TODO 존재. RGB 분리 패턴은 토큰 시스템의 한계.

### 4.3 dialog (3개)

| 속성 | 값 | 맥락 | 비고 |
|------|-----|------|------|
| `inline-size` | `480px` | var() fallback | `--mod-dialog-confirm-medium-width`의 기본값 |
| `min-inline-size` | `288px` | var() fallback | `--mod-dialog-min-inline-size`의 기본값 |
| `font-size` | `28px` | var() fallback | fullscreen 모드 heading 크기 — `--mod-dialog-fullscreen-header-text-size` |

> dialog는 size S(400px), M(480px), L(640px)을 모두 `--mod-*` fallback으로 처리. 글로벌 토큰이 아닌 컴포넌트 자체 크기 정의.

### 4.4 table (6개)

| 속성 | 값 | 맥락 | 비고 |
|------|-----|------|------|
| `outline` | `1px` | var() fallback | focus indicator outline (2회) |
| `outline-offset` | `0px` | var() fallback | outline offset 초기화 |
| `margin-block-start` | `0px` | var() fallback | 간격 초기화 |
| `padding-inline-start` | `0px` | var() fallback | 패딩 초기화 |
| `outline-offset` | `2px` | var() fallback | `--mod-table-focus-indicator-outline-offset` |

### 4.5 picker (1개)

| 속성 | 값 | 맥락 | 비고 |
|------|-----|------|------|
| `margin-block-start` | `1px` | 직접 | quiet variant의 `calc(... + (1px))` — border 보정용 |

### Hardcoded 값 분류 요약

| 유형 | 건수 | 설명 |
|------|:---:|------|
| `0px` 초기화 | 7 | margin/padding/outline-offset 리셋 |
| 크기 fallback | 3 | dialog width (288/480/28px) |
| `1px` 보정 | 4 | outline, box-shadow, border 보정 |
| `2px` offset | 1 | table focus outline-offset |
| `rgb()` 조합 | 4 | card의 RGB + opacity 패턴 |

---

## 5. View 1: Component → Token (컴포넌트별 사용 토큰)

### 5.1 button (142개 고유 토큰)

**글로벌 디자인 토큰** (컴포넌트 비종속):
`--spectrum-accent-background-color-default`, `--spectrum-accent-background-color-down`, `--spectrum-accent-background-color-hover`, `--spectrum-accent-background-color-key-focus`, `--spectrum-accent-color-200`, `--spectrum-accent-color-300`, `--spectrum-accent-color-900`, `--spectrum-accent-color-1000`, `--spectrum-accent-color-1100`, `--spectrum-accent-content-color-default`, `--spectrum-accent-content-color-down`, `--spectrum-accent-content-color-hover`, `--spectrum-accent-content-color-key-focus`, `--spectrum-animation-duration-100`, `--spectrum-bold-font-weight`, `--spectrum-border-width-200`, `--spectrum-component-height-75`, `--spectrum-component-height-100`, `--spectrum-component-height-200`, `--spectrum-component-height-300`, `--spectrum-component-pill-edge-to-text-75/100/200/300`, `--spectrum-component-pill-edge-to-visual-75/100/200/300`, `--spectrum-component-pill-edge-to-visual-only-75/100/200/300`, `--spectrum-component-top-to-workflow-icon-75/100/200/300`, `--spectrum-disabled-background-color`, `--spectrum-disabled-border-color`, `--spectrum-disabled-content-color`, `--spectrum-disabled-static-black-*`, `--spectrum-disabled-static-white-*`, `--spectrum-focus-indicator-color`, `--spectrum-focus-indicator-gap`, `--spectrum-focus-indicator-thickness`, `--spectrum-font-size-75/100/200/300`, `--spectrum-gray-200/300/400/800/900`, `--spectrum-negative-background-color-*`, `--spectrum-negative-color-*`, `--spectrum-negative-content-color-*`, `--spectrum-neutral-background-color-*`, `--spectrum-neutral-content-color-*`, `--spectrum-progress-circle-thickness-medium`, `--spectrum-static-black-focus-indicator-color`, `--spectrum-static-white-focus-indicator-color`, `--spectrum-text-to-visual-75/100/200/300`, `--spectrum-white`, `--spectrum-workflow-icon-size-75/100/200/300`

**컴포넌트 내부 토큰** (`--spectrum-button-*`):
`--spectrum-button-animation-duration`, `--spectrum-button-background-color-*`, `--spectrum-button-border-color-*`, `--spectrum-button-border-radius`, `--spectrum-button-border-width`, `--spectrum-button-bottom-to-text`, `--spectrum-button-bottom-to-text-small/medium/large/extra-large`, `--spectrum-button-content-color-*`, `--spectrum-button-edge-to-text`, `--spectrum-button-edge-to-visual`, `--spectrum-button-edge-to-visual-only`, `--spectrum-button-focus-indicator-color`, `--spectrum-button-focus-ring-gap`, `--spectrum-button-focus-ring-thickness`, `--spectrum-button-font-size`, `--spectrum-button-height`, `--spectrum-button-intended-icon-size`, `--spectrum-button-line-height`, `--spectrum-button-min-width`, `--spectrum-button-minimum-width-multiplier`, `--spectrum-button-padding-label-to-icon`, `--spectrum-button-sized-*`, `--spectrum-button-top-to-icon`, `--spectrum-button-top-to-text`, `--spectrum-button-top-to-text-small/medium/large/extra-large`

### 5.2 textfield (154개 고유 토큰)

**글로벌**: `--spectrum-animation-duration-100`, `--spectrum-character-count-to-field-quiet-*`, `--spectrum-checkmark-icon-size-75/100/200/300`, `--spectrum-component-bottom-to-text-75/100/200`, `--spectrum-component-edge-to-text-75/100/200`, `--spectrum-component-height-75/100/200/300`, `--spectrum-component-top-to-text-100`, `--spectrum-corner-radius-100`, `--spectrum-disabled-content-color`, `--spectrum-field-edge-to-alert-icon-*`, `--spectrum-field-edge-to-border-quiet`, `--spectrum-field-edge-to-text-quiet`, `--spectrum-field-edge-to-validation-icon-*`, `--spectrum-field-label-to-component`, `--spectrum-field-label-to-component-quiet-*`, `--spectrum-field-text-to-alert-icon-*`, `--spectrum-field-text-to-validation-icon-*`, `--spectrum-field-top-to-validation-icon-*`, `--spectrum-focus-indicator-color/gap/thickness`, `--spectrum-font-size-75/100/200/300`, `--spectrum-help-text-to-component`, `--spectrum-negative-border-color-*`, `--spectrum-negative-visual-color`, `--spectrum-neutral-content-color-*`, `--spectrum-positive-visual-color`, `--spectrum-regular-font-weight`, `--spectrum-sans-font-family-stack`, `--spectrum-side-label-character-count-*`, `--spectrum-spacing-100/200`, `--spectrum-text-area-min-*`, `--spectrum-text-field-minimum-width-multiplier`, `--spectrum-workflow-icon-size-75/100/200/300`

**컴포넌트 내부** (`--spectrum-textfield-*`): background-color, border-color (7개 상태), border-width, character-count-*, corner-radius, focus-indicator-*, font-family/weight, height, helptext-spacing, icon-color/size/spacing (valid/invalid), input-line-height, label-spacing, min-width, placeholder-font-size, spacing-*, text-color (9개 상태), width

### 5.3 card (75개 고유 토큰)

**글로벌**: `--spectrum-animation-duration-100`, `--spectrum-background-base-color`, `--spectrum-background-layer-2-color`, `--spectrum-blue-700`, `--spectrum-body-color`, `--spectrum-body-line-height`, `--spectrum-body-sans-serif-font-style/weight`, `--spectrum-body-size-s`, `--spectrum-border-width-100`, `--spectrum-corner-radius-100`, `--spectrum-drop-shadow-blur/color/x/y`, `--spectrum-focus-indicator-color/thickness`, `--spectrum-gray-100-rgb`, `--spectrum-heading-color`, `--spectrum-heading-line-height`, `--spectrum-heading-sans-serif-font-style/weight`, `--spectrum-heading-size-xxs`, `--spectrum-sans-font-family-stack`, `--spectrum-spacing-100/200/300/400`

**컴포넌트 내부** (`--spectrum-card-*`): actions-*, background-color, body-*, border-*, content-*, corner-radius, divider-color, focus-indicator-*, footer-*, horizontal-*, minimum-width, preview-*, selected-*, selection-*, subtitle-*, title-*

### 5.4 dialog (25개 고유 토큰)

**글로벌**: `--spectrum-component-bottom-to-text-300`, `--spectrum-component-height-100`, `--spectrum-component-pill-edge-to-text-100`, `--spectrum-gray-800`, `--spectrum-gray-900`, `--spectrum-heading-sans-serif-font-weight`, `--spectrum-line-height-100`, `--spectrum-regular-font-weight`, `--spectrum-spacing-50/200/300/600`

**컴포넌트 내부** (`--spectrum-dialog-*`): confirm-border-radius, confirm-buttongroup-padding-top, confirm-close-button-padding/size, confirm-description-padding/text-color/text-size, confirm-divider-block-spacing-*, confirm-gap-size, confirm-hero-height, confirm-padding-grid, confirm-title-text-size

### 5.5 checkbox (80개 고유 토큰)

**글로벌**: `--spectrum-accent-color-900/1000/1100`, `--spectrum-animation-duration-100`, `--spectrum-border-width-200`, `--spectrum-cjk-line-height-100`, `--spectrum-component-height-75/100/200/300`, `--spectrum-component-top-to-text-75/100/200/300`, `--spectrum-disabled-content-color`, `--spectrum-focus-indicator-color/gap/thickness`, `--spectrum-font-size-75/100/200/300`, `--spectrum-line-height-100`, `--spectrum-negative-color-900/1000/1100`, `--spectrum-neutral-background-color-selected-*`, `--spectrum-neutral-content-color-*`, `--spectrum-text-to-control-75/100/200/300`

**컴포넌트 내부** (`--spectrum-checkbox-*`): animation-duration, border-width, checkmark-color, content-color-*, control-color-*, control-corner-radius, control-selected-color-*, control-size(-small/medium/large/extra-large), emphasized-color-*, focus-indicator-*, font-size, height, invalid-color-*, line-height(-cjk), selected-border-width, spacing, text-to-control, top-to-text

### 5.6 tag (140개 고유 토큰)

**글로벌**: `--spectrum-accent-background-color-*`, `--spectrum-animation-duration-100`, `--spectrum-avatar-opacity-disabled`, `--spectrum-border-width-100`, `--spectrum-clearbutton-fill-background-color/size`, `--spectrum-component-height-75/100/200`, `--spectrum-component-top-to-text-75/100/200`, `--spectrum-component-top-to-workflow-icon-75/100/200`, `--spectrum-disabled-content-color`, `--spectrum-focus-indicator-color/gap/thickness`, `--spectrum-font-size-75/100/200`, `--spectrum-line-height-100`, `--spectrum-negative-background-color-*`, `--spectrum-negative-color-900/1000/1100`, `--spectrum-negative-content-color-*`, `--spectrum-neutral-background-color-selected-*`, `--spectrum-regular-font-weight`, `--spectrum-text-to-visual-75/100/200`, `--spectrum-white`, `--spectrum-workflow-icon-size-75/100/200`

**컴포넌트 내부** (`--spectrum-tag-*`): animation-duration, avatar-spacing-*, background-color-* (16개 변형), border-color-* (20개 변형), border-width, clear-button-spacing-*, content-color-* (12개 변형), corner-radius, focus-ring-*, font-size, height, icon-size/spacing-*, label-*, size-small/medium/large-*, spacing-inline-start, top-to-avatar-*, top-to-cross-icon-*

### 5.7 inlinealert (50개 고유 토큰)

**글로벌**: `--spectrum-background-layer-2-color`, `--spectrum-body-color/line-height/sans-serif-font-style/weight/size-s`, `--spectrum-border-width-200`, `--spectrum-component-height-50`, `--spectrum-corner-radius-100`, `--spectrum-heading-color/line-height/sans-serif-font-style/weight/size-xxs`, `--spectrum-in-line-alert-minimum-width`, `--spectrum-informative-visual-color`, `--spectrum-negative-visual-color`, `--spectrum-neutral-visual-color`, `--spectrum-notice-visual-color`, `--spectrum-positive-visual-color`, `--spectrum-sans-font-family-stack`, `--spectrum-spacing-300/400`, `--spectrum-workflow-icon-size-100`

**컴포넌트 내부** (`--spectrum-inlinealert-*`): background-color, border-and-icon-color(-info/notice/positive/negative), border-radius/width, content-color/font-*, header-color/min-block-size, heading-font-*, icon-size, min-inline-size, spacing-*

### 5.8 tabs (103개 고유 토큰)

**글로벌**: `--spectrum-accent-content-color-default/hover/key-focus`, `--spectrum-animation-duration-100`, `--spectrum-animation-ease-in-out`, `--spectrum-border-width-200`, `--spectrum-corner-radius-100`, `--spectrum-default-font-style`, `--spectrum-focus-indicator-color/thickness`, `--spectrum-font-size-75/100/200/300`, `--spectrum-gray-500`, `--spectrum-line-height-100`, `--spectrum-neutral-subdued-content-color-*`, `--spectrum-sans-font-family-stack`, `--spectrum-tab-item-*` (48개: bottom-to-text-*, compact-height-*, focus-indicator-gap-*, height-*, start-to-edge-*, to-tab-item-horizontal/vertical-*, top-to-text-*, top-to-text-compact-*, top-to-workflow-icon-*, top-to-workflow-icon-compact-*), `--spectrum-text-to-visual-75/100/200/300`, `--spectrum-workflow-icon-size-50/75/100/200`

**컴포넌트 내부** (`--spectrum-tabs-*`): animation-duration/ease, bottom-to-text, color(-disabled/hover/key-focus/selected), divider-*, focus-indicator-*, font-*, icon-size/to-text, item-height/horizontal-spacing/vertical-spacing, line-height, list-background-direction, selection-indicator-color, start-to-edge, top-to-icon/text

### 5.9 table (206개 고유 토큰)

**글로벌**: `--spectrum-accent-visual-color`, `--spectrum-animation-duration-100`, `--spectrum-background-layer-1-color`, `--spectrum-blue-900-rgb`, `--spectrum-body-color`, `--spectrum-bold-font-weight`, `--spectrum-checkbox-control-size-small`, `--spectrum-component-bottom-to-text-75/100/200/300`, `--spectrum-component-height-75/100/200/300`, `--spectrum-component-top-to-text-75/100/200/300`, `--spectrum-corner-radius-100`, `--spectrum-default-font-style`, `--spectrum-drop-zone-background-color-opacity/rgb`, `--spectrum-focus-indicator-color/thickness`, `--spectrum-font-size-75/100/200/300`, `--spectrum-gray-50/75/200/300`, `--spectrum-gray-700-rgb`, `--spectrum-gray-900-rgb`, `--spectrum-line-height-100`, `--spectrum-logical-rotation`, `--spectrum-neutral-content-color-default`, `--spectrum-neutral-subdued-content-color-*`, `--spectrum-regular-font-weight`, `--spectrum-sans-font-family-stack`, `--spectrum-spacing-300`, `--spectrum-text-to-visual-100/200/300`, `--spectrum-thumbnail-size-50/200/300/500/700/800`, `--spectrum-transparent-white-100`

**컴포넌트 내부** (`--spectrum-table-*`): border-color/divider-width/radius/width, cell-*, checkbox-to-text, collapsible-*, column-header-row-*, default-vertical-align, disclosure-icon-size, divider-color, drop-zone-*, edge-to-content, focus-indicator-*, header-*, icon-color-*, icon-to-text, min-header-height, min-row-height, outer-border-inline-width, row-* (height, background, text, font, opacity 등 60+개), section-header-*, selected-*, summary-row-*, thumbnail-* (30+개), transition-duration

### 5.10 picker (146개 고유 토큰)

**글로벌**: `--spectrum-animation-duration-100`, `--spectrum-component-bottom-to-text-75/100/200/300`, `--spectrum-component-edge-to-text-75/100/200/300`, `--spectrum-component-height-75/100/200/300`, `--spectrum-component-to-menu-small/medium/large/extra-large`, `--spectrum-component-top-to-text-75/100/200/300`, `--spectrum-corner-radius-100`, `--spectrum-default-font-style`, `--spectrum-disabled-background-color/content-color`, `--spectrum-field-edge-to-text-quiet`, `--spectrum-field-end-edge-to-disclosure-icon-75/100/200/300`, `--spectrum-field-label-to-component(-quiet-*)`, `--spectrum-field-text-to-alert-icon-*`, `--spectrum-field-top-to-alert-icon-*`, `--spectrum-field-top-to-disclosure-icon-75/100/200/300`, `--spectrum-field-top-to-progress-circle-*`, `--spectrum-field-width`, `--spectrum-focus-indicator-color/gap/thickness`, `--spectrum-font-size-75/100/200/300`, `--spectrum-line-height-100`, `--spectrum-negative-border-color-*`, `--spectrum-negative-visual-color`, `--spectrum-neutral-content-color-*`, `--spectrum-regular-font-weight`, `--spectrum-text-to-visual-75/100/200/300`

**컴포넌트 내부** (`--spectrum-picker-*`): animation-duration, background-color-*, block-size, border-color-* (14개 변형), border-radius/width, end-edge-to-disclousure-icon-quiet, focus-indicator-*, font-color-* (7개 상태), font-size/weight, icon-color-* (8개 상태), inline-size, line-height, minimum-width-multiplier, placeholder-font-style, spacing-* (16개), visual-to-disclosure-icon-*

---

## 6. View 2: Token → Component (토큰별 사용 컴포넌트)

### 6.1 최다 사용 토큰 TOP 30

| 순위 | 토큰 | 사용 컴포넌트 수 | 해당 컴포넌트 |
|:---:|------|:---:|------|
| 1 | `--spectrum-animation-duration-100` | **8** | button, card, checkbox, picker, table, tabs, tag, textfield |
| 2 | `--spectrum-focus-indicator-color` | **8** | button, card, checkbox, picker, table, tabs, tag, textfield |
| 3 | `--spectrum-focus-indicator-thickness` | **8** | button, card, checkbox, picker, table, tabs, tag, textfield |
| 4 | `--spectrum-component-height-100` | **7** | button, checkbox, dialog, picker, table, tag, textfield |
| 5 | `--spectrum-font-size-100` | **7** | button, checkbox, picker, table, tabs, tag, textfield |
| 6 | `--spectrum-font-size-200` | **7** | button, checkbox, picker, table, tabs, tag, textfield |
| 7 | `--spectrum-font-size-75` | **7** | button, checkbox, picker, table, tabs, tag, textfield |
| 8 | `--spectrum-component-height-200` | **6** | button, checkbox, picker, table, tag, textfield |
| 9 | `--spectrum-component-height-75` | **6** | button, checkbox, picker, table, tag, textfield |
| 10 | `--spectrum-font-size-300` | **6** | button, checkbox, picker, table, tabs, textfield |
| 11 | `--spectrum-corner-radius-100` | **6** | card, inlinealert, picker, table, tabs, textfield |
| 12 | `--spectrum-line-height-100` | **6** | checkbox, dialog, picker, table, tabs, tag |
| 13 | `--spectrum-component-height-300` | **5** | button, checkbox, picker, table, textfield |
| 14 | `--spectrum-disabled-content-color` | **5** | button, checkbox, picker, tag, textfield |
| 15 | `--spectrum-focus-indicator-gap` | **5** | button, checkbox, picker, tag, textfield |
| 16 | `--spectrum-neutral-content-color-default` | **5** | button, checkbox, picker, table, textfield |
| 17 | `--spectrum-text-to-visual-100` | **5** | button, picker, table, tabs, tag |
| 18 | `--spectrum-text-to-visual-200` | **5** | button, picker, table, tabs, tag |
| 19 | `--spectrum-workflow-icon-size-100` | **5** | button, inlinealert, tabs, tag, textfield |
| 20 | `--spectrum-component-top-to-text-100` | **5** | checkbox, picker, table, tag, textfield |
| 21 | `--spectrum-regular-font-weight` | **5** | dialog, picker, table, tag, textfield |
| 22 | `--spectrum-sans-font-family-stack` | **5** | card, inlinealert, table, tabs, textfield |
| 23 | `--spectrum-border-width-200` | **4** | button, checkbox, inlinealert, tabs |
| 24 | `--spectrum-neutral-content-color-hover` | **4** | button, checkbox, picker, textfield |
| 25 | `--spectrum-neutral-content-color-key-focus` | **4** | button, checkbox, picker, textfield |
| 26 | `--spectrum-text-to-visual-300` | **4** | button, picker, table, tabs |
| 27 | `--spectrum-text-to-visual-75` | **4** | button, picker, tabs, tag |
| 28 | `--spectrum-workflow-icon-size-200` | **4** | button, tabs, tag, textfield |
| 29 | `--spectrum-workflow-icon-size-75` | **4** | button, tabs, tag, textfield |
| 30 | `--spectrum-spacing-300` | **4** | card, dialog, inlinealert, table |

### 6.2 토큰 카테고리별 분포

| 카테고리 | 대표 토큰 | 사용 컴포넌트 수 |
|---------|----------|:---:|
| **Animation** | `--spectrum-animation-duration-100` | 8 |
| **Focus Indicator** | `--spectrum-focus-indicator-color/thickness/gap` | 5~8 |
| **Component Height** | `--spectrum-component-height-75/100/200/300` | 5~7 |
| **Font Size** | `--spectrum-font-size-75/100/200/300` | 6~7 |
| **Corner Radius** | `--spectrum-corner-radius-100` | 6 |
| **Spacing** | `--spectrum-spacing-100/200/300/400` | 2~4 |
| **Neutral Content Color** | `--spectrum-neutral-content-color-*` | 4~5 |
| **Disabled** | `--spectrum-disabled-content-color` | 5 |
| **Icon Size** | `--spectrum-workflow-icon-size-*` | 4~5 |
| **Text-to-Visual** | `--spectrum-text-to-visual-*` | 4~5 |
| **Typography** | `--spectrum-sans-font-family-stack`, `--spectrum-regular-font-weight` | 5 |

### 6.3 단일 컴포넌트 전용 토큰 (독점 의존)

아래 토큰 카테고리들은 특정 컴포넌트에서만 사용:

| 토큰 접두사 | 전용 컴포넌트 | 고유 토큰 수 |
|------------|:---:|:---:|
| `--spectrum-table-row-*` | table | ~60 |
| `--spectrum-table-thumbnail-*` | table | ~30 |
| `--spectrum-tab-item-*` | tabs | ~48 |
| `--spectrum-tag-border-color-*` | tag | ~20 |
| `--spectrum-picker-spacing-*` | picker | ~16 |
| `--spectrum-textfield-icon-*` | textfield | ~12 |
| `--spectrum-dialog-confirm-*` | dialog | ~13 |
| `--spectrum-card-title/body-*` | card | ~12 |

---

## 7. 아키텍처 패턴 분석

### 7.1 3-Layer Token 아키텍처

Spectrum CSS의 모든 컴포넌트는 일관된 3층 override 구조를 사용:

```
Layer 3 (최우선): --highcontrast-*  ← Windows High Contrast Mode 전용
Layer 2 (중간):   --mod-*           ← 소비자(Consumer) override API
Layer 1 (기본):   --spectrum-*      ← 디자인 시스템 글로벌/컴포넌트 토큰
```

**실제 CSS 패턴**:
```css
color: var(--highcontrast-checkbox-content-color-default,
       var(--mod-checkbox-content-color-default,
       var(--spectrum-checkbox-content-color-default)));
```

### 7.2 컴포넌트 내부 토큰 추상화

각 컴포넌트는 글로벌 토큰을 직접 참조하지 않고, 컴포넌트 전용 중간 토큰을 정의한 후 사용:

```css
/* Step 1: 글로벌 토큰 → 컴포넌트 토큰 매핑 */
.spectrum-Checkbox {
  --spectrum-checkbox-content-color-default: var(--spectrum-neutral-content-color-default);
}

/* Step 2: 컴포넌트 토큰 → 실제 속성에 적용 (3-layer override) */
.spectrum-Checkbox {
  color: var(--highcontrast-checkbox-content-color-default,
         var(--mod-checkbox-content-color-default,
         var(--spectrum-checkbox-content-color-default)));
}
```

이 패턴의 효과:
- 글로벌 토큰 변경 시 컴포넌트별 매핑만 수정하면 됨
- `--mod-*`으로 소비자 override 가능하면서도 시스템 기본값 유지
- `--highcontrast-*`로 접근성 모드 완전 분리

### 7.3 Size Variant 구현

T-shirt size는 별도 CSS 클래스에서 컴포넌트 토큰을 재정의하는 방식:

```css
.spectrum-Checkbox--sizeS {
  --spectrum-checkbox-font-size: var(--spectrum-font-size-75);
  --spectrum-checkbox-height: var(--spectrum-component-height-75);
  --spectrum-checkbox-control-size: var(--spectrum-checkbox-control-size-small);
}
```

모든 size variant가 글로벌 스케일 토큰(`-75`, `-100`, `-200`, `-300`)을 참조하므로, 스케일 시스템 변경이 자동으로 전파.

---

## 8. 결론 및 시사점

### 토큰화 성숙도

| 지표 | 값 | 평가 |
|------|-----|------|
| 평균 Token 의존율 | **98.9%** | 최상위 — 거의 모든 값이 토큰経由 |
| Hardcoded 값 총계 | **19개** (10개 컴포넌트) | 극소 — 대부분 0px 리셋 또는 fallback |
| `--mod-*` override API | **536개** 고유 훅 | 풍부한 소비자 커스터마이즈 표면 |
| `--highcontrast-*` WHCM 지원 | **134개** (8/10 컴포넌트) | 강력한 접근성 지원 |
| 고유 토큰 총계 | **1,121개** | 대규모이나 컴포넌트 내부 추상화 포함 |

### Figma↔Code 매핑 관점

1. **토큰 이름 일관성**: `--spectrum-{category}-{property}-{scale}` 규칙이 엄격히 유지되어 Figma Variables와의 1:1 매핑 용이
2. **컴포넌트 토큰 추상화 계층**: Figma의 Component-level token과 CSS의 `--spectrum-{component}-*` 토큰이 정확히 대응
3. **Variant 구조**: Figma의 Variant property(Size, State)가 CSS의 BEM modifier(`--sizeS`, `.is-selected`)와 직접 매핑
4. **Hardcoded 값의 성격**: 19개 중 대부분이 `0px` 리셋 또는 dialog 크기 fallback으로, 디자인 의도가 아닌 레이아웃 보정 — Figma 매핑에 영향 없음
5. **RGB 분리 패턴**: card의 `rgb(var(...-rgb), opacity)` 패턴은 Figma의 opacity 속성과 코드 간 구조적 불일치 야기 가능
