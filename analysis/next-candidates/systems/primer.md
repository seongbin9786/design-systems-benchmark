# Primer (GitHub) 소스 실측 분석

- 실측 대상: `sources-candidates/primer-react` + `sources-candidates/primer-primitives`
- 실측 버전: `@primer/react` 38.35.1 (`primer-react/packages/react/package.json:4`), `@primer/primitives` 11.10.0 (`primer-primitives/package.json:3`)
- 실측일: 2026-08-13

## 0. 요약

**플랫폼 판정: responsive (데스크톱 우선 반응형).**

Primer는 GitHub.com 웹을 위한 시스템이다. 기본 밀도와 어휘는 데스크톱을 향한다. 그러나 narrow viewport 적응 장치를 시스템 차원에서 내장했다. 모바일 전용 컴포넌트는 없다. 대신 기존 컴포넌트가 viewport에 따라 형태를 바꾼다.

| 판정 근거 | 소스 위치 |
|---|---|
| viewport 토큰 narrow/regular/wide + portrait/landscape | `primer-primitives/src/tokens/functional/size/viewport.json5:3-27` |
| 터치 타깃 토큰 이원화: coarse 44px, fine 16px | `functional/size/size-coarse.json5:5`, `functional/size/size-fine.json5:5` |
| 컴포넌트 CSS의 `@media (pointer: coarse)` 44px 확장 | `ToggleSwitch/ToggleSwitch.module.css:89-97`, `SegmentedControl/SegmentedControl.module.css:270-276` |
| 전체화면 오버레이의 safe-area + 100dvh 처리 | `Overlay/Overlay.module.css:217-222` |
| Dialog가 narrow에서 `bottom`/`fullscreen` 위치를 지원 | `Dialog/Dialog.tsx:145` |
| 데스크톱 지향 반증: hover 스타일 CSS 38개 파일, `KeybindingHint` 컴포넌트, `DataTable`/`SplitPageLayout` 등 데스크톱 셸 | `packages/react/src/` 디렉터리 실측 |

핵심 요약 4줄.

1. 토큰은 base, functional, component의 3계층이다. CSS 변수로 빌드한다. 테마는 14종이다.
2. 컴포넌트는 상위 디렉터리 기준 74개다. primitive와 GitHub 도메인(use-case) 컴포넌트가 섞여 있다.
3. variant 철학: primitive의 variant 축은 의미 5종 + 크기 3종 수준으로 작게 유지한다. 용도는 variant가 아니라 별도 컴포넌트로 분리한다(ConfirmationDialog, StateLabel).
4. 모바일 어휘(BottomSheet, Toast, TabBar 등)는 컴포넌트로 존재하지 않는다. bottom-sheet는 experimental SelectPanel2의 variant 값으로만 존재한다.

## 1. 토큰 아키텍처

**3계층 + fallback.** 저장소를 컴포넌트와 분리했다(`primer-primitives`). 포맷은 W3C Design Tokens 유사 JSON5다.

| 계층 | 역할 | 정의 위치 |
|---|---|---|
| base | 원시값. 색 스케일, 픽셀 크기, 서체 원값 | `src/tokens/base/{color,size,typography,motion}/` |
| functional | 의미 부여. 다크/고대비 오버라이드를 이 계층에서 처리 | `src/tokens/functional/{color,size,spacing,typography,shadow,motion,border}/` |
| component | 컴포넌트 내부 전용. functional을 참조 | `src/tokens/component/*.json5` (button, overlay, menu 등 29개) |
| fallback | 구버전 색상 폴백 | `src/tokens/fallback/color-fallbacks.json` |

네이밍 예시 (참조 방향은 항상 component → functional → base):

| 토큰 | 값 | 위치 |
|---|---|---|
| `base.size.44` | 44px | `base/size/size.json5` |
| `fgColor.default` | `{base.color.neutral.13}` | `functional/color/fgColor.json5:2-5` |
| `bgColor.emphasis` | 고대비 강조 배경 | `functional/color/bgColor.json5:87-105` |
| `space.xxs` | `{base.size.2}` | `functional/spacing/space.json5:3-5` |
| `control.minTarget.auto` (coarse) | `{base.size.44}` | `functional/size/size-coarse.json5:5` |
| `button.default.fgColor.rest` | `{control.fgColor.rest}` | `component/button.json5:4-7` |

특이점 3가지.

1. 터치 타깃을 토큰으로 이원화했다. `size-coarse.json5`는 44px(WCAG 2.5.5), `size-fine.json5`는 16px을 최소 타깃으로 정의한다.
2. 테마 오버라이드를 별도 파일이 아니라 토큰 안의 `org.primer.overrides` 확장 필드로 관리한다(`fgColor.json5:17-23`). 빌드가 테마 14종(light, dark, dark-dimmed, 고대비, 색각이상 변형)의 CSS 파일로 전개한다(`scripts/themes.config.ts:5-226`).
3. `org.primer.llm` 확장 필드에 LLM용 사용 규칙을 넣었다(`size-coarse.json5:9-12`). AI 도구가 토큰을 고르게 하려는 장치다.

빌드 산출물은 CSS custom properties다(`scripts/buildTokens.ts:42`). breakpoint는 320/544/768/1012/1280/1400px 6단계다(`functional/size/breakpoints.json5`).

## 2. 컴포넌트 인벤토리

**총 74개.** 기준: `packages/react/src`에서 `ls -d [A-Z]*/ | wc -l`. 전체 84개 디렉터리 중 소문자 10개(`__tests__`, `deprecated`, `experimental`, `hooks`, `internal`, `legacy-theme`, `live-region`, `next`, `stories`, `utils`)를 제외했다. 74개에는 인프라 성격인 `FeatureFlags`가 포함된다. `experimental/`에 IssueLabel, SelectPanel2, Tabs, UnderlinePanels가 더 있다. `deprecated/`에 DialogV1, FilteredSearch 등이 있다.

| 구분 | 예시 |
|---|---|
| primitive | Button, IconButton, Checkbox, Radio, Select, TextInput, Textarea, Dialog, Overlay, Popover, Tooltip, Avatar, Label, Link, Heading, Text, Spinner, ProgressBar, Stack, ToggleSwitch, SegmentedControl, ActionList, ActionMenu |
| use-case (GitHub 도메인) | BranchName(브랜치명 표기), StateLabel(이슈/PR 상태), Timeline(활동 로그), TopicTag, CounterLabel, AvatarStack, Blankslate(빈 상태), DataTable, TreeView(파일 트리), SelectPanel(필터형 선택 패널), KeybindingHint(단축키 표기), RelativeTime, ConfirmationDialog, PageHeader, SplitPageLayout, Header(GitHub 상단 바), IssueLabel(experimental) |

도메인 컴포넌트의 비중이 크다. GitHub 화면 어휘(브랜치, 이슈, PR, 단축키)가 컴포넌트 이름에 그대로 박혀 있다.

## 3. variant 철학

### 3.1 Button

`packages/react/src/Button/types.ts:5-9` 인용.

```ts
export type VariantType = 'default' | 'primary' | 'invisible' | 'danger' | 'link'
export type Size = 'small' | 'medium' | 'large'
export type AlignContent = 'start' | 'center'
```

| 축 | 값 | 위치 |
|---|---|---|
| variant | default, primary, invisible, danger, link (5종) | `Button/types.ts:5` |
| size | small, medium, large (3종) | `Button/types.ts:7` |
| 상태 축 | disabled, loading, inactive | `Button/types.ts:28-45` |
| 레이아웃 축 | block, labelWrap, alignContent | `Button/types.ts:32,49,56` |
| 슬롯 | leadingVisual, trailingVisual, trailingAction, count | `Button/types.ts:68-84` |

IconButton과 LinkButton은 variant 값이 아니라 별도 컴포넌트다(`Button/types.ts:87,98`). variant 축은 의미(톤)만 담는다. 용도명 variant(예: 확인 버튼, 구매 버튼)는 없다.

### 3.2 오버레이: Dialog

| 축 | 값 | 위치 |
|---|---|---|
| width | small(296), medium(320), large(480), xlarge(640) + 임의 CSS 값 | `Dialog/Dialog.tsx:200-207` |
| height | small(480), large(640), auto | `Dialog/Dialog.tsx:194-198` |
| position | `'center' \| 'left' \| 'right' \| ResponsiveValue<'left'\|'right'\|'bottom'\|'fullscreen'\|'center'>` | `Dialog/Dialog.tsx:145` |
| align | top, center, bottom | `Dialog/Dialog.tsx:153` |

position이 핵심이다. viewport별로 다른 값을 주는 `ResponsiveValue` 객체를 받는다. narrow에서 `bottom`을 주면 사실상 bottom sheet가 된다. 저수준 `Overlay`도 `responsiveVariant?: 'fullscreen'`을 갖는다(`Overlay/Overlay.tsx:53`). 주석에 "bottomsheet를 나중에 추가할 수 있다"라고 적혀 있다.

experimental SelectPanel2는 이 방향을 타입으로 굳혔다(`experimental/SelectPanel2/SelectPanel.tsx:61`).

```ts
variant?: 'anchored' | 'modal' | ResponsiveValue<'anchored' | 'modal', 'full-screen' | 'bottom-sheet'>
```

### 3.3 리스트: ActionList

| 축 | 값 | 위치 |
|---|---|---|
| List variant | inset, horizontal-inset, full | `ActionList/shared.ts:141` |
| List selectionVariant | single, radio, multiple | `ActionList/shared.ts:145` |
| Item variant | default, danger (2종뿐) | `ActionList/shared.ts:35` |
| Item size | medium, large | `ActionList/shared.ts:36` |
| Item 상태 | inactive(inactiveText), loading | `ActionList/shared.ts:50-57` |

Item의 의미 variant는 default와 danger 2개뿐이다. 선택 모드는 별도 축(selectionVariant)으로 분리했다.

### 3.4 use-case variant 실존 여부

있다. 단, variant 값이 아니라 **별도 컴포넌트**로 존재한다.

1. `ConfirmationDialog`: 확인/취소 전용 다이얼로그 래퍼. `confirmButtonType?: 'normal' | 'primary' | 'danger'` (`ConfirmationDialog/ConfirmationDialog.tsx:35`). 기본 문구가 Cancel/OK로 박혀 있다(`:88-89`).
2. `StateLabel`: GitHub 도메인 상태 17종이 `status` prop에 박혀 있다. `issueOpened`, `pullMerged`, `issueClosedNotPlanned`, `alertFixed` 등 (`StateLabel/StateLabel.tsx:24-42`).
3. `BranchName`, `TopicTag`, `KeybindingHint`: 용도가 이름 자체다.

정리하면 Primer의 철학은 이렇다. primitive의 variant 축은 의미 톤 + 크기로 최소화한다. 용도(use-case)가 생기면 variant를 늘리지 않고 컴포넌트를 새로 만든다. 그 결과 인벤토리의 절반 가까이가 도메인 컴포넌트다.

## 4. 모바일 어휘

모바일 전용 컴포넌트 디렉터리는 0개다. 실측 결과:

| 어휘 | 실존 여부 | 근거 |
|---|---|---|
| BottomSheet | 컴포넌트 없음. experimental SelectPanel2의 narrow variant 값 `'bottom-sheet'`로만 존재 | `experimental/SelectPanel2/SelectPanel.tsx:61` |
| ActionSheet | 없음 | 디렉터리/grep 0건 |
| SafeArea | 컴포넌트 없음. Overlay 전체화면 CSS가 `env(safe-area-inset-bottom)` 처리 | `Overlay/Overlay.module.css:217` |
| PullToRefresh | 없음 | grep 0건 |
| SwipeAction | 없음 | grep 0건 |
| IndexBar | 없음 | grep 0건 |
| FloatingPanel/Bubble | 없음 | grep 0건 |
| TabBar | 없음. 데스크톱 내비인 UnderlineNav/TabNav만 존재 | `src/UnderlineNav/`, `src/TabNav/` |
| NavBar | 없음. GitHub 상단 바인 Header만 존재 | `src/Header/` |
| Toast | 없음. Flash, Banner, InlineMessage가 인라인 알림을 담당 | `src/Flash/`, `src/Banner/` |

터치 대응은 컴포넌트가 아니라 CSS 레벨에 있다. `@media (pointer: coarse)`에서 히트 영역을 44px로 확장한다(`ToggleSwitch/ToggleSwitch.module.css:89-97`, `TreeView/TreeView.module.css:77,264`, `internal/components/TextInputInnerAction.module.css:20-26`). 터치 제스처(스와이프, 드래그 시트) 코드는 없다.

## 5. 스타일링과 테마

**CSS Modules + CSS 변수 + data-attribute variant.** styled-components는 src에서 0건이다(grep 실측). `.module.css` 파일은 115개다(stories 제외).

동작 방식 3단계.

1. 토큰: primer-primitives가 테마별 CSS custom properties 파일을 빌드한다(`scripts/buildTokens.ts:42`).
2. 컴포넌트: TSX가 variant를 data-attribute로 출력한다. `data-size={size}`, `data-variant={variant}` (`Button/ButtonBase.tsx:98-99`). CSS Module이 `&:where([data-variant='primary'])` 셀렉터로 스타일을 건다(`Button/ButtonBase.module.css:265,316`). 값은 `var(--button-default-fgColor-rest)`처럼 토큰 변수를 참조한다(`ButtonBase.module.css:11`).
3. 테마 전환: ThemeProvider가 루트에 `data-color-mode`, `data-light-theme`, `data-dark-theme` 속성을 설정한다(`internal/components/ThemeProviderBase.tsx:17-19`). JS 재렌더 없이 CSS 변수 스코프만 바뀐다. JS theme 객체 방식(구 ThemeProvider)은 deprecated다(`ThemeProvider.tsx:31`).

## 6. 신규 DS 시사점 (모바일 웹뷰 기준)

1. **토큰 3계층과 네이밍을 차용한다.** base → functional(fgColor/bgColor/borderColor/space 접두) → component 구조는 웹뷰 CSS 변수와 궁합이 좋다. 테마 오버라이드를 토큰 파일 안(`org.primer.overrides`)에 두는 방식은 파일 수를 줄인다.
2. **coarse/fine 이원 타깃 토큰에서 coarse만 채택한다.** Primer는 `control.minTarget`을 coarse 44px, fine 16px로 나눴다(`size-coarse.json5:5`, `size-fine.json5:5`). 모바일 웹뷰는 coarse 고정이므로 44px을 기본 토큰으로 박고 fine 계열은 만들지 않는다.
3. **오버레이는 bottom-sheet를 1급으로 승격한다.** Primer는 데스크톱 Dialog에 ResponsiveValue로 narrow 분기를 얹는 중이고, experimental에서야 `'bottom-sheet'` 값이 등장한다(`SelectPanel2/SelectPanel.tsx:61`). 모바일 전용이라면 이 역방향 개조를 반복할 이유가 없다. 처음부터 BottomSheet를 독립 컴포넌트로 설계한다.
4. **use-case는 variant가 아니라 별도 컴포넌트로 만든다.** Primer는 Button variant를 5종으로 고정하고, ConfirmationDialog와 StateLabel 같은 용도 컴포넌트를 primitive 위에 쌓았다. Seed의 ActionButton 논쟁에 대한 답: primitive 축은 동결하고, 용도 계층을 별도 레이어(디렉터리)로 분리하면 두 마리를 다 잡는다.
5. **safe-area와 100dvh 처리를 시스템 차원에 내장한다.** Primer는 전체화면 Overlay CSS에 `env(safe-area-inset-bottom)`과 100dvh Safari 보정을 넣었다(`Overlay.module.css:217-222`). 웹뷰 DS는 이를 개별 컴포넌트 CSS가 아니라 공용 토큰/믹스인으로 승격해 모든 고정 요소에 일괄 적용한다.
