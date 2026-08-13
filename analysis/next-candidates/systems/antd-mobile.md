# Ant Design Mobile (antd-mobile) 실측 분석

- 소스: `/Users/seongbin/workspaces/design-systems-benchmark/sources-candidates/ant-design-mobile`
- 버전: `5.42.4-alpha.0` (package.json `version` 실측)
- 분석일: 2026-08-13

## 0. 요약

**판정: mobile-first.** antd-mobile 은 데스크톱 대응을 아예 하지 않는 모바일 전용 시스템이다.

| 항목 | 실측 결과 |
| --- | --- |
| 플랫폼 지향 | mobile-first. `.less` 전체에 `@media` 쿼리 0건, `:hover` 0건 |
| 컴포넌트 총수 | 83개 (`src/components` 디렉터리 수 = `src/index.ts` default export 수) |
| 토큰 | CSS 변수 3계층: global(`--adm-*`) → 컴포넌트 공개(`--adm-button-*`) → 인스턴스 로컬(`--text-color`) |
| variant 철학 | 직교 축 조합(color × fill × size × shape). 용도별 변형은 새 variant 가 아니라 래퍼 컴포넌트로 만든다 |
| 스타일링 | Less 로 정적 CSS 를 빌드한다. 테마는 런타임 CSS 변수로 바꾼다. CSS-in-JS 없음 |
| 다크 모드 | `html[data-prefers-color-scheme='dark']` 속성 스위치 |

핵심 관찰: antd(데스크톱)와 같은 브랜드지만 코드와 어휘를 공유하지 않는다. antd 의 cssinjs 토큰 시스템, `Table`, `Menu`, `Breadcrumb`, `Tooltip` 같은 데스크톱 어휘가 없다. 대신 `Picker`, `TabBar`, `SwipeAction`, `PullToRefresh` 같은 모바일 어휘로 채웠다. Ant 진영은 데스크톱과 모바일을 별도 시스템으로 분리하는 전략을 택했다.

### 플랫폼 판정 근거 5가지

| 근거 | 소스 위치 |
| --- | --- |
| SafeArea 전용 컴포넌트. `env(safe-area-inset-*)` 를 패딩으로 변환한다 | `src/components/safe-area/safe-area.less:8-13` |
| 터치 제스처 라이브러리 `@use-gesture/react` 를 10개 컴포넌트가 쓴다 (popup, swiper, slider, swipe-action, pull-to-refresh, floating-panel, floating-bubble, image-viewer, picker-view, rate) | `package.json` dependencies, `src/components/popup/popup.tsx:73-87` |
| `.less` 파일 전체에 `@media` 브레이크포인트 0건, `:hover` 셀렉터 0건. 눌림 피드백은 전부 `:active` | `src/components/button/button.less:53`, `src/global/global.less:26` |
| 탭 하이라이트 제거를 루트에서 처리한다 (`-webkit-tap-highlight-color`) | `src/global/global.less:5` |
| 바닥 고정 컴포넌트가 SafeArea 를 내장한다. TabBar, ActionSheet, Picker, NumberKeyboard, ImageViewer | `src/components/tab-bar/tab-bar.tsx:137`, `src/components/action-sheet/action-sheet.tsx:49` (`safeArea: true` 기본값) |

## 1. 토큰 아키텍처

계층은 3개다. 전부 CSS 커스텀 프로퍼티다. 빌드 타임 토큰 파이프라인이 없다.

| 계층 | 역할 | 정의 위치 | 예시 |
| --- | --- | --- | --- |
| 1. Global 테마 토큰 | 색, 폰트 크기, 라운드를 `:root` 에 선언 | `src/global/theme-default.less:1-54` | `--adm-color-primary`, `--adm-font-size-1`~`10`, `--adm-radius-s/m/l` |
| 2. 컴포넌트 공개 변수 | 컴포넌트 단위 전역 오버라이드 채널. `var(--adm-button-X, 기본값)` 패턴 | `src/components/button/button.less:6-14` | `--adm-button-text-color`, `--adm-button-border-radius` |
| 3. 인스턴스 로컬 변수 | 개별 인스턴스의 `style` prop 으로 주입. 타입으로 허용 목록을 강제 | `src/components/button/button.tsx:40-47`, `src/utils/native-props.ts:5-9` | `--text-color`, `--background-color`, `--border-radius` |

네이밍 예시:

- `--adm-color-primary`, `--adm-color-text-light-solid` (`theme-default.less:19,42`)
- `--adm-font-size-main` (`theme-default.less:46`, 시맨틱 별칭. `--adm-font-size-5` 를 가리킨다)
- `--adm-radius-m` (`theme-default.less:4`)
- `--adm-button-border-radius` (`button.less:11`, 컴포넌트 공개 변수)
- `--adm-safe-area-multiple` (`safe-area.less:4`, 웹뷰가 safe-area 를 이중 적용할 때 0 으로 끄는 스위치)

특이점 2가지.

1. 3계층이 antd v5 의 seed → map → alias 3계층과 다르다. antd-mobile 의 계층은 "누가 오버라이드하는가" 기준이다. 전역 테마, 컴포넌트 전역, 인스턴스 순이다.
2. 인스턴스 계층을 TypeScript 로 검증한다. `NativeProps<'--text-color'>` 제네릭이 허용 CSS 변수 목록을 타입에 새긴다 (`native-props.ts:5-9`). 문서가 아니라 타입이 계약이다.

## 2. 컴포넌트 인벤토리

- 총수: **83개**
- 세는 기준: `ls src/components | wc -l` = 83. 교차 검증: `grep -c "export { default as" src/index.ts` = 83. 두 값이 일치한다. `config-provider`, `safe-area` 같은 유틸성 컴포넌트도 포함한 수다.

| 분류 | 예시 |
| --- | --- |
| Primitive (범용 조립 블록) | Button, Space, Grid, Divider, Tag, Avatar, Image, Input, TextArea, Switch, CheckBox, Radio, Slider, Popup, Mask, List |
| Use-case (용도 지정) | Dialog(alert/confirm), ActionSheet, ErrorBlock, Result, ResultPage, PasscodeInput, NumberKeyboard, SearchBar, ImageUploader, PullToRefresh, IndexBar, CheckList, Stepper |
| 모바일 인터랙션 전용 | SwipeAction, FloatingPanel, FloatingBubble, TabBar, NavBar, Picker 계열 6종, InfiniteScroll |

use-case 층이 두껍다. 83개 중 절반 이상이 특정 화면 패턴을 겨냥한다. 예: `PasscodeInput`(인증번호), `ImageUploader`(사진 업로드 그리드), `ErrorBlock`(4종 오류 화면), `CheckList`(선택 목록 = List + 체크 상태 합성, `src/components/check-list/check-list.tsx:15`).

## 3. variant 철학

### 3.1 Button: 직교 축 5개

`src/components/button/button.tsx:21-35` 타입 정의 인용:

```ts
export type ButtonProps = {
  color?: 'default' | 'primary' | 'success' | 'warning' | 'danger'   // :22
  fill?: 'solid' | 'outline' | 'none'                                 // :23
  size?: 'mini' | 'small' | 'middle' | 'large'                        // :24
  block?: boolean                                                     // :25
  loading?: boolean | 'auto'                                          // :26
  shape?: 'default' | 'rounded' | 'rectangular'                       // :34
}
```

- `variant` 라는 합성 prop 이 없다. 의미(color)와 형태(fill, shape)와 크기(size)를 분리했다. 5 × 3 × 4 × 3 = 180 조합이 이론상 전부 유효하다.
- antd(데스크톱)의 `type='primary'|'dashed'|'link'|'text'` + `danger` boolean 방식과 다르다. antd-mobile 이 더 직교적이다.
- 조합으로 못 만드는 스타일은 인스턴스 CSS 변수로 뚫는다 (`button.tsx:40-47` 의 `--text-color` 등 6개).
- `loading: 'auto'` 가 특이하다. `onClick` 이 Promise 를 반환하면 버튼이 스스로 로딩 상태에 들어간다 (`button.tsx:77-92`). 모바일 폼 제출 패턴을 컴포넌트에 내장했다.

### 3.2 오버레이 계열: Popup 의 변형 축

`src/components/popup/popup.tsx:20-25`:

- `position?: 'bottom' | 'top' | 'left' | 'right'` (:22, 기본값 bottom)
- `closeOnSwipe?: boolean` (:23, `useDrag` 스와이프로 닫기, :73-87)
- 공통 축은 `PopupBaseProps` 로 분리: mask, closeOnMaskClick, showCloseButton, destroyOnClose 등 (`popup-base-props.tsx`)

오버레이는 variant 가 아니라 **혈통(계열 분화)** 으로 확장한다: Mask → Popup(가장자리) / CenterPopup(중앙) → Dialog, Modal(CenterPopup 기반, `dialog.tsx:7`) / ActionSheet(Popup 기반, `action-sheet.tsx:6`). 각 단계가 의견을 한 겹씩 더한다.

### 3.3 리스트 계열: List 의 변형 축

- `List.mode?: 'default' | 'card'` (`src/components/list/list.tsx:11`). 전폭 목록과 카드형 목록 2종뿐이다.
- `ListItem` 은 variant 없이 슬롯으로 조립한다: `title`, `description`, `prefix`, `extra`, `arrowIcon`, `clickable` (`src/components/list/list-item.tsx:12-28`).
- 세부 조정은 CSS 변수 12개로 연다 (`list.tsx:13-26`, `--prefix-width`, `--active-background-color` 등).

### 3.4 use-case variant 실존 사례

있다. 다만 primitive 의 variant 축을 늘리지 않고 **래퍼 계층에서** 만든다.

| 사례 | 내용 | 근거 |
| --- | --- | --- |
| `DialogActionButton` | Button 을 `fill='none' shape='rectangular' block color={danger?'danger':'primary'}` 로 고정한 다이얼로그 전용 버튼 | `src/components/dialog/dialog-action-button.tsx:22-36` |
| `Dialog.confirm` | 확인/취소 2버튼을 자동 생성. confirm 은 `bold: true`. `Promise<boolean>` 반환 | `src/components/dialog/confirm.tsx:40-59` |
| `ActionSheet` Action | 액션 항목에 `danger`, `bold` 용도 플래그 | `src/components/action-sheet/action-sheet.tsx:12-20` |
| `ErrorBlock.status` | `'default' \| 'disconnected' \| 'empty' \| 'busy'` 4종 오류 화면 프리셋 | `src/components/error-block/error-block.tsx:10-18` |
| `Result.status` | `'success' \| 'error' \| 'info' \| 'waiting' \| 'warning'` | `src/components/result/result.tsx:15` |

정리: **primitive 는 직교 축 + CSS 변수 탈출구, use-case 는 합성 컴포넌트.** Seed Design 의 ActionButton 처럼 용도를 이름에 박은 버튼 변형은 primitive 층에 없다. 같은 역할을 `DialogActionButton` 같은 내부 래퍼가 담당한다.

## 4. 모바일 어휘

디렉터리 실측 결과. 위치는 전부 `src/components/` 아래다.

| 어휘 | 실존 | 디렉터리 |
| --- | --- | --- |
| BottomSheet | 이름으로는 없음 | `popup`(position bottom) + `floating-panel` 이 역할 분담 |
| ActionSheet | O | `action-sheet` |
| SafeArea | O | `safe-area` |
| PullToRefresh | O | `pull-to-refresh` |
| SwipeAction | O | `swipe-action` |
| IndexBar | O | `index-bar` |
| FloatingPanel | O | `floating-panel` |
| FloatingBubble | O | `floating-bubble` |
| TabBar | O | `tab-bar` |
| NavBar | O | `nav-bar` |
| Toast | O | `toast` |
| NumberKeyboard | O | `number-keyboard` |
| PasscodeInput | O | `passcode-input` |
| Picker 계열 | O | `picker`, `picker-view`, `date-picker`, `cascade-picker` 등 6종 |
| InfiniteScroll | O | `infinite-scroll` |

antd(데스크톱)에 있는 `Table`, `Pagination`, `Menu`, `Breadcrumb`, `Tooltip`, `Descriptions` 는 여기에 없다. 데스크톱의 hover 팝업(`Tooltip`)은 터치용 `Popover` 로 대체된다. 데스크톱의 `Select` 드롭다운은 바닥에서 올라오는 `Picker` 로 대체된다.

## 5. 스타일링과 테마

| 항목 | 실측 |
| --- | --- |
| CSS 방식 | Less 소스를 정적 CSS 로 빌드. CSS-in-JS 없음. 클래스 프리픽스 `adm-` |
| 테마 값 전달 | 전부 CSS 커스텀 프로퍼티. JS 테마 객체 없음 |
| 다크 모드 | `html[data-prefers-color-scheme='dark']` 선택자에서 토큰 재정의 (`src/global/theme-dark.less:1`). 앱이 속성을 직접 토글한다 (`src/global/demos/dark-mode/demo1.tsx:25`) |
| 구형 브라우저 | CSS 변수 미지원 환경용 정적 fallback 을 `@supports not` 으로 제공 (`src/global/css-vars-patch.less:1`, patch 파일 18개) |
| 애니메이션 | `@react-spring/web` 물리 스프링 (`popup.tsx:54-61`). CSS transition 은 보조 |
| ConfigProvider | 테마가 아니라 locale 과 컴포넌트 기본 prop 을 주입한다 (`popup.tsx:34-35`) |

antd v5 가 cssinjs(런타임 CSS-in-JS)로 간 것과 정반대다. 모바일 쪽은 런타임 스타일 엔진 비용을 피했다.

## 6. 신규 DS 시사점 (모바일 웹뷰 기준)

1. **인스턴스 CSS 변수 탈출구를 타입으로 계약하라.** `NativeProps<'--text-color'>` 패턴 (`button.tsx:40-47`, `native-props.ts:5-9`) 은 variant 폭발 없이 일회성 커스텀을 흡수한다. 컴포넌트마다 허용 변수를 타입 유니온으로 공개하면 문서와 계약이 하나가 된다.
2. **use-case 는 variant 축이 아니라 래퍼로 만들어라.** antd-mobile 은 Button 축을 직교 5개로 고정하고, 다이얼로그 버튼은 `DialogActionButton` 래퍼가 prop 을 고정해서 만든다 (`dialog-action-button.tsx:22-36`). Seed 의 ActionButton 고민에 대한 대답이 된다: primitive 층은 직교 축, use-case 층은 합성 컴포넌트로 분리 가능하다.
3. **SafeArea 를 컴포넌트로 만들고 바닥 고정 컴포넌트에 기본 내장하라.** `safeArea: true` 기본값 (`action-sheet.tsx:49`) 과 `--adm-safe-area-multiple` 끄기 스위치 (`safe-area.less:4`) 조합이 웹뷰에서 특히 유효하다. 네이티브 쉘이 inset 을 이미 처리하는 화면에서 CSS 변수 하나로 끌 수 있다.
4. **오버레이는 혈통으로 설계하라.** Mask → Popup/CenterPopup → Dialog/Modal/ActionSheet 의 계층 (`dialog.tsx:7`, `action-sheet.tsx:6`) 은 오버레이 종류가 늘어도 열림/닫힘, 스크롤 잠금, 포탈 로직을 한 곳에 둔다. 상위에는 `Dialog.confirm` 같은 Promise 반환 명령형 API 를 얹는다 (`confirm.tsx:32`).
5. **웹뷰 테마는 정적 CSS + CSS 변수 + html 속성 스위치로 충분하다.** antd-mobile 은 이 조합으로 다크 모드와 브랜드 오버라이드를 전부 처리한다 (`theme-dark.less:1`). CSS-in-JS 런타임 없이 시작하는 편이 웹뷰 초기 렌더 비용에 유리하다.
