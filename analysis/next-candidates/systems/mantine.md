# Mantine 실측 분석

- 대상: `sources-candidates/mantine` (sparse 클론, `packages/@mantine/core`만 포함)
- 실측 버전: **9.5.1** (`packages/@mantine/core/package.json`의 `version`, 루트 `package.json`도 동일)
- 클론 시점: HEAD 커밋 2026-08-11

## 0. 요약

**플랫폼 판정: responsive (범용 반응형, 데스크톱 우위).**

Mantine은 브레이크포인트 도구를 전면에 갖춘 범용 웹 라이브러리다. 모바일은 "대응"하고 데스크톱은 "지향"한다. 판정 근거는 다음과 같다.

| 신호 | 실측 결과 | 근거 |
|---|---|---|
| 반응형 도구 | 5단 브레이크포인트, `hiddenFrom`/`visibleFrom` prop, `use-matches` 훅 | `src/core/Box/Box.tsx:39-42`, `src/core/MantineProvider/use-matches/use-matches.ts` |
| 데스크톱 어휘 | FloatingWindow(드래그 창), Menubar, Splitter, HoverCard, Kbd, AppShell | `src/components/` 디렉터리 실존 |
| 모바일 어휘 | BottomSheet, ActionSheet, PullToRefresh, SwipeAction, TabBar 전부 없음 | 컴포넌트 115개 디렉터리 전수 확인 |
| 터치 타깃 | Button 기본(sm) 높이 36px, compact-xs는 22px | `src/components/Button/Button.module.css:2-12` |
| safe-area | AppShell footer 한 곳만 처리 | `src/components/AppShell/AppShell.module.css:181-182` |
| 제스처 | Drawer, Modal에 스와이프 닫기 코드 없음 | `src/components/Drawer/`, `src/components/Modal/` grep 결과 0건 |
| 터치 보정 | `-webkit-tap-highlight-color` 18개 파일, `touch-action: manipulation` 적용 | `src/components/UnstyledButton/UnstyledButton.module.css:11` |
| hover 처리 | 18개 CSS가 `@mixin hover` 사용, 생 `:hover`는 5개 파일뿐 | `src/components/Button/Button.module.css:107` |

핵심 요약 3줄:
1. 토큰은 3계층이다: JS 테마 객체 → 전역 CSS 변수(`--mantine-*`, 시맨틱 별칭 포함) → 컴포넌트 스코프 CSS 변수(`--button-*`).
2. variant는 전부 시각 톤(filled, light, outline 등)이다. 용도(use-case) variant는 없다. 용도는 variant가 아니라 컴포넌트 이름(CopyButton, PasswordInput)으로 푼다.
3. 스타일링은 CSS Modules + CSS 변수다. 런타임 CSS-in-JS가 없다. 다크 모드는 `data-mantine-color-scheme` 속성으로 전환한다.

## 1. 토큰 아키텍처

**3계층 구조다.**

| 계층 | 역할 | 정의 위치 |
|---|---|---|
| 1. JS 테마 객체 | 원천 스케일 정의. colors(10단계 tuple), spacing, fontSizes, radius, shadows, breakpoints, headings | `src/core/MantineProvider/default-theme.ts:9-109`, 타입은 `theme.types.ts` |
| 2. 전역 CSS 변수 | 테마를 `--mantine-*` 변수로 변환. 원시 스케일 + 시맨틱 별칭(text, body, error, dimmed, primary-*) + variant 색(`-filled`, `-light`)을 라이트/다크 블록으로 이중 정의 | `src/core/MantineProvider/default-css-variables.css` (527줄), 생성기는 `MantineCssVariables/default-css-variables-resolver.ts` |
| 3. 컴포넌트 CSS 변수 | 컴포넌트별 공개 계약. props를 `createVarsResolver`로 인스턴스 인라인 변수에 매핑 | 예: `src/components/Button/Button.tsx:50-62`(타입), `Button.tsx:127-150`(resolver), `Button.module.css:2-12`(기본값) |

특이점:
- 시맨틱 별칭 계층이 얇지만 존재한다. `--mantine-color-text`, `--mantine-color-body`, `--mantine-color-dimmed`가 다크 블록(`default-css-variables.css:263-278`)과 라이트 블록(`:401-411`)에 각각 정의된다.
- variant 색상 토큰(`--mantine-color-blue-filled`, `--mantine-color-blue-light-hover`)이 전역 변수 계층에 미리 구워진다. 컴포넌트는 이 토큰을 참조만 한다.
- 모든 rem 값에 `--mantine-scale` 배수가 붙는다(`default-css-variables.css:38-42`). 루트 폰트 크기와 무관하게 전체 UI를 배율 조정할 수 있다.

네이밍 예시:

| 토큰 | 계층 | 근거 |
|---|---|---|
| `--mantine-color-blue-6` | 전역 원시 | `default-css-variables.css:179` |
| `--mantine-primary-color-filled` | 전역 별칭 | `default-css-variables.css:27` |
| `--mantine-color-body` | 전역 시맨틱 | `default-css-variables.css:269,402` |
| `--mantine-spacing-md` | 전역 스케일 | `default-css-variables.css:39` |
| `--button-height-compact-xs` | 컴포넌트 | `Button.module.css:8` |
| `--modal-size-md` | 컴포넌트 | `Modal.module.css:4` |

## 2. 컴포넌트 인벤토리

**총 115개.**

- 계수 방법: `ls -d packages/@mantine/core/src/components/*/ | wc -l` = 115. 디렉터리 1개를 컴포넌트 1개로 센다. `index.ts` 파일은 제외된다. ButtonGroup 같은 하위 컴포넌트는 부모 디렉터리에 포함되므로 별도로 세지 않는다.

| 구분 | 예시 |
|---|---|
| primitive (합성 재료) | UnstyledButton, Text, Paper, Group, Stack, Flex, Grid, SimpleGrid, Center, Container, Space, AspectRatio, Portal, Overlay, Transition, FocusTrap, VisuallyHidden, ScrollArea, Collapse, Combobox |
| 범용 조립품 | Button, Modal, Drawer, Tabs, Select, Checkbox, Radio, Switch, Table, Menu, Popover, Tooltip, Card, Badge, Accordion |
| use-case (용도가 이름에 박힘) | CopyButton, FileButton, CloseButton, Burger, PasswordInput, PinInput, ColorInput, JsonInput, MaskInput, BackgroundImage, LoadingOverlay, TableOfContents, EmptyState, NavLink, Dialog, Notification, Spoiler, Highlight, Rating, Timeline, Stepper |
| 데스크톱 특화 | FloatingWindow, Menubar, Splitter, HoverCard, Kbd, AppShell |

- use-case 처리 방식이 뚜렷하다. CopyButton은 `value`와 `timeout`만 받는 headless 래퍼다(`src/components/CopyButton/CopyButton.tsx:4-13`). 용도를 variant로 만들지 않고 컴포넌트로 분리한다.

## 3. variant 철학

### Button

variant 축 전체 인용 (`src/components/Button/Button.tsx:40-48`):

```ts
export type ButtonVariant =
  | 'filled'
  | 'light'
  | 'outline'
  | 'transparent'
  | 'white'
  | 'subtle'
  | 'default'
  | 'gradient';
```

직교 축 구성:

| 축 | 값 | 근거 |
|---|---|---|
| variant | 위 8종, 전부 시각 톤 | `Button.tsx:40-48` |
| color | 테마 색 아무거나 (`MantineColor`) | `Button.tsx:70-71` |
| size | `xs~xl` + `compact-xs~compact-xl` | `Button.tsx:37` |
| radius, fullWidth, justify | 형태 보조 축 | `Button.tsx:73-86` |

핵심 메커니즘: variant 색상 계산을 컴포넌트가 하지 않는다. 테마의 `variantColorResolver` 한 함수가 (color, variant) 쌍을 background, hover, color, border 4개 값으로 변환한다(`Button.tsx:129-133`). 기본 resolver는 9개 분기를 가진다: none, filled, light, outline, subtle, transparent, white, gradient, default (`src/core/MantineProvider/color-functions/default-variant-colors-resolver/default-variant-colors-resolver.ts:40-235`). Button, ActionIcon, Badge, NavLink가 같은 resolver를 공유한다. 사용자는 resolver를 교체해서 커스텀 variant를 전 컴포넌트에 일괄 추가할 수 있다.

### 오버레이 계열: Modal (+ Drawer)

Modal의 변형 축 (`src/components/Modal/ModalRoot.tsx:24-44`):

| 축 | 값 | 근거 |
|---|---|---|
| size | xs 320px ~ xl 780px + 임의값 | `Modal.module.css:2-7` |
| fullScreen | boolean | `ModalRoot.tsx:42-43` |
| centered | boolean | `ModalRoot.tsx:39-40` |
| yOffset / xOffset | 기본 `5dvh` / `5vw` | `ModalRoot.tsx:27-31,64` |
| radius, transitionProps, scrollAreaComponent | 보조 축 | `ModalRoot.tsx:33-37,63` |

Drawer는 `position: 'bottom' | 'left' | 'right' | 'top'` 축을 가진다(`src/components/Drawer/DrawerRoot.tsx:20`). named variant는 두 컴포넌트 모두 없다. 형태 파라미터의 조합으로만 변형한다.

### 리스트 계열: List (+ NavLink)

List는 타이포그래피 리스트(ul/ol)다. 모바일 셀 리스트가 아니다. 축 (`src/components/List/List.tsx:31-61`):

| 축 | 값 | 근거 |
|---|---|---|
| type | `'ordered' \| 'unordered'` | `List.tsx:35-36` |
| withPadding, icon, spacing, center, listStyleType | 형태 보조 축 | `List.tsx:38-54` |

셀에 가까운 컴포넌트는 NavLink다. variant는 `'filled' | 'light' | 'subtle'` 3종이고 역시 시각 톤이다(`src/components/NavLink/NavLink.tsx:29`).

### use-case variant 존재 여부

**variant 수준에서는 없다.** 115개 컴포넌트의 variant는 전부 시각 톤이다. Seed Design의 ActionButton 같은 용도 지정 variant, 확인/취소 전용 변형, danger variant가 없다. 위험 동작은 `color="red"`를 조합해서 표현한다. 용도는 컴포넌트 이름 수준에서만 존재한다: CopyButton, FileButton, PasswordInput, Burger, CloseButton(`CloseButtonVariant = 'subtle' | 'transparent'`, `src/components/CloseButton/CloseButton.tsx:19`).

## 4. 모바일 어휘

**모바일 전용 컴포넌트가 없다.** 디렉터리 전수 확인 결과:

| 모바일 어휘 | 실존 여부 | 대체물 |
|---|---|---|
| BottomSheet | 없음 | Drawer `position="bottom"` (`DrawerRoot.tsx:20`). 드래그 닫기 제스처 없음 |
| ActionSheet | 없음 | 없음 (Menu는 데스크톱 드롭다운) |
| SafeArea | 없음 | AppShell footer에만 `env(safe-area-inset-bottom)` (`AppShell.module.css:181-182`) |
| PullToRefresh | 없음 | 없음 |
| SwipeAction | 없음 | 없음 |
| IndexBar | 없음 | 없음 |
| FloatingPanel / Bubble | 없음 | FloatingWindow는 데스크톱 드래그 창, Affix는 고정 배치 |
| TabBar | 없음 | Tabs는 콘텐츠 탭. 하단 내비게이션 아님 |
| NavBar | 없음 | AppShellNavbar는 데스크톱 사이드바 |
| Toast | 없음(core 기준) | Notification은 표시용 껍데기. 큐/스택은 별도 패키지 `@mantine/notifications` (이 클론에 없음) |

터치 대응은 "보정" 수준으로만 존재한다: `-webkit-tap-highlight-color: transparent` 18개 파일, `touch-action: manipulation` (`UnstyledButton.module.css:11`, `Paper.module.css:7`), Slider와 Splitter의 터치 좌표 처리(`src/components/Slider/utils/get-client-position/get-client-position.ts`).

## 5. 스타일링과 테마

| 항목 | 방식 | 근거 |
|---|---|---|
| CSS 방식 | CSS Modules(`*.module.css`) + postcss-preset-mantine(autoRem, mixin) | 각 컴포넌트 디렉터리, `postcss.config.cjs:3-5` |
| 런타임 | CSS-in-JS 없음. 동적 값은 인라인 CSS 변수로만 주입(`createVarsResolver`) | `Button.tsx:127-150` |
| 커스터마이즈 API | Styles API: 부위별 `classNames`/`styles`(`stylesNames`), 상태는 data 속성(`data-full-screen` 등) | `src/core/styles-api/`, `ModalRoot.tsx:116-117` |
| hover | `@mixin hover`로 hover 스타일을 감싼다. 생 `:hover`는 5개 파일뿐 | `Button.module.css:107`. mixin 정의는 외부 패키지 postcss-preset-mantine에 있어 이 클론에서는 확인 불가 |
| 다크 모드 | html의 `data-mantine-color-scheme` 속성 전환. 토큰을 라이트/다크 블록에 이중 정의 | `default-css-variables.css:263-264,396-397`, `MantineProvider.tsx:36,77-89` |
| 상태 저장 | `localStorageColorSchemeManager` 기본, storage 이벤트로 탭 간 동기화 | `color-scheme-managers/local-storage-manager.ts:21-42` |
| SSR | `ColorSchemeScript`로 첫 페인트 전 속성 주입 | `src/core/MantineProvider/ColorSchemeScript/` |
| 배율 | 모든 rem에 `--mantine-scale` 곱, `autoRem`으로 px 작성을 rem으로 자동 변환 | `default-css-variables.css`, `postcss.config.cjs:4` |

## 6. 신규 DS 시사점 (모바일 웹뷰 기준)

1. **variantColorResolver 패턴을 가져온다.** (color, variant) → 4개 색 값 변환을 테마의 단일 함수로 중앙화한다. variant 추가가 resolver 분기 1개로 끝난다. 컴포넌트 N개를 수정하지 않는다. 근거: `default-variant-colors-resolver.ts:40-235`를 Button, NavLink, Badge가 공유.
2. **컴포넌트 스코프 CSS 변수를 공개 계약으로 삼는다.** `--button-height` 같은 변수 계층이 있으면 인스턴스 오버라이드에 새 variant가 필요 없다. 런타임 CSS-in-JS가 없어 웹뷰 성능에도 유리하다. 근거: `Button.tsx:50-62` + `Button.module.css:2-12`.
3. **사이즈 스케일은 Mantine 값을 상속하지 않는다.** Mantine 기본 버튼과 인풋은 36px이고 compact는 22px까지 내려간다(`Button.module.css:2-12`, `Input.module.css:6-18`). 데스크톱 밀도 기준이다. 모바일 DS는 기본 44px 이상으로 스케일을 새로 끊어야 한다.
4. **모바일 오버레이 어휘는 직접 만들어야 한다.** Mantine은 BottomSheet를 Drawer `position="bottom"`으로 때우고 제스처와 SafeArea 컴포넌트가 없다. 웹뷰 DS는 드래그 닫기와 safe-area를 1급 기능으로 갖춘 BottomSheet를 별도 설계해야 한다. Mantine에서 재사용할 것은 ModalBase의 포커스 트랩, 스크롤 잠금, 전환 인프라 구조다(`src/components/ModalBase/`).
5. **hover는 mixin으로 강제한다.** Mantine은 hover 스타일을 `@mixin hover`로 감싸 터치 기기 오작동을 막는다(18개 파일 사용, 생 `:hover` 5개). 웹뷰 DS에서는 이 규칙을 lint로 강제할 가치가 있다.
6. **다크 모드는 data 속성 + localStorage 관리자 + SSR 스크립트 조합이면 충분하다.** 웹뷰에서 네이티브 테마와 동기화할 때 `colorSchemeManager` 인터페이스(`color-scheme-managers/types.ts`)처럼 저장소를 주입식으로 추상화하면 브리지 연동이 쉬워진다.
