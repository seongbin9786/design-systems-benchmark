# Semi Design (ByteDance) 소스 실측 분석

- 실측 대상: `sources-candidates/semi-design` (sparse 클론: `packages/semi-ui`, `packages/semi-foundation`, `packages/semi-theme-default`)
- 실측 버전: 2.102.0 (`packages/semi-ui/package.json`, `packages/semi-foundation/package.json`, `packages/semi-theme-default/package.json` 모두 동일)

## 0. 요약

**판정: desktop.** Semi Design 은 데스크톱 중후반부(어드민, 사무용 웹) 를 위한 시스템이다. 모바일 전용 컴포넌트가 하나도 없다. 반응형 grid 와 breakpoint 구독 유틸은 있으나, 이는 데스크톱 창 크기 대응 수준이다.

| 판정 근거 | 실측 값 | 출처 |
|---|---|---|
| safe-area 처리 | 0건 (3개 패키지 전체 grep) | `grep -rln "safe-area\|safeArea\|env(safe"` 결과 없음 |
| hover 의존도 | scss 파일 50개에서 `:hover` 279회 | `packages/semi-foundation/**/*.scss` |
| 컨트롤 높이 | 24 / 32 / 40px, 터치 가이드(44px) 미달 | `packages/semi-theme-default/scss/variables.scss:4-6` |
| 터치 제스처 코드 | dragMove, resizable, slider 3곳뿐. 스와이프, 풀투리프레시 없음 | `packages/semi-foundation/dragMove/foundation.ts` 등 |
| 키보드 전제 컴포넌트 | HotKeys(단축키) 컴포넌트 존재 | `packages/semi-ui/hotKeys/` |
| 모바일 전용 컴포넌트 | BottomSheet, ActionSheet, TabBar, NavBar 등 전부 부재 | `packages/semi-ui/` 디렉터리 목록 |
| 반응형 장치 | grid breakpoint 6단계 + ConfigProvider 의 opt-in breakpoint 구독 | `packages/semi-foundation/grid/grid.scss:85-117`, `packages/semi-ui/configProvider/responsiveTypes.ts:5` |

핵심 특징 요약:

| 항목 | 실측 결과 |
|---|---|
| 토큰 | 3계층: palette(RGB 채널) → semantic(CSS 변수) → component(SCSS 변수) |
| 컴포넌트 수 | 디렉터리 기준 83개 (인프라성 4개 포함) |
| Button 축 | type 5 x theme 4 x size 3 + boolean(block, circle, loading, colorful) |
| use-case 처리 | variant 가 아니라 별도 컴포넌트로 승격 (Modal.confirm, Popconfirm, Feedback, PinCode) |
| 스타일링 | SCSS 컴파일 + CSS 변수 런타임 토큰, 테마는 npm 패키지 교체 |

## 1. 토큰 아키텍처

3계층이다. 색상은 CSS 변수로 런타임에 산다. 치수와 간격은 SCSS 변수로 컴파일 타임에 박힌다.

| 계층 | 역할 | 형태 | 정의 파일 |
|---|---|---|---|
| 1. palette | 원색 램프. 색상 12종 x 명도 0~9 를 RGB 채널 트리플("0,100,250")로 정의 | CSS 변수 | `packages/semi-theme-default/scss/_palette.scss:1` |
| 2. semantic | 역할 색(primary, success, danger), 층위 색(bg-0~4, text-0~3, fill-0~2), radius, shadow | CSS 변수 | `packages/semi-theme-default/scss/global.scss:3-146` |
| 2'. global sizing | 컨트롤 높이, spacing 9단계, z-index, 폰트 | SCSS 변수 | `packages/semi-theme-default/scss/variables.scss` |
| 3. component | 컴포넌트별 파트 x 상태 토큰. semantic 을 참조 | SCSS 변수 | `packages/semi-foundation/<comp>/variables.scss` |

네이밍 예시:

| 토큰 | 계층 | 출처 |
|---|---|---|
| `--semi-blue-5: 0,100,250` | palette (RGB 채널) | `_palette.scss` |
| `--semi-color-primary-hover: rgba(var(--semi-blue-6), 1)` | semantic | `global.scss:11` |
| `--semi-color-bg-2` (모달 층), `--semi-color-text-2` (次요 텍스트) | semantic, 서수 층위 | `global.scss:96-107` |
| `$color-button_primary-bg-default: var(--semi-color-primary)` | component | `packages/semi-foundation/button/variables.scss:2` |
| `$spacing-base-tight: 12px`, `$height-control-default: 32px` | global sizing | `variables.scss` |

특기 사항 2가지:

1. palette 를 RGB 채널로 두고 semantic 에서 `rgba(var(--x), alpha)` 로 합성한다. 알파 변형을 토큰 추가 없이 만든다. 예: `--semi-color-disabled-text: rgba(var(--semi-grey-9), .35)` (`global.scss:71`).
2. 최근 컴포넌트는 컴포넌트 스코프 CSS 변수도 추가했다. 예: `.semi-button { --semi-button-colorful-fill-primary: ... }` (`packages/semi-foundation/button/cssVariables.scss:3-11`).

## 2. 컴포넌트 인벤토리

- 총수: **83개** 디렉터리.
- 세는 기준: `packages/semi-ui` 에서 `ls -d */ | grep -v '^_' | grep -vE '^(icons|locale|scripts)/' | wc -l`. 언더스코어 내부 모듈(_base, _portal 등 6개)과 icons, locale, scripts 를 제외했다.
- 83개 중 configProvider, trigger, resizeObserver, dragMove 4개는 인프라성 유틸이다. 순수 UI 컴포넌트는 약 79개다.

| 구분 | 예시 |
|---|---|
| primitive | Button, Input, Checkbox, Radio, Switch, Select, Tag, Typography, Space, Divider, Grid, Layout, Modal, Popover, Tooltip |
| 데이터 중심(어드민 어휘) | Table, Tree, TreeSelect, Transfer, Pagination, Breadcrumb, Navigation, SideSheet, Descriptions, Form |
| use-case(용도 지정) | Popconfirm, Feedback, PinCode, UserGuide, Banner, Empty, BackTop, FloatButton |
| 도메인 특화 | Chat, AiChatInput, AiChatDialogue, AudioPlayer, VideoPlayer, Cropper, JsonViewer, MarkdownRender, CodeHighlight, ColorPicker, Calendar |

AI 채팅 계열(chat, aiChatInput, aiChatDialogue)이 3개나 있다. ByteDance 제품(도메인) 수요가 시스템에 직접 들어온 사례다.

## 3. variant 철학

### 3.1 Button: 직교 3축 + boolean 수식어

타입 정의 원문 (`packages/semi-ui/button/Button.tsx:13-16`):

```ts
export type HtmlType = 'button' | 'reset' | 'submit';
export type Size = 'default' | 'small' | 'large';
export type Theme = 'solid' | 'borderless' | 'light' | 'outline';
export type Type = 'primary' | 'secondary' | 'tertiary' | 'warning' | 'danger';
```

| 축 | 값 | 의미 |
|---|---|---|
| type | primary, secondary, tertiary, warning, danger (5) | 의미 역할 |
| theme | solid, light(기본), borderless, outline (4) | 시각 강도 |
| size | small, default, large (3) | 크기 |
| boolean | block, circle (`Button.tsx:20-21`), loading, colorful (`Button.tsx:40`) | 형태, 상태 수식어 |

철학: 의미 역할(type)과 시각 강도(theme)를 직교 축으로 분리한다. 5 x 4 = 20 조합을 이름 20개가 아니라 축 2개로 표현한다. 용도(확인, 취소, 삭제)를 이름에 박은 버튼은 없다. colorful 은 AI 씬 전용 boolean 으로, AI 색 토큰(`--semi-color-ai-general`, `global.scss:127`)을 쓴다.

### 3.2 오버레이: Modal

| 축 | 값 | 출처 |
|---|---|---|
| size | small(기본), medium, large, full-width | `packages/semi-foundation/modal/constants.ts:10`, 기본값 `Modal.tsx:107` |
| fullScreen | boolean | `Modal.tsx:86` |
| use-case 정적 메서드 | `Modal.info / success / error / warning / confirm` | `packages/semi-ui/modal/Modal.tsx:196-213` |

use-case 는 variant prop 이 아니라 정적 메서드로 제공한다. 내부적으로 `withInfo(props)` 같은 데코레이터가 아이콘과 버튼 구성을 주입한다 (`packages/semi-ui/modal/confirm.tsx`).

### 3.3 리스트: List

| 축 | 값 | 출처 |
|---|---|---|
| layout | vertical(기본), horizontal | `packages/semi-ui/list/index.tsx:24` |
| size | small, default, large | `index.tsx:25` |
| bordered, split | boolean | `index.tsx:21,26` |
| grid | Grid 객체 주입으로 카드 그리드 전환 | `index.tsx:30` |

### 3.4 use-case variant 존재 여부: 있다, 단 컴포넌트 단위로

Semi 는 primitive 의 variant 를 순수 축으로 유지한다. 용도는 별도 컴포넌트나 정적 메서드로 승격한다.

| 사례 | 형태 | 출처 |
|---|---|---|
| Modal.confirm / info / error | 정적 메서드 | `Modal.tsx:196-213` |
| Popconfirm | 위험 동작 확인 전용 팝오버 컴포넌트 | `packages/semi-ui/popconfirm/` |
| Feedback | 설문, 이모지 피드백 수집 전용. mode: popup, type: emoji 기본값 | `packages/semi-ui/feedback/index.tsx:26-27,65-66` |
| PinCode | 인증 코드 입력 전용 | `packages/semi-ui/pincode/` |
| UserGuide | 온보딩 투어 전용 | `packages/semi-ui/userGuide/` |
| Banner type | info, danger, warning, success (semantic 까지만) | `packages/semi-ui/banner/index.tsx:18` |

## 4. 모바일 어휘

**모바일 전용 컴포넌트는 0개다.** `packages/semi-ui` 디렉터리 83개를 전수 대조했다.

| 어휘 | 존재 | 비고 |
|---|---|---|
| BottomSheet | 없음 | 유사물은 SideSheet(데스크톱 드로어, 기본 우측) |
| ActionSheet | 없음 | Dropdown, Popconfirm 으로 대체하는 구조 |
| SafeArea | 없음 | `safe-area` 문자열 자체가 0건 |
| PullToRefresh | 없음 | |
| SwipeAction | 없음 | |
| IndexBar | 없음 | |
| FloatingPanel / Bubble | 없음 | FloatButton 은 있으나 데스크톱 겸용 |
| TabBar | 없음 | Tabs 는 데스크톱 탭 |
| NavBar | 없음 | Navigation 은 사이드바형 어드민 내비게이션 |
| Toast | 있음(겸용) | 상단 알림형. 모바일 전용 설계가 아니다 |

ByteDance 는 모바일용으로 별도 라인업을 둔다. 이 저장소에는 포함되지 않았다.

## 5. 스타일링과 테마

| 항목 | 실측 결과 | 출처 |
|---|---|---|
| CSS 방식 | SCSS. 컴포넌트가 foundation 의 scss 를 직접 import | `packages/semi-ui/button/Button.tsx:5` (`import '@douyinfe/semi-foundation/button/button.scss'`) |
| 로직/뷰 분리 | foundation(프레임워크 무관 로직 + scss) / ui(React 어댑터) / theme(토큰) 3패키지 | `packages/` 구조 |
| 색 토큰 런타임 | CSS 변수. 컴포넌트 SCSS 변수가 `var(--semi-*)` 를 참조 | `packages/semi-foundation/button/variables.scss:2` |
| 다크 모드 | `body[theme-mode="dark"]` 속성 셀렉터가 동일 변수 세트를 재정의. `.semi-always-light / .semi-always-dark` 로 부분 고정 가능 | `packages/semi-theme-default/scss/global.scss:3,146` |
| 브랜드 테마 교체 | 테마를 npm 패키지(`semi-theme-*`)로 배포하고 webpack 플러그인이 기본 테마를 교체 | `packages/semi-ui/package.json` 의 `@douyinfe/semi-theme-default` 의존, 루트 `syncRegistry.sh` 및 semi-webpack-plugin 빌드 스크립트 참조 |
| Shadow DOM 대응 | 토큰 셀렉터에 `:host` 포함 | `global.scss:3` |

주의점: 색은 런타임 교체가 되지만, 높이와 spacing 은 SCSS 컴파일 타임 값이다. 치수 체계를 바꾸려면 테마 패키지를 다시 빌드해야 한다.

## 6. 신규 DS 시사점 (모바일 웹뷰 기준)

1. **type x theme 직교 2축을 가져온다.** 의미 역할 5개와 시각 강도 4개를 분리하면, use-case 버튼 없이도 조합 20개를 축 2개로 커버한다. 모바일에서는 상태 축의 hover 를 pressed 로 치환해야 한다. Semi 는 hover 를 279곳에 박아 이 부분은 이식 불가다.
2. **RGB 채널 팔레트 + rgba 합성 기법을 가져온다.** `--x: 0,100,250` 형태로 두고 `rgba(var(--x), .35)` 로 알파 변형을 만들면, disabled 와 dim 계열 토큰 수가 줄어든다. 웹뷰 CSS 변수 환경에 그대로 이식된다.
3. **서수 층위 토큰(bg-0~4, text-0~3)을 가져온다.** 페이지, 카드, 모달, 토스트의 층위를 토큰으로 고정하면, 다크 모드에서 층위별 명도 역전을 한 파일(`global.scss` 의 dark 블록)에서 관리할 수 있다.
4. **use-case 는 variant 가 아니라 컴포넌트 승격으로 처리한다.** Semi 는 primitive 의 축을 순수하게 유지하고, 확인 다이얼로그(Modal.confirm), 위험 확인(Popconfirm), 인증 입력(PinCode)을 별도 이름으로 승격했다. Seed 식 use-case variant 대비, primitive API 가 오염되지 않는 장점을 실물로 보여준다.
5. **치수 토큰까지 런타임 변수로 올려야 한다.** Semi 는 색만 CSS 변수이고 높이, spacing 은 SCSS 컴파일 값이다. 웹뷰 DS 는 폰트 스케일과 밀도 전환이 필요하므로, 치수도 CSS 변수로 정의하는 편이 낫다. Semi 의 이 제약을 반면교사로 삼는다.
6. **모바일 어휘는 Semi 에서 얻을 수 없다.** BottomSheet, ActionSheet, SafeArea 가 전부 부재다. Semi 는 토큰 구조와 variant 설계의 참고처이고, 모바일 컴포넌트 어휘의 참고처가 아니다.
