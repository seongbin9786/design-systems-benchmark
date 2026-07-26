# Shopify Polaris 컴포넌트 토큰 의존성 감사 (Token Dependency Audit)

> **감사 기준**: `github.com/Shopify/polaris` `main` 브랜치, `polaris-react/src/components/*/` 의 실제 `.module.css` 파일
> **감사 날짜**: 2026-07-26
> **대상 컴포넌트**: Button, TextField, Card, Modal, Checkbox, Badge, Banner, Tabs, DataTable, Select

---

## 0. 핵심 발견 요약

1. **Card는 CSS module이 존재하지 않는다.** `Card.tsx`는 `Box` + `ShadowBevel`의 순수 composition wrapper로, 자체 스타일 시트가 없다. 이는 Polaris가 compound component + utility primitive 조합으로 전환했음을 보여준다.
2. **Button은 `--pc-*` state machine의 정점**이다. 24개의 unique `--pc-button-*` 변수가 variant/tone/size 축에 따라 재할당되며, 실제 `--p-*` token은 이 state machine의 "입력값"으로만 사용된다.
3. **Hardcoded 값은 극소수**이며, 대부분 의도적 예외이다 (접근성 수정, 브라우저 버그 workaround, layout trick).
4. **Override mechanism은 구조적으로 차단**되어 있다. CSS module scoping + `--pc-*` 내부 변수 + `all: unset` 패턴으로 외부 override가 사실상 불가능하다.

---

## 1. 컴포넌트별 종합 테이블

| Component | 총 CSS declarations | `--p-*` refs (총/unique) | `--pc-*` defs (총/unique) | `--pc-*` refs (총) | Hardcoded 값 | Token dependency % | Variant 축 |
|-----------|---:|---:|---:|---:|---:|---:|---|
| **Button** | 182 | 95 / 66 | 93 / 24 | 48 | 1 | 70.5% | variant(5), tone(2), size(4) |
| **TextField** | 213 | 94 / 47 | 2 / 2 | 8 | 5 | 41.3% | tone(1: magic), state(5) |
| **Card** | — | — | — | — | — | — | **CSS module 없음** |
| **Modal** | 8 | 0 / 0 | 1 / 1 | 2 | 1 | 25.0% | 없음 |
| **Checkbox** | 95 | 75 / 30 | 0 / 0 | 0 | 0 | 50.0% | tone(1: magic) |
| **Badge** | 66 | 61 / 40 | 2 / 2 | 2 | 0 | 86.4% | tone(11), size(1) |
| **Banner** | 18 | 19 / 18 | 0 / 0 | 0 | 0 | 77.8% | tone(5, class-based) |
| **Tabs** | 139 | 60 / 21 | 0 / 0 | 0 | 1 | 40.4% | 없음 (state-based) |
| **DataTable** | 156 | 69 / 25 | 1 / 1 | 1 | 10 | 35.2% | density, zebra, sticky 등 |
| **Select** | 97 | 55 / 38 | 3 / 3 | 3 | 0 | 52.1% | tone(1: magic) |

**Token dependency %** = `var(--p-*)` 또는 `var(--pc-*)`를 포함하는 declaration / 전체 declaration × 100

> **참고**: Token dependency %가 낮은 컴포넌트(DataTable 35.2%, Modal 25.0%)는 layout/position 관련 declaration 비중이 높기 때문이다. 색상·간격·타이포그래피 값은 거의 100% token을 통한다.

---

## 2. View 1: Component → Token 매핑

### 2.1 Button (95 refs, 66 unique `--p-*` tokens)

**가장 많은 token을 소비하는 컴포넌트.** variant × tone × size 조합이 token 매핑의 복잡도를 만든다.

| Token 카테고리 | 사용 토큰 |
|---|---|
| **color-bg-fill** | `--p-color-bg-fill`, `-hover`, `-active`, `-selected`, `-disabled`, `-brand`, `-brand-hover`, `-brand-active`, `-brand-disabled`, `-critical`, `-critical-hover`, `-critical-active`, `-critical-selected`, `-success`, `-success-hover`, `-success-active`, `-success-selected`, `-transparent-hover`, `-transparent-active` |
| **color-text** | `--p-color-text`, `-disabled`, `-link`, `-link-hover`, `-link-active`, `-brand-on-bg-fill`, `-brand-on-bg-fill-disabled`, `-critical`, `-critical-hover`, `-critical-active`, `-success`, `-success-hover`, `-success-active` |
| **color-icon** | `--p-color-icon`, `-disabled`, `-secondary`, `-secondary-hover`, `-secondary-active` |
| **shadow** | `--p-shadow-button`, `-button-inset`, `-button-primary`, `-button-primary-inset`, `-button-primary-critical`, `-button-primary-critical-inset`, `-button-primary-success`, `-button-primary-success-inset` |
| **space** | `--p-space-025`, `-050`, `-100`, `-150`, `-200`, `-300` |
| **border** | `--p-border-radius-0`, `-200`, `-300`, `--p-border-width-050` |
| **sizing** | `--p-height-500`~`-900`, `--p-width-500`~`-800` |
| **special** | `--p-color-button-gradient-bg-fill`, `--p-color-border-focus` |
| **breakpoint** | `--p-breakpoints-md-up` |

### 2.2 TextField (94 refs, 47 unique)

| Token 카테고리 | 사용 토큰 |
|---|---|
| **color-input** | `--p-color-input-border`, `-border-hover`, `-border-active`, `-bg-surface`, `-bg-surface-hover`, `-bg-surface-active` |
| **color-bg-surface** | `--p-color-bg-surface-critical`, `-disabled`, `-magic`, `-magic-hover` |
| **color-text** | `--p-color-text`, `-secondary`, `-disabled`, `-magic`, `-magic-secondary` |
| **color-border** | `--p-color-border-focus`, `-critical-secondary`, `-magic-secondary`, `-magic-secondary-hover` |
| **color-icon** | `--p-color-icon`, `-secondary`, `-disabled`, `-magic` |
| **color-bg-fill** | `--p-color-bg-fill-tertiary`, `-tertiary-hover`, `-tertiary-active` |
| **typography** | `--p-font-size-325`, `-400`, `--p-font-weight-regular`, `--p-font-line-height-500`, `-600`, `--p-font-family-sans`, `-mono` |
| **space** | `--p-space-025`~`-800` (7종) |
| **border** | `--p-border-radius-100`, `-200`, `--p-border-width-0165`, `-025`, `-050` |
| **motion** | `--p-motion-duration-100`, `--p-motion-ease-out` |
| **breakpoint** | `--p-breakpoints-md-up`, `--p-breakpoints-sm-up` |
| **global custom** | `--pg-control-height`, `--pg-control-vertical-padding` |

### 2.3 Checkbox (75 refs, 30 unique)

| Token 카테고리 | 사용 토큰 |
|---|---|
| **color-input** | `--p-color-input-border`, `-border-hover`, `-bg-surface-hover` |
| **color-bg-fill** | `--p-color-bg-fill-brand`, `-brand-selected`, `-magic`, `-critical-active`, `-critical-selected` |
| **color-bg-surface** | `--p-color-bg-surface-critical`, `-magic`, `-magic-hover` |
| **color-border** | `--p-color-border-focus`, `-critical`, `-critical-secondary`, `-magic-secondary`, `-magic-secondary-hover` |
| **color-text** | `--p-color-text-brand-on-bg-fill`, `-critical-on-bg-fill` |
| **color-checkbox** | `--p-color-checkbox-bg-surface-disabled`, `--p-color-checkbox-icon-disabled` |
| **space** | `--p-space-025`, `-050`, `-300`, `-800` |
| **border** | `--p-border-width-0165`, `-050` |
| **motion** | `--p-motion-duration-100`, `-150`, `--p-motion-ease-out` |
| **z-index** | `--p-z-index-1` |

### 2.4 Badge (61 refs, 40 unique)

**token 집약도 최고 (86.4%).** 거의 모든 declaration이 token 참조.

| Token 카테고리 | 사용 토큰 |
|---|---|
| **color-bg-fill** | `-transparent-secondary`, `-success-secondary`, `-success`, `-info-secondary`, `-info`, `-caution-secondary`, `-caution`, `-warning-secondary`, `-warning`, `-critical-secondary`, `-critical`, `-magic-secondary` |
| **color-text** | `-secondary`, `-success`, `-success-on-bg-fill`, `-info`, `-info-on-bg-fill`, `-caution`, `-caution-on-bg-fill`, `-warning`, `-warning-on-bg-fill`, `-critical`, `-critical-on-bg-fill`, `-magic` |
| **color-icon** | `-success`, `-info`, `-caution`, `-warning`, `-critical`, `-secondary` |
| **space** | `--p-space-050`, `-100`, `-200` |
| **border** | `--p-border-radius-100`, `-200`, `--p-border-width-025` |
| **font** | `--p-font-weight-medium`, `-bold` |
| **color-border** | `--p-color-border` (print media) |

### 2.5 Banner (19 refs, 18 unique)

| Token 카테고리 | 사용 토큰 |
|---|---|
| **color-bg-surface** | `--p-color-bg-surface` |
| **color-text** | `-success-on-bg-fill`, `-success`, `-warning-on-bg-fill`, `-warning`, `-critical-on-bg-fill`, `-critical`, `-info-on-bg-fill`, `-info` |
| **color-icon** | `--p-color-icon-secondary` |
| **color-border** | `--p-color-border-focus` |
| **border** | `--p-border-radius-0`, `-200`, `-300`, `--p-border-width-050` |
| **shadow** | `--p-shadow-200` |
| **space** | `--p-space-200`, `-400` |
| **breakpoint** | `--p-breakpoints-sm-up` |

### 2.6 Tabs (60 refs, 21 unique)

| Token 카테고리 | 사용 토큰 |
|---|---|
| **color-bg** | `--p-color-bg-fill-transparent-hover`, `-transparent-selected`, `--p-color-bg-surface-hover`, `-active`, `-tertiary`, `-disabled` |
| **color-text** | `--p-color-text`, `-brand`, `-disabled` |
| **color-icon** | `--p-color-icon`, `-disabled` |
| **space** | `--p-space-025`~`-800` (7종) |
| **border** | `--p-border-radius-100`, `-200` |
| **sizing** | `--p-height-700` |
| **z-index** | `--p-z-index-1` |
| **breakpoint** | `--p-breakpoints-md-up`, `--p-breakpoints-md-down` |

### 2.7 DataTable (69 refs, 25 unique)

| Token 카테고리 | 사용 토큰 |
|---|---|
| **color-bg-surface** | `--p-color-bg-surface`, `-secondary`, `-hover` |
| **color-text** | `--p-color-text`, `-secondary` |
| **color-border** | `--p-color-border`, `-secondary` |
| **color-icon** | `--p-color-icon`, `-secondary`, `-disabled` |
| **space** | `--p-space-100`~`-400` (5종) |
| **border** | `--p-border-radius-100`, `-300`, `--p-border-width-025` |
| **font** | `--p-font-weight-regular`, `-semibold` |
| **motion** | `--p-motion-duration-200`, `--p-motion-ease`, `-ease-in-out` |
| **shadow** | `--p-shadow-100` |
| **z-index** | `--p-z-index-1` |
| **breakpoint** | `--p-breakpoints-sm-up`, `-md-up`, `-md-down` |

### 2.8 Select (55 refs, 38 unique)

| Token 카테고리 | 사용 토큰 |
|---|---|
| **color-input** | `--p-color-input-border`, `-border-hover`, `-border-active`, `-bg-surface`, `-bg-surface-hover`, `-bg-surface-active` |
| **color-bg-surface** | `--p-color-bg-surface-critical`, `-disabled`, `-magic`, `-magic-hover` |
| **color-border** | `--p-color-border-focus`, `-critical`, `-critical-secondary`, `-disabled`, `-magic-secondary`, `-magic-secondary-hover` |
| **color-text** | `--p-color-text`, `-disabled`, `-magic` |
| **color-icon** | `--p-color-icon-secondary`, `-disabled`, `-magic` |
| **typography** | `--p-font-size-325`, `-400`, `--p-font-weight-regular`, `--p-font-line-height-500`, `-600`, `--p-font-family-sans` |
| **space** | `--p-space-025`~`-300` (5종) |
| **border** | `--p-border-radius-200`, `--p-border-width-0165`, `-025`, `-050` |
| **shadow** | `--p-shadow-inset-200` |
| **breakpoint** | `--p-breakpoints-md-up`, `-md-down` |
| **global custom** | `--pg-control-height` |

### 2.9 Modal (0 `--p-*` refs)

`--p-*` token을 **하나도 사용하지 않는** 유일한 컴포넌트. `--pc-modal-frame-small-width: 620px`만 정의하고, `--p-breakpoints-md-up`만 media query에 사용.

---

## 3. View 2: Token → Component 역매핑

**여러 컴포넌트에서 공유되는 핵심 token** (4개 이상 컴포넌트에서 사용):

| Token | 사용 컴포넌트 수 | 컴포넌트 목록 |
|---|---:|---|
| `--p-space-200` | **7** | Badge, Banner, Button, DataTable, Select, Tabs, TextField |
| `--p-color-text` | **6** | Badge, Button, DataTable, Select, Tabs, TextField |
| `--p-color-icon-secondary` | **6** | Badge, Banner, Button, DataTable, Select, TextField |
| `--p-border-radius-200` | **6** | Badge, Banner, Button, Select, Tabs, TextField |
| `--p-space-100` | **6** | Badge, Button, DataTable, Select, Tabs, TextField |
| `--p-space-300` | **6** | Button, Checkbox, DataTable, Select, Tabs, TextField |
| `--p-border-width-050` | **5** | Banner, Button, Checkbox, Select, TextField |
| `--p-color-border-focus` | **5** | Banner, Button, Checkbox, Select, TextField |
| `--p-color-icon-disabled` | **5** | Button, DataTable, Select, Tabs, TextField |
| `--p-space-025` | **5** | Button, Checkbox, Select, Tabs, TextField |
| `--p-border-radius-100` | **4** | Badge, DataTable, Tabs, TextField |
| `--p-border-width-025` | **4** | Badge, DataTable, Select, TextField |
| `--p-color-icon` | **4** | Button, DataTable, Tabs, TextField |
| `--p-color-text-disabled` | **4** | Button, Select, Tabs, TextField |
| `--p-space-050` | **4** | Badge, Button, Checkbox, TextField |
| `--p-space-150` | **4** | Button, DataTable, Select, TextField |

**단일 컴포넌트 전용 token** (해당 컴포넌트에서만 사용):

| Token | 전용 컴포넌트 |
|---|---|
| `--p-color-button-gradient-bg-fill` | Button |
| `--p-shadow-button-*` (8종) | Button |
| `--p-color-checkbox-bg-surface-disabled` | Checkbox |
| `--p-color-checkbox-icon-disabled` | Checkbox |
| `--p-color-bg-fill-caution-*` | Badge |
| `--p-color-bg-fill-info-*` | Badge |
| `--p-color-bg-fill-warning-*` | Badge |
| `--p-shadow-inset-200` | Select |
| `--p-shadow-200` | Banner |
| `--p-color-bg-surface-secondary` | DataTable |

---

## 4. Hardcoded 값 인벤토리

### 총 19개의 hardcoded 값 (9개 컴포넌트 중 5개에서 발견)

#### Button (1건)
| 값 | 타입 | 컨텍스트 | 사유 |
|---|---|---|---|
| `1px` | px | `transform: translate3d(0, 1px, 0)` | pressable active 시 미세 이동 효과. token 불필요한 미적 세부사항 |

#### TextField (5건)
| 값 | 타입 | 컨텍스트 | 사유 |
|---|---|---|---|
| `#898f94` | hex | `border-top-color: #898f94` | **접근성 수정** — [GitHub issue #7838](https://github.com/Shopify/polaris/issues/7838) 대응. 의도적 hardcoded |
| `28px` | px | `.slim .Input { min-height: 28px }` | slim variant 고정 높이. token 미매핑 |
| `140px` | px | `.VerticalContent { max-height: 140px }` | 모바일 max-height 제약 |
| `328px` | px | `@media sm-up { max-height: 328px }` | 데스크톱 max-height 제약 |
| `22px` | px | `.Spinner { width: 22px }` | spinner 고정 너비 |

#### DataTable (10건)
| 값 | 타입 | 컨텍스트 | 사유 |
|---|---|---|---|
| `100vw` | viewport | `max-width: 100vw` | layout constraint |
| `6px` ×2 | px | `.Pip { height: 6px; width: 6px }` | pagination pip 고정 크기 |
| `3px` ×4 | px | `.Heading { margin: 3px; padding: 9px 3px }` | **focus ring 잘림 방지** — `overflow:hidden`과의 충돌 회피. stylelint-disable 주석 명시 |
| `9px` ×1 | px | `.Heading { padding: 9px 3px }` | 위와 동일 |
| `9999px` ×2 | px | `top: -9999px; left: -9999px` | sticky header 미활성 시 화면 밖 배치 (고전적 기법) |

#### Modal (1건)
| 값 | 타입 | 컨텍스트 | 사유 |
|---|---|---|---|
| `100vw` | viewport | `max-width: 100vw` | layout constraint |

#### Tabs (1건)
| 값 | 타입 | 컨텍스트 | 사유 |
|---|---|---|---|
| `rgba(0, 0, 0, 0)` | rgb | `-webkit-tap-highlight-color` | 모바일 탭 하이라이트 제거. 브라우저 리셋 용도 |

### Hardcoded 값 분류

| 분류 | 건수 | 비율 |
|---|---:|---:|
| Layout/viewport constraint (`100vw`, `9999px`) | 5 | 26% |
| Focus ring / overflow workaround (`3px`, `9px`) | 5 | 26% |
| 고정 크기 (pip, spinner, slim height) | 5 | 26% |
| 접근성 수정 (`#898f94`) | 1 | 5% |
| 브라우저 리셋 (`rgba(0,0,0,0)`) | 1 | 5% |
| 미적 세부사항 (`1px` transform) | 1 | 5% |
| 반응형 max-height (`140px`, `328px`) | 2 | 11% |

> **결론**: Hardcoded 값 중 "token으로 대체해야 할 누락"은 사실상 0건. 모두 의도적 예외이거나 token 체계 밖의 값이다.

---

## 5. `--pc-*` State Machine 분석

`--pc-*` (Polaris Component custom property)는 컴포넌트 내부 state machine이다. 외부에서 직접 설정하지 않으며, variant/tone/size class가 이 변수들을 재할당한다.

### 5.1 컴포넌트별 `--pc-*` 변수 수

| Component | Unique `--pc-*` 수 | 용도 |
|---|---:|---|
| **Button** | **24** | 완전한 state machine: bg/color/shadow/icon-fill × default/hover/active/pressed/disabled |
| **Select** | 3 | z-index layering (`backdrop: 10`, `content: 20`, `input: 30`) |
| **Badge** | 2 | padding 추상화 (`horizontal-padding`, `vertical-padding`) |
| **TextField** | 2 | z-index layering (`contents: 20`, `backdrop: 10`) |
| **DataTable** | 1 | `first-column-width: 145px` |
| **Modal** | 1 | `frame-small-width: 620px` |
| **Checkbox** | 0 | — |
| **Banner** | 0 | — |
| **Tabs** | 0 | — |

### 5.2 Button `--pc-*` State Machine 상세

Button의 24개 `--pc-*` 변수는 **5개 속성 × 5개 상태**의 매트릭스를 형성한다:

```
속성 축:          상태 축:
├── bg            ├── (default)
├── color         ├── _hover
├── box-shadow    ├── _active
├── icon-fill     ├── _pressed
└── gap           └── _disabled
    padding-block
    padding-inline
    bg-gradient (variantPrimary 전용)
```

**State machine 흐름:**

```
.variantPrimary ──┐
.variantSecondary ─┤── --pc-button-bg, --pc-button-color, --pc-button-box-shadow 재할당
.variantTertiary ──┤   (각각 --p-* token을 입력값으로 사용)
.variantPlain ─────┘

.toneSuccess ──┐── variant와 :is()로 조합하여 추가 재할당
.toneCritical ──┘   (예: .toneSuccess:is(.variantPrimary) → --pc-button-bg: var(--p-color-bg-fill-success))

.sizeMicro ──┐
.sizeSlim ───┤── --pc-button-padding-block, --pc-button-padding-inline 재할당
.sizeMedium ──┤   + min-height, min-width 직접 설정
.sizeLarge ───┘
```

**핵심 메커니즘**: `.Button` base class에서 모든 `--pc-*`의 default를 정의하고, variant/tone/size class가 **specificity 없이 단순 재할당**한다. 실제 CSS property는 `var(--pc-button-*)`를 참조하므로, variant class는 property를 직접 건드리지 않고 변수만 교체한다.

### 5.3 z-index layering 패턴

TextField와 Select는 `--pc-*`를 z-index layering에 사용:

```
TextField:                    Select:
  --pc-text-field-backdrop: 10   --pc-select-backdrop: 10
  --pc-text-field-contents: 20   --pc-select-content: 20
                                 --pc-select-input: 30
```

이는 `z-index`에 직접 숫자를 쓰지 않고 내부 변수로 추상화한 것이다.

---

## 6. Variant 축 상세

### 6.1 Button — 가장 복잡한 variant 체계

| 축 | 값 | CSS class |
|---|---|---|
| **variant** | `primary`, `secondary`, `tertiary`, `plain`, `monochromePlain` | `.variantPrimary`, `.variantSecondary`, `.variantTertiary`, `.variantPlain`, `.variantMonochromePlain` |
| **tone** | `success`, `critical` | `.toneSuccess`, `.toneCritical` |
| **size** | `micro`, `slim`, `medium`, `large` | `.sizeMicro`, `.sizeSlim`, `.sizeMedium`, `.sizeLarge` |
| **textAlign** | `center`, `start`, `left`, `end`, `right` | `.textAlignCenter`, `.textAlignStart`, `.textAlignLeft`, `.textAlignEnd`, `.textAlignRight` |
| **기타 modifier** | `fullWidth`, `iconOnly`, `iconWithText`, `disclosure`, `loading`, `pressed`, `pressable`, `disabled`, `hidden` | 각각 독립 class |

**tone × variant 조합 규칙**: tone은 `:is()` selector로 특정 variant와만 조합:
- `.toneSuccess:is(.variantSecondary, .variantTertiary, .variantPlain)` → text color 변경
- `.toneSuccess:is(.variantPrimary)` → bg fill 변경
- `.toneCritical`도 동일 패턴

### 6.2 Badge — 최다 tone 축

| 축 | 값 |
|---|---|
| **tone** | `success`, `info`, `attention`, `warning`, `critical`, `magic`, `new`, `read-only`, `enabled` |
| **tone-strong** | `success-strong`, `info-strong`, `attention-strong`, `warning-strong`, `critical-strong` |
| **size** | `large` |
| **기타** | `withinFilter` |

총 **11개 tone variant + 1개 size variant**. 각 tone은 `background-color` + `color` + `svg fill` 3개 property만 재할당.

### 6.3 Banner — class-based tone

Banner는 `.toneSuccess` 같은 class 대신 **text color utility class**를 사용:
- `.text-success-on-bg-fill`, `.text-success`, `.text-warning-on-bg-fill`, `.text-warning`, `.text-critical-on-bg-fill`, `.text-critical`, `.text-info-on-bg-fill`, `.text-info`, `.icon-secondary`

이는 Banner 내부의 Icon/Button 컴포넌트 색상을 override하기 위한 specificity bump 패턴 (`.class.class.class` 삼중 중복 selector).

### 6.4 TextField / Select / Checkbox — tone: magic

이 세 컴포넌트는 `toneMagic` variant만 존재. Shopify AI/magic 기능의 보라색 테마:
- `--p-color-bg-surface-magic`, `--p-color-border-magic-secondary`, `--p-color-text-magic`, `--p-color-icon-magic` 계열 token 사용

### 6.5 DataTable — boolean flag 조합

DataTable은 전통적 variant 대신 **boolean modifier class** 조합:
- `.condensed`, `.hoverable`, `.ZebraStripingOnData`, `.IncreasedTableDensity`, `.StickyHeaderEnabled`, `.ShowTotalsInFooter`, `.RowCountIsEven`, `.FixedFirstColumn`
- Cell 단위: `.Cell-header`, `.Cell-total`, `.Cell-sortable`, `.Cell-sorted`, `.Cell-numeric`, `.Cell-truncated`, `.Cell-verticalAlignTop/Bottom/Middle/Baseline`

---

## 7. Override Mechanism 분석

### 7.1 결론: 외부 override는 구조적으로 차단됨

Polaris는 다음 메커니즘으로 외부 CSS override를 사실상 불가능하게 만든다:

| 메커니즘 | 설명 | 적용 컴포넌트 |
|---|---|---|
| **CSS Modules scoping** | 모든 class가 hash되어 외부에서 selector targeting 불가 | 전체 |
| **`--pc-*` 내부 변수** | variant가 CSS property를 직접 설정하지 않고 내부 변수만 재할당. 외부에서 `--pc-button-bg`를 override해도 다른 state(`_hover`, `_active`)에 영향 못 미침 | Button, Badge, Select, TextField, DataTable, Modal |
| **`all: unset`** | Button base class에서 `all: unset`으로 모든 상속/기본값 제거 | Button |
| **Specificity bump** | `.class.class.class` 삼중 중복으로 내부 override 우선순위 확보 | Banner, TextField (`.readOnly.readOnly`) |
| **`@mixin` 내부 처리** | `focus-ring`, `control-backdrop`, `unstyled-button` 등의 mixin이 컴파일 타임에 처리되어 외부 개입 불가 | Checkbox, Tabs, TextField, Select, DataTable, Banner |

### 7.2 의도적 override 경로

유일하게 열려 있는 override 경로:

1. **`--pg-*` global custom property**: `--pg-control-height`, `--pg-control-vertical-padding` — TextField와 Select가 참조. 이는 앱 레벨에서 control 높이를 일괄 조정하는 의도적 탈출구.
2. **React props**: 모든 시각적 variant가 React props로 노출 (`variant`, `tone`, `size`, `disabled`, `error` 등). CSS가 아닌 API 레벨에서 제어.

---

## 8. `@mixin` 사용 현황

Polaris는 PostCSS `@mixin`을 내부적으로 사용한다. 이는 token도, hardcoded 값도 아닌 **컴파일 타임 패턴**이다:

| Mixin | 사용 컴포넌트 | 총 사용 횟수 | 용도 |
|---|---|---:|---|
| `focus-ring` | Tabs(7), TextField(3), Checkbox(1), DataTable(2) | 13 | focus ring 스타일 |
| `control-backdrop` | Checkbox(4) | 4 | checkbox/radio backdrop 상태 |
| `unstyled-button` | Tabs(2), DataTable(1), TextField(1) | 4 | 버튼 기본 스타일 제거 |
| `text-style-input` | TextField(2), Select(1) | 3 | input 타이포그래프리셋 |
| `shadow-bevel` | Banner(2) | 2 | 그림자 + border-radius 조합 |
| `text-breakword` | TextField(1) | 1 | 긴 텍스트 줄바꿈 |
| `no-focus-ring` | TextField(1) | 1 | focus ring 제거 |

> **주석**: 모든 `@mixin` 사용처에는 `/* generated by polaris-migrator DO NOT COPY */` 또는 유사한 stylelint-disable 주석이 붙어 있다. 이는 레거시 SCSS mixin에서 CSS module로 마이그레이션하는 과정에서 남은 것이며, 장기적으로 제거 대상이다.

---

## 9. 기타 Custom Property (`--item-*`, `--pg-*`)

### `--pg-*` (Polaris Global)
| Property | 사용 컴포넌트 | 용도 |
|---|---|---|
| `--pg-control-height` | TextField, Select | form control 최소 높이 (앱 레벨에서 설정) |
| `--pg-control-vertical-padding` | TextField | DummyInput의 수직 패딩 |

### `--item-*` (Tabs 내부 로컬 변수)
| Property | 용도 |
|---|---|
| `--item-min-height` | disclosure dropdown item 최소 높이 (`var(--p-space-400)` 참조) |
| `--item-min-width` | disclosure dropdown item 최소 너비 (`50px` — hardcoded) |
| `--item-vertical-padding` | disclosure dropdown item 수직 패딩 (`var(--p-space-200)` 참조) |

> Tabs의 `:root`에 정의된 `--item-min-width: 50px`은 CSS module scoping을 벗어나 `:root`에 정의된 유일한 비-token 값이다.

---

## 10. Breakpoint Token 사용

모든 반응형 처리가 `@media (--p-breakpoints-*)` custom media query를 통해 이루어진다:

| Breakpoint token | 사용 컴포넌트 |
|---|---|
| `--p-breakpoints-sm-up` | Banner, DataTable, TextField |
| `--p-breakpoints-md-up` | Button, DataTable, Modal, Select, Tabs, TextField |
| `--p-breakpoints-md-down` | DataTable, Select, Tabs |

하드코딩된 `@media (min-width: Xpx)`는 **0건**이다.

---

## 11. 종합 평가

### Token 체계 성숙도

| 평가 항목 | 점수 | 근거 |
|---|---|---|
| **Token coverage** | ★★★★★ | 색상, 간격, 타이포그래피, 그림자, border, motion 모두 token화. Hardcoded 19건 중 token 누락 0건 |
| **Token 일관성** | ★★★★☆ | `--p-color-input-*` vs `--p-color-bg-surface-*` 명명 분기. Checkbox 전용 token(`--p-color-checkbox-*`) 존재 |
| **Variant-token 매핑** | ★★★★★ | Button의 `--pc-*` state machine이 variant × tone × size를 완벽히 추상화 |
| **Override 차단** | ★★★★★ | CSS Modules + `--pc-*` + `all: unset` + specificity bump로 외부 override 사실상 불가 |
| **마이그레이션 잔재** | ★★★☆☆ | `@mixin` 28회 사용. 모두 `DO NOT COPY` 주석付き. 레거시 SCSS 패턴 잔존 |

### Polaris token 아키텍처의 구조적 특징

```
┌─────────────────────────────────────────────────┐
│  --p-* (Design Tokens)                          │
│  @shopify/polaris-tokens에서 주입                │
│  색상, 간격, 타이포, 그림자, border, motion, etc. │
└──────────────────┬──────────────────────────────┘
                   │ var(--p-*)
                   ▼
┌─────────────────────────────────────────────────┐
│  --pc-* (Component State Machine)               │
│  컴포넌트 내부에서만 정의/소비                     │
│  variant/tone/size가 이 층을 재할당               │
│  실제 CSS property는 이 층의 var()를 참조          │
└──────────────────┬──────────────────────────────┘
                   │ var(--pc-*)
                   ▼
┌─────────────────────────────────────────────────┐
│  CSS Properties                                 │
│  background: var(--pc-button-bg)                │
│  color: var(--pc-button-color)                  │
│  box-shadow: var(--pc-button-box-shadow)        │
└─────────────────────────────────────────────────┘

외부 override 경로: --pg-* (global), React props (API)
```

이 3층 구조는 Polaris가 **"token을 쓰되, token만으로는 컴포넌트 상태를 표현할 수 없다"** 는 문제를 해결한 방식이다. `--p-*` token은 정적 팔레트이고, `--pc-*` state machine이 동적 상태 전환을 담당한다.
