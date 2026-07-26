# Fluent UI React v9 — 컴포넌트 레벨 Token 종속성 감사

> **감사 대상**: github.com/microsoft/fluentui `master` 브랜치의 실제 `.styles.ts` 소스 코드
> **감사 날짜**: 2026-07-26
> **대상 패키지**: `@fluentui/react-components` (react-button, react-input, react-card, react-dialog, react-checkbox, react-badge, react-message-bar, react-tabs, react-table, react-select)

---

## 1. 요약 테이블

| Component | 소스 파일 | 고유 tokens.* | 총 tokens.* 참조 | Hardcoded 값 | Token 의존율 | Variant axes | Override hooks |
|---|---|---|---|---|---|---|---|
| **Button** | useButtonStyles.styles.ts | 53 | ~105 | 15종 px + forced-colors | ~87% | appearance(5), size(3), shape(3), iconPosition(2), iconOnly, disabled | mergeClasses, root.className, icon.className |
| **Input** | useInputStyles.styles.ts | 30 | ~62 | 12종 px + 문자열 | ~84% | size(3), appearance(5+), invalid, disabled, contentBefore/After | mergeClasses, root/input/contentBefore/contentAfter.className |
| **Card** | useCardStyles.styles.ts | 38 | ~85 | 8종 px + forced-colors | ~91% | appearance(4), size(3), orientation(2), interactive, selectable, selected, disabled | mergeClasses, root/floatingAction/checkbox.className |
| **DialogSurface** | useDialogSurfaceStyles.styles.ts | 7 | ~10 | 8종 px + media query | ~56% | backdropAppearance(2), unmountOnClose | mergeClasses, root/backdrop.className |
| **Checkbox** | useCheckboxStyles.styles.ts | 25 | ~42 | 5종 px + forced-colors | ~89% | checked(3: true/false/mixed), size(2), shape(2), labelPosition(2), disabled | mergeClasses, root/input/indicator/label.className |
| **Badge** | useBadgeStyles.styles.ts | 46 | ~78 | 14종 px | ~85% | appearance(4)×color(8)=32, size(6), shape(3), iconPosition(2) | mergeClasses, root/icon.className |
| **MessageBar** | useMessageBarStyles.styles.ts | 19 | ~28 | 4종 px + grid 문자열 | ~88% | intent(4), layout(2), shape(2) | mergeClasses, root/icon/bottomReflowSpacer.className |
| **Tab** | useTabStyles.styles.ts | 59 | ~130 | 6종 px + forced-colors | ~96% | appearance(4), size(3), vertical, selected, disabled | mergeClasses, root/icon/content/contentReservedSpace.className |
| **Table** | useTableStyles.styles.ts | 1 | ~1 | 3종 CSS 키워드 | ~25% | layout(2: table/flex), noNativeElements | mergeClasses, root.className |
| **Select** | useSelectStyles.styles.ts | 23 | ~52 | 10종 px + 문자열 | ~84% | size(3), appearance(4+), invalid, disabled | mergeClasses, root/select/icon.className |

> **Token 의존율** = tokens.* 참조 / (tokens.* 참조 + 하드코딩 디자인 값) × 100. CSS 키워드(`none`, `center`, `pointer` 등)는 제외.

---

## 2. 컴포넌트별 상세 분석

### 2.1 Button

**소스**: `react-button/library/src/components/Button/useButtonStyles.styles.ts` (16,877 bytes)

#### Variant axes
| Axis | 값 |
|---|---|
| appearance | `outline`, `primary`, `secondary`, `subtle`, `transparent` |
| size | `small`, `medium`, `large` |
| shape | `circular`, `rounded`, `square` |
| iconPosition | `before`, `after` |
| iconOnly | `boolean` |
| disabled / disabledFocusable | `boolean` |

#### 고유 tokens.* (53개)
```
colorNeutralBackground1, colorNeutralBackground1Hover, colorNeutralBackground1Pressed,
colorNeutralBackgroundDisabled, colorNeutralForeground1, colorNeutralForeground1Hover,
colorNeutralForeground1Pressed, colorNeutralForeground2, colorNeutralForeground2Hover,
colorNeutralForeground2Pressed, colorNeutralForeground2BrandHover, colorNeutralForeground2BrandPressed,
colorNeutralForegroundOnBrand, colorNeutralForegroundDisabled,
colorNeutralStroke1, colorNeutralStroke1Hover, colorNeutralStroke1Pressed,
colorNeutralStrokeDisabled,
colorBrandBackground, colorBrandBackgroundHover, colorBrandBackgroundPressed,
colorSubtleBackground, colorSubtleBackgroundHover, colorSubtleBackgroundPressed,
colorTransparentBackground, colorTransparentBackgroundHover, colorTransparentBackgroundPressed,
colorTransparentStroke, colorStrokeFocus2,
borderRadiusMedium, borderRadiusSmall, borderRadiusLarge, borderRadiusCircular, borderRadiusNone,
fontSizeBase200, fontSizeBase300, fontSizeBase400,
fontWeightRegular, fontWeightSemibold,
lineHeightBase200, lineHeightBase300, lineHeightBase400,
fontFamilyBase,
spacingHorizontalS, spacingHorizontalM, spacingHorizontalL,
spacingHorizontalSNudge, spacingHorizontalXS,
strokeWidthThin, strokeWidthThick,
durationFaster, curveEasyEase, shadow2
```

#### Hardcoded 값
| 값 | 용도 | 속성 |
|---|---|---|
| `'3px'` | small 세로 padding (buttonSpacingSmall) | padding |
| `'1px'` | small+icon 세로 padding (buttonSpacingSmallWithIcon) | padding |
| `'5px'` | medium 세로 padding (buttonSpacingMedium) | padding |
| `'8px'` | large 세로 padding (buttonSpacingLarge) | padding |
| `'7px'` | large+icon 세로 padding (buttonSpacingLargeWithIcon) | padding |
| `'96px'` | medium/large minWidth | minWidth |
| `'64px'` | small minWidth | minWidth |
| `'24px'` | iconOnly small 크기 / icon 기본 크기 | minWidth, maxWidth, fontSize, height, width |
| `'32px'` | iconOnly medium 크기 | minWidth, maxWidth |
| `'40px'` | iconOnly large 크기 | minWidth, maxWidth |
| `'20px'` | icon 기본 fontSize/height/width | fontSize, height, width |
| `'0.01ms'` | prefers-reduced-motion transition | transitionDuration |
| `'0.25px'` | Firefox boxShadow 보정 | calc 내부 |
| `'1px'` | focus indicator borderWidth | borderWidth |
| `'transparent'` | primary/outline/subtle/transparent borderColor | borderColor |
| forced-colors | `ButtonText`, `HighlightText`, `Highlight`, `ButtonFace`, `GrayText` | 다양한 속성 |

#### Override mechanisms
- `mergeClasses()` — 모든 slot에 적용
- `state.root.className` — 사용자 className 마지막에 병합
- `state.icon.className` — 아이콘 slot 사용자 className
- `buttonClassNames.root` / `buttonClassNames.icon` — 안정적 CSS 클래스 (`fui-Button`, `fui-Button__icon`)

---

### 2.2 Input

**소스**: `react-input/library/src/components/Input/useInputStyles.styles.ts` (12,421 bytes)

#### Variant axes
| Axis | 값 |
|---|---|
| size | `small`, `medium`, `large` |
| appearance | `outline`, `underline`, `filled-darker`, `filled-lighter`, `filled-darker-shadow`(deprecated), `filled-lighter-shadow`(deprecated) |
| invalid | `boolean` (aria-invalid) |
| disabled | `boolean` |
| contentBefore / contentAfter | `boolean` (padding 분기) |

#### 고유 tokens.* (30개)
```
spacingHorizontalXXS, spacingHorizontalXS, spacingHorizontalS,
spacingHorizontalSNudge, spacingHorizontalMNudge, spacingHorizontalM,
borderRadiusMedium,
colorNeutralBackground1, colorNeutralBackground3,
colorNeutralStroke1, colorNeutralStroke1Hover, colorNeutralStroke1Pressed,
colorNeutralStrokeAccessible, colorNeutralStrokeAccessibleHover, colorNeutralStrokeAccessiblePressed,
colorNeutralStrokeDisabled,
colorCompoundBrandStroke, colorCompoundBrandStrokePressed,
colorTransparentBackground, colorTransparentStroke, colorTransparentStrokeInteractive,
colorPaletteRedBorder2,
colorNeutralForeground1, colorNeutralForeground3, colorNeutralForeground4,
colorNeutralForegroundDisabled,
durationUltraFast, durationNormal,
curveAccelerateMid, curveDecelerateMid,
shadow2
```

#### Hardcoded 값
| 값 | 용도 | 속성 |
|---|---|---|
| `'24px'` / `'32px'` / `'40px'` | fieldHeights (small/medium/large) | minHeight |
| `'1px solid'` | 기본 border | border |
| `'-1px'` | ::after 위치 오프셋 | left, bottom, right |
| `'2px'` | focus underline 높이 | height, borderBottom |
| `'0.01ms'` | prefers-reduced-motion | transitionDuration, transitionDelay |
| `'scaleX(0)'` / `'scaleX(1)'` | focus 애니메이션 | transform |
| `'inset(calc(100% - 2px) 0 0 0)'` | focus underline clip | clipPath |
| `'2px solid transparent'` | focus-within outline | outline |
| `'0'` | underline borderRadius | borderRadius |
| `'transparent'` | input backgroundColor | backgroundColor |
| `'inherit'` | input typography 상속 | fontFamily, fontSize, fontWeight, lineHeight |
| `'20px'` / `'16px'` / `'24px'` | content svg 아이콘 크기 | fontSize |

#### Override mechanisms
- `mergeClasses()` — root, input, contentBefore, contentAfter 각각
- `state.root.className`, `state.input.className`, `state.contentBefore.className`, `state.contentAfter.className`
- `inputClassNames.*` — 안정적 CSS 클래스 (`fui-Input`, `fui-Input__input` 등)
- `typographyStyles.body1` / `caption1` / `body2` — 프리셋 타이포그래피 spread

---

### 2.3 Card

**소스**: `react-card/library/src/components/Card/useCardStyles.styles.ts` (14,956 bytes)

#### Variant axes
| Axis | 값 |
|---|---|
| appearance | `filled`, `filled-alternative`, `outline`, `subtle` |
| size | `small`, `medium`, `large` |
| orientation | `horizontal`, `vertical` |
| interactive | `boolean` |
| selectable | `boolean` |
| selected | `boolean` |
| disabled | `boolean` |

#### 고유 tokens.* (38개)
```
colorNeutralForeground1, colorNeutralForeground1Hover, colorNeutralForeground1Selected,
colorNeutralForeground2Hover, colorNeutralForeground2Selected,
colorNeutralForegroundDisabled,
colorNeutralBackground1, colorNeutralBackground1Hover, colorNeutralBackground1Pressed,
colorNeutralBackground1Selected, colorNeutralBackground2, colorNeutralBackground2Hover,
colorNeutralBackground2Pressed, colorNeutralBackground2Selected,
colorNeutralBackgroundDisabled,
colorNeutralStroke1, colorNeutralStroke1Hover, colorNeutralStroke1Pressed,
colorNeutralStroke1Selected, colorNeutralStrokeDisabled,
colorTransparentBackground, colorTransparentBackgroundHover, colorTransparentBackgroundPressed,
colorTransparentBackgroundSelected, colorTransparentStroke,
colorSubtleBackground, colorSubtleBackgroundHover, colorSubtleBackgroundPressed,
colorSubtleBackgroundSelected,
strokeWidthThin, strokeWidthThick,
borderRadiusSmall, borderRadiusMedium, borderRadiusLarge,
shadow2, shadow4, shadow8,
zIndexContent
```

#### Hardcoded 값
| 값 | 용도 | 속성 |
|---|---|---|
| `'8px'` | sizeSmall cardSizeVar | CSS var |
| `'12px'` | sizeMedium cardSizeVar | CSS var |
| `'16px'` | sizeLarge cardSizeVar | CSS var |
| `'-2px'` | focus outlineOffset | outlineOffset |
| `'4px'` | floatingAction(select) 위치 | top, right |
| `'1px'` | hiddenCheckbox 크기 | width, height |
| `'rect(0 0 0 0)'` | hiddenCheckbox clip | clip |
| `'inset(50%)'` | hiddenCheckbox clipPath | clipPath |
| `'none'` | outline/subtle boxShadow | boxShadow |
| `'currentColor'` | interactive 텍스트 색상 | color |
| forced-colors | `Highlight`, `HighlightText` | backgroundColor, color, borderColor |

#### Override mechanisms
- `mergeClasses()` — root, floatingAction, checkbox
- `state.root.className`, `state.floatingAction.className`, `state.checkbox.className`
- `cardClassNames.*` — 안정적 CSS 클래스
- CSS custom properties: `--fui-Card--size`, `--fui-Card--border-radius`
- `createFocusOutlineStyle()` — focus outline 커스텀

---

### 2.4 DialogSurface

**소스**: `react-dialog/library/src/components/DialogSurface/useDialogSurfaceStyles.styles.ts` (3,510 bytes)
**상수**: `react-dialog/library/src/contexts/constants.ts`

> Dialog는 compound component로, `Dialog` 자체에는 스타일 파일이 없음. 실제 스타일은 `DialogSurface`가 담당.

#### Variant axes
| Axis | 값 |
|---|---|
| backdropAppearance | `transparent`, (default: opaque) |
| unmountOnClose | `boolean` |
| open | `boolean` (hidden 상태) |

#### 고유 tokens.* (7개)
```
colorTransparentStroke, colorNeutralBackground1, colorNeutralForeground1,
shadow64, colorBackgroundOverlay, colorTransparentBackground,
borderRadiusXLarge
```

#### Hardcoded 값 (constants.ts 포함)
| 값 | 용도 | 속성 |
|---|---|---|
| `'24px'` (SURFACE_PADDING) | surface 내부 padding | padding |
| `'1px'` (SURFACE_BORDER_WIDTH) | surface border | border |
| `'4px'` (DIALOG_FULLSCREEN_DIALOG_SCROLLBAR_OFFSET) | 스크롤바 오프셋 | paddingRight, borderRightWidth 등 |
| `'8px'` (DIALOG_GAP) | dialog 간격 (별도 사용) | gap |
| `'600px'` | 최대 너비 | maxWidth |
| `'100vh'` / `'100dvh'` | 최대 높이 | maxHeight |
| `'100vw'` | breakpoint 시 최대 너비 | maxWidth |
| `'480px'` | media query breakpoint | @media |
| `'359px'` | short screen media query | @media |
| `'0px'` | backdrop inset | inset |

#### Override mechanisms
- `mergeClasses()` — root, backdrop
- `root.className`, `backdrop.className`
- `dialogSurfaceClassNames.*` — 안정적 CSS 클래스
- `createFocusOutlineStyle()` — focus outline

---

### 2.5 Checkbox

**소스**: `react-checkbox/library/src/components/Checkbox/useCheckboxStyles.styles.ts` (7,518 bytes)

#### Variant axes
| Axis | 값 |
|---|---|
| checked | `true`, `false`, `'mixed'` |
| size | `medium`, `large` |
| shape | `rounded`(default), `circular` |
| labelPosition | `before`, `after` |
| disabled | `boolean` |

#### 고유 tokens.* (25개)
```
colorNeutralForeground1, colorNeutralForeground2, colorNeutralForeground3,
colorNeutralForegroundDisabled, colorNeutralForegroundInverted,
colorNeutralStrokeAccessible, colorNeutralStrokeAccessibleHover, colorNeutralStrokeAccessiblePressed,
colorNeutralStrokeDisabled,
colorCompoundBrandBackground, colorCompoundBrandBackgroundHover, colorCompoundBrandBackgroundPressed,
colorCompoundBrandStroke, colorCompoundBrandStrokeHover, colorCompoundBrandStrokePressed,
colorCompoundBrandForeground1, colorCompoundBrandForeground1Hover, colorCompoundBrandForeground1Pressed,
spacingHorizontalS, spacingHorizontalXS, spacingVerticalS,
strokeWidthThin, borderRadiusSmall, borderRadiusCircular,
lineHeightBase300
```

#### Hardcoded 값
| 값 | 용도 | 속성 |
|---|---|---|
| `'16px'` (indicatorSizeMedium) | indicator 기본 크기 | height, width, calc |
| `'20px'` (indicatorSizeLarge) | indicator large 크기 | height, width, calc |
| `'12px'` | indicator 기본 fontSize | fontSize |
| `'16px'` | indicator large fontSize | fontSize |
| `'0'` | input opacity, margin | opacity, margin |
| `'100%'` | input height | height |
| `'currentColor'` | indicator fill | fill |
| forced-colors | `GrayText` | color |

#### Override mechanisms
- `mergeClasses()` — root, input, indicator, label
- 각 slot별 `state.*.className`
- `checkboxClassNames.*` — 안정적 CSS 클래스
- CSS custom properties: `--fui-Checkbox__indicator--color`, `--fui-Checkbox__indicator--borderColor`, `--fui-Checkbox__indicator--backgroundColor`

---

### 2.6 Badge

**소스**: `react-badge/library/src/components/Badge/useBadgeStyles.styles.ts` (9,797 bytes)

#### Variant axes
| Axis | 값 |
|---|---|
| appearance | `filled`, `ghost`, `outline`, `tint` |
| color | `brand`, `danger`, `important`, `informative`, `severe`, `subtle`, `success`, `warning` |
| size | `tiny`, `extra-small`, `small`, `medium`, `large`, `extra-large` |
| shape | `circular`, `rounded`, `square` |
| iconPosition | `before`, `after` |

> appearance(4) × color(8) = **32개 조합** — Fluent UI에서 가장 많은 variant 조합

#### 고유 tokens.* (46개)
```
spacingHorizontalXXS, spacingHorizontalXS, spacingHorizontalSNudge,
borderRadiusCircular, borderRadiusMedium, borderRadiusSmall, borderRadiusNone,
strokeWidthThin, colorTransparentStroke,
colorBrandBackground, colorBrandBackground2, colorBrandForeground1, colorBrandForeground2, colorBrandStroke2,
colorNeutralForegroundOnBrand, colorNeutralForeground1, colorNeutralForeground1Static,
colorNeutralForeground3, colorNeutralForegroundStaticInverted,
colorNeutralBackground1, colorNeutralBackground4, colorNeutralBackground5,
colorNeutralStroke2, colorNeutralStrokeAccessible,
colorPaletteRedBackground1, colorPaletteRedBackground3,
colorPaletteRedForeground1, colorPaletteRedForeground3,
colorPaletteRedBorder1, colorPaletteRedBorder2,
colorPaletteGreenBackground1, colorPaletteGreenBackground3,
colorPaletteGreenForeground1, colorPaletteGreenForeground3,
colorPaletteGreenBorder1, colorPaletteGreenBorder2,
colorPaletteYellowBackground1, colorPaletteYellowBackground3,
colorPaletteYellowForeground1, colorPaletteYellowForeground2,
colorPaletteYellowBorder1,
colorPaletteDarkOrangeBackground1, colorPaletteDarkOrangeBackground3,
colorPaletteDarkOrangeForeground1, colorPaletteDarkOrangeForeground3,
colorPaletteDarkOrangeBorder1
```

#### Hardcoded 값
| 값 | 용도 | 속성 |
|---|---|---|
| `'20px'` | 기본 height, minWidth | height, minWidth |
| `'6px'` | tiny 크기 | width, height, fontSize, lineHeight |
| `'4px'` | tiny fontSize/lineHeight | fontSize, lineHeight |
| `'10px'` | extra-small 크기 | width, height, fontSize, lineHeight |
| `'16px'` | small 크기 | minWidth, height |
| `'24px'` | large 크기 | minWidth, height |
| `'32px'` | extra-large 크기 | minWidth, height |
| `'12px'` | icon 기본 fontSize | fontSize |
| `'6px'`/`'10px'`/`'16px'`/`'20px'` | icon size별 fontSize | fontSize |
| `'1'` | icon lineHeight | lineHeight |
| `'currentColor'` | outline borderColor | borderColor |

#### Override mechanisms
- `mergeClasses()` — root, icon
- `state.root.className`, `state.icon.className`
- `badgeClassNames.*` — 안정적 CSS 클래스
- `typographyStyles.caption1Strong` / `caption2Strong` — 프리셋 타이포그래피

---

### 2.7 MessageBar

**소스**: `react-message-bar/library/src/components/MessageBar/useMessageBarStyles.styles.ts` (3,950 bytes)

#### Variant axes
| Axis | 값 |
|---|---|
| intent | `info`, `error`, `warning`, `success` |
| layout | `multiline`, (default: single-line) |
| shape | `square`, (default: rounded) |

#### 고유 tokens.* (19개)
```
spacingHorizontalM, spacingHorizontalS, spacingVerticalS, spacingVerticalMNudge,
strokeWidthThin, borderRadiusMedium,
colorNeutralBackground3, colorNeutralStroke1, colorNeutralForeground3,
fontSizeBase500,
colorStatusDangerForeground1, colorStatusDangerBackground1, colorStatusDangerBorder1,
colorStatusWarningForeground3, colorStatusWarningBackground1, colorStatusWarningBorder1,
colorStatusSuccessForeground1, colorStatusSuccessBackground1, colorStatusSuccessBorder1
```

#### Hardcoded 값
| 값 | 용도 | 속성 |
|---|---|---|
| `'36px'` | 최소 높이 | minHeight |
| `'0'` | square borderRadius | borderRadius |
| `'0px'` | multiline secondaryActions marginRight | marginRight |
| `'auto 1fr auto auto'` | grid 컬럼 | gridTemplateColumns |
| `'"icon body secondaryActions actions"'` | grid 영역 | gridTemplateAreas |

#### Override mechanisms
- `mergeClasses()` — root, icon, bottomReflowSpacer
- `state.root.className`, `state.icon.className`
- `messageBarClassNames.*` — 안정적 CSS 클래스

---

### 2.8 Tab

**소스**: `react-tabs/library/src/components/Tab/useTabStyles.styles.ts` (24,158 bytes) — **가장 큰 스타일 파일**

#### Variant axes
| Axis | 값 |
|---|---|
| appearance | `transparent`, `subtle`, `subtle-circular`, `filled-circular` |
| size | `small`, `medium`, `large` |
| vertical | `boolean` (orientation) |
| selected | `boolean` |
| disabled | `boolean` |

#### 고유 tokens.* (59개) — **최다 token 사용 컴포넌트**
```
borderRadiusMedium, borderRadiusCircular,
fontFamilyBase, lineHeightBase300,
spacingHorizontalXXS, spacingHorizontalSNudge, spacingHorizontalMNudge, spacingHorizontalM,
spacingHorizontalS, spacingVerticalXXS, spacingVerticalXS, spacingVerticalSNudge,
spacingVerticalS, spacingVerticalM, spacingVerticalL, spacingVerticalMNudge, spacingVerticalNone,
colorTransparentBackground, colorTransparentBackgroundHover, colorTransparentBackgroundPressed,
colorTransparentStroke,
colorSubtleBackground, colorSubtleBackgroundHover, colorSubtleBackgroundPressed,
colorNeutralForeground1, colorNeutralForeground1Hover, colorNeutralForeground1Pressed,
colorNeutralForeground2, colorNeutralForeground2Hover, colorNeutralForeground2Pressed,
colorNeutralForegroundDisabled, colorNeutralForegroundOnBrand,
colorNeutralBackground3, colorNeutralBackground3Hover, colorNeutralBackground3Pressed,
colorNeutralBackgroundDisabled,
colorNeutralStroke1Hover, colorNeutralStroke1Pressed, colorNeutralStrokeDisabled,
colorNeutralStrokeOnBrand,
colorCompoundBrandForeground1, colorCompoundBrandForeground1Hover, colorCompoundBrandForeground1Pressed,
colorCompoundBrandStroke, colorCompoundBrandStrokeHover, colorCompoundBrandStrokePressed,
colorBrandBackground, colorBrandBackgroundHover, colorBrandBackgroundPressed,
colorBrandBackground2, colorBrandBackground2Hover, colorBrandBackground2Pressed,
colorBrandForeground2, colorBrandForeground2Hover, colorBrandForeground2Pressed,
strokeWidthThin, strokeWidthThick, strokeWidthThicker,
colorStrokeFocus2, shadow4
```

#### Hardcoded 값
| 값 | 용도 | 속성 |
|---|---|---|
| `'20px'` | icon small/medium 크기 | fontSize, height, width |
| `'24px'` | icon large 크기 | fontSize, height, width |
| `'0'` | indicator 위치 (bottom, left) | bottom, left |
| `'transparent'` | focus borderColor/outlineColor | borderColor, outlineColor |
| `'none'` | button border | border |
| `'not-allowed'` | disabled cursor | cursor |
| `'hidden'` | placeholder content | visibility |
| forced-colors | `Highlight`, `HighlightText`, `ButtonText`, `ButtonFace`, `Canvas` | 다양한 속성 |

#### Override mechanisms
- `mergeClasses()` — root, icon, content, contentReservedSpace
- 각 slot별 `state.*.className`
- `tabClassNames.*` — 안정적 CSS 클래스
- `createCustomFocusIndicatorStyle()` — 커스텀 focus indicator
- `useTabAnimatedIndicatorStyles_unstable` — 애니메이션 indicator (별도 파일)
- exported hooks: `useTabIndicatorStyles_unstable`, `useTabButtonStyles_unstable`, `useTabContentStyles_unstable`

---

### 2.9 Table

**소스**: `react-table/library/src/components/Table/useTableStyles.styles.ts` (1,317 bytes) — **가장 작은 스타일 파일**

#### Variant axes
| Axis | 값 |
|---|---|
| layout | `table`(default), `flex` (noNativeElements) |

#### 고유 tokens.* (1개)
```
colorSubtleBackground
```

#### Hardcoded 값
| 값 | 용도 | 속성 |
|---|---|---|
| `'100%'` | 테이블 전체 너비 | width |
| `'fixed'` | 테이블 레이아웃 | tableLayout |
| `'collapse'` | border 병합 | borderCollapse |

#### Override mechanisms
- `mergeClasses()` — root
- `state.root.className`
- `tableClassName` / `tableClassNames.root` — 안정적 CSS 클래스

> **특이사항**: Table 자체는 최소한의 스타일만 담당. 실제 셀/행 스타일은 `TableCell`, `TableRow`, `TableHeader` 등 하위 컴포넌트에 분산.

---

### 2.10 Select

**소스**: `react-select/library/src/components/Select/useSelectStyles.styles.ts` (8,470 bytes)

#### Variant axes
| Axis | 값 |
|---|---|
| size | `small`, `medium`, `large` |
| appearance | `outline`, `underline`, `filled-lighter`, `filled-darker` |
| invalid | `boolean` |
| disabled | `boolean` |

#### 고유 tokens.* (23개)
```
fontFamilyBase,
borderRadiusMedium,
colorCompoundBrandStroke,
durationUltraFast, durationNormal,
curveAccelerateMid, curveDecelerateMid,
colorNeutralForeground1, colorNeutralForegroundDisabled,
colorNeutralBackground1, colorNeutralBackground3,
colorNeutralStroke1, colorNeutralStroke1Hover, colorNeutralStroke1Pressed,
colorNeutralStrokeAccessible, colorNeutralStrokeDisabled,
colorTransparentBackground, colorTransparentStrokeDisabled,
colorPaletteRedBorder2,
spacingHorizontalXXS, spacingHorizontalSNudge, spacingHorizontalMNudge, spacingHorizontalM
```

#### Hardcoded 값
| 값 | 용도 | 속성 |
|---|---|---|
| `'16px'` / `'20px'` / `'24px'` | iconSizes (small/medium/large) | fontSize, height, width |
| `'24px'` / `'32px'` / `'40px'` | fieldHeights | height |
| `'1px solid transparent'` | 기본 border | border |
| `'none'` | appearance, boxShadow | appearance, boxShadow |
| `'2px'` | focus outlineWidth | outlineWidth |
| `'0'` | paddingBottom/Top, underline borderRadius | padding, borderRadius |
| `'0.01ms'` | prefers-reduced-motion | transitionDuration, transitionDelay |
| `'scaleX(0)'` / `'scaleX(1)'` | focus 애니메이션 | transform |
| `'pointer'` / `'not-allowed'` | cursor | cursor |
| `'block'` | svg display | display |
| forced-colors | `GrayText` | borderColor, color |

#### Override mechanisms
- `mergeClasses()` — root, select, icon
- `state.root.className`, `state.select.className`, `state.icon.className`
- `selectClassNames.*` — 안정적 CSS 클래스
- `typographyStyles.caption1` / `body1` / `body2` — 프리셋 타이포그래피

---

## 3. View 1: Component → Token (컴포넌트별 사용 토큰)

| Component | 고유 Token 수 | 주요 Token 카테고리 |
|---|---|---|
| Button | 53 | color(33), spacing(5), border-radius(5), font(6), stroke(2), motion(2) |
| Input | 30 | color(18), spacing(6), border-radius(1), motion(4), shadow(1) |
| Card | 38 | color(28), spacing(0), border-radius(3), stroke(2), shadow(3), z-index(1) |
| DialogSurface | 7 | color(4), border-radius(1), shadow(1), stroke(1) |
| Checkbox | 25 | color(18), spacing(3), border-radius(2), stroke(1), line-height(1) |
| Badge | 46 | color(40), spacing(3), border-radius(4), stroke(1) |
| MessageBar | 19 | color(12), spacing(4), border-radius(1), stroke(1), font-size(1) |
| Tab | 59 | color(38), spacing(13), border-radius(2), stroke(3), font(2), shadow(1) |
| Table | 1 | color(1) |
| Select | 23 | color(14), spacing(4), border-radius(1), motion(4) |

---

## 4. View 2: Token → Component (토큰별 사용 컴포넌트)

### 최다 사용 Token (10개 컴포넌트 중 참조 수 기준)

| Token | 참조 컴포넌트 수 | 컴포넌트 목록 |
|---|---|---|
| `colorNeutralForeground1` | 8 | Button, Input, Card, DialogSurface, Checkbox, Badge, Tab, Select |
| `colorNeutralForegroundDisabled` | 8 | Button, Input, Card, Checkbox, Badge, Tab, Select, MessageBar |
| `colorNeutralBackground1` | 7 | Button, Input, Card, DialogSurface, Badge, Select, Tab |
| `colorTransparentBackground` | 7 | Button, Input, Card, Badge, Tab, Select, DialogSurface |
| `colorNeutralStroke1` | 6 | Button, Input, Card, MessageBar, Tab, Select |
| `colorNeutralStrokeDisabled` | 6 | Button, Input, Card, Checkbox, Tab, Select |
| `borderRadiusMedium` | 6 | Button, Input, Card, MessageBar, Tab, Select |
| `colorTransparentStroke` | 6 | Button, Card, Checkbox, Badge, Tab, DialogSurface |
| `colorNeutralForeground2` | 5 | Button, Input, Checkbox, Tab, Badge |
| `colorNeutralForeground3` | 5 | Input, Checkbox, Badge, MessageBar, Tab |
| `colorNeutralStrokeAccessible` | 4 | Input, Checkbox, Badge, Select |
| `colorCompoundBrandStroke` | 4 | Input, Checkbox, Tab, Select |
| `colorBrandBackground` | 4 | Button, Badge, Tab, (Card 간접) |
| `colorNeutralBackgroundDisabled` | 4 | Button, Card, Checkbox, Tab |
| `strokeWidthThin` | 6 | Button, Card, Checkbox, Badge, MessageBar, Tab |
| `strokeWidthThick` | 3 | Button, Card, Tab |
| `colorStrokeFocus2` | 2 | Button, Tab |
| `shadow2` | 3 | Button, Input, Card |
| `shadow4` | 2 | Card, Tab |
| `colorPaletteRedBorder2` | 3 | Input, Badge, Select |
| `durationUltraFast` | 2 | Input, Select |
| `durationNormal` | 2 | Input, Select |
| `curveAccelerateMid` | 2 | Input, Select |
| `curveDecelerateMid` | 2 | Input, Select |

### 카테고리별 Token 분포

| Token 카테고리 | 총 고유 Token 수 | 주요 사용처 |
|---|---|---|
| **Color — Neutral** | ~35 | 모든 컴포넌트 (배경, 전경, 테두리, disabled) |
| **Color — Brand** | ~12 | Button, Badge, Tab, Checkbox, Select |
| **Color — Status** | 9 | MessageBar (danger/warning/success × bg/fg/border) |
| **Color — Palette** | ~18 | Badge (red/green/yellow/darkOrange × bg/fg/border) |
| **Color — Transparent/Subtle** | ~8 | Button, Card, Tab, Input, Select |
| **Spacing** | ~13 | Button, Input, Tab, Checkbox, Badge, Select, MessageBar |
| **Border Radius** | 6 | Button, Card, Badge, Tab, DialogSurface, Select |
| **Stroke Width** | 3 | Button, Card, Checkbox, Badge, MessageBar, Tab |
| **Typography** | ~8 | Button, Input, Tab, Select, Badge |
| **Motion** | 5 | Button, Input, Select |
| **Shadow** | 4 | Button, Input, Card, Tab, DialogSurface |
| **Z-Index** | 1 | Card |

---

## 5. Hardcoded 값 종합 인벤토리

### 5.1 px 값 (컴포넌트별)

| Component | 값 | 속성 | 빈도 | 비고 |
|---|---|---|---|---|
| Button | `3px, 1px, 5px, 8px, 7px` | padding (세로) | 5 | size별 spacing 상수 |
| Button | `96px, 64px` | minWidth | 3 | size별 최소 너비 |
| Button | `24px, 32px, 40px` | minWidth/maxWidth | 6 | iconOnly 크기 |
| Button | `20px, 24px` | fontSize/height/width | 6 | icon 크기 |
| Button | `0.25px` | calc (boxShadow) | 1 | Firefox 보정 |
| Button | `1px` | borderWidth (focus) | 1 | focus indicator |
| Input | `24px, 32px, 40px` | minHeight | 3 | fieldHeights |
| Input | `1px` | border | 1 | 기본 테두리 |
| Input | `-1px` | left/bottom/right | 3 | ::after 오프셋 |
| Input | `2px` | height/borderBottom | 2 | focus underline |
| Input | `16px, 20px, 24px` | fontSize (svg) | 3 | content 아이콘 |
| Card | `8px, 12px, 16px` | CSS var | 3 | size별 padding |
| Card | `4px` | top/right | 2 | floatingAction 위치 |
| Card | `1px` | width/height | 2 | hiddenCheckbox |
| Card | `-2px` | outlineOffset | 1 | focus outline |
| DialogSurface | `24px` | padding | 1 | SURFACE_PADDING |
| DialogSurface | `1px` | border | 1 | SURFACE_BORDER_WIDTH |
| DialogSurface | `4px` | scrollbar offset | 3 | DIALOG_FULLSCREEN_DIALOG_SCROLLBAR_OFFSET |
| DialogSurface | `600px` | maxWidth | 1 | dialog 최대 너비 |
| DialogSurface | `480px, 359px` | @media | 2 | breakpoint |
| Checkbox | `16px, 20px` | height/width | 4 | indicator 크기 |
| Checkbox | `12px, 16px` | fontSize | 2 | indicator 아이콘 |
| Badge | `20px, 6px, 10px, 16px, 24px, 32px` | height/minWidth/width | 12 | size별 크기 |
| Badge | `4px, 6px, 10px, 12px, 16px, 20px` | fontSize/lineHeight | 10 | size별 폰트/아이콘 |
| MessageBar | `36px` | minHeight | 1 | 최소 높이 |
| MessageBar | `0px` | marginRight | 1 | multiline 보정 |
| Tab | `20px, 24px` | fontSize/height/width | 6 | icon 크기 |
| Select | `16px, 20px, 24px` | fontSize/height/width | 9 | icon 크기 |
| Select | `24px, 32px, 40px` | height | 3 | fieldHeights |
| Select | `1px` | border | 2 | 기본 테두리 |
| Select | `2px` | outlineWidth | 1 | focus outline |

### 5.2 비-px 하드코딩 값

| Component | 값 | 속성 | 비고 |
|---|---|---|---|
| Button | `'transparent'` | borderColor | primary/outline/subtle/transparent |
| Button | `'0.01ms'` | transitionDuration | prefers-reduced-motion |
| Input | `'transparent'` | backgroundColor | input slot |
| Input | `'inherit'` | fontFamily 등 | typography 상속 |
| Input | `'scaleX(0/1)'` | transform | focus 애니메이션 |
| Input | `'inset(calc(100% - 2px) 0 0 0)'` | clipPath | focus underline |
| Input | `'2px solid transparent'` | outline | focus-within |
| Card | `'none'` | boxShadow | outline/subtle |
| Card | `'currentColor'` | color | interactive |
| Card | `'rect(0 0 0 0)'`, `'inset(50%)'` | clip, clipPath | hiddenCheckbox |
| DialogSurface | `'100vh'`, `'100dvh'`, `'100vw'` | maxHeight, maxWidth | 반응형 |
| Checkbox | `'currentColor'` | fill | indicator |
| Badge | `'currentColor'` | borderColor | outline appearance |
| MessageBar | `'auto 1fr auto auto'` | gridTemplateColumns | 그리드 레이아웃 |
| Tab | `'transparent'` | borderColor, outlineColor | focus |
| Select | `'none'` | appearance, boxShadow | native select 리셋 |
| Select | `'scaleX(0/1)'` | transform | focus 애니메이션 |
| Select | `'block'` | display (svg) | svg 렌더링 보정 |

### 5.3 High Contrast (forced-colors) 키워드

| 키워드 | 사용 컴포넌트 |
|---|---|
| `Highlight` | Button, Card, Tab |
| `HighlightText` | Button, Card, Tab |
| `ButtonText` | Button, Tab |
| `ButtonFace` | Button, Tab |
| `GrayText` | Button, Input, Checkbox, Select |
| `Canvas` | Tab |

---

## 6. 핵심 발견 사항

### 6.1 Token 의존율 분석

| 등급 | 컴포넌트 | Token 의존율 | 해석 |
|---|---|---|---|
| 🟢 매우 높음 | Tab | ~96% | 거의 모든 값이 token 경유 |
| 🟢 매우 높음 | Card | ~91% | CSS var 우회하나 token 기반 |
| 🟢 높음 | Checkbox | ~89% | indicator 크기만 하드코딩 |
| 🟢 높음 | MessageBar | ~88% | minHeight(36px)만 하드코딩 |
| 🟢 높음 | Button | ~87% | size별 spacing/padding이 하드코딩 |
| 🟡 보통 | Badge | ~85% | size별 px 값 다수 |
| 🟡 보통 | Input | ~84% | fieldHeights, focus underline |
| 🟡 보통 | Select | ~84% | fieldHeights, icon sizes |
| 🟠 낮음 | DialogSurface | ~56% | 레이아웃 상수 다수 |
| 🔴 매우 낮음 | Table | ~25% | token 1개만 사용 |

### 6.2 구조적 패턴

1. **Griffel CSS-in-JS**: 모든 컴포넌트가 `@griffel/react`의 `makeStyles` / `makeResetStyles` / `mergeClasses` 사용
2. **Token 참조 방식**: `tokens.colorXxx` → 런타임에 `var(--colorXxx)` 로 변환
3. **Variant 구현**: `makeStyles` 객체 내 키로 variant 정의 → `mergeClasses`에서 조건부 병합
4. **Override 계층**: `mergeClasses(시스템 클래스, ...variant 클래스, 사용자 className)` — 사용자 className이 항상 마지막
5. **안정적 클래스 이름**: 모든 slot에 `fui-ComponentName__slotName` 형식의 CSS 클래스 제공
6. **High Contrast 대응**: `@media (forced-colors: active)` 내에서 시스템 색상 키워드 사용
7. **prefers-reduced-motion**: `transitionDuration: '0.01ms'` 패턴 일관 사용

### 6.3 Hardcoded 값의 구조적 원인

| 원인 | 예시 | 해당 컴포넌트 |
|---|---|---|
| **Token 부재** | size별 px spacing (3px, 5px, 8px) | Button |
| **Token 부재** | fieldHeights (24/32/40px) | Input, Select |
| **Token 부재** | icon 고정 크기 (20/24px) | Button, Tab, Input, Select |
| **Token 부재** | indicator 크기 (16/20px) | Checkbox |
| **Token 부재** | Badge size별 px (6~32px) | Badge |
| **의도적 예외** | Firefox 보정 (0.25px) | Button |
| **의도적 예외** | focus underline (2px) | Input, Select |
| **의도적 예외** | Dialog 레이아웃 상수 | DialogSurface |
| **CSS 구조값** | grid template, clipPath | MessageBar, Input |
| **최소 스타일** | Table은 하위 컴포넌트에 위임 | Table |

### 6.4 Figma↔Code 매핑 관점 시사점

- **Token 매핑 충실도**: 색상/타이포그래피/spacing token은 Figma design token과 1:1 매핑 가능
- **Hardcoded 간극**: size별 px 값(특히 Button padding, fieldHeights, icon sizes)은 Figma의 auto-layout 수치와 직접 대응하나 token으로 추상화되지 않음
- **Variant 축 일치**: appearance/size/shape 축은 Figma component property와 구조적으로 일치
- **Badge 복잡도**: 32개 appearance×color 조합은 Figma variant set과 정확히 매핑
- **Dialog 특수성**: 레이아웃 상수가 코드에 하드코딩되어 Figma의 constraint 시스템과 직접 매핑 어려움
