# ABC Def (LINE / LY Corporation) 실측 분석

- 저장소: `sources-candidates/abc-def` (github.com/line/abc-def)
- 실측 버전: 2.2.0 (`packages/styles/package.json`, `packages/react/package.json`, `packages/vue/package.json` 모두 동일)
- 라이선스: Apache-2.0

## 0. 요약

**결론: ABC Def 는 데스크톱 위주(desktop) 시스템이다.** shadcn/ui 계보를 CSS-first 로 재구성한 사내 웹 어드민/서비스용 키트다. 모바일 웹뷰 어휘는 사실상 없다.

| 판정 항목 | 실측 결과 | 근거 |
|---|---|---|
| 플랫폼 지향 | desktop | 아래 4개 근거 |
| 기본 터치 타깃 | Button default 32px(h-8), xs 24px(h-6) | `packages/styles/src/components/button.css:131-145` |
| hover 의존도 | 컴포넌트 CSS 49개 중 24개가 hover 스타일 보유 | `grep -l hover packages/styles/src/components/*.css` |
| safe-area 처리 | 0건. `pointer: coarse`, `any-hover` 도 0건 | `grep -rn 'safe-area\|pointer:\|any-hover' packages/` |
| 데스크톱 전용 어휘 | Kbd, Menubar, ContextMenu, Command(팔레트), HoverCard, Sidebar, Resizable | `packages/react/src/components/` 디렉터리 |
| 모바일 대응 | 부분적. useIsMobile(768px) 은 Sidebar 1곳만 사용 | `packages/react/src/hooks/use-mobile.tsx:18`, `packages/react/src/components/sidebar.tsx:80` |

핵심 특징 3가지:

1. 토큰과 셀렉터를 `@line/abc-def-styles` 한 패키지에 두고, React 와 Vue 가 같은 클래스 계약을 소비한다. 루트 README 가 이를 "CSS-first design system" 으로 선언한다 (`README.md:3`).
2. 토큰은 3계층이다: Tailwind v4 primitive, semantic, component (`packages/styles/README.md:28-34`).
3. variant 는 역할(톤) 기반 6종이다. 용도(use-case) variant 는 없고, AlertDialogAction/Cancel 같은 조합 프리셋만 있다.

## 1. 토큰 아키텍처

3계층 구조를 README 가 공식 선언하고, 파일이 그대로 뒷받침한다 (`packages/styles/README.md:28-34`).

| 계층 | 역할 | 정의 위치 | 예시 |
|---|---|---|---|
| 1. primitive | 원색 팔레트. 저장소 안에 정의가 없고 Tailwind CSS v4 테마 변수를 그대로 쓴다 | tailwindcss 패키지 기본 테마 | `--color-zinc-950`, `--color-white`, `--color-red-500` |
| 2. semantic | 역할 변수. 라이트 값은 `:root`, 다크 값은 `.dark` 로 재정의 | `packages/styles/src/semantic.css:1-69` | `--primary`, `--muted-foreground`, `--border-input`, `--ring` |
| 3. component | 컴포넌트별 변수. semantic 을 참조. 자동 생성 파일로 집약 | `packages/styles/src/components/variables.css` (611줄, 생성물) + 각 컴포넌트 CSS | `--button-bg-primary`, `--dialog-overlay-bg`, `--badge-bg-default-hover` |

네이밍 예시 5개:

| 토큰 | 계층 | 위치 |
|---|---|---|
| `--color-zinc-950` | primitive | Tailwind 테마. `semantic.css:5` 에서 참조 |
| `--primary` / `--primary-foreground` | semantic | `packages/styles/src/semantic.css:10-11` |
| `--muted-foreground` | semantic | `packages/styles/src/semantic.css:17` |
| `--button-bg-primary-hover` | component | `packages/styles/src/components/variables.css:110` |
| `--dropdown-menu-item-bg-destructive-focus` | component | `packages/styles/src/components/variables.css:342` |

component 계층 네이밍 규칙: `--{컴포넌트}-{부위}-{속성(bg/fg/border/ring)}-{variant}-{상태(hover/expanded/focus/checked)}`.

특이점 2가지:

- `variables.css` 는 컴포넌트 CSS 에서 스크립트로 추출한 생성물이다. 파일 머리말이 `pnpm generate:variables` 를 명시한다 (`variables.css:1-4`). 오버라이드 지점 전체를 한 파일에서 볼 수 있다.
- `--surface` 는 `.dark` 블록에만 정의된다 (`semantic.css:43-44`). 라이트 모드에서 `--card-bg: var(--surface)` 는 빈 값으로 풀린다. 라이트 카드가 투명 배경이 되는 설계다.

## 2. 컴포넌트 인벤토리

- 총수: **53개** 컴포넌트 패밀리.
- 세는 방법: `ls packages/react/src/components | wc -l` = 53. 파일 1개가 패밀리 1개다(예: `dialog.tsx` 안에 Dialog, DialogContent 등 서브컴포넌트 포함).
- 교차 검증: Vue 패키지도 같은 53개 디렉터리를 가진다 (`ls packages/vue/src/components` = 53 + index.ts). 스타일은 49개 CSS 파일이 대응한다 (`packages/styles/src/components/*.css` 51개 중 index.css, variables.css 제외).

| 구분 | 컴포넌트 |
|---|---|
| primitive (범용 부품) | Button, ButtonGroup, Input, Textarea, Checkbox, RadioGroup, Switch, Select, NativeSelect, Slider, Badge, Avatar, Separator, Label, Tabs, Accordion, Collapsible, Card, Table, Progress, Tooltip, Popover, Dialog, Sheet, Drawer, AlertDialog, DropdownMenu, ContextMenu, ScrollArea, AspectRatio, Skeleton, Spinner, Toggle, ToggleGroup, Item, Kbd, Alert |
| 패턴/용도 지정 성격 | Command(⌘K 팔레트), Combobox, InputOTP(OTP 입력), InputGroup, Field(폼 필드 조립), Empty(빈 상태), Sidebar(앱 셸), NavigationMenu, Menubar, Breadcrumb, Pagination, Calendar, Carousel, Resizable, Sonner(Toaster) |

인벤토리 성격: shadcn/ui 의 컴포넌트 목록과 거의 1:1 이다. Radix UI, Base UI, vaul, cmdk, embla, sonner 를 조합한다 (`packages/react/package.json:46-61`).

## 3. variant 철학

**요약: variant 는 시각 톤 축이다. 용도 축이 아니다.** variant(톤), size(밀도), rounded(형태) 3축을 직교로 둔다. 용도는 variant 로 만들지 않고, 조합 컴포넌트의 기본값으로만 주입한다.

### 3.1 Button: 3축

`packages/react/src/components/button.tsx:25-60` 인용:

```ts
export const buttonVariants = cva("button", {
  variants: {
    variant: {
      default: "button-variant-default",
      secondary: "button-variant-secondary",
      destructive: "button-variant-destructive",
      ghost: "button-variant-ghost",
      link: "button-variant-link",
      outline: "button-variant-outline",
    },
    size: {
      xs, sm, default, lg, xl,
      icon, "icon-xs", "icon-sm", "icon-lg", "icon-xl",
    },
    rounded: { xs, sm, default, lg, xl },
  },
});
```

| 축 | 값 | 개수 |
|---|---|---|
| variant | default, secondary, destructive, ghost, link, outline | 6 |
| size | xs, sm, default, lg, xl + icon 5종 | 10 |
| rounded | xs, sm, default, lg, xl | 5 |

상태 축은 CSS 변수 접미사로 표현한다: `-hover`, `-expanded` (`packages/styles/src/components/button.css:11-17`). `-pressed`, `-active` 계열은 없다. 데스크톱 상호작용 모델이다.

### 3.2 오버레이: Sheet

Sheet 는 variant 대신 `side` prop 1축을 가진다. `packages/react/src/components/sheet.tsx:63-67` 인용:

```ts
side = "right",
...
side?: "top" | "right" | "bottom" | "left";
```

Dialog 는 variant 축이 없다. `showCloseButton` boolean 하나만 있다 (`dialog.tsx:62-69`). Drawer 는 vaul 의 `data-vaul-drawer-direction`(bottom/left/right/top) 을 CSS 에서 분기한다 (`packages/styles/src/components/drawer.css:19-23`).

### 3.3 리스트: Item

`packages/react/src/components/item.tsx:49-66` 인용:

```ts
const itemVariants = cva("item", {
  variants: {
    variant: { default, outline, muted },
    size: { default, sm, xs },
  },
});
```

ItemMedia 는 콘텐츠 종류 축을 가진다: `variant: { default, icon, image }` (`item.tsx:88-99`).

### 3.4 use-case variant 존재 여부

**Seed Design 방식의 use-case variant 는 없다.** 용도 주입은 2가지 형태로만 나타난다.

1. 조합 프리셋: AlertDialogAction 은 Button(variant=default), AlertDialogCancel 은 Button(variant=outline) 을 기본값으로 감싼다 (`packages/react/src/components/alert-dialog.tsx:144-171`). 확인/취소 용도에 톤 기본값만 배선하고, variant prop 으로 뒤집을 수 있게 열어 둔다.
2. 용도 지정 컴포넌트: InputOTP(OTP 입력), Command(커맨드 팔레트), Empty(빈 상태), Field(폼 필드) 는 이름에 용도가 박혀 있다. 그러나 이는 variant 가 아니라 별도 컴포넌트다.

## 4. 모바일 어휘

**결론: 모바일 전용 어휘가 사실상 없다.** 디렉터리 실측 결과:

| 어휘 | 존재 | 비고 |
|---|---|---|
| BottomSheet | 없음 | Drawer(vaul) 의 direction=bottom 이 대체. rounded-t, max-h-80vh (`drawer.css:19`) |
| ActionSheet | 없음 | |
| SafeArea | 없음 | `env(safe-area-*)` 참조 0건 |
| PullToRefresh | 없음 | |
| SwipeAction | 없음 | touch 관련 CSS 는 touch-none/touch-manipulation 3건뿐 (`scroll-area.css:21`, `slider.css:11`, `carousel.css:22`) |
| IndexBar | 없음 | |
| FloatingPanel / Bubble | 없음 | |
| TabBar | 없음 | Tabs 는 데스크톱 탭 |
| NavBar | 없음 | NavigationMenu 는 데스크톱 수평 내비게이션 |
| Toast | 있음 | Sonner 래퍼 Toaster (`packages/react/src/components/sonner.tsx:29`) |

모바일 성격이 있는 요소는 3개다: Drawer(vaul 바텀 드로어, 드래그 핸들 포함), Carousel(embla, 터치 스와이프), useIsMobile 훅(768px 분기, Sidebar 가 모바일에서 Sheet 로 전환. `sidebar.tsx:80`).

## 5. 스타일링과 테마

| 항목 | 실측 |
|---|---|
| CSS 방식 | Tailwind CSS v4 기반 CSS-first. 컴포넌트는 시맨틱 클래스(`button`, `button-variant-default`)만 출력하고, 실제 스타일은 styles 패키지의 `@apply` + CSS 변수가 담당 |
| 클래스 조합 | class-variance-authority(cva) + tailwind-merge (`button.tsx:25`, `packages/react/src/lib/utils`) |
| 스타일 배포 | 빌드 산출물 없이 authored CSS 를 그대로 npm 배포. 소비자가 Tailwind v4 로 `@import` 처리 (`packages/styles/README.md:23-26`) |
| 테마 전환 | `.dark` 클래스 오버라이드. semantic 26개 + component 예외 몇 개만 재정의 (`semantic.css:39-69`, `variables.css:613-701`). 토글은 소비 앱 책임 |
| 상태 노출 | 모든 컴포넌트가 `data-slot`, `data-variant`, `data-size` 속성을 출력 (`button.tsx:75-78`) |
| 프레임워크 | React 19 + Vue 가 같은 클래스 계약 소비. 루트 export 없이 서브패스 import 강제 (`README.md:40`) |

## 6. 신규 DS 시사점 (모바일 웹뷰 기준)

1. **3계층 토큰 계약을 그대로 채택할 만하다.** primitive(팔레트), semantic(역할), component(부위별 오버라이드 지점)의 분리가 파일 단위로 깨끗하다. 특히 component 토큰을 소스에서 추출해 `variables.css` 한 파일로 생성하는 방식(`variables.css:1-4`)은 "테마 커스터마이징 표면 전체를 한 파일로 문서화"하는 효과가 있다. 우리 DS 에도 생성 파이프라인째 이식할 수 있다.
2. **스타일과 프레임워크 패키지의 분리는 웹뷰 DS 에 유효하다.** 클래스 계약 하나로 React/Vue 가 픽셀 동일성을 얻는다. 웹뷰 앱에 레거시 페이지나 제2 프레임워크가 섞일 가능성이 있으면 이 구조가 보험이 된다.
3. **상태 토큰 축은 반면교사다.** abc-def 는 `-hover`, `-expanded` 만 있고 `-pressed` 가 없다 (`button.css:11-17`). 모바일 웹뷰 DS 는 처음부터 `-pressed`(active) 를 1급 상태 축으로 두고, hover 는 `@media (any-hover: hover)` 가드 아래에만 둬야 한다. abc-def 는 이 가드가 0건이다.
4. **크기 스케일을 그대로 가져오면 안 된다.** default 32px, xs 24px 은 데스크톱 밀도다 (`button.css:131-145`). 모바일 기본은 44px 이상으로 잡고, 데스크톱형 xs/icon-xs 스케일은 빼는 편이 안전하다.
5. **use-case 주입은 "조합 프리셋" 패턴이 참고할 만하다.** AlertDialogAction/Cancel 처럼 primitive Button 을 감싸며 용도별 기본 variant 만 배선하는 방식 (`alert-dialog.tsx:144-171`)은, Seed 식 use-case 컴포넌트(ActionButton)와 순수 primitive 사이의 절충안이다. primitive 계층을 오염시키지 않으면서 확인/취소 같은 반복 용도의 기본값을 표준화할 수 있다.
