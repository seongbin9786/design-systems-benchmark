# VKUI (VK) 소스 실측 분석

- 실측 대상: `sources-candidates/vkui` (sparse, packages/vkui만), `sources-candidates/vkui-tokens`
- 버전: `@vkontakte/vkui` 8.3.0 (vkui/packages/vkui/package.json:3)
- 경로 표기: 이 문서의 파일 경로는 `sources-candidates/` 기준 상대 경로다.

## 0. 요약

| 항목 | 판정 |
|---|---|
| 플랫폼 지향 | mobile-first. 모바일 웹뷰가 기본이고 데스크톱(vkcom)은 opt-in 적응이다 |
| 토큰 | 3계층. figma 원시값 JSON, 시맨틱+컴포넌트 토큰(TS 기술), 테마 상속. 빌드로 CSS 변수 산출 |
| 컴포넌트 | 총 156개 디렉터리. 앱 셸(Epic/Root/View/Panel)까지 컴포넌트로 제공 |
| variant 철학 | primitive는 직교 축(mode x appearance x size). 용도는 별도 컴포넌트로 분리 |
| 스타일링 | CSS Modules + PostCSS + CSS 변수. 루트 클래스 교체로 테마 전환 |

플랫폼 판정 근거:

1. platform 자동 감지는 ios 또는 android만 반환한다. android가 기본 플랫폼이다. vkcom은 vk.com 미니앱용으로 명시 지정해야 한다 (vkui/packages/vkui/src/lib/platform.ts:10-22).
2. safe-area inset을 전역 CSS 변수로 정의한다 (vkui/packages/vkui/src/styles/constants.css:100-115). Tabbar와 PanelHeader가 이 변수를 소비한다 (Tabbar/Tabbar.module.css:10, PanelHeader/PanelHeader.module.css:70).
3. View가 iOS 엣지 스와이프 백 제스처를 직접 구현한다 (vkui/packages/vkui/src/components/View/View.tsx:40-50, 106-114).
4. PullToRefresh, Tabbar, ActionSheet, ModalPage(스냅 포인트) 같은 모바일 셸 컴포넌트가 1급 시민이다.
5. 데스크톱 대응도 있다. ActionSheet는 데스크톱에서 menu, 모바일에서 sheet를 자동 선택한다 (ActionSheet/ActionSheet.tsx:163). SplitLayout/SplitCol로 다단 레이아웃을 만든다. 그래서 순수 mobile-only가 아니라 mobile-first + 데스크톱 적응이다.

## 1. 토큰 아키텍처

토큰은 별도 저장소 `vkui-tokens`에 있다. 구조는 3계층이다.

| 계층 | 역할 | 위치 |
|---|---|---|
| 1. 원시값 | Figma에서 추출한 팔레트 JSON | vkui-tokens/src/themeDescriptions/base/figma/vk.json (vk.ts:10에서 import) |
| 2. 시맨틱 + 컴포넌트 토큰 | TS로 테마를 기술. 색/타이포/크기/컴포넌트 치수 | vkui-tokens/src/themeDescriptions/base/vk.ts |
| 3. 테마 상속 | 기본 테마를 spread로 상속하고 차이만 덮어쓴다 | vkui-tokens/src/themeDescriptions/themes/* (69개 테마 인터페이스) |

특이점 2가지가 있다.

1. 토큰 값 자체가 구조체다. 색 토큰은 normal/hover/active 상태를 내장한다 (base/vk.ts:50-57). 크기 토큰은 regular/compact 밀도를 내장한다 (themes/vkIOS/index.ts:24-28의 `sizeSwitchHeight { regular: 31, compact: 27 }`).
2. 컴포넌트 토큰이 테마 계층에 산다. `sizeSwitchHeight`, `sizePanelHeaderHeight` 같은 토큰을 테마별로 덮어쓴다 (themes/vkIOS/index.ts:24-40).

테마 상속의 실례: vkIOS 테마는 `...lightTheme`으로 vkBase를 펼치고 `themeInheritsFrom: 'vkBase'`를 선언한다 (themes/vkIOS/index.ts:9).

빌드는 css, scss, less, pcss, styl, js, json 포맷을 산출한다 (vkui-tokens/README.md:12). CSS 변수 이름 규칙은 `--vkui--{token}--{state}`다. 예: `--vkui--color_background--hover` (README.md:69).

네이밍 예시 (base/vk.ts 실측):

| 토큰 | 위치 |
|---|---|
| `colorBackgroundAccent` | base/vk.ts:31 |
| `colorTextPrimary` | base/vk.ts:121 |
| `fontTitle1` | base/vk.ts:379 |
| `sizeBorderRadius` | base/vk.ts:548 |
| `sizeButtonPaddingHorizontal` | base/vk.ts:612 |
| CSS 산출물: `--vkui--color_background--hover` | vkui-tokens/README.md:69 |

## 2. 컴포넌트 인벤토리

- 총수: 156개
- 세는 방법: `find vkui/packages/vkui/src/components -maxdepth 1 -type d | tail -n +2 | wc -l`
- 기준: `src/components` 바로 아래 디렉터리 1개를 컴포넌트 1개로 센다. Provider, Context, 내부용 Base 컴포넌트(ImageBase, TooltipBase 등)를 포함한 수치다.

분류 예시:

| 분류 | 예시 |
|---|---|
| primitive | Button, Input, Checkbox, Radio, Switch, Select, Textarea, Slider, Avatar, Badge, Card, Spinner, Progress, Link, IconButton, Flex, Box, Separator, Typography |
| 앱 셸 | AppRoot, Epic, Root, View, Panel, PanelHeader, SplitLayout, SplitCol, FixedLayout, Tabbar |
| 오버레이 | ActionSheet, Alert, ModalRoot, ModalPage, ModalCard, Popover, Snackbar, ScreenSpinner |
| 리스트 | List, Cell, SimpleCell, RichCell, MiniInfoCell, HorizontalCell, CellButton |
| use-case 지정 | PanelHeaderBack, PanelHeaderClose, PanelHeaderSubmit, PanelHeaderEdit, WriteBar, WriteBarIcon, ModalDismissButton, ActionSheetDefaultIosCloseItem, SubnavigationBar, UsersStack |
| 제스처/인프라 | Touch, Tappable, Clickable, PullToRefresh, CustomScrollView, FocusTrap |

앱 셸 계층이 특징이다. Epic(하단 탭 셸) > Root/View(화면 스택) > Panel(개별 화면) 구조다. Epic은 `tabbar` prop을 직접 받는다 (Epic/Epic.tsx:16). View는 스와이프 백과 화면 전환 애니메이션을 소유한다. Epic은 스토리별 스크롤 위치를 보존한다 (Epic/ScrollSaver.tsx).

## 3. variant 철학

### 3.1 Button: 직교 3축

vkui/packages/vkui/src/components/Button/Button.tsx:58-73 인용:

```ts
mode?: 'primary' | 'secondary' | 'tertiary' | 'outline' | 'link' | undefined;   // :58
appearance?: 'accent' | 'positive' | 'negative' | 'neutral' | 'overlay'
  | 'accent-invariable' | undefined;                                            // :62-69
size?: 's' | 'm' | 'l' | undefined;                                             // :73
```

| 축 | 값 | 의미 |
|---|---|---|
| mode | primary, secondary, tertiary, outline, link (5종) | 시각적 위계 |
| appearance | accent, positive, negative, neutral, overlay, accent-invariable (6종) | 색 의미 |
| size | s, m, l (3종) | 크기 |
| 보조 | stretched, rounded, align, elevation, loading | 불리언/단계 축 (Button.tsx:77-118) |

위계(mode)와 색 의미(appearance)를 분리한 점이 핵심이다. 이론상 5 x 6 x 3 = 90 조합이 나온다. 조합 제한은 타입에 없다.

### 3.2 오버레이: ActionSheet

- `mode?: 'sheet' | 'menu'` (ActionSheet/ActionSheet.tsx:103). 미지정 시 데스크톱이면 menu, 아니면 sheet를 선택한다 (ActionSheet.tsx:163).
- 같은 API로 모바일에서는 바텀시트, 데스크톱에서는 드롭다운 메뉴를 렌더한다. 렌더러를 분기한다 (ActionSheet.tsx:191).
- ModalPage는 variant 대신 스냅 포인트 축을 쓴다. `settlingHeight`(기본 50)와 `dynamicContentHeight`로 시트 높이를 제어한다 (ModalPage/ModalPage.tsx:27-28).

### 3.3 리스트: Cell 계열

리스트 셀을 3단으로 나눈다. SimpleCell(표시) < Cell(편집) < RichCell(리치 콘텐츠).

- SimpleCell: variant 축이 거의 없다. before/after/subtitle/indicator 같은 슬롯 prop으로 조립한다 (SimpleCell/SimpleCell.tsx:21-81). 유일한 축은 `chevron?: 'auto' | 'always'`이고 auto는 iOS에서만 쉐브론을 그린다 (SimpleCell.tsx:72).
- Cell: `mode?: 'removable' | 'selectable'`와 `draggable` (Cell/Cell.tsx:26, 30). 편집 동작이 variant다.

### 3.4 use-case variant: 있다, 많다

| 사례 | 인용 |
|---|---|
| ActionSheetItem `mode?: 'default' \| 'destructive' \| 'cancel'` | ActionSheetItem/ActionSheetItem.tsx:33 |
| PanelHeaderSubmit: 확인 전용 헤더 버튼. 기본 라벨 'Готово'(완료) | PanelHeaderSubmit/PanelHeaderSubmit.tsx:18 |
| PanelHeaderBack: 뒤로가기 전용. 기본 라벨 'Назад'(뒤로). iOS에서만 라벨 노출 | PanelHeaderBack/PanelHeaderBack.tsx:78, 87 |
| WriteBarIcon `mode?: 'attach' \| 'send' \| 'done'`: 채팅 입력창 전용 아이콘 버튼 | WriteBarIcon/WriteBarIcon.tsx:41 |
| CellButton `appearance?: 'accent' \| 'neutral' \| 'negative'`: 리스트 안 행동 버튼, negative는 파괴 동작용 | CellButton/CellButton.tsx:90 |

패턴이 일관된다. primitive(Button, Cell)는 직교 축만 갖는다. 용도는 variant로 붙이지 않고 이름 있는 별도 컴포넌트(PanelHeaderSubmit, CellButton, WriteBarIcon)로 만든다. 예외적으로 오버레이 아이템(ActionSheetItem)은 destructive/cancel 같은 용도 variant를 갖는다.

또 하나의 암묵 variant 축은 platform이다. `platform: 'android' | 'ios' | 'vkcom'` (lib/platform.ts:15)이 컴포넌트 렌더를 바꾼다. 예: PanelHeaderSubmit은 iOS에서 텍스트, 그 외에서 아이콘을 그린다 (PanelHeaderSubmit.tsx:26-31).

## 4. 모바일 어휘

디렉터리 실존 확인 결과다 (vkui/packages/vkui/src/components/ 기준).

| 어휘 | 존재 | VKUI 이름 | 비고 |
|---|---|---|---|
| BottomSheet | O | ModalPage, ActionSheet(mode=sheet) | 스냅 포인트, 드래그 닫기 지원 |
| ActionSheet | O | ActionSheet, ActionSheetItem | destructive/cancel 모드 포함 |
| SafeArea | O (컴포넌트 아님) | `--vkui_internal--safe_area_inset_*` 전역 변수 | styles/constants.css:100-115 |
| PullToRefresh | O | PullToRefresh | Touch 기반 자체 구현 |
| SwipeAction | X | 없음 | Cell mode=removable은 버튼 방식 삭제다 |
| IndexBar | X | 없음 | |
| FloatingPanel/Bubble | X | 없음 | FixedLayout이 고정 배치만 담당 |
| TabBar | O | Tabbar, TabbarItem | Epic이 tabbar prop으로 수용 |
| NavBar | O | PanelHeader + Back/Close/Submit/Edit | safe-area top 반영 |
| Toast | O (유사) | Snackbar | |
| 제스처 프리미티브 | O | Touch, Tappable | PullToRefresh, View가 재사용 |
| 스와이프 백 | O | View의 onSwipeBack | View/View.tsx:40-50 |
| 채팅 입력바 | O | WriteBar, WriteBarIcon | 메신저 특화 |

## 5. 스타일링과 테마

| 항목 | 실측 |
|---|---|
| CSS 방식 | CSS Modules (`*.module.css`) + PostCSS. CSS-in-JS 없음 |
| 토큰 소비 | vkui-tokens가 생성한 CSS 변수 `--vkui--*`를 import (styles/themes.css:1-7) |
| 테마 전환 | 루트 클래스 교체. `vkui--vkBase--light` 같은 클래스가 platform x colorScheme 매트릭스로 정해진다 (lib/tokens/constants.ts:1-14) |
| 컬러 스킴 감지 | ColorSchemeProvider + useAutoDetectColorScheme (ConfigProvider/ConfigProvider.tsx:37) |
| 반응형 | 빌드 시 생성한 custom media (styles/customMedias.generated.css). 브레이크포인트 6개: 320/768/1024/1280 + 높이 2개 (lib/adaptivity/breakpoints.ts:1-8) |
| 밀도 | AdaptivityProvider의 viewWidth/viewHeight/density/hasPointer (AdaptivityProvider.tsx:17-24). sizeX/sizeY는 v8에서 deprecated, viewWidth/density로 이행 중 (AdaptivityProvider.tsx:40-47) |
| DPI 대응 | 보더 두께를 dppx 미디어 쿼리로 서브픽셀 전환 (styles/dynamicTokens.css:15-27) |

테마 전환 흐름: ConfigProvider가 platform과 colorScheme을 결정한다. TokensClassProvider가 자식 루트에 토큰 클래스를 주입한다 (lib/tokens/TokensClassProvider.tsx:14-20). CSS 변수 값만 바뀌고 컴포넌트 CSS는 그대로다.

## 6. 신규 DS 시사점 (모바일 웹뷰 기준)

1. 앱 셸을 DS에 포함할지 결정하라. VKUI는 Epic/Root/View/Panel + 스와이프 백 + 스크롤 보존까지 DS가 소유한다. 웹뷰 앱에서 네이티브 유사 내비게이션을 표준화하려면 이 계층이 가장 효과가 크다. 단, 라우터와의 결합 비용이 따라온다.
2. 토큰 값에 상태와 밀도를 내장하는 방식을 검토하라. VKUI 토큰은 `{ normal, hover, active }`와 `{ regular, compact }`를 값 구조로 갖는다. 컴포넌트 코드 수정 없이 터치/포인터 환경 차이를 토큰 차원에서 흡수한다. 모바일 웹뷰 단일 타깃이면 이 복잡도는 줄여도 된다. 반대로 태블릿/데스크톱 확장 계획이 있으면 초기에 넣어야 한다.
3. primitive와 use-case의 분리 규칙을 VKUI처럼 정하라. primitive는 직교 축(mode x appearance x size)만 갖는다. 용도는 PanelHeaderSubmit, CellButton, WriteBarIcon처럼 이름 있는 별도 컴포넌트로 만든다. 오버레이 아이템만 destructive/cancel 용도 variant를 허용한다. 이 규칙이면 Seed Design식 use-case 컴포넌트와 primitive 계층이 충돌 없이 공존한다.
4. safe-area를 컴포넌트가 아니라 전역 CSS 변수 1곳에서 정의하라. VKUI는 constants.css에서 `env(safe-area-inset-*)`를 변수로 감싸고 Tabbar/PanelHeader/ModalCard가 소비한다. 웹뷰 DS의 최소 필수 기반이다.
5. 데스크톱 적응이 필요하면 ActionSheet 패턴을 참고하라. 같은 컴포넌트 API가 뷰포트에 따라 sheet와 menu로 갈린다. 화면별 분기 코드를 앱이 아니라 DS가 갖는다.
