# Seed Design (당근) 실측 분석

분석 기준 소스: `sources-candidates/seed-design` (github.com/daangn/seed-design, 로컬 클론)

## 0. 요약

| 항목 | 실측 결과 |
| --- | --- |
| 버전 | `@seed-design/react` 2.2.2, `@seed-design/css` 2.4.2, `@seed-design/rootage` 2.4.0 |
| 플랫폼 판정 | **mobile-first**, 그중에서도 웹뷰 임베드를 1급 타깃으로 설계 |
| 토큰 계층 | 3계층: palette/scale → semantic(bg/fg/stroke) → component slot·state 토큰 |
| 컴포넌트 수 | styled React 컴포넌트 87개 디렉터리, headless 패키지 42개, 컴포넌트 토큰 스펙 YAML 99개 |
| variant 철학 | 컴포넌트를 용도별로 쪼갠다. 각 컴포넌트의 variant 축은 1~3개로 좁게 유지한다 |
| 스타일링 | qvism 레시피(TS 소스) → 빌드 타임 정적 CSS + CSS 변수. 런타임 CSS-in-JS 없음 |

플랫폼 판정 근거 요약:

- 테마 부트 스크립트가 웹뷰 브리지(`window.AndroidFunction`, `window.webkit.messageHandlers`)로 iOS/Android를 감지한다. 감지 실패 시 기본값도 `ios`다. (`packages/css/theming/index.mjs:36-42`)
- hover 대신 `engaged`(`:--engaged`) 커스텀 셀렉터를 쓴다. `@media (hover: hover) and (pointer: fine)`으로 입력 장치를 분기한다. (`packages/qvism-preset/src/utils/pseudo.ts:28-32`)
- safe-area를 전역 CSS 변수로 정규화한다. (`packages/qvism-preset/src/global.ts:7-17`)
- PullToRefresh headless 패키지가 touch/pointer 이벤트를 직접 처리한다. (`packages/react-headless/pull-to-refresh/src/normalize-event.ts`)
- 당근의 모바일 내비게이션 스택 stackflow 전용 AppScreen/AppBar 패키지가 있다. (`packages/stackflow/src/components/`)
- breakpoint는 min-width 기준 5단계다. base 0부터 시작한다. (`packages/css/breakpoints/index.mjs:4-17`)
- `ResponsiveDialog`는 좁은 화면에서 BottomSheet, 넓은 화면에서 ContentDialog를 렌더한다. 데스크톱은 적응 대상이지 기준이 아니다. (`packages/react/src/components/ResponsiveDialog/`)
- 저장소 문서가 명시한다: "active: hover/pressed, 모바일 우선이므로 hover보다 권장". (`TECH.md` Pseudo 선택자 표)

## 1. 토큰 아키텍처

### 1.1 파이프라인

Figma 변수 → rootage YAML(단일 소스) → 생성물(CSS 변수, TS 타입, 레시피 변수) 순서로 흐른다. (`TECH.md` 아키텍처 개요)

| 단계 | 위치 | 형태 |
| --- | --- | --- |
| 토큰 정의(소스) | `packages/rootage/*.yaml` | `kind: Tokens` YAML, theme-light/theme-dark 모드 값 |
| 컴포넌트 스펙(소스) | `packages/rootage/components/*.yaml` (99개) | `kind: ComponentSpec`, slot·variant·state별 값 |
| 생성물: CSS 변수 + TS | `packages/css/vars/` | `--seed-*` CSS 변수를 감싼 TS 상수 |
| 생성물: 레시피 CSS | `packages/css/recipes/` | 컴포넌트별 정적 CSS + `.d.ts` |

### 1.2 3계층 구조

| 계층 | 역할 | 예시 | 근거 |
| --- | --- | --- | --- |
| 1. palette/scale | 원시 값. 라이트/다크 모드별 hex, px | `$color.palette.gray-00`, `$dimension.x8` = 32px | `packages/rootage/color.yaml:9`, `packages/rootage/dimension.yaml:44-46` |
| 2. semantic | 의미 기반 별칭. palette를 참조 | `$color.bg.brand-solid` → carrot-600 | `packages/rootage/color.yaml:463-467` |
| 3. component | 컴포넌트 slot·state별 값. semantic/scale을 참조 | action-button `size=large`의 `minHeight: $dimension.x13` | `packages/rootage/components/action-button.yaml:452` |

특이점: semantic 계층이 pressed 상태 쌍을 내장한다. 예: `$color.bg.brand-solid`와 `$color.bg.brand-solid-pressed`. (`packages/rootage/color.yaml:463-472`) 터치 인터랙션의 pressed 피드백을 토큰 수준에서 표준화한 것이다.

### 1.3 네이밍 예시

| 토큰(YAML) | 생성된 CSS 변수 | 근거 |
| --- | --- | --- |
| `$color.palette.carrot-600` | `--seed-color-palette-carrot-600` | `packages/rootage/color.yaml:73` |
| `$color.bg.brand-solid-pressed` | `--seed-color-bg-brand-solid-pressed` | `packages/css/vars/color/bg.mjs:2` |
| `$color.fg.neutral-muted` | `--seed-color-fg-neutral-muted` | `packages/rootage/color.yaml:429` |
| `$dimension.x13` (= 52px) | 컴포넌트 변수로 참조 | `packages/rootage/dimension.yaml:56-58` |
| `$font-weight.bold` | `--seed-font-weight-bold` | `packages/rootage/font-weight.yaml` |

## 2. 컴포넌트 인벤토리

### 2.1 집계

| 대상 | 수 | 집계 방법 |
| --- | --- | --- |
| styled React 컴포넌트 | 87 | `find packages/react/src/components -maxdepth 1 -type d ! -name components ! -name private \| wc -l` |
| headless 패키지 | 42 | `packages/react-headless/` 하위 디렉터리. 이 중 presence, portal, prevent-scroll 등 9개 내외는 동작 유틸리티 |
| 컴포넌트 토큰 스펙 | 99 | `ls packages/rootage/components/*.yaml \| wc -l` |

`private` 디렉터리(내부 전용 Icon, WheelPicker 등)는 87에서 제외했다.

### 2.2 primitive 계층 (범용, 용도 중립)

Box, Flex, Stack(VStack/HStack), Inline, Columns, Grid, GridItem, AspectRatio, Float, Divider, Text, Icon, Portal, VisuallyHidden, Skeleton. (`packages/react/src/components/` 디렉터리 목록)

### 2.3 use-case 계층 (용도가 이름에 박힌 컴포넌트)

| 그룹 | 컴포넌트 | 용도 구분 |
| --- | --- | --- |
| 버튼 | ActionButton, ReactionButton, FieldButton, Fab, ExtendedFab, FloatingActionButton, ContextualFloatingButton, ToggleButton | 범용 Button이 없다. 액션/반응/입력 보조/플로팅을 컴포넌트로 분리 |
| 칩 | ActionChip, ControlChip, Chip | 액션 트리거와 선택 컨트롤을 분리 |
| 오버레이 | Dialog, ContentDialog, BottomSheet, ActionSheet, ExtendedActionSheet, MenuSheet, SwipeableMenuSheet, ResponsiveDialog | 목적별 오버레이를 별도 컴포넌트로 제공 |
| 배너/안내 | Callout, InlineBanner, PageBanner, Snackbar, HelpBubble | 위치와 목적으로 구분 |
| 뱃지 | Badge, NotificationBadge, Count, MannerTempBadge | 알림/수량/도메인 용도 분리 |
| 도메인 전용 | MannerTemp, MannerTempBadge, Celsius, IdentityPlaceholder | 당근 서비스 도메인(매너온도) 컴포넌트를 DS에 포함 |

## 3. variant 철학

### 3.1 Button(= ActionButton)의 variant 축 전체

생성 타입 정의 원문 인용. (`packages/css/recipes/action-button.d.ts:13,22,29`)

```ts
variant: "brandSolid" | "neutralSolid" | "neutralWeak" | "criticalSolid"
       | "brandOutline" | "neutralOutline" | "ghost";   // 13행
size: "xsmall" | "small" | "medium" | "large";           // 22행
layout: "withText" | "iconOnly";                          // 29행
```

React 쪽 추가 축: `ghost` 전용 `color`, `fontWeight` prop과 `loading` 상태. (`packages/react/src/components/ActionButton/ActionButton.tsx:22-41`)

특징 3가지:

1. variant 이름이 의도를 인코딩한다. brand/neutral/critical(의미) × solid/weak/outline(강도) 조합이다. 색상 이름이 아니다.
2. 타입 JSDoc에 사용 규칙을 박아 넣었다. 예: "`neutralSolid`: 대부분의 화면에서 CTA로 사용합니다. 한 화면에 하나만 사용하는 것을 권장합니다." (`packages/css/recipes/action-button.d.ts:5`)
3. size별 minHeight를 토큰으로 고정한다. xsmall 32px, small 36px, medium 40px, large 52px. (`packages/rootage/components/action-button.yaml:356,388,420,452`, 값은 `dimension.yaml`)

### 3.2 오버레이: BottomSheet

variant 축은 2개뿐이다. (`packages/qvism-preset/src/recipes/bottom-sheet.ts:200-284`)

| 축 | 값 | 근거 |
| --- | --- | --- |
| `headerAlign` | `left` \| `center` | bottom-sheet.ts:201 |
| `skipAnimation` | boolean | bottom-sheet.ts:230 |

오버레이의 용도 분화는 variant가 아니라 컴포넌트 분리로 해결한다. 확인 액션 목록은 ActionSheet, 컨텍스트 메뉴는 MenuSheet, 콘텐츠 시트는 BottomSheet, 알림성 모달은 Dialog로 나눈다. ActionSheet의 항목은 `tone: neutral | critical` 축으로 파괴적 액션을 구분한다. (`packages/qvism-preset/src/recipes/action-sheet-item.ts:40-52`)

### 3.3 리스트: List / ListItem

variant 축은 `highlighted: boolean` 1개다. (`packages/css/recipes/list-item.d.ts:5`)

변형은 variant 대신 slot 조합으로 만든다. Root, Item, Content, Title, Detail, Prefix, Suffix 슬롯을 제공한다. (`packages/react/src/components/List/List.namespace.ts`) Item은 Checkbox/RadioGroup/Switch의 headless context를 감지해 상태 스타일을 입힌다. (`packages/react/src/components/List/List.tsx:14-19`)

### 3.4 use-case variant 판정

있다. 두 층위에서 나타난다.

- 컴포넌트 층위: 2.3의 표 전체. 특히 범용 Button 없이 ActionButton부터 시작하는 결정이 핵심이다.
- variant 층위: ActionButton의 `criticalSolid`("삭제나 초기화처럼 되돌릴 수 없는 작업"), ActionSheetItem의 `tone=critical`, ListItem의 `highlighted`.

정리하면, Seed의 규칙은 이렇다: 용도가 다르면 컴포넌트를 새로 만든다. 같은 컴포넌트 안의 variant는 의미 축(brand/neutral/critical)과 크기 축으로 제한한다. 축 수는 1~3개를 유지한다.

## 4. 모바일 어휘

| 어휘 | 실존 여부 | 위치 |
| --- | --- | --- |
| BottomSheet | 있음 (+ BottomSheetHandle) | `packages/react/src/components/BottomSheet/` |
| ActionSheet | 있음 (+ ExtendedActionSheet) | `packages/react/src/components/ActionSheet/` |
| MenuSheet / SwipeableMenuSheet | 있음 | `packages/react/src/components/MenuSheet/`, `SwipeableMenuSheet/` |
| PullToRefresh | 있음, styled + headless | `packages/react/src/components/PullToRefresh/`, `packages/react-headless/pull-to-refresh/` |
| SafeArea | CSS 변수로 있음: `--seed-safe-area-top/bottom` | `packages/qvism-preset/src/global.ts:7-17` |
| Toast | 없음. Snackbar가 대체. safe-area 오프셋 내장 | `packages/qvism-preset/src/recipes/snackbar.ts:21-23` |
| FAB 계열 | 있음: Fab, ExtendedFab, FloatingActionButton, ContextualFloatingButton | `packages/react/src/components/` |
| Bubble | 있음: HelpBubble, HelpBubbleTooltip | `packages/react/src/components/HelpBubble/` |
| NavBar/AppBar | 있음: stackflow용 AppBar, AppScreen. 토큰은 top-navigation | `packages/stackflow/src/components/`, `packages/rootage/components/top-navigation.yaml` |
| WheelPicker (iOS식 휠) | 있음, 내부 전용. TimePicker가 사용 | `packages/react/src/components/private/WheelPicker.tsx` |
| SegmentedControl / ChipTabs | 있음 | `packages/react/src/components/` |
| TabBar | 없음. Tabs, ChipTabs로 대체 | - |
| SwipeAction | 전용 컴포넌트 없음. SwipeableMenuSheet만 존재 | - |
| IndexBar | 없음 | - |

추가 근거: Lynx(모바일 크로스플랫폼 프레임워크) 전용 패키지 `@seed-design/lynx-react` 0.3.1이 별도로 존재한다. (`packages/lynx-react/package.json`)

## 5. 스타일링과 테마

### 5.1 CSS 방식

- 소스는 TS 레시피다. `defineRecipe({ base, variants, compoundVariants, defaultVariants })` 형태로 작성한다. (`packages/qvism-preset/src/recipes/*.ts`)
- 빌드 타임에 정적 CSS와 타입을 생성한다. 결과는 `packages/css/recipes/*.css` + `*.d.ts`다. 런타임 CSS-in-JS가 없다.
- 모든 값은 `--seed-*` CSS 변수를 거친다. React는 생성된 레시피 함수로 클래스명만 조합한다. (`packages/react/src/components/ActionButton/ActionButton.tsx:58`)
- `@layer` 버전(`all.layered.css`)과 Tailwind 3/4 플러그인도 제공한다. (`packages/css/`, `packages/tailwind3-plugin/`, `packages/tailwind4-theme/`)

### 5.2 테마 전환

- html 루트의 data 속성으로 전환한다: `data-seed-color-mode`(system | light-only | dark-only), `data-seed-user-color-scheme`(light | dark), `data-seed-platform`(ios | android). (`packages/css/theming/index.mjs`, `mode.mjs:1`)
- FOUC 방지용 인라인 부트 스크립트 `generateThemingScript`를 제공한다. 이 스크립트가 `prefers-color-scheme` 구독, 웹뷰 브리지 기반 플랫폼 감지, iOS 폰트 스케일링 활성화를 모두 처리한다. (`packages/css/theming/index.mjs:3-52`)
- 다크모드는 토큰 계층에서 해결한다. 모든 색 토큰이 theme-light/theme-dark 값 쌍을 가진다. (`packages/rootage/color.yaml`)

### 5.3 인터랙션 상태

- `engaged` 커스텀 셀렉터가 hover/active를 통합한다. postcss-engaged 플러그인이 장치 능력별로 `:hover`(포인터 장치)와 `:active`(터치 장치)로 컴파일한다. (`packages/qvism-preset/src/utils/pseudo.ts:28-32`, `ecosystem/postcss-engaged/src/index.ts:44-46`)
- 레시피 소스에서 hover 문자열은 2개 파일(list-item, select)에만 나타난다. 모두 `isHoverableInputDevice` 미디어 가드 안에 있다. (`packages/qvism-preset/src/recipes/list-item.ts:150-153`)

## 6. 신규 DS 시사점 (모바일 웹뷰 앱 기준)

1. hover를 1급 상태로 두지 않는다. Seed의 engaged 패턴을 채택한다: pressed를 기본 인터랙션 상태로 정의하고, `@media (hover: hover) and (pointer: fine)` 가드 안에서만 hover를 허용한다. semantic 색 토큰에 `-pressed` 쌍을 내장한다.
2. 웹뷰 플랫폼 감지를 테마 부트 스크립트에 넣는다. Seed처럼 브리지 객체(`window.webkit.messageHandlers` 등)로 iOS/Android를 판별하고, html data 속성 하나로 색 모드와 플랫폼 토큰을 스위칭한다. FOUC 방지와 다크모드를 한 스크립트로 해결한다.
3. use-case 분화는 variant 축이 아니라 컴포넌트 분리로 한다. 범용 Button에 축을 쌓는 대신 ActionButton처럼 용도 이름의 컴포넌트를 만들고, 각 컴포넌트의 variant 축은 3개 이하로 유지한다. variant 값 이름은 의미(brand/neutral/critical × solid/weak/outline)로 짓고, 사용 규칙을 타입 JSDoc에 박는다.
4. 오버레이는 목적별 컴포넌트 세트(BottomSheet, ActionSheet, MenuSheet, Dialog)로 나눈다. 그리고 ResponsiveDialog 같은 어댑터 1개로 breakpoint에 따라 BottomSheet와 Dialog를 전환한다. 태블릿/데스크톱 대응 비용을 어댑터 1개로 격리할 수 있다.
5. safe-area를 컴포넌트마다 처리하지 않는다. 전역 CSS 변수(`--seed-safe-area-*`)로 한 번 정규화하고, 하단 고정 컴포넌트(Snackbar, Sheet, FAB) 레시피가 그 변수를 참조하게 한다.
