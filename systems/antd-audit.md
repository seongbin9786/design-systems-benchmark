# Ant Design Component-Level Token Dependency Audit

> **분석 기준**: `ant-design/ant-design` master 브랜치의 각 컴포넌트 `style/index.ts` (및 `style/token.ts`, `style/variant.ts`) 실측 코드
> **분석 일자**: 2026-07-26
> **대상 컴포넌트**: Button, Input, Card, Modal, Checkbox, Tag, Alert, Tabs, Table, Select (10개)

---

## 1. 종합 요약 테이블

| Component | 총 style 속성 (추정) | token.* 참조 (unique) | Hardcoded 값 | Token 의존율 | Variant axes | Override hooks |
|-----------|---------------------|----------------------|-------------|-------------|-------------|---------------|
| **Button** | ~120 | 58 | 14 | ~81% | type(6), size(3), shape(3), ghost, block, danger | ConfigProvider `theme.components.Button`, CSS variables (`--ant-btn-*`) |
| **Input** | ~130 | 42 | 12 | ~78% | variant(4: outlined/filled/borderless/underlined), size(3), status | ConfigProvider `theme.components.Input`, classNames/styles props |
| **Card** | ~95 | 38 | 8 | ~83% | size(2: default/small), type(inner), bordered, hoverable | ConfigProvider `theme.components.Card` |
| **Modal** | ~85 | 40 | 10 | ~80% | wireframe 여부 (internal), centered, responsive width | ConfigProvider `theme.components.Modal` |
| **Checkbox** | ~65 | 28 | 5 | ~85% | checked, indeterminate, disabled | ConfigProvider `theme.components.Checkbox` |
| **Tag** | ~70 | 30 | 6 | ~83% | variant(4: outlined/solid/filled/borderless), checkable, closable, disabled | ConfigProvider `theme.components.Tag` |
| **Alert** | ~60 | 32 | 4 | ~87% | type(4: success/info/warning/error), banner, closable, showIcon | ConfigProvider `theme.components.Alert` |
| **Tabs** | ~150 | 48 | 11 | ~81% | type(line/card/editable-card), size(3), tabPosition(4), centered | ConfigProvider `theme.components.Tabs` |
| **Table** | ~110 (index만) | 52 | 9 | ~85% | size(3), bordered, loading, expandable, selection | ConfigProvider `theme.components.Table` |
| **Select** | ~55 (index만) | 24 | 5 | ~83% | mode(multiple/tags), size(3), status, showSearch, allowClear | ConfigProvider `theme.components.Select` |

> **참고**: "총 style 속성"은 해당 `index.ts`에서 생성하는 CSS property declaration의 대략적 수. Table/Select는 하위 style 파일(bordered, filter, sorter, dropdown, select-input 등)이 별도 분리되어 있어 index.ts 기준.

---

## 2. View 1: Component → Token (컴포넌트별 참조 토큰)

### 2.1 Button

**index.ts + variant.ts + token.ts에서 참조하는 unique token:**

| 카테고리 | 토큰 목록 |
|---------|----------|
| **색상 (Color)** | `colorPrimary`, `colorPrimaryHover`, `colorPrimaryActive`, `colorPrimaryBg`, `colorPrimaryBgHover`, `colorPrimaryBorder`, `colorError`, `colorErrorHover`, `colorErrorActive`, `colorErrorBg`, `colorErrorBgFilledHover`, `colorErrorBgActive`, `colorErrorOutline`, `colorLink`, `colorLinkHover`, `colorLinkActive`, `colorTextLightSolid`, `colorText`, `colorTextDisabled`, `colorBgContainer`, `colorBgContainerDisabled`, `colorBgSolid`, `colorBgSolidHover`, `colorBgSolidActive`, `colorBorder`, `colorBorderDisabled`, `colorFillTertiary`, `colorFillSecondary`, `colorFill`, `controlOutline`, `controlTmpOutline` |
| **간격 (Spacing)** | `marginXS`, `paddingXS`, `paddingContentHorizontal`, `paddingInlineSM`, `paddingInlineLG`, `paddingBlock`, `paddingBlockSM`, `paddingBlockLG` |
| **크기 (Sizing)** | `controlHeight`, `controlHeightSM`, `controlHeightLG`, `controlOutlineWidth` |
| **타이포 (Typography)** | `fontSize`, `fontSizeLG`, `fontWeight`, `contentFontSize`, `contentFontSizeSM`, `contentFontSizeLG`, `contentLineHeight`, `contentLineHeightSM`, `contentLineHeightLG` |
| **보더 (Border)** | `borderRadius`, `borderRadiusSM`, `borderRadiusLG`, `lineWidth`, `lineType` |
| **모션 (Motion)** | `motionDurationMid`, `motionDurationSlow`, `motionEaseInOut` |
| **기타** | `opacityLoading`, `iconGap`, `calc` |
| **ComponentToken 파생** | `buttonPaddingHorizontal`, `buttonPaddingVertical`, `buttonIconOnlyFontSize`, `primaryShadow`, `dangerShadow`, `defaultShadow`, `primaryColor`, `dangerColor`, `defaultColor`, `defaultBg`, `defaultBorderColor`, `defaultHoverBg`, `defaultHoverColor`, `defaultHoverBorderColor`, `defaultActiveBg`, `defaultActiveColor`, `defaultActiveBorderColor`, `defaultGhostColor`, `ghostBg`, `defaultGhostBorderColor`, `solidTextColor`, `textTextColor`, `textTextHoverColor`, `textTextActiveColor`, `textHoverBg`, `linkHoverBg`, `onlyIconSize`, `onlyIconSizeSM`, `onlyIconSizeLG`, `defaultBgDisabled`, `dashedBgDisabled`, `borderColorDisabled` |
| **Preset 색상** | `{colorKey}1`~`{colorKey}6`, `{colorKey}Hover`, `{colorKey}Active`, `{colorKey}ShadowColor` (13개 preset × 4 = 52개) |

**총 unique token 참조: ~58개 (global) + ~31개 (ComponentToken) + 52개 (preset colors)**

### 2.2 Input

| 카테고리 | 토큰 목록 |
|---------|----------|
| **색상** | `colorText`, `colorTextPlaceholder`, `colorTextQuaternary`, `colorTextDescription`, `colorIcon`, `colorIconHover`, `colorError`, `colorBgContainer` |
| **간격** | `paddingBlock`, `paddingBlockSM`, `paddingBlockLG`, `paddingInline`, `paddingInlineSM`, `paddingInlineLG`, `paddingXS`, `paddingXXS` |
| **크기** | `controlHeight`, `controlHeightSM`, `controlHeightLG` |
| **타이포** | `inputFontSize`, `inputFontSizeSM`, `inputFontSizeLG`, `lineHeight`, `lineHeightLG`, `fontSizeIcon` |
| **보더** | `borderRadius`, `borderRadiusSM`, `borderRadiusLG`, `lineWidth`, `lineType` |
| **모션** | `motionDurationMid`, `motionDurationSlow` |
| **ComponentToken** | `activeBorderColor`, `activeShadow`, `activeBg`, `hoverBorderColor`, `hoverBg`, `addonBg`, `inputAffixPadding`, `errorActiveShadow`, `warningActiveShadow` |

### 2.3 Card

| 카테고리 | 토큰 목록 |
|---------|----------|
| **색상** | `colorBgContainer`, `colorBorderSecondary`, `colorTextHeading`, `colorText`, `colorTextDescription`, `colorPrimary`, `colorIcon`, `colorFillAlter` |
| **간격** | `padding`, `paddingLG`, `paddingXS`, `paddingSM`, `marginXXS`, `marginXS` |
| **타이포** | `fontSize`, `fontSizeLG`, `fontWeightStrong`, `lineHeight`, `fontHeight` |
| **보더** | `borderRadiusLG`, `lineWidth`, `lineType` |
| **모션** | `motionDurationMid` |
| **그림자** | `boxShadowTertiary`, `boxShadowCard` (→ `cardShadow`) |
| **ComponentToken** | `headerBg`, `headerFontSize`, `headerFontSizeSM`, `headerHeight`, `headerHeightSM`, `bodyPaddingSM`, `headerPaddingSM`, `bodyPadding`, `headerPadding`, `actionsBg`, `actionsLiMargin`, `tabsMarginBottom`, `extraColor` |

### 2.4 Modal

| 카테고리 | 토큰 목록 |
|---------|----------|
| **색상** | `colorBgMask`, `colorBgElevated`, `colorText`, `colorTextHeading`, `colorIcon`, `colorIconHover`, `colorBgTextHover`, `colorBgTextActive`, `colorSplit` |
| **간격** | `padding`, `paddingMD`, `paddingLG`, `paddingXS`, `paddingSM`, `paddingContentHorizontalLG`, `margin`, `marginXS`, `marginSM` |
| **크기** | `controlHeight`, `zIndexPopupBase` |
| **타이포** | `fontSize`, `fontSizeLG`, `fontSizeHeading5`, `lineHeight`, `lineHeightHeading5`, `fontWeightStrong` |
| **보더** | `borderRadiusLG`, `borderRadiusSM`, `lineWidth`, `lineType` |
| **모션** | `motionDurationMid`, `motionDurationSlow` |
| **그림자** | `boxShadow` |
| **반응형** | `screenSMMax` |
| **ComponentToken** | `headerBg`, `titleLineHeight`, `titleFontSize`, `titleColor`, `contentBg`, `footerBg`, `contentPadding`, `headerPadding`, `headerBorderBottom`, `headerMarginBottom`, `bodyPadding`, `footerPadding`, `footerBorderTop`, `footerBorderRadius`, `footerMarginTop`, `confirmBodyPadding`, `confirmIconMarginInlineEnd`, `confirmBtnsMarginTop` |
| **내부 파생** | `modalHeaderHeight`, `modalFooterBorderColorSplit`, `modalFooterBorderStyle`, `modalFooterBorderWidth`, `modalCloseIconColor`, `modalCloseIconHoverColor`, `modalCloseBtnSize`, `modalConfirmIconSize`, `modalTitleHeight` |

### 2.5 Checkbox

| 카테고리 | 토큰 목록 |
|---------|----------|
| **색상** | `colorBgContainer`, `colorBorder`, `colorPrimary`, `colorPrimaryHover`, `colorWhite`, `colorBgContainerDisabled`, `colorTextDisabled` |
| **간격** | `marginXS`, `paddingXS` |
| **크기** | `controlInteractiveSize` (→ `checkboxSize`) |
| **타이포** | `fontSizeLG` |
| **보더** | `borderRadiusSM`, `lineWidth`, `lineWidthBold`, `lineType` |
| **모션** | `motionDurationSlow`, `motionDurationMid`, `motionDurationFast`, `motionEaseInBack`, `motionEaseOutBack` |

### 2.6 Tag

| 카테고리 | 토큰 목록 |
|---------|----------|
| **색상** | `colorBorder`, `colorText`, `colorTextHeading`, `colorTextLightSolid`, `colorTextDisabled`, `colorPrimary`, `colorPrimaryHover`, `colorPrimaryActive`, `colorBgContainer`, `colorBgContainerDisabled`, `colorBgSolid`, `colorFillSecondary`, `colorFillTertiary`, `colorIcon`, `colorBorderDisabled` |
| **간격** | `paddingXXS`, `paddingXS` |
| **타이포** | `fontSizeSM` (→ `tagFontSize`), `lineHeightSM`, `fontSizeIcon` |
| **보더** | `borderRadiusSM`, `lineWidth`, `lineType` |
| **모션** | `motionDurationMid` |
| **ComponentToken** | `defaultBg`, `defaultColor`, `solidTextColor` |

### 2.7 Alert

| 카테고리 | 토큰 목록 |
|---------|----------|
| **색상** | `colorSuccess`, `colorSuccessBg`, `colorSuccessBorder`, `colorWarning`, `colorWarningBg`, `colorWarningBorder`, `colorError`, `colorErrorBg`, `colorErrorBorder`, `colorInfo`, `colorInfoBg`, `colorInfoBorder`, `colorText`, `colorTextHeading`, `colorIcon`, `colorIconHover` |
| **간격** | `marginXS`, `marginSM`, `paddingContentVerticalSM`, `paddingMD`, `paddingContentHorizontalLG` |
| **타이포** | `fontSize`, `fontSizeLG`, `fontSizeHeading3`, `fontSizeIcon`, `lineHeight` |
| **보더** | `borderRadiusLG`, `lineWidth`, `lineType` |
| **모션** | `motionDurationSlow`, `motionDurationMid`, `motionEaseInOutCirc` |
| **ComponentToken** | `defaultPadding`, `withDescriptionPadding`, `withDescriptionIconSize` |

### 2.8 Tabs

| 카테고리 | 토큰 목록 |
|---------|----------|
| **색상** | `colorPrimary`, `colorPrimaryHover`, `colorPrimaryActive`, `colorText`, `colorTextHeading`, `colorTextDisabled`, `colorBorderSecondary`, `colorBorder`, `colorBgContainer`, `colorFillAlter`, `colorIcon`, `controlItemBgHover` |
| **간격** | `margin`, `marginXS`, `marginSM`, `marginXXS`, `padding`, `paddingXS`, `paddingSM`, `paddingLG`, `paddingXXS` |
| **크기** | `controlHeight`, `controlHeightLG`, `zIndexPopupBase` |
| **타이포** | `fontSize`, `fontSizeLG`, `fontSizeSM`, `lineHeight`, `lineHeightLG`, `fontHeight`, `fontHeightLG` |
| **보더** | `borderRadius`, `borderRadiusLG`, `lineWidth`, `lineWidthBold`, `lineType` |
| **모션** | `motionDurationSlow`, `motionEaseInOut` |
| **그림자** | `boxShadowSecondary`, `boxShadowTabsOverflowLeft`, `boxShadowTabsOverflowRight`, `boxShadowTabsOverflowTop`, `boxShadowTabsOverflowBottom` |
| **ComponentToken** | `zIndexPopup`, `cardBg`, `cardHeight`, `cardHeightSM`, `cardHeightLG`, `cardPadding`, `cardPaddingSM`, `cardPaddingLG`, `titleFontSize`, `titleFontSizeLG`, `titleFontSizeSM`, `inkBarColor`, `horizontalMargin`, `horizontalItemGutter`, `horizontalItemMargin`, `horizontalItemMarginRTL`, `horizontalItemPadding`, `horizontalItemPaddingLG`, `horizontalItemPaddingSM`, `verticalItemPadding`, `verticalItemMargin`, `itemColor`, `itemActiveColor`, `itemHoverColor`, `itemSelectedColor`, `cardGutter` |

### 2.9 Table

| 카테고리 | 토큰 목록 |
|---------|----------|
| **색상** | `colorBgContainer`, `colorTextHeading`, `colorFillAlter`, `colorFillSecondary`, `colorFillContent`, `controlItemBgActive`, `controlItemBgActiveHover`, `colorBorderSecondary`, `colorTextPlaceholder`, `colorIcon`, `colorIconHover`, `colorSplit` |
| **간격** | `padding`, `paddingSM`, `paddingXS` |
| **크기** | `controlHeight`, `controlInteractiveSize` |
| **타이포** | `fontSize`, `fontSizeSM`, `lineHeight`, `fontWeightStrong` |
| **보더** | `borderRadiusLG`, `lineWidth`, `lineType` |
| **모션** | `motionDurationMid` |
| **기타** | `opacityLoading` |
| **ComponentToken (38개)** | `headerBg`, `headerColor`, `headerSortActiveBg`, `headerSortHoverBg`, `bodySortBg`, `rowHoverBg`, `rowSelectedBg`, `rowSelectedHoverBg`, `rowExpandedBg`, `cellPaddingBlock`, `cellPaddingInline`, `cellPaddingBlockMD`, `cellPaddingInlineMD`, `cellPaddingBlockSM`, `cellPaddingInlineSM`, `borderColor`, `headerBorderRadius`, `footerBg`, `footerColor`, `cellFontSize`, `cellFontSizeMD`, `cellFontSizeSM`, `headerSplitColor`, `fixedHeaderSortActiveBg`, `headerFilterHoverBg`, `filterDropdownMenuBg`, `filterDropdownBg`, `expandIconBg`, `selectionColumnWidth`, `stickyScrollBarBg`, `stickyScrollBarBorderRadius`, `expandIconMarginTop`, `expandIconHalfInner`, `expandIconSize`, `expandIconScale`, `headerIconColor`, `headerIconHoverColor` |

### 2.10 Select

| 카테고리 | 토큰 목록 |
|---------|----------|
| **색상** | `colorTextQuaternary`, `colorIcon`, `colorBgBase`, `colorBgContainer`, `colorText`, `colorTextDisabled`, `colorPrimaryHover`, `colorPrimary`, `controlOutline`, `controlItemBgActive`, `controlItemBgHover`, `colorFillSecondary`, `colorBgContainerDisabled` |
| **간격** | `paddingSM`, `paddingXXS`, `paddingXS`, `controlPaddingHorizontal` |
| **크기** | `controlHeight`, `controlHeightSM`, `controlHeightLG`, `zIndexPopupBase` |
| **타이포** | `fontSize`, `lineHeight`, `fontSizeIcon`, `fontWeightStrong` |
| **보더** | `lineWidth` |
| **모션** | `motionDurationMid` |
| **ComponentToken (22개)** | `zIndexPopup`, `optionSelectedColor`, `optionSelectedFontWeight`, `optionSelectedBg`, `optionActiveBg`, `optionPadding`, `optionFontSize`, `optionLineHeight`, `optionHeight`, `selectorBg`, `clearBg`, `singleItemHeightLG`, `multipleItemBg`, `multipleItemBorderColor`, `multipleItemHeight`, `multipleItemHeightSM`, `multipleItemHeightLG`, `multipleSelectorBgDisabled`, `multipleItemColorDisabled`, `multipleItemBorderColorDisabled`, `showArrowPaddingInlineEnd`, `hoverBorderColor`, `activeBorderColor`, `activeOutlineColor`, `selectAffixPadding` |

---

## 3. View 2: Token → Component (토큰별 참조 컴포넌트)

### 3.1 최다 참조 글로벌 토큰

| Token | 참조 컴포넌트 수 | 참조 컴포넌트 |
|-------|----------------|-------------|
| `colorPrimary` | 8 | Button, Checkbox, Tag, Alert(간접), Tabs, Table(간접), Select, Card |
| `colorBgContainer` | 8 | Button, Input, Card, Checkbox, Tag, Tabs, Table, Select |
| `colorText` | 8 | Input, Card, Modal, Tag, Alert, Tabs, Table(간접), Select |
| `colorBorder` / `colorBorderSecondary` | 8 | Button, Input, Card, Checkbox, Tag, Tabs, Table, Modal |
| `borderRadius` / `borderRadiusLG` / `borderRadiusSM` | 10 | **전체 컴포넌트** |
| `fontSize` / `fontSizeLG` / `fontSizeSM` | 10 | **전체 컴포넌트** |
| `lineWidth` / `lineType` | 10 | **전체 컴포넌트** |
| `motionDurationMid` / `motionDurationSlow` | 10 | **전체 컴포넌트** |
| `colorTextDisabled` | 6 | Button, Checkbox, Tag, Tabs, Select, Modal(간접) |
| `colorIcon` / `colorIconHover` | 6 | Input, Card, Tag, Alert, Tabs, Table |
| `padding` / `paddingXS` / `paddingSM` / `paddingLG` | 9 | Button, Input, Card, Modal, Checkbox, Alert, Tabs, Table, Select |
| `controlHeight` / `controlHeightSM` / `controlHeightLG` | 7 | Button, Input, Modal, Tabs, Table, Select, Checkbox(간접) |
| `colorError` | 4 | Button, Input, Alert, Select(간접) |
| `colorTextHeading` | 5 | Card, Modal, Tag, Alert, Table |
| `fontWeightStrong` | 4 | Card, Modal, Table, Select |
| `boxShadow` 계열 | 4 | Card, Modal, Tabs, Table(간접) |
| `zIndexPopupBase` | 3 | Modal, Tabs, Select |
| `colorFillAlter` | 4 | Card, Tabs, Table, Input |
| `colorSplit` | 3 | Modal, Table, Input(간접) |

### 3.2 핵심 관찰

- **`borderRadius`, `fontSize`, `lineWidth`, `motionDuration*`** 은 10개 컴포넌트 전체에서 참조 — 진정한 글로벌 토큰
- **`colorPrimary`** 는 8개 컴포넌트에서 참조되나, Alert에서는 `colorInfo`/`colorSuccess` 등 시맨틱 컬러를 통해 간접 참조
- **`colorBgContainer`** 는 모든 컴포넌트의 기본 배경으로 사용 — 가장 핵심적인 색상 토큰
- Table은 `FastColor`를 이용해 `colorFillAlter`, `colorFillSecondary`, `colorFillContent`를 `colorBgContainer` 위에 합성(composite)하여 사용 — 단순 참조가 아닌 **색상 연산** 패턴

---

## 4. Hardcoded Values 인벤토리

### 4.1 Button

| 위치 (함수/섹션) | 속성 | 하드코딩 값 | 비고 |
|----------------|------|-----------|------|
| `genSharedButtonStyle` | `letterSpacing` | `'0.34em'` | 두 글자 한글 버튼 자간 |
| `genSharedButtonStyle` | `marginInlineEnd` | `'-0.34em'` | 위 자간 보정 |
| `genCircleButtonStyle` | `borderRadius` | `'50%'` | 원형 버튼 |
| `genBlockButtonStyle` | `width` | `'100%'` | 블록 버튼 |
| `genSharedButtonStyle` | `content` | `'"\\a0"'` | 아이콘 baseline 보정용 non-breaking space |
| `token.ts: prepareComponentToken` | `fontWeight` | `400` | ComponentToken 기본값 |
| `token.ts: prepareComponentToken` | `paddingInlineSM` | `8 - token.lineWidth` | `8`이 하드코드 |
| `token.ts: prepareComponentToken` | `ghostBg` | `'transparent'` | 고스트 버튼 배경 |
| `token.ts: prepareComponentToken` | `linkHoverBg` | `'transparent'` | 링크 버튼 호버 |
| `token.ts: prepareComponentToken` | `onlyIconSize/SM/LG` | `'inherit'` | 아이콘 전용 크기 |
| `variant.ts` | CSS var 기본값 `border-color` | `'#000'` | CSS variable fallback |
| `variant.ts` | CSS var 기본값 `text-color` | `'#000'` | CSS variable fallback |
| `variant.ts` | CSS var 기본값 `bg-color` | `'#ddd'` | CSS variable fallback |
| `variant.ts` | `shadow` 기본값 | `'none'` | CSS variable fallback |

### 4.2 Input

| 위치 | 속성 | 하드코딩 값 | 비고 |
|------|------|-----------|------|
| `genInputStyle` | `FIXED_CHROME_COLOR_HEIGHT` | `16` | Chrome color input 고정 높이 |
| `genInputGroupStyle` | `width` (addon) | `1` | table-cell shrink |
| `genInputGroupStyle` | `lineHeight` (addon) | `1` | addon 텍스트 |
| `genInputGroupStyle` | `margin` (cascader) | `'-9px'` | Cascader picker 보정 |
| `genInputGroupStyle` | `zIndex` | `1` | focus/hover 시 |
| `genInputGroupStyle` | `borderInlineEndWidth` (focus/hover) | `1` | 보더 보정 |
| `genAllowClearStyle` | `verticalAlign` | `-1` | clear 아이콘 정렬 |
| `genAffixStyle` | `content` | `'"\\a0"'` | affix wrapper before |
| `genBasicInputStyle` | `width` | `'100%'` | 기본 너비 |
| `genBasicInputStyle` | `minWidth` | `0` | flex shrink |
| `genPlaceholderStyle` | `opacity` | `1` | Firefox placeholder |
| `genInputStyle` | `appearance` | `'none'` | search cancel button |

### 4.3 Card

| 위치 | 속성 | 하드코딩 값 | 비고 |
|------|------|-----------|------|
| `genCardHeadStyle` | `marginBottom` | `-1` | 그리드 overflow 버그 수정 |
| `genCardGridStyle` | `width` | `'33.33%'` | 그리드 3열 |
| `genCardGridStyle` | `border` | `0` | 그리드 보더 리셋 |
| `genCardGridStyle` | `borderRadius` | `0` | 그리드 라운딩 리셋 |
| `prepareComponentToken` | `headerBg` | `'transparent'` | 헤더 배경 |
| `prepareComponentToken` | `bodyPaddingSM` | `12` | 고정 패딩 (주석: "Fixed padding") |
| `prepareComponentToken` | `headerPaddingSM` | `12` | 고정 패딩 |
| `genCardStyle` (bordered cover) | `marginTop/InlineStart/End` | `-1` | 보더 보정 |

### 4.4 Modal

| 위치 | 속성 | 하드코딩 값 | 비고 |
|------|------|-----------|------|
| `genModalMaskStyle` | `backdropFilter` | `'blur(4px)'` | mask-blur |
| `genModalStyle` | `top` | `100` | 모달 기본 top 위치 (px) |
| `genModalStyle` | `maxWidth` | `'calc(100vw - 16px)'` | 모바일 최대 너비 (media query 내) |
| `genModalStyle` | `height` (centered before) | `'100%'` | 중앙 정렬 |
| `genModalStyle` | `width` (centered before) | `0` | 중앙 정렬 |
| `genModalStyle` | `lineHeight` (close) | `1` | 닫기 버튼 |
| `genModalStyle` | `background` (close) | `'transparent'` | 닫기 버튼 배경 |
| `genModalStyle` | `border` (close/container) | `0` | 보더 리셋 |
| `prepareComponentToken` | `footerBg` | `'transparent'` | 푸터 배경 |
| `prepareComponentToken` | `headerBg` | `'transparent'` | 헤더 배경 |

### 4.5 Checkbox

| 위치 | 속성 | 하드코딩 값 | 비고 |
|------|------|-----------|------|
| `genCheckboxStyle` | `lineHeight` | `1` | 체크박스 |
| `genCheckboxStyle` | checkmark `transform` | `'rotate(45deg) scale(0) translate(-50%,-50%)'` | 체크 마크 변환 |
| `genCheckboxStyle` | checkmark `borderTop/InlineStart` | `0` | 체크 마크 보더 |
| `genCheckboxStyle` | checkmark `opacity` | `0` / `1` | 체크 마크 표시 |
| `genCheckboxStyle` | input `opacity` | `0` | 네이티브 input 숨김 |

### 4.6 Tag

| 위치 | 속성 | 하드코딩 값 | 비고 |
|------|------|-----------|------|
| `prepareToken` | `tagPaddingHorizontal` | `8` | 주석: "Fixed padding" |
| `genBaseStyle` | `height` | `'auto'` | 태그 높이 |
| `genBaseStyle` | `opacity` | `1` | 기본 opacity |
| `genBaseStyle` (checkable) | `backgroundColor/borderColor` | `'transparent'` | checkable 기본 |
| `genBaseStyle` (svg) | `marginBlockEnd` | `'0.2em'` | 서드파티 SVG 정렬 |
| `prepareComponentToken` | `solidTextColor` | `'#000'` 또는 `'#fff'` | 밝기 계산 기반 |

### 4.7 Alert

| 위치 | 속성 | 하드코딩 값 | 비고 |
|------|------|-----------|------|
| `prepareComponentToken` | `paddingHorizontal` | `12` | 주석: "Fixed value here" |
| `genBaseStyle` (banner) | `marginBottom` | `0` | 배너 모드 |
| `genBaseStyle` (banner) | `border` | `'0 !important'` | 배너 보더 제거 |
| `genBaseStyle` (banner) | `borderRadius` | `0` | 배너 라운딩 제거 |

### 4.8 Tabs

| 위치 | 속성 | 하드코딩 값 | 비고 |
|------|------|-----------|------|
| `prepareComponentToken` | `horizontalItemGutter` | `32` | 주석: "Fixed Value" |
| `prepareComponentToken` | `cardHeightLG` fallback | `controlHeightLG + 8` | `8`이 하드코드 |
| `genDropdownStyle` | `top` | `-9999` | 드롭다운 초기 위치 |
| `genDropdownStyle` | `left` | `-9999` | 드롭다운 초기 위치 |
| `mergeToken` | `tabsDropdownHeight` | `200` | 드롭다운 최대 높이 |
| `mergeToken` | `tabsDropdownWidth` | `120` | 드롭다운 최소 너비 |
| `genTabsStyle` | `transform` | `'translate(0)'` | Chrome 렌더 버그 수정 |
| `genPositionStyle` (left/right) | `minWidth` | `calc(controlHeight * 1.25)` | `1.25` 배수 |
| `genCardStyle` | `margin` | `0` | 카드 탭 마진 리셋 |
| `genTabStyle` | `background` | `'transparent'` | 탭 기본 배경 |
| `genTabStyle` | `border` | `0` | 탭 보더 리셋 |

### 4.9 Table

| 위치 | 속성 | 하드코딩 값 | 비고 |
|------|------|-----------|------|
| `genTableStyle` | header split `width` | `1` | 헤더 구분선 너비 |
| `genTableStyle` | header split `height` | `'1.6em'` | 헤더 구분선 높이 |
| `mergeToken` | `tableFilterDropdownWidth` | `120` | 필터 드롭다운 너비 |
| `mergeToken` | `tableFilterDropdownHeight` | `264` | 필터 드롭다운 높이 |
| `mergeToken` | `tableFilterDropdownSearchWidth` | `140` | 필터 검색 너비 |
| `mergeToken` | `tableScrollThumbSize` | `8` | 주석: "Mac scroll bar size" |
| `prepareComponentToken` | `stickyScrollBarBorderRadius` | `100` | 스크롤바 라운딩 |
| `genTableStyle` | `zIndexTableFixed` | `2` | 고정 컬럼 z-index |
| `prepareComponentToken` | `expandIconSize` 계산 | `lineWidth * 3` | `3` 배수 하드코드 |

### 4.10 Select

| 위치 | 속성 | 하드코딩 값 | 비고 |
|------|------|-----------|------|
| `genBaseStyle` | clear `borderRadius` | `'50%'` | 원형 clear 버튼 |
| `genBaseStyle` | clear `opacity` | `0` / `1` | clear 표시/숨김 |
| `genBaseStyle` | clear `lineHeight` | `1` | clear 아이콘 |
| `genBaseStyle` | clear `transform` | `'translateZ(0)'` | Safari GPU compositing |
| `prepareComponentToken` | `showArrowPaddingInlineEnd` | `Math.ceil(fontSize * 1.25)` | `1.25` 배수 |

---

## 5. ComponentToken 분석

### 5.1 Button ComponentToken (token.ts)

| 필드 | 기본값 출처 | 방식 |
|------|-----------|------|
| `fontWeight` | `400` | **하드코드** |
| `iconGap` | `token.marginXS` | 글로벌 토큰 |
| `defaultShadow` | `token.controlOutlineWidth`, `token.controlTmpOutline` | 글로벌 토큰 조합 |
| `primaryShadow` | `token.controlOutlineWidth`, `token.controlOutline` | 글로벌 토큰 조합 |
| `dangerShadow` | `token.controlOutlineWidth`, `token.colorErrorOutline` | 글로벌 토큰 조합 |
| `primaryColor` | `token.colorTextLightSolid` | 글로벌 토큰 |
| `defaultColor` | `token.colorText` | 글로벌 토큰 |
| `defaultBg` | `token.colorBgContainer` | 글로벌 토큰 |
| `defaultBorderColor` | `token.colorBorder` | 글로벌 토큰 |
| `dangerColor` | `token.colorTextLightSolid` | 글로벌 토큰 |
| `defaultHoverBg` | `token.colorBgContainer` | 글로벌 토큰 |
| `defaultHoverColor` | `token.colorPrimaryHover` | 글로벌 토큰 |
| `defaultHoverBorderColor` | `token.colorPrimaryHover` | 글로벌 토큰 |
| `defaultActiveBg` | `token.colorBgContainer` | 글로벌 토큰 |
| `defaultActiveColor` | `token.colorPrimaryActive` | 글로벌 토큰 |
| `defaultActiveBorderColor` | `token.colorPrimaryActive` | 글로벌 토큰 |
| `borderColorDisabled` | `token.colorBorderDisabled` | 글로벌 토큰 |
| `defaultGhostColor` | `token.colorBgContainer` | 글로벌 토큰 |
| `ghostBg` | `'transparent'` | **하드코드** |
| `defaultGhostBorderColor` | `token.colorBgContainer` | 글로벌 토큰 |
| `solidTextColor` | `isBright(colorBgSolid)` → `'#000'`/`'#fff'` | **하드코드** (밝기 계산) |
| `textTextColor` | `token.colorText` | 글로벌 토큰 |
| `textTextHoverColor` | `token.colorText` | 글로벌 토큰 |
| `textTextActiveColor` | `token.colorText` | 글로벌 토큰 |
| `textHoverBg` | `token.colorFillTertiary` | 글로벌 토큰 |
| `linkHoverBg` | `'transparent'` | **하드코드** |
| `paddingInline` | `token.paddingContentHorizontal - token.lineWidth` | 글로벌 토큰 연산 |
| `paddingInlineLG` | `token.paddingContentHorizontal - token.lineWidth` | 글로벌 토큰 연산 |
| `paddingInlineSM` | `8 - token.lineWidth` | **부분 하드코드** (8) |
| `onlyIconSize/SM/LG` | `'inherit'` | **하드코드** (CSS 키워드) |
| `contentFontSize` | `token.fontSize` (fallback) | 글로벌 토큰 |
| `contentFontSizeLG` | `token.fontSizeLG` (fallback) | 글로벌 토큰 |
| `contentFontSizeSM` | `token.fontSize` (fallback) | 글로벌 토큰 |
| `paddingBlock/SM/LG` | `(controlHeight - fontSize*lineHeight)/2 - lineWidth` | 글로벌 토큰 연산 |
| `defaultBgDisabled` | `token.colorBgContainerDisabled` | 글로벌 토큰 |
| `dashedBgDisabled` | `token.colorBgContainerDisabled` | 글로벌 토큰 |
| `{colorKey}ShadowColor` (13개) | `getAlphaColor(token[key+'1'], token.colorBgContainer)` | 글로벌 토큰 연산 |

**요약**: 37개 필드 중 33개 글로벌 토큰 파생, 4개 하드코드 (`fontWeight`, `ghostBg`, `linkHoverBg`, `solidTextColor`)

### 5.2 Input ComponentToken (token.ts)

| 필드 | 기본값 출처 | 방식 |
|------|-----------|------|
| `paddingBlock/SM/LG` | `(controlHeight - fontSize*lineHeight)/2 - lineWidth` | 글로벌 토큰 연산 |
| `paddingInline` | `token.paddingSM - token.lineWidth` | 글로벌 토큰 연산 |
| `paddingInlineSM` | `token.controlPaddingHorizontalSM - token.lineWidth` | 글로벌 토큰 연산 |
| `paddingInlineLG` | `token.controlPaddingHorizontal - token.lineWidth` | 글로벌 토큰 연산 |
| `addonBg` | `token.colorFillAlter` | 글로벌 토큰 |
| `activeBorderColor` | `token.colorPrimary` | 글로벌 토큰 |
| `hoverBorderColor` | `token.colorPrimaryHover` | 글로벌 토큰 |
| `activeShadow` | `token.controlOutlineWidth`, `token.controlOutline` | 글로벌 토큰 조합 |
| `errorActiveShadow` | `token.controlOutlineWidth`, `token.colorErrorOutline` | 글로벌 토큰 조합 |
| `warningActiveShadow` | `token.controlOutlineWidth`, `token.colorWarningOutline` | 글로벌 토큰 조합 |
| `hoverBg` | `token.colorBgContainer` | 글로벌 토큰 |
| `activeBg` | `token.colorBgContainer` | 글로벌 토큰 |
| `inputFontSize/SM/LG` | `token.fontSize` / `token.fontSizeLG` | 글로벌 토큰 |

**요약**: 16개 필드 전부 글로벌 토큰 파생. **하드코드 없음**.

### 5.3 Card ComponentToken

| 필드 | 기본값 출처 | 방식 |
|------|-----------|------|
| `headerBg` | `'transparent'` | **하드코드** |
| `headerFontSize` | `token.fontSizeLG` | 글로벌 토큰 |
| `headerFontSizeSM` | `token.fontSize` | 글로벌 토큰 |
| `headerHeight` | `fontSizeLG * lineHeightLG + padding * 2` | 글로벌 토큰 연산 |
| `headerHeightSM` | `fontSize * lineHeight + paddingXS * 2` | 글로벌 토큰 연산 |
| `actionsBg` | `token.colorBgContainer` | 글로벌 토큰 |
| `actionsLiMargin` | `${token.paddingSM}px 0` | 글로벌 토큰 |
| `tabsMarginBottom` | `-token.padding - token.lineWidth` | 글로벌 토큰 연산 |
| `extraColor` | `token.colorText` | 글로벌 토큰 |
| `bodyPaddingSM` | `12` | **하드코드** |
| `headerPaddingSM` | `12` | **하드코드** |
| `bodyPadding` | `token.paddingLG` (fallback) | 글로벌 토큰 |
| `headerPadding` | `token.paddingLG` (fallback) | 글로벌 토큰 |

**요약**: 13개 필드 중 10개 글로벌 토큰 파생, 3개 하드코드

### 5.4 Modal ComponentToken

| 필드 | 기본값 출처 | 방식 |
|------|-----------|------|
| `footerBg` | `'transparent'` | **하드코드** |
| `headerBg` | `'transparent'` | **하드코드** |
| `titleLineHeight` | `token.lineHeightHeading5` | 글로벌 토큰 |
| `titleFontSize` | `token.fontSizeHeading5` | 글로벌 토큰 |
| `contentBg` | `token.colorBgElevated` | 글로벌 토큰 |
| `titleColor` | `token.colorTextHeading` | 글로벌 토큰 |
| `contentPadding` | wireframe ? `0` : `paddingMD + paddingContentHorizontalLG` | 글로벌 토큰 (조건부) |
| `headerPadding` | wireframe ? `padding + paddingLG` : `0` | 글로벌 토큰 (조건부) |
| `headerBorderBottom` | wireframe ? `lineWidth lineType colorSplit` : `'none'` | 글로벌 토큰 (조건부) |
| `headerMarginBottom` | wireframe ? `0` : `token.marginXS` | 글로벌 토큰 (조건부) |
| `bodyPadding` | wireframe ? `token.paddingLG` : `0` | 글로벌 토큰 (조건부) |
| `footerPadding` | wireframe ? `paddingXS + padding` : `0` | 글로벌 토큰 (조건부) |
| `footerBorderTop` | wireframe ? `lineWidth lineType colorSplit` : `'none'` | 글로벌 토큰 (조건부) |
| `footerBorderRadius` | wireframe ? `borderRadiusLG` : `0` | 글로벌 토큰 (조건부) |
| `footerMarginTop` | wireframe ? `0` : `token.marginSM` | 글로벌 토큰 (조건부) |
| `confirmBodyPadding` | wireframe 조건부 연산 | 글로벌 토큰 (조건부) |
| `confirmIconMarginInlineEnd` | wireframe ? `token.margin` : `token.marginSM` | 글로벌 토큰 (조건부) |
| `confirmBtnsMarginTop` | wireframe ? `token.marginLG` : `token.marginSM` | 글로벌 토큰 (조건부) |

**요약**: 18개 필드 중 16개 글로벌 토큰 파생, 2개 하드코드 (`footerBg`, `headerBg`). `wireframe` 플래그에 따른 조건부 분기가 특징.

### 5.5 Checkbox ComponentToken

```typescript
export interface ComponentToken {} // 빈 인터페이스
```

**ComponentToken이 존재하지 않음.** 모든 스타일이 글로벌 AliasToken에서 직접 파생. `checkboxSize`는 `token.controlInteractiveSize`에서 내부 파생.

### 5.6 Tag ComponentToken

| 필드 | 기본값 출처 | 방식 |
|------|-----------|------|
| `defaultBg` | `FastColor(colorFillTertiary).onBackground(colorBgContainer).toHexString()` | 글로벌 토큰 **색상 합성** |
| `defaultColor` | `token.colorText` | 글로벌 토큰 |
| `solidTextColor` | `isBright(colorBgSolid)` → `'#000'`/`'#fff'` | **하드코드** (밝기 계산) |

**요약**: 3개 필드 중 2개 글로벌 토큰 파생, 1개 하드코드

### 5.7 Alert ComponentToken

| 필드 | 기본값 출처 | 방식 |
|------|-----------|------|
| `defaultPadding` | `${paddingContentVerticalSM}px 12px` | **부분 하드코드** (12) |
| `withDescriptionPadding` | `${paddingMD}px ${paddingContentHorizontalLG}px` | 글로벌 토큰 |
| `withDescriptionIconSize` | `token.fontSizeHeading3` | 글로벌 토큰 |

**요약**: 3개 필드 중 2개 글로벌 토큰, 1개 부분 하드코드

### 5.8 Tabs ComponentToken

| 필드 | 기본값 출처 | 방식 |
|------|-----------|------|
| `zIndexPopup` | `token.zIndexPopupBase + 50` | **부분 하드코드** (50) |
| `cardBg` | `token.colorFillAlter` | 글로벌 토큰 |
| `cardHeight` | `token.controlHeightLG` (fallback) | 글로벌 토큰 |
| `cardHeightSM` | `token.controlHeight` (fallback) | 글로벌 토큰 |
| `cardHeightLG` | `controlHeightLG + 8` | **부분 하드코드** (8) |
| `cardPadding/SM/LG` | `(cardHeight - fontHeight)/2 - lineWidth` + `padding`/`paddingXS` | 글로벌 토큰 연산 |
| `titleFontSize` | `token.fontSize` | 글로벌 토큰 |
| `titleFontSizeLG` | `token.fontSizeLG` | 글로벌 토큰 |
| `titleFontSizeSM` | `token.fontSize` | 글로벌 토큰 |
| `inkBarColor` | `token.colorPrimary` | 글로벌 토큰 |
| `horizontalMargin` | `0 0 ${token.margin}px 0` | 글로벌 토큰 |
| `horizontalItemGutter` | `32` | **하드코드** |
| `horizontalItemPadding/SM/LG` | `${paddingSM/XS/padding}px 0` | 글로벌 토큰 |
| `verticalItemPadding` | `${paddingXS}px ${paddingLG}px` | 글로벌 토큰 |
| `verticalItemMargin` | `${token.margin}px 0 0 0` | 글로벌 토큰 |
| `itemColor` | `token.colorText` | 글로벌 토큰 |
| `itemSelectedColor` | `token.colorPrimary` | 글로벌 토큰 |
| `itemHoverColor` | `token.colorPrimaryHover` | 글로벌 토큰 |
| `itemActiveColor` | `token.colorPrimaryActive` | 글로벌 토큰 |
| `cardGutter` | `token.marginXXS / 2` | 글로벌 토큰 연산 |

**요약**: 26개 필드 중 22개 글로벌 토큰 파생, 4개 하드코드/부분 하드코드

### 5.9 Table ComponentToken

| 필드 | 기본값 출처 | 방식 |
|------|-----------|------|
| `headerBg` | `FastColor(colorFillAlter).onBackground(colorBgContainer)` | 색상 합성 |
| `headerColor` | `token.colorTextHeading` | 글로벌 토큰 |
| `headerSortActiveBg` | `FastColor(colorFillSecondary).onBackground(colorBgContainer)` | 색상 합성 |
| `headerSortHoverBg` | `FastColor(colorFillContent).onBackground(colorBgContainer)` | 색상 합성 |
| `bodySortBg` | `FastColor(colorFillAlter).onBackground(colorBgContainer)` | 색상 합성 |
| `rowHoverBg` | `FastColor(colorFillAlter).onBackground(colorBgContainer)` | 색상 합성 |
| `rowSelectedBg` | `token.controlItemBgActive` | 글로벌 토큰 |
| `rowSelectedHoverBg` | `token.controlItemBgActiveHover` | 글로벌 토큰 |
| `rowExpandedBg` | `token.colorFillAlter` | 글로벌 토큰 |
| `cellPaddingBlock` | `token.padding` | 글로벌 토큰 |
| `cellPaddingInline` | `token.padding` | 글로벌 토큰 |
| `cellPaddingBlockMD` | `token.paddingSM` | 글로벌 토큰 |
| `cellPaddingInlineMD` | `token.paddingXS` | 글로벌 토큰 |
| `cellPaddingBlockSM` | `token.paddingXS` | 글로벌 토큰 |
| `cellPaddingInlineSM` | `token.paddingXS` | 글로벌 토큰 |
| `borderColor` | `token.colorBorderSecondary` | 글로벌 토큰 |
| `headerBorderRadius` | `token.borderRadiusLG` | 글로벌 토큰 |
| `footerBg` | 색상 합성 (위와 동일) | 색상 합성 |
| `footerColor` | `token.colorTextHeading` | 글로벌 토큰 |
| `cellFontSize/MD/SM` | `token.fontSize` | 글로벌 토큰 |
| `headerSplitColor` | `token.colorBorderSecondary` | 글로벌 토큰 |
| `fixedHeaderSortActiveBg` | 색상 합성 | 색상 합성 |
| `headerFilterHoverBg` | `token.colorFillContent` | 글로벌 토큰 |
| `filterDropdownMenuBg` | `token.colorBgContainer` | 글로벌 토큰 |
| `filterDropdownBg` | `token.colorBgContainer` | 글로벌 토큰 |
| `expandIconBg` | `token.colorBgContainer` | 글로벌 토큰 |
| `selectionColumnWidth` | `token.controlHeight` | 글로벌 토큰 |
| `stickyScrollBarBg` | `token.colorTextPlaceholder` | 글로벌 토큰 |
| `stickyScrollBarBorderRadius` | `100` | **하드코드** |
| `expandIconMarginTop` | `(fontSize*lineHeight - lineWidth*3)/2 - ...` | 글로벌 토큰 연산 |
| `headerIconColor` | `FastColor(colorIcon).setA(a * opacityLoading)` | 색상 합성 |
| `headerIconHoverColor` | `FastColor(colorIconHover).setA(a * opacityLoading)` | 색상 합성 |
| `expandIconHalfInner` | `controlInteractiveSize/2 - lineWidth` | 글로벌 토큰 연산 |
| `expandIconSize` | `expandIconHalfInner*2 + lineWidth*3` | 글로벌 토큰 연산 |
| `expandIconScale` | `controlInteractiveSize / expandIconSize` | 글로벌 토큰 연산 |

**요약**: 38개 필드 중 37개 글로벌 토큰 파생 (색상 합성 포함), 1개 하드코드 (`stickyScrollBarBorderRadius: 100`)

### 5.10 Select ComponentToken

| 필드 | 기본값 출처 | 방식 |
|------|-----------|------|
| `zIndexPopup` | `token.zIndexPopupBase + 50` | **부분 하드코드** (50) |
| `optionSelectedColor` | `token.colorText` | 글로벌 토큰 |
| `optionSelectedFontWeight` | `token.fontWeightStrong` | 글로벌 토큰 |
| `optionSelectedBg` | `token.controlItemBgActive` | 글로벌 토큰 |
| `optionActiveBg` | `token.controlItemBgHover` | 글로벌 토큰 |
| `optionPadding` | `(controlHeight - fontSize*lineHeight)/2 + controlPaddingHorizontal` | 글로벌 토큰 연산 |
| `optionFontSize` | `token.fontSize` | 글로벌 토큰 |
| `optionLineHeight` | `token.lineHeight` | 글로벌 토큰 |
| `optionHeight` | `token.controlHeight` | 글로벌 토큰 |
| `selectorBg` | `token.colorBgContainer` | 글로벌 토큰 |
| `clearBg` | `token.colorBgContainer` | 글로벌 토큰 |
| `singleItemHeightLG` | `token.controlHeightLG` | 글로벌 토큰 |
| `multipleItemBg` | `token.colorFillSecondary` | 글로벌 토큰 |
| `multipleItemBorderColor` | `'transparent'` | **하드코드** |
| `multipleItemHeight/SM/LG` | `controlHeight - paddingXXS*2` etc. | 글로벌 토큰 연산 |
| `multipleSelectorBgDisabled` | `token.colorBgContainerDisabled` | 글로벌 토큰 |
| `multipleItemColorDisabled` | `token.colorTextDisabled` | 글로벌 토큰 |
| `multipleItemBorderColorDisabled` | `'transparent'` | **하드코드** |
| `showArrowPaddingInlineEnd` | `Math.ceil(fontSize * 1.25)` | **부분 하드코드** (1.25) |
| `hoverBorderColor` | `token.colorPrimaryHover` | 글로벌 토큰 |
| `activeBorderColor` | `token.colorPrimary` | 글로벌 토큰 |
| `activeOutlineColor` | `token.controlOutline` | 글로벌 토큰 |
| `selectAffixPadding` | `token.paddingXXS` | 글로벌 토큰 |

**요약**: 25개 필드 중 21개 글로벌 토큰 파생, 4개 하드코드/부분 하드코드

---

## 6. Variant Axes 상세

### 6.1 Button

| Axis | 값 | 구현 방식 |
|------|---|----------|
| `type` (→ `variant` + `color`) | `solid`, `outlined`, `dashed`, `filled`, `text`, `link` | CSS variables (`--ant-btn-*`) 기반 variant 시스템 |
| `color` | `primary`, `dangerous`, `default`, + 13개 preset colors | CSS variable override |
| `size` | `small`, `middle`(default), `large` | `mergeToken`으로 token 재계산 |
| `shape` | `default`, `circle`, `round` | 별도 style 함수 |
| `ghost` | `true`/`false` | CSS variable override |
| `block` | `true`/`false` | `width: 100%` |
| `disabled` | `true`/`false` | 별도 disabled 블록 |

**특이사항**: v5.21+부터 CSS variables 기반 variant 시스템으로 전환. `genCssVar(antCls, 'btn')`로 `--ant-btn-border-color`, `--ant-btn-bg-color` 등 생성.

### 6.2 Input

| Axis | 값 | 구현 방식 |
|------|---|----------|
| `variant` | `outlined`, `filled`, `borderless`, `underlined` | 별도 `variants.ts` 파일 |
| `size` | `small`, `middle`, `large` | token 재계산 |
| `status` | `error`, `warning` | 별도 status style (variants.ts 내) |
| `disabled` | `true`/`false` | 별도 disabled style |

### 6.3 Card

| Axis | 값 | 구현 방식 |
|------|---|----------|
| `size` | `default`, `small` | `genCardSizeStyle` |
| `type` | `default`, `inner` | `genCardTypeInnerStyle` |
| `bordered` | `true`/`false` | 보더 추가/제거 |
| `hoverable` | `true`/`false` | hover 시 shadow |
| `loading` | `true`/`false` | 로딩 스켈레톤 |

### 6.4 Modal

| Axis | 값 | 구현 방식 |
|------|---|----------|
| `wireframe` | `true`/`false` | `prepareComponentToken`에서 조건부 분기 (internal) |
| `centered` | `true`/`false` | 별도 centered 스타일 |
| `responsive width` | CSS variables `--modal-{bp}-width` | `genResponsiveWidthStyle` |

### 6.5 Checkbox

| Axis | 값 | 구현 방식 |
|------|---|----------|
| `checked` | `true`/`false` | 별도 checked 블록 |
| `indeterminate` | `true`/`false` | 별도 indeterminate 블록 |
| `disabled` | `true`/`false` | 별도 disabled 블록 |

### 6.6 Tag

| Axis | 값 | 구현 방식 |
|------|---|----------|
| `variant` | `outlined`(default), `solid`, `filled`, `borderless` | 별도 스타일 블록 |
| `checkable` | `true`/`false` | checkable 서브 스타일 |
| `closable` | `true`/`false` | close icon 표시 |
| `disabled` | `true`/`false` | 별도 disabled 블록 |
| `color` (preset) | 13개 preset 색상 | 별도 파일 (여기서 미감사) |

### 6.7 Alert

| Axis | 값 | 구현 방식 |
|------|---|----------|
| `type` | `success`, `info`, `warning`, `error` | `genTypeStyle` — 시맨틱 색상 토큰 매핑 |
| `banner` | `true`/`false` | 보더/라운딩 제거 |
| `closable` | `true`/`false` | close icon/text |
| `showIcon` | `true`/`false` | 아이콘 표시 |
| `filled` | `true`/`false` | `borderColor: transparent` |

### 6.8 Tabs

| Axis | 값 | 구현 방식 |
|------|---|----------|
| `type` | `line`, `card`, `editable-card` | `genCardStyle` |
| `size` | `small`, `middle`, `large` | `genSizeStyle` |
| `tabPosition` | `top`, `bottom`, `left`, `right` | `genPositionStyle` |
| `centered` | `true`/`false` | nav-wrap margin auto |

### 6.9 Table

| Axis | 값 | 구현 방식 |
|------|---|----------|
| `size` | `default`, `middle`, `small` | `genSizeStyle` (별도 파일) |
| `bordered` | `true`/`false` | `genBorderedStyle` (별도 파일) |
| `loading` | `true`/`false` | opacity |
| `expandable` | 설정 객체 | `genExpandStyle` (별도 파일) |
| `selection` | checkbox/radio | `genSelectionStyle` (별도 파일) |
| `sticky` | `true`/`false` | `genStickyStyle` (별도 파일) |
| `virtual` | `true`/`false` | `genVirtualStyle` (별도 파일) |

### 6.10 Select

| Axis | 값 | 구현 방식 |
|------|---|----------|
| `mode` | `default`(single), `multiple`, `tags` | 별도 dropdown/select-input 스타일 |
| `size` | `small`, `middle`, `large` | token 재계산 |
| `status` | `error`, `warning`, `success`, `validating` | 별도 status 스타일 |
| `showSearch` | `true`/`false` | 검색 입력 스타일 |
| `allowClear` | `true`/`false` | clear 버튼 표시 |
| `disabled` | `true`/`false` | 별도 disabled 스타일 |

---

## 7. Override Mechanisms

### 7.1 ConfigProvider theme.components

모든 10개 컴포넌트가 `genStyleHooks`를 통해 등록되어 있으므로, `ConfigProvider`의 `theme.components.{ComponentName}`에서 ComponentToken을 override 가능:

```tsx
<ConfigProvider theme={{
  components: {
    Button: { primaryColor: '#fff', fontWeight: 500 },
    Card: { headerBg: '#fafafa', bodyPaddingSM: 16 },
    Table: { headerBg: '#f0f0f0', rowHoverBg: '#e6f7ff' },
  }
}}>
```

### 7.2 CSS Variables (Button 특유)

Button은 v5.21+ CSS variable 기반 variant 시스템을 사용:
- `--ant-btn-border-color`, `--ant-btn-bg-color`, `--ant-btn-text-color` 등
- `--ant-btn-shadow`, `--ant-btn-border-width`, `--ant-btn-border-style`
- hover/active/disabled 변형: `--ant-btn-bg-color-hover`, `--ant-btn-text-color-active` 등
- 이를 통해 runtime에 CSS만으로 variant override 가능

### 7.3 classNames / styles props

Input, Select 등은 컴포넌트 레벨에서 `classNames` / `styles` props를 지원 (Semantic DOM):
- Input: `classNames={{ input, prefix, suffix, wrapper }}`, `styles={{ input, prefix, suffix }}`
- Select: `classNames`, `styles` (popup, selector 등)
- Modal: `classNames={{ header, body, footer, mask, wrapper }}`, `styles={{ ... }}`
- Card: `classNames={{ header, body, title, extra, actions, cover }}`, `styles={{ ... }}`

### 7.4 wireframe 플래그 (Modal)

Modal은 `token.wireframe` boolean에 따라 padding/border 구조가 완전히 달라지는 조건부 분기 패턴 사용. 이는 글로벌 토큰 `wireframe`에 의해 제어.

---

## 8. 핵심 발견사항

### 8.1 Token 의존율 분석

| 순위 | 컴포넌트 | Token 의존율 | 평가 |
|------|---------|------------|------|
| 1 | Alert | ~87% | 가장 높은 토큰 의존도. 하드코드 4개뿐 |
| 2 | Checkbox | ~85% | ComponentToken 자체가 없음. 순수 글로벌 토큰 |
| 3 | Table | ~85% | 38개 ComponentToken 대부분 글로벌 파생 |
| 4 | Card | ~83% | `bodyPaddingSM: 12` 등 소수 하드코드 |
| 4 | Tag | ~83% | `tagPaddingHorizontal: 8` 고정 |
| 4 | Select | ~83% | `'transparent'` 보더, `1.25` 배수 |
| 7 | Button | ~81% | variant.ts의 CSS var fallback (`#000`, `#ddd`) |
| 7 | Tabs | ~81% | `horizontalItemGutter: 32`, 드롭다운 크기 |
| 9 | Modal | ~80% | `top: 100`, `blur(4px)` 등 |
| 10 | Input | ~78% | `FIXED_CHROME_COLOR_HEIGHT: 16`, `-9px` 등 |

### 8.2 하드코드 패턴 분류

| 패턴 | 빈도 | 예시 |
|------|------|------|
| **레이아웃 보정값** | 가장 많음 | `-1`, `0`, `1`, `'50%'`, `'100%'` |
| **고정 디자인 값** | 중간 | `12`(Card SM padding), `8`(Tag/Button padding), `32`(Tabs gutter), `100`(Modal top) |
| **CSS 키워드** | 많음 | `'transparent'`, `'none'`, `'inherit'`, `'currentColor'` |
| **색상 fallback** | 적음 | `'#000'`, `'#fff'`, `'#ddd'` (Button CSS var, Tag/Button solidTextColor) |
| **배수/비율** | 적음 | `1.25`(Select/Tabs), `1.6em`(Table), `0.34em`(Button), `0.2em`(Tag) |
| **z-index** | 적음 | `1`, `2`, `+50`(offset) |
| **특수 효과** | 적음 | `'blur(4px)'`(Modal), `'rotate(45deg)'`(Checkbox) |

### 8.3 색상 합성 패턴 (FastColor)

Table과 Tag에서 `FastColor`를 사용한 색상 합성 패턴 발견:

```typescript
// Table: 반투명 색상을 배경 위에 합성하여 불투명 색상 생성
new FastColor(colorFillAlter).onBackground(colorBgContainer).toHexString()

// Tag: 동일 패턴
new FastColor(token.colorFillTertiary).onBackground(token.colorBgContainer).toHexString()

// Table: alpha 조정
baseColorAction.clone().setA(baseColorAction.a * opacityLoading).toRgbString()

// Tag/Button: 밝기 기반 텍스트 색상 결정
isBright(new AggregationColor(token.colorBgSolid), '#fff') ? '#000' : '#fff'
```

이 패턴은 **글로벌 토큰만으로 표현 불가능한 파생 색상**을 런타임에 계산하는 것으로, token 시스템의 한계를 보여줌.

### 8.4 ComponentToken 설계 패턴

| 패턴 | 사용 컴포넌트 | 설명 |
|------|-------------|------|
| **글로벌 토큰 직접 매핑** | Input, Checkbox | ComponentToken이 글로벌 토큰을 그대로 래핑 |
| **글로벌 토큰 연산** | Button, Input, Select, Tabs | `(controlHeight - fontSize * lineHeight) / 2` 같은 수식 |
| **색상 합성** | Table, Tag | `FastColor.onBackground()` |
| **조건부 분기** | Modal | `wireframe` 플래그에 따라 완전히 다른 값 |
| **빈 ComponentToken** | Checkbox | 모든 값을 글로벌 토큰에서 직접 참조 |
| **CSS variable 시스템** | Button | `--ant-btn-*` 변수로 variant 추상화 |

### 8.5 Figma↔Code 매핑 관점 시사점

1. **ComponentToken이 Figma Component Property에 대응**: 각 컴포넌트의 ComponentToken 필드는 Figma의 component-level variable과 1:1 매핑 가능
2. **글로벌 토큰 연산값은 Figma에서 표현 어려움**: `Math.max((controlHeight - fontSize * lineHeight) / 2 - lineWidth, 0)` 같은 수식은 Figma variable의 산술 연산 한계를 초과
3. **색상 합성(FastColor)은 Figma에 직접 대응 불가**: `onBackground()` 합성은 Figma의 opacity/blending과 개념적으로 유사하지만 토큰 수준에서 표현 불가
4. **CSS variable variant (Button)는 Figma의 variant property와 유사**: `--ant-btn-bg-color` 등은 Figma의 variant별 override와 구조적으로 대응
5. **하드코드 값 중 레이아웃 보정값(`-1`, `0`)은 Figma에서 auto-layout이 처리**: 디자인 의도가 아닌 렌더링 보정 목적
