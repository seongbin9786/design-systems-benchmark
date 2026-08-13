# Seed Design 컴포넌트 전수 분류: L1 / L2 / L3

L1(범용 primitive), L2(use-case 컴포넌트), L3(도메인 컴포넌트)는 이 벤치마크가 제안한 프레임이다.
Seed 공식 문서에는 이 구분이 없다. 이 문서는 클론 소스에서 전수를 뽑아 그 프레임으로 분류한 결과다.

- 대상: `sources-candidates/seed-design/packages/react/src/components` 디렉터리 87개 (2026-08-13, MANIFEST.md 커밋 기준)
- 별도 계층: react-headless 패키지 42개, stackflow 패키지(AppBar, AppScreen)

## 결론

| 계층 | 수 | 비중 |
|---|---|---|
| L1 범용 primitive | 40 | 46% |
| L2 use-case | 44 | 51% |
| L3 당근 도메인 | 3 | 3% |

- **styled 계층의 절반이 L2다.** "Seed답다"는 인상의 실체가 이 비중이다.
- **L1이 없는 게 아니다.** 레이아웃과 폼 컨트롤 40개는 styled에 있고, 행동 primitive(dialog, floating, dismissible-layer 등) 42개는 headless 패키지로 내려가 있다.
- **범용 Button만 없다.** 87개 중 Button 디렉터리가 없다. 버튼은 전부 L2(ActionButton, ReactionButton, FieldButton, Fab 계열)로만 존재한다. Seed 채택 시 유일하게 재검토할 지점이다.
- Seed에도 데스크톱 적응 어휘가 있다(SidePanel, SideNavigation, Responsive* 3종). 모바일 전용이 아니라 "모바일 기준 + 데스크톱 적응" 구조다.

## L1: 범용 primitive (40)

### 레이아웃, 유틸 (16)

| 컴포넌트 | 비고 |
|---|---|
| Box, Flex, Stack, Inline, Columns, Grid, GridItem | 레이아웃 기본 |
| AspectRatio, Float, Layout, ConsistentWidth, ResponsivePair, ScrollFog | 레이아웃 보조 |
| Portal, VisuallyHidden, Divider | 유틸 |

### 표시 (9)

| 컴포넌트 | 비고 |
|---|---|
| Text, Icon | 타이포, 아이콘 |
| Avatar, Badge, Count | Count는 수량 표시라 L2로 볼 여지도 있음 (애매) |
| Skeleton, LoadingIndicator, ProgressCircle, ImageFrame | 로딩, 이미지 |

### 폼, 컨트롤 (15)

| 컴포넌트 | 비고 |
|---|---|
| Checkbox, RadioGroup, Switch, Slider, Select, TextField | 폼 컨트롤 |
| Field, Fieldset | 폼 조립 인프라 |
| Tabs, SegmentedControl, ToggleButton, Accordion, List, Menu | 범용 상호작용 |
| Chip | ActionChip과 ControlChip의 기반 (애매: 내부 기반 성격) |

## L2: use-case 컴포넌트 (44)

### 버튼 계열 (7) : 범용 Button 없이 전부 용도명

| 컴포넌트 | 용도 |
|---|---|
| ActionButton | 화면의 주 행동. variant 7값 + JSDoc 사용 규칙 |
| ReactionButton | 좋아요 등 반응 |
| FieldButton | 폼 필드 안 버튼 |
| Fab, ExtendedFab, FloatingActionButton, ContextualFloatingButton | 떠 있는 행동 버튼 4분화 |

### 칩, 탭 변형 (3)

| 컴포넌트 | 용도 |
|---|---|
| ActionChip | 행동 트리거 칩 |
| ControlChip | 선택 상태 칩 |
| ChipTabs | 칩 형태 탭 (애매: 형태 변형 성격) |

### 오버레이 (9) : 목적별 분리의 교과서

| 컴포넌트 | 용도 |
|---|---|
| BottomSheet, BottomSheetHandle | 바텀시트 |
| ActionSheet, ExtendedActionSheet | 행동 선택 시트 |
| MenuSheet, SwipeableMenuSheet | 메뉴 시트 |
| Dialog, ContentDialog | 알럿형, 콘텐츠형 다이얼로그 |
| ResponsiveDialog | 좁으면 BottomSheet, 넓으면 ContentDialog 어댑터 |

### 피드백, 안내 (8)

| 컴포넌트 | 용도 |
|---|---|
| Snackbar | 토스트 대체, safe-area 오프셋 내장 |
| Callout, InlineBanner, PageBanner | 배너를 위치와 목적으로 3분화 |
| HelpBubble, HelpBubbleTooltip | 안내 말풍선 |
| ContentPlaceholder, IdentityPlaceholder | 빈 상태, 프로필 기본 이미지 |

### 입력 특화 (6)

| 컴포넌트 | 용도 |
|---|---|
| AttachmentInput, AttachmentDisplay | 사진 첨부 입력, 표시 |
| DatePicker, TimePicker | 휠 피커 기반 (애매: 범용 폼 컨트롤로 볼 여지) |
| QuantityPicker | 수량 증감 |
| RadioGroupField | Field + RadioGroup 프리셋 배선 (L2 배선 방식의 실물 사례) |

### 내비게이션, 셸 (8)

| 컴포넌트 | 용도 |
|---|---|
| NavigationMenu, SideNavigation | 내비게이션 |
| SidePanel, ResponsiveSidePanel | 데스크톱 적응용 패널 |
| Footer | 하단 고정 영역 |
| PullToRefresh | 당겨서 새로고침 |
| SelectBox, TagGroup | 카드형 선택, 태그 묶음 |

### 콘텐츠 (3)

| 컴포넌트 | 용도 |
|---|---|
| Article, LinkContent | 콘텐츠, 링크 표시 (애매) |
| NotificationBadge | 알림 배지 |

## L3: 당근 도메인 (3)

| 컴포넌트 | 용도 |
|---|---|
| MannerTemp, MannerTempBadge | 매너온도 표시 |
| Celsius | 온도 숫자 표기 |

L3가 L2와 같은 패키지에 동거한다. 신규 DS에서는 별도 네임스페이스로 격리할 것을 권고했다(insights.html 4장).

## 별도 계층

### react-headless (42): 행동 L1

accordion, attachment-display, avatar, checkbox, collapsible, date-picker, dialog, dismissible-layer,
drawer, field, field-button, fieldset, file-upload, floating, image, menu, middle-truncate,
navigation-menu, popover, portal, presence, prevent-scroll, primitive, progress, pull-to-refresh,
quantity-picker, radio-group, scrollable, segmented-control, select, side-navigation, slider,
snackbar, supports, switch, tabs, text-field, time-picker, toggle, tooltip, use-controllable-state, wheel-picker

- styled L2가 이 행동 primitive를 조합한다. "L1이 사라진 것이 아니라 headless로 내려갔다"는 근거다.
- WheelPicker는 headless에만 있고 styled로는 DatePicker와 TimePicker가 감싼다.

### stackflow (2): 앱 셸

AppBar, AppScreen. 화면 전환 스택(stackflow 라우터)과 결합된 패키지다.
insights.html 5장의 "앱 셸 소유권" 결정 항목이 이 계층이다.

## 신규 DS에 주는 시사점

1. Seed의 실제 구성비(L1 46% : L2 51%)를 초기 목표로 삼을 만하다. L2가 절반이어도 시스템은 성립한다.
2. L2는 전부 "L1 조합 + 프리셋 + 사용 규칙"이다. RadioGroupField가 배선 방식의 최소 사례다.
3. 범용 Button 부재만 예외 처리한다: 신규 DS는 L1에 Button을 두고, ActionButton류를 L2로 얹는다.
4. headless 분리는 2단계 과제로 미뤄도 된다. Seed도 styled가 headless를 감싸는 구조라, 처음에는 styled 단일 계층으로 시작하고 행동 추출은 나중에 해도 API가 깨지지 않는다.
