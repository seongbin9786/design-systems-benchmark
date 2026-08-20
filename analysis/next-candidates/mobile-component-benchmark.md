# 모바일 3사 컴포넌트 교차 벤치마크: antd-mobile · Seed · VKUI

- 대상: [insights 리포트](insights.html)에서 **mobile-first**로 판정된 3개 시스템만 골랐다
- 소스: `sources-candidates/` 로컬 클론 (고정 커밋: `sources-candidates/MANIFEST.md`)
- 분석일: 2026-08-13
- 측정 방법: 각 시스템의 컴포넌트 디렉터리를 전수 나열하고, 같은 개념끼리 교차 매핑했다

| 시스템 | 조직 | 측정 위치 | 개수 |
|---|---|---|---|
| antd-mobile | Ant Group | `ant-design-mobile/src/components/` | 83 |
| Seed | 당근 | `seed-design/packages/react/src/components/` + `react-headless/` + `stackflow/` | 87 + 42 + 2 |
| VKUI | VK | `vkui/packages/vkui/src/components/` | 156 |

## 0. 무엇이 고민이었나

기존 벤치마크는 데스크톱 시스템(MUI, Fluent, Carbon 등)이 중심이었다.
모바일 웹뷰용 신규 DS를 설계하려면 다른 질문이 필요했다.

1. 모바일 시스템들이 **공통으로 갖춘 컴포넌트**는 무엇인가? → 그게 신규 DS의 최소 세트다.
2. 시스템마다 **갈리는 컴포넌트**는 무엇인가? → 그건 제품 성격에 따라 선택할 지점이다.
3. 같은 개념을 **다른 이름**으로 부르는 경우는? → 이름을 정할 때 다수결 근거가 된다.

기존 문서는 이 질문에 답하지 않았다.
[insights 리포트](insights.html)는 "누가 mobile-first인가"까지만 판정했다.
[seed-component-tiers.md](seed-component-tiers.md)는 Seed 하나만 분류했다.
이 문서가 3사 교차 비교를 채운다.

## 0.5 먼저 알아야 할 개념 3개

**바텀시트(bottom sheet)** — 화면 아래에서 올라와 드래그로 높이를 조절하는 패널.
모바일 UI의 핵심 오버레이인데, 3사가 전부 다른 이름으로 부른다.

```tsx
// antd-mobile — FloatingPanel. anchors 배열이 멈춤 높이다
<FloatingPanel anchors={[100, window.innerHeight * 0.8]}>내용</FloatingPanel>

// Seed — BottomSheet. Root/Content 조립식
<BottomSheet.Root>
  <BottomSheet.Content>내용</BottomSheet.Content>
</BottomSheet.Root>

// VKUI — ModalPage. settlingHeight(%)가 멈춤 높이다
<ModalPage settlingHeight={80}>내용</ModalPage>
```

**앱 셸(app shell)** — 화면 전환·내비바·탭바 같은 "앱의 뼈대".
보통은 앱 코드의 몫인데, VKUI는 이것까지 컴포넌트로 판다.

```tsx
// VKUI — 화면 스택 자체가 컴포넌트다. iOS 스와이프 백도 View가 처리한다
<Root activeView="main">
  <View id="main" activePanel="feed">
    <Panel id="feed">
      <PanelHeader>피드</PanelHeader>
    </Panel>
  </View>
</Root>
```

**휠 피커(wheel picker)** — iOS 스타일 드럼 롤 선택기.
데스크톱의 `<select>` 드롭다운을 대체하는 모바일 입력 방식이다.

```tsx
// antd-mobile — 1급 컴포넌트. 열(column) 2중 배열로 정의한다
<Picker columns={[["월", "화", "수"]]} />
// Seed — 내부 구현만 있다 (private/WheelPicker.tsx). 공개 API가 아니다
// VKUI — 아예 없다. Calendar와 NativeSelect로 대신한다
```

## 1. 결론 요약

1. **3사 교집합 19개 개념이 곧 "모바일 DS 최소 세트"다.**
   당겨서 새로고침, 액션시트, 바텀시트, 스낵바, 상단 내비바, 탭, 세그먼트, 리스트 셀,
   폼 컨트롤 6종(체크박스·라디오·스위치·슬라이더·텍스트 입력·셀렉트), 날짜 입력,
   아바타, 배지, 스켈레톤, 빈 상태, 로딩, 프로그레스, 팝오버, 이미지, 업로더.
   서로 독립적으로 만든 3사가 전부 이 세트에 수렴했다.

2. **개수 차이(83 vs 131 vs 156)는 커버리지 차이가 아니라 "어디까지 시스템 몫인가"의 차이다.**
   antd-mobile은 화면 *안* 위젯만 판다. 셸은 앱 몫이다.
   Seed는 위젯(87)과 행동 로직(headless 42)을 나누고, 셸(AppScreen·AppBar)은 stackflow 패키지로 뺐다.
   VKUI는 앱 셸(Epic·Root·View·Panel)까지 전부 한 패키지에 넣었다.

3. **갈리는 지점은 4개다. 전부 제품 전략의 차이로 설명된다.**
   하단 탭바(Seed만 없음), 휠 피커(antd-mobile만 1급), FAB(VKUI만 없음), 캐러셀(Seed만 없음).
   상세는 §4.

4. **모바일 UI의 기본 단위는 버튼이 아니라 "셀(리스트 행)"이다.**
   VKUI는 셀을 6종으로 분화했고(Cell·SimpleCell·RichCell·MiniInfoCell·CellButton·HorizontalCell),
   antd-mobile과 Seed도 List를 1급으로 둔다.
   데스크톱 벤치마크에서는 보이지 않던 패턴이다.

## 2. 규모: 숫자가 다른 이유

| | antd-mobile | Seed | VKUI |
|---|---|---|---|
| 공개 컴포넌트 | 83 | 87 (styled) | 156 |
| 행동 로직 분리층 | 없음 (컴포넌트에 내장) | 42 (react-headless) | 없음 (컴포넌트에 내장) |
| 앱 셸 | 없음 (앱 몫) | 별도 패키지 (stackflow 2개) | 포함 (Epic·Root·View·Panel 등) |
| 인프라 성격 포함분 | config-provider 1개 | Portal 등 소수 | Provider·Context 9개, *Base 변형 다수 |

VKUI 156개를 그대로 antd-mobile 83개와 비교하면 안 된다.
VKUI는 앱 셸 ~20개, Provider·Context 9개, 내부 기반(*Base, InputLike 등) ~10개를 포함한 수다.
이를 빼면 세 시스템의 "화면 안 위젯" 규모는 80~120개 선으로 수렴한다.

## 3. 교집합: 3사 전원 보유 (19개 개념)

이름이 다른 칸은 **같은 개념을 다르게 부르는 것**이다.

| 개념 | antd-mobile | Seed | VKUI |
|---|---|---|---|
| 당겨서 새로고침 | pull-to-refresh | PullToRefresh | PullToRefresh |
| 액션시트 | action-sheet | ActionSheet · ExtendedActionSheet · MenuSheet | ActionSheet |
| 바텀시트 | floating-panel | BottomSheet | ModalPage (snap point) |
| 다이얼로그 | dialog · modal | Dialog · ContentDialog | Alert · ModalCard |
| 토스트/스낵바 | toast | Snackbar | Snackbar |
| 상단 내비바 | nav-bar | AppBar (stackflow) | PanelHeader (+ 부속 7종) |
| 탭 | tabs · capsule-tabs · jumbo-tabs | Tabs · ChipTabs | Tabs |
| 세그먼트 | segmented | SegmentedControl | SegmentedControl |
| 리스트/셀 | list | List | Cell 계열 6종 |
| 텍스트 입력 | input · text-area | TextField | Input · Textarea |
| 선택 컨트롤 | checkbox · radio · switch | Checkbox · RadioGroup · Switch | Checkbox · Radio · Switch |
| 슬라이더 | slider | Slider | Slider |
| 셀렉트 | selector · check-list | Select · SelectBox | Select · CustomSelect · NativeSelect |
| 날짜 입력 | date-picker · calendar 계열 | DatePicker · TimePicker | Calendar 계열 · DateInput |
| 업로더 | image-uploader | AttachmentInput | File · DropZone |
| 아바타 | avatar | Avatar | Avatar · GridAvatar |
| 배지/카운트 | badge | Badge · Count · NotificationBadge | Badge · Counter · ContentBadge |
| 스켈레톤/로딩 | skeleton · loading · progress-circle | Skeleton · LoadingIndicator · ProgressCircle | Skeleton · Spinner · Progress |
| 빈 상태 | empty · error-block · result | ContentPlaceholder | Placeholder |

여기에 팝오버/툴팁(popover / HelpBubble / Popover·Tooltip)과 이미지(image / ImageFrame / Image)까지 넓게 잡으면 21개다.

**신규 DS에 적용:** 이 표의 개념은 논쟁 없이 채택한다. 우선순위 논의 대상이 아니다.

## 4. 갈림: 2사 보유, 1사 부재 (4개 지점)

| 개념 | antd-mobile | Seed | VKUI | 부재의 이유 (추정 포함) |
|---|---|---|---|---|
| 하단 탭바 | tab-bar | **없음** | Tabbar | 당근 앱은 탭바가 네이티브다. 웹뷰 DS에는 필요가 없다 |
| 휠 피커 | picker 계열 8종 | 내부용만 (private) | **없음** | antd-mobile만 iOS 관습을 정면 채택했다. VKUI는 Calendar·NativeSelect로 대체한다 |
| FAB | floating-bubble | Fab 계열 4종 | **없음** | VK 소셜 UI에는 떠 있는 행동 버튼 관습이 없다 |
| 캐러셀/스와이퍼 | swiper | **없음** | Gallery · CardScroll · HorizontalScroll | 당근 피드는 세로 스크롤 중심이다 |
| 검색바 | search-bar | **없음** | Search | 〃 (검색 UI가 네이티브 영역) |
| 스테퍼(수량) | stepper | QuantityPicker | **없음** | 커머스 어휘. VK에는 장바구니가 없다 |

**신규 DS에 적용:** 이 표는 제품 성격으로 결정한다.
네이티브 앱에 임베드되는 웹뷰라면 Seed처럼 탭바·검색을 뺀다.
웹 자체가 앱이라면 antd-mobile·VKUI처럼 넣는다.

## 5. 고유: 1사만 보유

### antd-mobile만 (8)

| 컴포넌트 | 성격 |
|---|---|
| swipe-action | 셀을 옆으로 밀어 버튼 노출. **3사 중 유일한 스와이프 행동 컴포넌트** |
| index-bar | 연락처식 A–Z 인덱스 |
| number-keyboard · virtual-input · passcode-input | 커스텀 숫자 키보드 3종 세트 (결제·인증 어휘) |
| infinite-scroll | 무한 스크롤 |
| water-mark · notice-bar · tree-select | 중국 앱 생태계 어휘 |

### Seed만

| 컴포넌트 | 성격 |
|---|---|
| headless 42개 패키지 층 | 행동 로직을 스타일과 분리 판매. **3사 중 유일한 이층 구조** |
| ResponsiveDialog · ResponsivePair · ResponsiveSidePanel | 화면 폭으로 형태를 바꾸는 적응 컴포넌트 |
| MannerTemp · MannerTempBadge · Celsius | 당근 도메인 (매너온도) |
| 범용 Button **부재** | ActionButton 등 용도 버튼 7종만 존재. 상세: [seed-component-tiers.md](seed-component-tiers.md) |

### VKUI만

| 컴포넌트 | 성격 |
|---|---|
| Epic · Root · View · Panel · SplitLayout | 앱 셸 전체. View가 iOS 스와이프 백을 직접 구현 |
| Touch · Tappable · Clickable | 터치 primitive를 공개 API로 수출 |
| Cell · SimpleCell · RichCell · MiniInfoCell · CellButton · HorizontalCell | 셀 6분화. 시스템의 실질 중심 |
| UsersStack · WriteBar · OnboardingTooltip | VK 소셜 도메인 |

## 6. 신규 DS 시사점

1. **§3 교집합 19개를 최소 세트로 확정한다.** 3사가 독립적으로 수렴한 목록이라 근거가 가장 강하다.
2. **셸 포함 여부를 먼저 결정한다.** 웹뷰 임베드형이면 Seed 모델(셸 별도 패키지), 풀 웹앱이면 VKUI 모델(셸 포함). 이 결정이 인벤토리 20개분을 좌우한다.
3. **셀(리스트 행)을 버튼급 1급 컴포넌트로 설계한다.** 3사 공통 패턴이고, 데스크톱 시스템에서 이식할 수 없는 부분이다.
4. **이름은 다수결로 정한다.** 예: 당겨서 새로고침은 3사 모두 PullToRefresh다. 바텀시트는 3사가 다 다르므로(§0.5) 가장 서술적인 BottomSheet(Seed)를 따른다.
5. **스와이프 행동(swipe-action)은 antd-mobile 하나만 갖고 있다.** 채택하려면 참고 대상이 하나뿐이라는 위험을 안고 간다.

---

<details>
<summary>부록 A. antd-mobile 83개 전수 분류</summary>

측정: `ls sources-candidates/ant-design-mobile/src/components/` (디렉터리 83개)

| 분류 | 컴포넌트 |
|---|---|
| 셸/내비 (8) | nav-bar, tab-bar, tabs, capsule-tabs, jumbo-tabs, side-bar, index-bar, page-indicator |
| 오버레이 (9) | action-sheet, dialog, modal, popup, center-popup, popover, mask, toast, floating-panel |
| 제스처 (4) | pull-to-refresh, swipe-action, swiper, floating-bubble |
| 폼/입력 (31) | button, form, input, text-area, virtual-input, passcode-input, number-keyboard, checkbox, radio, switch, slider, rate, stepper, selector, check-list, search-bar, segmented, picker, picker-view, cascade-picker, cascade-picker-view, cascader, cascader-view, date-picker, date-picker-view, calendar, calendar-picker, calendar-picker-view, image-uploader, tree-select, dropdown |
| 표시/데이터 (18) | list, card, image, image-viewer, avatar, badge, tag, ellipsis, empty, error-block, result, result-page, notice-bar, steps, collapse, infinite-scroll, water-mark, footer |
| 피드백/로딩 (6) | skeleton, loading, dot-loading, spin-loading, progress-bar, progress-circle |
| 레이아웃/유틸 (7) | grid, space, divider, safe-area, auto-center, scroll-mask, config-provider |

picker 계열이 8개로 전체의 10%다. 휠 피커에 가장 진심인 시스템이다.

</details>

<details>
<summary>부록 B. Seed 87 + 42 + 2 구조</summary>

측정: `seed-design/packages/react/src/components/` 87개(private 제외),
`react-headless/` 42개, `stackflow/src/components/` 2개(AppBar, AppScreen).

styled 87개의 L1/L2/L3 전수 분류는 [seed-component-tiers.md](seed-component-tiers.md)에 이미 있다.
여기서는 중복하지 않는다. 요지만 옮긴다:

- L1 범용 primitive 40 (46%) · L2 use-case 44 (51%) · L3 당근 도메인 3 (3%)
- 범용 Button이 없다. 버튼은 전부 용도명(ActionButton 등 7종)이다.
- 행동 primitive(dialog, floating, dismissible-layer, wheel-picker 등)는 headless 42개로 내려가 있다.

</details>

<details>
<summary>부록 C. VKUI 156개 전수 분류</summary>

측정: `ls sources-candidates/vkui/packages/vkui/src/components/` (디렉터리 156개)

| 분류 | 컴포넌트 |
|---|---|
| 앱 셸 (12) | AppRoot, Epic, Root, RootComponent, View, Panel, SplitLayout, SplitCol, FixedLayout, PopoutWrapper, ModalRoot, ModalOutlet |
| 상단 내비바 (10) | PanelHeader, PanelHeaderBack, PanelHeaderButton, PanelHeaderClose, PanelHeaderContent, PanelHeaderContext, PanelHeaderEdit, PanelHeaderSubmit, ModalPageHeader, ModalDismissButton |
| 하단/탭 내비 (8) | Tabbar, TabbarItem, Tabs, TabsItem, SubnavigationBar, SubnavigationButton, Pagination, ScrollArrow |
| 오버레이 (13) | ActionSheet, ActionSheetItem, Alert, ModalPage, ModalPageContent, ModalCard, ModalCardBase, ModalOverlay, ModalOutsideButton, ModalOutsideButtons, Popover, Popper, FloatingArrow |
| 피드백 (8) | Snackbar, ScreenSpinner, Spinner, PanelSpinner, Progress, Skeleton, Placeholder, FormStatus |
| 셀/리스트 (10) | Cell, SimpleCell, RichCell, MiniInfoCell, CellButton, CellButtonGroup, HorizontalCell, List, InfoRow, Removable |
| 버튼 (6) | Button, ButtonGroup, IconButton, ToolButton, WriteBar, WriteBarIcon |
| 폼/입력 (28) | Input, Textarea, Checkbox, Radio, RadioGroup, Switch, Slider, Select, CustomSelect, CustomSelectDropdown, CustomSelectOption, NativeSelect, SelectMimicry, SelectTypography, ChipsInput, ChipsInputBase, ChipsSelect, DateInput, DateRangeInput, Calendar 계열 6종, Search, File, DropZone |
| 폼 구조 (5) | FormField, FormFieldClearButton, FormItem, FormLayoutGroup, SelectionControl |
| 카드/미디어 (13) | Card, CardGrid, CardScroll, ContentCard, Banner, Gallery, CarouselBase, HorizontalScroll, Image, ImageBase, GridAvatar, Avatar, UsersStack |
| 표시 (14) | Badge, ContentBadge, Counter, Header, Footer, Group, Accordion, Typography, Link, Mark, Gradient, OnboardingTooltip, Tooltip, TooltipBase |
| 터치/포커스 primitive (5) | Touch, Tappable, Clickable, FocusTrap, PullToRefresh |
| 레이아웃 (8) | Div, Flex, Box, Group*, Spacing, Separator, SimpleGrid, AspectRatio |
| Provider/Context (9) | AdaptivityProvider, ConfigProvider, ColorSchemeProvider, DirectionProvider, LocaleProvider, PlatformProvider, NavIdContext, NavTransitionContext, NavTransitionDirectionContext |
| 내부 기반/기타 | InputLike, NumberInputLike, UnstyledTextField, CustomScrollView, VisuallyHidden, DropdownIcon, AdaptiveIconRenderer 등 |

분류 합계는 156과 정확히 일치하지 않는다. 일부 컴포넌트는 두 분류에 걸친다(예: Group).
분류는 이해를 돕는 근사이고, 총수 156은 `find` 실측이다.

</details>

<details>
<summary>부록 D. 매핑 판정의 애매한 케이스</summary>

| 판정 | 근거 |
|---|---|
| VKUI ModalPage = 바텀시트 | snap point 구현 보유 (`ModalPage.tsx`의 `settlingHeight` → `transformSettlingHeightToSnapPoint`) |
| Seed 휠 피커 = "내부용" | `packages/react/src/components/private/WheelPicker.tsx` + headless `wheel-picker` 패키지. styled 공개 export 없음 |
| VKUI Removable ≠ swipe-action | Removable은 편집 모드 삭제 버튼 노출이다. 스와이프 제스처가 아니다 |
| Seed SwipeableMenuSheet ≠ swipe-action | 시트 자체를 스와이프로 닫는 컴포넌트다. 셀 행동 노출이 아니다 |
| VKUI File·DropZone = 업로더 | 파일 입력 버튼 + 드래그 존. antd-mobile image-uploader보다 데스크톱 성격이 강하다 |
| Seed 하단 탭바 부재 | `grep -ril "tabbar" seed-design/packages/{react,stackflow}/src` → 0건 |
| VKUI 휠 피커 부재 | `grep -ril "wheel-picker\|wheelpicker" vkui/packages/vkui/src/components` → 0건 |

</details>
