# Base Web (Uber) 실측 분석

## 0. 요약

| 항목 | 실측 결과 |
| --- | --- |
| 시스템 | Base Web (baseui), Uber |
| 버전 | 18.2.0 (package.json:3) |
| 플랫폼 판정 | responsive. 데스크톱 출신 범용 웹 시스템에 모바일 계층을 최근 추가했다 |
| 컴포넌트 총수 | 81개 디렉터리 |
| 토큰 계층 | 색상 4계층: primitive, foundation, semantic, component |
| 스타일링 | Styletron 기반 atomic CSS-in-JS. 테마는 React Context로 주입 |
| 특징 | 전 컴포넌트 overrides 시스템. use-case 컴포넌트는 primitive Button 을 합성해서 만든다 |

플랫폼 판정 근거는 다음과 같다.

| 근거 | 판정 방향 | 출처 |
| --- | --- | --- |
| 반응형 breakpoint 3단: 320 / 600 / 1136 | responsive | src/themes/shared/breakpoints.ts:9-13 |
| hover 스타일을 `@media (hover: hover)` 로 감싼다 | 터치 인지 | src/button/styled-components.ts:470 |
| `minHitArea: 'tap'` 이 히트 영역을 48px 로 확장한다 | 터치 인지 | src/button/constants.ts:43-46, src/button/styled-components.ts:858-876 |
| 모바일 전용 컴포넌트 군 존재: sheet, mobile-header, bottom-navigation, sliding-button, page-control, button-dock | 모바일 추가 | src/ 디렉터리 |
| safe-area 처리 코드가 전무하다 (`safe-area`, `safeArea` grep 0건) | 모바일 미완성 | src/ 전체 grep |
| 데스크톱 전용 대형 컴포넌트 존재: data-table, header-navigation, timezonepicker | 데스크톱 출신 | src/ 디렉터리 |

결론: mobile-first 는 아니다. 데스크톱 웹에서 출발한 시스템이 18.x 에서 모바일 어휘를 흡수하는 중이다.

## 1. 토큰 아키텍처

색상 토큰은 4계층이다. 각 계층은 함수로 이전 계층을 받아 합성된다 (src/themes/light-theme/create-light-theme.ts:20-36).

| 계층 | 역할 | 정의 파일 | 네이밍 예시 |
| --- | --- | --- | --- |
| 1. primitive | 순수 팔레트. 테마 무관 | src/tokens/color-primitive-tokens.ts | `gray50`, `red600`, `brandDefault600` |
| 2. foundation | 브랜드 의미 팔레트. 테마별 정의 | src/themes/light-theme/color-foundation-tokens.ts:11-33 | `primaryA`, `accent400`, `negative500` |
| 3. semantic | 역할 토큰. UI 의미 단위 | src/themes/light-theme/color-semantic-tokens.ts:23-52 | `backgroundPrimary`, `contentSecondary`, `borderOpaque` |
| 4. component | 컴포넌트별 슬롯 토큰 | src/themes/light-theme/color-component-tokens.ts:16-45 | `buttonPrimaryFill`, `bottomNavigationSelectedText` |

색상 외 토큰은 라이트와 다크가 공유한다. 위치는 src/themes/shared/ 이다.

| 종류 | 파일 | 예시 |
| --- | --- | --- |
| sizing | src/themes/shared/sizing.ts | `scale550: '14px'`, `scale1200: '48px'` |
| typography | src/themes/shared/typography.ts:147-162 | `LabelLarge`, `ParagraphMedium`, `DisplayLarge` |
| breakpoints, media-query | src/themes/shared/breakpoints.ts | `small: 320`, `large: 1136` |
| 기타 | animation.ts, borders.ts, lighting.ts, grid.ts | - |

특이점: foundation 만 바꿔도 semantic 과 component 가 함수로 재계산된다 (create-light-theme.ts:20-27). 브랜드 재테마 비용이 낮다. 대신 component 토큰 수가 수백 개라 유지 비용이 크다.

## 2. 컴포넌트 인벤토리

집계 방법: `find src -maxdepth 1 -type d` 로 상위 디렉터리를 센다. 비컴포넌트 10개(a11y, helpers, locale, styles, template-component, test, themes, tokens, types, utils)를 제외한다. 결과는 81개다.

주의: v2 중복이 별도 디렉터리로 존재한다. checkbox / checkbox-v2, radio / radio-v2, tabs / tabs-motion, table / table-grid / table-semantic, file-uploader / file-uploader-basic, modal / dialog.

| 분류 | 예시 |
| --- | --- |
| primitive (범용 원자) | button, input, textarea, checkbox, radio, select, slider, switch, tag, badge, avatar, popover, tooltip, modal, list, menu, tabs, accordion, card |
| layout | block, flex-grid, layout-grid, aspect-ratio-box, divider |
| use-case (용도 지정) | button-timed, sliding-button, button-dock, payment-card, phone-input, pin-code, datepicker, timepicker, timezonepicker, file-uploader, app-nav-bar, mobile-header, bottom-navigation, message-card, system-banner, page-control, dnd-list, map-marker |
| 데스크톱 지향 | data-table, header-navigation, side-navigation, tree-view, pagination |

primitive 계층과 use-case 계층이 한 패키지 안에 평면으로 공존한다. Seed Design 처럼 계층을 패키지로 분리하지 않았다.

## 3. variant 철학

### 3.1 Button 의 variant 축

정의 위치: src/button/constants.ts. props 결합 위치: src/button/types.ts:27-65.

| 축 | 값 | 출처 |
| --- | --- | --- |
| kind | `primary`, `secondary`, `tertiary`, `dangerPrimary`, `dangerSecondary`, `dangerTertiary` | src/button/constants.ts:7-14 |
| shape | `default`, `rectangular`, `rounded`, `pill`, `round`(deprecated), `circle`, `square` | src/button/constants.ts:20-31 |
| size | `mini`, `default`, `compact`, `large`, `xSmall`, `small`, `medium` (신구 네이밍 공존) | src/button/constants.ts:33-41 |
| minHitArea | `tap`, `click` | src/button/constants.ts:43-46 |
| widthType | `hug`, `fill` | src/button/constants.ts:48-51 |
| 상태 boolean | `isLoading`, `isSelected`, `disabled`, `backgroundSafe` | src/button/types.ts:34-46 |

kind 축에 danger 용도가 직교 축이 아니라 값으로 박혀 있다. 색상 의도(primary/danger)와 강조 수준(primary/secondary/tertiary)을 한 축에 6값으로 폈다.

### 3.2 오버레이 계열: Dialog (신형)

구형 Modal 과 신형 Dialog 가 공존한다.

| 컴포넌트 | 축 | 값 | 출처 |
| --- | --- | --- | --- |
| Dialog | size | `xSmall`, `small`, `medium`, `large` | src/dialog/constants.ts:7-12 |
| Dialog | placement | `center`, `topLeft`, `topCenter`, `topRight`, `bottomLeft`, `bottomCenter`, `bottomRight` | src/dialog/constants.ts:14-22 |
| Modal (구형) | size | `default`(500px), `full`, `auto` | src/modal/constants.ts:7-17 |
| Modal (구형) | role | `dialog`, `alertdialog` | src/modal/constants.ts:19-22 |
| Sheet | 변형 축 없음. `draggable`, `topPosition` prop 만 있다 | - | src/sheet/types.ts:35-46 |

Dialog 는 `buttonDock` prop 으로 ButtonDock(하단 버튼 영역)을 내장한다 (src/dialog/types.ts:29-30). 오버레이와 액션 영역을 조립식으로 묶었다.

### 3.3 리스트 계열: ListItem

| 축 | 값 | 출처 |
| --- | --- | --- |
| artworkSize | `SMALL`, `MEDIUM`, `LARGE` | src/list/constants.ts:7-11 |
| shape | `DEFAULT`, `ROUND` | src/list/constants.ts:13-16 |
| 구조 prop | `artwork`, `endEnhancer`, `sublist` | src/list/types.ts:40-57 |

`onClick` 이 있으면 li 를 button 태그로 바꾸고 탭 타깃 스타일을 적용한다 (src/list/list-item.tsx:54,80-81). 터치 인터랙션을 prop 존재 여부로 자동 판단한다.

### 3.4 use-case variant 실존 사례

| 사례 | 내용 | 출처 |
| --- | --- | --- |
| Button `kind: dangerPrimary` | 파괴적 액션 용도가 kind 값에 박혀 있다 | src/button/constants.ts:11-13 |
| Button `minHitArea: 'tap'` | 모바일 탭 용도 전용 값. `::before` 로 48px 히트 영역 확장 | src/button/styled-components.ts:858-876 |
| ButtonTimed | 카운트다운 후 자동 실행되는 확인 버튼. Button props 를 상속 | src/button-timed/types.ts:14-19 |
| SlidingButton | 밀어서 확정하는 버튼. threshold `low`(20%) / `high`(80%) | src/sliding-button/types.ts:21-38 |
| ButtonDock | `primaryAction`, `secondaryActions`, `dismissiveAction` 슬롯을 가진 하단 버튼 영역 | src/button-dock/types.ts:15-21 |
| Sheet ActionButton | Button 에 `kind: tertiary`, `shape: square`, 48px 탭 타깃을 프리셋 | src/sheet/action-button.tsx:10-46 |

공통 패턴: use-case 컴포넌트는 primitive 를 포크하지 않는다. Button 을 import 해서 프리셋 props 와 overrides 로 합성한다.

## 4. 모바일 어휘

| 어휘 | 실존 여부 | 디렉터리 / 근거 |
| --- | --- | --- |
| BottomSheet | 있음 (이름은 Sheet). Grabber 와 draggable 지원 | src/sheet/, src/sheet/types.ts:15,39 |
| TabBar | 있음 (이름은 BottomNavigation) | src/bottom-navigation/ |
| NavBar | 있음 (이름은 MobileHeader). `fixed` / `floating` 타입 | src/mobile-header/, src/mobile-header/constants.ts:6-9 |
| PageControl (iOS 점 인디케이터) | 있음 | src/page-control/ |
| SwipeAction | 부분적. 밀어서 확정하는 SlidingButton 만 있다. 리스트 스와이프는 없다 | src/sliding-button/sliding-button.tsx:64-115 (Pointer Events) |
| Toast / Snackbar | 둘 다 있음 | src/toast/, src/snackbar/ |
| Drawer | 있음 | src/drawer/ |
| ActionSheet | 없음. Sheet 로 대체 |
| SafeArea | 없음. grep 0건 |
| PullToRefresh | 없음 |
| IndexBar | 없음 |
| FloatingPanel / Bubble | 없음 |

앱 셸 어휘(TabBar, NavBar, BottomSheet)는 갖췄다. 제스처 어휘(PullToRefresh, SwipeAction, IndexBar)는 없다. safe-area 는 사용자 몫이다.

## 5. 스타일링과 테마

| 항목 | 실측 |
| --- | --- |
| CSS 방식 | Styletron atomic CSS-in-JS. peerDependencies 에 `styletron-react >= 6` (package.json) |
| 테마 주입 | React Context. `ThemeContext` 에 theme 객체를 넣는다 (src/styles/theme-provider.tsx:12-18) |
| 앱 루트 | BaseProvider 가 LayersManager 와 ThemeProvider 를 묶는다 (src/helpers/base-provider.tsx:13-24) |
| 테마 전환 | theme 객체 교체 방식. LightTheme / DarkTheme / createLightTheme / createDarkTheme. CSS 변수를 쓰지 않는다 |
| 폰트 변형 테마 | move-theme (Uber Move 폰트 적용판) 이 별도 존재 (src/themes/move-theme/) |
| 커스터마이징 | 전 컴포넌트가 내부 요소별 `overrides` prop 을 노출한다 (예: src/button/types.ts:12-20 의 7개 슬롯) |

CSS 변수 기반이 아니라서 테마 전환 시 리렌더가 발생한다. 런타임 CSS-in-JS 라서 웹뷰 초기 로드에 스타일 계산 비용이 붙는다.

## 6. 신규 DS 시사점 (모바일 웹뷰 기준)

1. `minHitArea: 'tap'` 패턴을 가져온다. 시각 크기를 유지한 채 `::before` 가상 요소로 히트 영역만 48px 로 넓힌다 (src/button/styled-components.ts:858-876). 밀도 높은 모바일 UI 에서 터치 정확도 문제를 그대로 푼다.
2. hover 스타일은 전부 `@media (hover: hover)` 안에 넣는 규칙을 컨벤션으로 채택한다 (src/button/styled-components.ts:470). 웹뷰의 sticky hover 버그를 원천 차단한다.
3. use-case 계층은 포크가 아니라 합성으로 만든다. ButtonTimed, SlidingButton, Sheet ActionButton 전부 primitive Button 에 프리셋 props 를 얹은 래퍼다. Seed 식 use-case 컴포넌트를 도입하더라도 primitive 위 합성 레이어로 두면 유지 비용이 낮다.
4. 용도 축 설계는 Base Web 방식을 피한다. kind 6값(primary~dangerTertiary)은 색상 의도와 강조 수준을 한 축에 뭉쳤다. 신규 DS 는 `variant(강조) x tone(의도)` 2축 직교가 조합 폭발 없이 더 깔끔하다. 또한 size 축의 신구 네이밍 공존(mini/xSmall, compact/small)은 초기 네이밍 실패의 이월 비용을 보여준다 (src/button/constants.ts:33-41).
5. component 토큰 계층(4계층째)은 선택 도입한다. Base Web 은 `buttonPrimaryFill` 같은 토큰을 수백 개 유지한다. 소규모 팀은 primitive, semantic 2~3계층으로 시작하고, foundation 을 함수 입력으로 받아 상위 계층을 재계산하는 구조(create-light-theme.ts:20-27)만 가져오는 편이 낫다.
6. safe-area, PullToRefresh, SwipeAction 은 Base Web 에서 가져올 것이 없다. 이 영역은 Seed Design 같은 모바일 전용 시스템을 참조해야 한다.
