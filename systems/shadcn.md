# shadcn/ui (built on Radix UI)

> **GitHub**: [shadcn-ui/ui](https://github.com/shadcn-ui/ui) (119.8k stars) · [radix-ui/primitives](https://github.com/radix-ui/primitives)
> **Docs**: [ui.shadcn.com](https://ui.shadcn.com) · [radix-ui.com](https://www.radix-ui.com)
> **라이선스**: MIT
> **핵심 정체성**: npm 패키지가 아닌 **코드 배포 플랫폼(code distribution platform)**. 컴포넌트를 설치하는 것이 아니라 프로젝트로 복사(copy)하여 소유(own)하는 구조.

---

## 1. 토큰 아키텍처

### 계층 구조

shadcn/ui의 토큰은 **CSS custom properties + Tailwind CSS theme** 2층 구조로, 전통적 design system의 primitive → semantic → component 3단계와는 다르다.

| 계층 | 역할 | 예시 |
|------|------|------|
| **CSS Variables (semantic)** | `:root` / `.dark`에 정의되는 의미론적 색상 토큰 | `--primary`, `--destructive`, `--muted-foreground` |
| **Tailwind theme mapping** | CSS variables를 Tailwind utility class로 연결 | `bg-primary`, `text-muted-foreground` |
| **Component-level classes** | CVA variant에서 Tailwind class 조합으로 직접 정의 | `bg-primary text-primary-foreground hover:bg-primary/90` |

**primitive 계층이 부재**한다. `--primary`가 `oklch(0.205 0 0)`이라는 raw 값을 직접 가지며, 중간에 `--color-neutral-900` 같은 primitive 토큰 레이어가 없다. 이는 Tier 1 시스템(Material Design의 tonal palette, Spectrum의 global color tokens)과 구조적으로 구별되는 지점이다.

### 네이밍 컨벤션

- **CSS variables**: `--kebab-case` (예: `--card-foreground`, `--sidebar-primary-foreground`)
- **Tailwind classes**: CSS variable명을 그대로 utility로 사용 (`bg-card`, `text-sidebar-primary-foreground`)
- **의미론적 쌍(pair) 구조**: `--X` / `--X-foreground` 패턴으로 배경색-전경색을 쌍으로 정의

### 전체 CSS 변수 인벤토리 (v4, oklch 기반)

| 카테고리 | 변수 | 수량 |
|----------|------|------|
| **Core** | `--background`, `--foreground` | 2 |
| **Card** | `--card`, `--card-foreground` | 2 |
| **Popover** | `--popover`, `--popover-foreground` | 2 |
| **Primary** | `--primary`, `--primary-foreground` | 2 |
| **Secondary** | `--secondary`, `--secondary-foreground` | 2 |
| **Muted** | `--muted`, `--muted-foreground` | 2 |
| **Accent** | `--accent`, `--accent-foreground` | 2 |
| **Destructive** | `--destructive` | 1 |
| **Border/Input/Ring** | `--border`, `--input`, `--ring` | 3 |
| **Chart** | `--chart-1` ~ `--chart-5` | 5 |
| **Sidebar** | `--sidebar`, `--sidebar-foreground`, `--sidebar-primary`, `--sidebar-primary-foreground`, `--sidebar-accent`, `--sidebar-accent-foreground`, `--sidebar-border`, `--sidebar-ring` | 8 |
| **Radius** | `--radius` | 1 |
| **합계** | | **~32개** |

### 테마 전환 / 다크모드

- `.dark` class를 `<html>`에 토글하는 방식 (next-themes 라이브러리 권장)
- `.dark` 셀렉터에서 동일 변수명을 다른 oklch 값으로 재정의
- **색상 공간**: v4부터 HSL → **oklch**로 전환. oklch는 지각적 균일성(perceptual uniformity)을 제공하여 테마 간 대비 일관성 유지에 유리

### 토큰 포맷 및 동기화

| 항목 | 상태 |
|------|------|
| CSS Variables | ✅ 기본 포맷 |
| Tailwind CSS theme | ✅ CSS variables를 `@theme`으로 연결 |
| Style Dictionary | ❌ 미사용 |
| Figma Variables | ❌ 공식 파이프라인 없음 |
| JSON 토큰 파일 | ❌ 미사용 |

**Figma Variables ↔ Code tokens 동기화 파이프라인이 존재하지 않는다.** 토큰의 single source of truth는 `globals.css`의 CSS variables이며, Figma 측에서는 커뮤니티 키트가 수동으로 이 값을 복제하는 구조이다.

---

## 2. 컴포넌트 인벤토리

### 총 컴포넌트 수

- **Code (공식 registry)**: **63개** (2025년 7월 기준, v4)
- **Figma (공식)**: **없음** — 커뮤니티 키트만 존재
- **Radix Primitives (기반 레이어)**: 28개 컴포넌트 + 6개 유틸리티 = **34개**

### 전체 컴포넌트 목록 (63개, A-Z)

Accordion, Alert, Alert Dialog, Aspect Ratio, Attachment*, Avatar, Badge, Breadcrumb, Bubble*, Button, Button Group, Calendar, Card, Carousel, Chart, Checkbox, Collapsible, Combobox, Command, Context Menu, Data Table, Date Picker, Dialog, Direction, Drawer, Dropdown Menu, Empty, Field, Hover Card, Input, Input Group, Input OTP, Item, Kbd, Label, Marker*, Menubar, Message*, Message Scroller*, Native Select, Navigation Menu, Pagination, Popover, Progress, Radio Group, Resizable, Scroll Area, Select, Separator, Sheet, Sidebar, Skeleton, Slider, Spinner, Switch, Table, Tabs, Textarea, Toast*, Toggle, Toggle Group, Tooltip, Typography

(*표시: 최근 추가된 신규 컴포넌트)

### 분류 체계 (문서 기반 유추)

| 카테고리 | 컴포넌트 | 수 |
|----------|---------|---|
| **폼/입력** | Button, Checkbox, Combobox, Date Picker, Field, Input, Input Group, Input OTP, Label, Native Select, Radio Group, Select, Slider, Switch, Textarea, Toggle, Toggle Group | 17 |
| **네비게이션** | Breadcrumb, Menubar, Navigation Menu, Pagination, Sidebar, Tabs | 6 |
| **데이터 표시** | Avatar, Badge, Calendar, Card, Chart, Data Table, Kbd, Progress, Skeleton, Spinner, Table, Typography | 12 |
| **오버레이/피드백** | Alert, Alert Dialog, Dialog, Drawer, Hover Card, Popover, Sheet, Toast, Tooltip | 9 |
| **레이아웃/구조** | Accordion, Aspect Ratio, Collapsible, Resizable, Scroll Area, Separator | 6 |
| **커맨드/인터랙션** | Command, Context Menu, Dropdown Menu | 3 |
| **AI/메시징 (신규)** | Attachment, Bubble, Marker, Message, Message Scroller | 5 |
| **기타** | Button Group, Direction, Empty, Item | 4 |

### 복합 컴포넌트 (Compound Components)

Radix 기반 컴포넌트는 대부분 compound component 패턴을 사용한다:

```tsx
<Accordion type="single">
  <AccordionItem value="item-1">
    <AccordionTrigger>제목</AccordionTrigger>
    <AccordionContent>내용</AccordionContent>
  </AccordionItem>
</Accordion>
```

`Dialog`, `DropdownMenu`, `Select`, `Tabs`, `ContextMenu`, `Menubar`, `NavigationMenu` 등 대부분의 인터랙티브 컴포넌트가 이 패턴을 따른다.

### 배포 모델: Copy-Paste Architecture

shadcn/ui는 npm 패키지로 설치하지 않는다. CLI를 통해 소스 코드를 프로젝트에 복사한다:

```bash
pnpm dlx shadcn@latest add button
# → 프로젝트의 @/components/ui/button.tsx에 코드 복사
```

- 복사된 코드는 **사용자의 코드**가 되며, 자유롭게 수정 가능
- 업데이트는 `--overwrite` 플래그로 수동 적용
- `eject` 명령어로 shadcn 의존성 자체를 제거하고 CSS를 인라인화 가능
- **Registry 시스템**: `registry.json` + `registry-item.json` 스키마로 커스텀 컴포넌트 배포 가능. GitHub 저장소를 registry로 사용 가능

---

## 3. Figma↔Code 매핑 충실도 (핵심 분석)

### 공식 Figma 키트: 없음

shadcn/ui는 **공식 Figma 라이브러리를 제공하지 않는다.** 문서의 Figma 페이지(ui.shadcn.com/docs/figma)에서도 명시적으로 "community contributed"라고 안내한다.

> "The Figma files are contributed by the community. If you have any questions or feedback, please reach out to the Figma file maintainers."

이는 Tier 1 시스템(Material Design, Spectrum, Carbon)이 공식 Figma 라이브러리를 first-party로 유지보수하는 것과 근본적으로 대비된다.

### 커뮤니티 Figma 키트 현황

| 키트 | 제작자 | 유형 | 특징 |
|------|--------|------|------|
| **shadcn/ui components** | Sitsiilia Bergmann | 무료 | 문서 공식 등재, 정기 유지보수 |
| **shadcn/ui design system** | Pietro Schirano | 무료 | 문서 공식 등재, 코드 구현과 1:1 매칭을 표방 |
| **shadcn/ui kit** | Matt Wierzbicki (shadcndesign.com) | 유료 | 8가지 스타일 통합, 2,000+ 컴포넌트, Figma 플러그인(코드 생성), 문서 공식 등재 |
| **shadcncraft Design System** | shadcncraft.com | 유료 (무료 티어 있음) | tweakcn 테마 연동, AI 워크플로우, Figma→React 내보내기 |
| **shadcn/studio UI Kit** | shadcnstudio.com | 유료 | 550+ 블록, 20+ 테마, AI 코드 변환 |
| **Shadcnblocks.com** | shadcnblocks.com | 유료 | 500+ Pro 블록, Figma MCP 지원 |
| **Obra shadcn/ui Pro** | Obra Studio | 유료 | 변수 일관성, 디자인→코드 플러그인 |
| **Shadcn Space** | shadcnspace.com | 유료 | 320+ 블록, 250+ 컴포넌트 |

### 근본적 매핑 한계: Copy-Paste 아키텍처와 Figma의 구조적 불일치

shadcn/ui의 Figma↔Code 매핑은 **구조적으로 Tier 1 시스템과 다른 문제**를 안고 있다:

#### 1) Code의 단일 원본(Single Source of Truth) 부재

npm 패키지 기반 시스템(Ant Design, MUI)은 `node_modules`에 고정된 컴포넌트 코드가 있으므로 Figma가 그 "하나의 코드"를 반영하면 된다. shadcn/ui는 코드가 각 프로젝트에 복사되는 순간 **fork**된다:

- 프로젝트 A의 `button.tsx`와 프로젝트 B의 `button.tsx`가 다를 수 있음
- Figma 키트가 "shadcn/ui의 Button"을 표현해도, 실제 프로젝트의 Button과 일치한다는 보장이 없음
- **매핑의 대상이 고정된 라이브러리가 아니라 움직이는 타겟**

#### 2) 스타일링의 코드 내재화

Tailwind utility class가 JSX에 인라인으로 존재하므로, Figma의 style/token 시스템과 1:1 대응이 어렵다:

```tsx
// 이 클래스 문자열 전체가 "스타일"인데, Figma에서 어떻게 표현할 것인가?
"inline-flex shrink-0 items-center justify-center gap-2 rounded-md text-sm
 font-medium whitespace-nowrap transition-all outline-none
 focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50
 disabled:pointer-events-none disabled:opacity-50"
```

- Figma의 Auto Layout이 `inline-flex items-center justify-center gap-2`에 대응 가능
- 그러나 `focus-visible:ring-[3px]`, `disabled:opacity-50` 같은 **상태 기반 반응형 스타일**은 Figma의 variant로만 근사 가능
- `hover:bg-primary/90`의 opacity modifier는 Figma의 color style과 직접 대응 불가

#### 3) Variant 매핑의 비대칭

| Code (CVA) | Figma 키트 (일반적) |
|------------|-------------------|
| `variant`: 6개 값 (default, destructive, outline, secondary, ghost, link) | Figma variant property로 매핑 가능 |
| `size`: 8개 값 (default, xs, sm, lg, icon, icon-xs, icon-sm, icon-lg) | Figma variant property로 매핑 가능 |
| `asChild`: Slot 기반 폴리모픽 렌더링 | **Figma 대응 불가** — 코드 전용 개념 |
| `className`: 임의 Tailwind class 추가 | **Figma 대응 불가** — 무한 커스터마이징 |
| `data-slot`, `data-variant` attributes | Figma에 해당 개념 없음 |

#### 4) Radix Primitive ↔ Figma 구조 간극

Radix의 compound component 구조(`Dialog.Root > Dialog.Trigger > Dialog.Portal > Dialog.Content > Dialog.Title > Dialog.Description > Dialog.Close`)는 Figma의 컴포넌트 계층과 본질적으로 다르다. Figma는 시각적 계층을, Radix는 동작/접근성 계층을 표현하기 때문이다.

### 매핑 충실도 종합 평가

| 항목 | 평가 |
|------|------|
| 1:1 대응률 | 커뮤니티 키트 의존. 무료 키트는 ~40-50개 수준, 유료 키트는 63개 전부 표방하나 검증 불가 |
| 네이밍 정합성 | 컴포넌트명은 대체로 일치. props명은 Figma kit마다 상이 |
| Variant 정합성 | 주요 variant(variant, size)는 매핑 가능. asChild, className 등 코드 전용 API는 매핑 불가 |
| 토큰 정합성 | CSS variables를 Figma Variables/Styles로 수동 복제. 자동 동기화 없음 |
| 구조적 대응 | Auto Layout ↔ Flexbox 부분 대응. 상태 스타일, 반응형은 근사만 가능 |
| 매핑 방향 | **Code-first**. Figma는 코드를 사후 추적하는 종속 변수 |

**결론**: shadcn/ui는 Figma↔Code 매핑 충실도에서 **구조적 한계**를 가진다. 이는 품질 문제가 아니라 아키텍처 선택의 결과이다. Code ownership을 극대화하는 대신, Figma와의 구조적 정합성을 포기한 것이다.

---

## 4. API 설계 철학

### 핵심 구조: Headless Primitive + Tailwind Styling + CVA Variants

shadcn/ui의 컴포넌트는 3개 레이어의 합성이다:

```
┌─────────────────────────────────────────┐
│  shadcn/ui Component (button.tsx)       │  ← 사용자 소유 코드
│  ┌───────────────────────────────────┐  │
│  │  CVA (class-variance-authority)   │  │  ← Variant → Tailwind class 매핑
│  │  ┌─────────────────────────────┐  │  │
│  │  │  Radix UI Primitive (Slot)  │  │  │  ← Headless 동작/접근성
│  │  └─────────────────────────────┘  │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### Button 소스코드로 보는 구조 (v4 registry)

```tsx
import { cva, type VariantProps } from "class-variance-authority"
import { Slot } from "radix-ui"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  // Base classes: 모든 variant에 공통 적용
  "inline-flex shrink-0 items-center justify-center gap-2 rounded-md text-sm font-medium ...",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-white hover:bg-destructive/90 ...",
        outline: "border bg-background shadow-xs hover:bg-accent ...",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground ...",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2 has-[>svg]:px-3",
        xs: "h-6 gap-1 rounded-md px-2 text-xs ...",
        sm: "h-8 gap-1.5 rounded-md px-3 ...",
        lg: "h-10 rounded-md px-6 ...",
        icon: "size-9",
        "icon-xs": "size-6 ...",
        "icon-sm": "size-8",
        "icon-lg": "size-10",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  }
)

function Button({ className, variant, size, asChild = false, ...props }:
  React.ComponentProps<"button"> & VariantProps<typeof buttonVariants> & { asChild?: boolean }
) {
  const Comp = asChild ? Slot.Root : "button"
  return (
    <Comp
      data-slot="button"
      data-variant={variant}
      data-size={size}
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  )
}
```

### 주요 설계 패턴

| 패턴 | 설명 |
|------|------|
| **CVA (class-variance-authority)** | Stitches에서 영감받은 variant → class 매핑 라이브러리. 타입 안전한 variant props 자동 생성 |
| **cn() 유틸리티** | `clsx` + `tailwind-merge` 조합. 조건부 class 병합 + Tailwind class 충돌 해결 |
| **asChild / Slot** | Radix의 `Slot` 컴포넌트로 자식 요소에 props를 병합. `<Button asChild><a href="/">` 패턴 |
| **Composition** | Compound component + children 기반. Configuration object API 없음 |
| **data-slot / data-variant** | v4부터 CSS 셀렉터 훅으로 `data-*` 속성 사용. 외부 스타일링 타겟팅 가능 |
| **buttonVariants export** | variant 함수를 별도 export하여 `<a>` 등 다른 요소에 동일 스타일 적용 가능 |

### Full Ownership 모델

- 컴포넌트 코드가 프로젝트에 복사되면 **사용자가 완전한 소유권**을 가짐
- `node_modules`에 숨겨진 추상화 없음 — 모든 코드가 가시적
- 커스터마이징에 제약 없음: CVA variant 추가, Radix props 직접 전달, Tailwind class 오버라이드 모두 가능
- 대가: 라이브러리 업데이트 시 수동 머지 필요, 프로젝트 간 컴포넌트 drift 발생 가능

### Base 라이브러리 선택 (v4 신규)

v4부터 3가지 base 라이브러리를 선택할 수 있다:

| Base | 설명 |
|------|------|
| `base` (Base UI) | MUI 팀의 headless 라이브러리 (기본값) |
| `radix` (Radix UI) | 기존 shadcn/ui의 기반. WorkOS 유지보수 |
| `aria` (React Aria) | Adobe의 접근성 특화 라이브러리 |

이는 shadcn/ui가 Radix에 종속된 것이 아니라, **headless primitive 레이어를 교체 가능한 아키텍처**로 진화했음을 보여준다.

---

## 5. 접근성

### Radix Headless 접근성 레이어

shadcn/ui의 접근성은 전적으로 Radix UI Primitives(또는 v4에서 선택한 base 라이브러리)에 위임된다. Radix의 접근성 보장:

| 영역 | 구현 |
|------|------|
| **WAI-ARIA 준수** | W3C WAI-ARIA Practices Guide의 디자인 패턴을 "가능한 한" 준수 |
| **ARIA 속성** | `role`, `aria-expanded`, `aria-selected`, `aria-modal` 등 컴포넌트에 내장 자동 적용 |
| **포커스 관리** | Dialog 열림 시 포커스 트랩, 닫힘 시 복원. `FocusScope` 내부 컴포넌트 사용 |
| **키보드 네비게이션** | Arrow keys (Menu, Select, Tabs), Escape (Dialog, Popover), Enter/Space (Button, Toggle), Home/End (Select, Menu) |
| **스크린 리더** | `VisuallyHidden` 컴포넌트로 시각적으로 숨기되 스크린 리더에는 노출 |
| **Dismiss 동작** | `DismissableLayer`로 외부 클릭, Escape 키에 의한 일관된 닫기 동작 |

### Radix 내부 접근성 빌딩 블록

공개 컴포넌트 뒤에 비공개 내부 모듈이 접근성을 처리한다:

- `react-focus-scope`: 포커스 트랩/복원
- `react-dismissable-layer`: 외부 상호작용 감지 및 닫기
- `react-popper`: Floating UI 기반 위치 결정 (Tooltip, Popover, DropdownMenu)
- `react-menu`: Menu 계열 공통 키보드/포커스 로직
- `react-presence`: 마운트/언마운트 애니메이션 중 접근성 유지

### 접근성의 구조적 특징

**장점**:
- 접근성 로직이 headless 레이어에 캡슐화되어, 스타일을 아무리 수정해도 접근성이 깨지지 않음
- Radix는 WorkOS(구 Vercel 지원)가 전담 유지보수 — 접근성 버그 수정이 shadcn/ui와 독립적으로 이루어짐
- WAI-ARIA 패턴 변경 시 Radix 업데이트만으로 반영 가능

**한계**:
- Radix가 제공하지 않는 컴포넌트(Data Table, Calendar, Chart 등)의 접근성은 shadcn/ui 자체 구현에 의존
- `asChild` / `Slot` 사용 시 개발자가 잘못된 요소를 전달하면 ARIA 시맨틱이 깨질 수 있음 (예: Button docs에서 `<a>`에 `role="button"`이 덮어씌워지는 문제 경고)
- v4에서 base 라이브러리 선택이 가능해지면서, base에 따라 접근성 수준이 달라질 수 있음

---

## 6. 동기화 거버넌스

### Figma↔Code 동기화: 없음 (By Design)

shadcn/ui에는 **Figma↔Code 동기화 메커니즘이 설계상 존재하지 않는다.** 이는 누락이 아니라 철학적 선택이다:

| 동기화 도구 | 상태 |
|------------|------|
| Style Dictionary | ❌ 미사용 |
| Tokens Studio (Figma) | ❌ 미사용 |
| Figma Variables API | ❌ 미사용 |
| 자체 동기화 도구 | ❌ 없음 |
| Figma Dev Mode 연동 | ❌ 공식 지원 없음 |

### 코드 배포 거버넌스

동기화 대신 **코드 배포(code distribution)** 에 초점을 맞춘 독자적 거버넌스 모델을 가진다:

```
shadcn/ui Registry (upstream)
        │
        │  pnpm dlx shadcn@latest add <component>
        ▼
사용자 프로젝트 (@/components/ui/*)
        │
        │  사용자가 직접 수정 (full ownership)
        ▼
프로젝트별 fork (drift 발생 가능)
```

- **Upstream**: shadcn/ui 공식 registry + 커뮤니티 registry
- **배포**: CLI 기반 코드 복사. npm versioning 없음
- **업데이트**: `--overwrite`로 수동. `--diff`로 변경사항 확인 가능
- **마이그레이션**: `migrate` 명령어로 아이콘, RTL, Radix 패키지 통합 등 일괄 변환
- **eject**: shadcn 의존성 완전 제거, CSS 인라인화 (비가역적)

### 커뮤니티 기여 모델

| 채널 | 역할 |
|------|------|
| GitHub PR | 컴포넌트 추가/수정 (shadcn-ui/ui 저장소) |
| Registry Directory | 커뮤니티 컴포넌트 registry 등록 |
| Figma Community | 커뮤니티 Figma 키트 (공식 검증 없음) |
| v0.dev | Vercel의 AI 기반 UI 생성. shadcn/ui 컴포넌트 출력 |

### 동기화 부재의 영향

**긍정적 측면**:
- Figma라는 "또 하나의 원본"을 유지보수할 비용이 없음
- 코드가 유일한 원본(single source of truth)이므로 token/component drift가 Figma 측에서 발생할 수 없음
- 디자인-개발 핸드오프 프로세스가 불필요 — 개발자가 직접 코드를 소유

**부정적 측면**:
- 디자이너가 Code를 읽지 않으면 현재 구현 상태를 파악할 수 없음
- Figma에서 작업한 디자인이 Code와 일치하는지 검증할 자동화된 방법 없음
- 커뮤니티 Figma 키트의 품질/최신성 편차가 크고, 공식 검증 프로세스 없음
- 대규모 팀에서 디자인 일관성(consistency)을 코드 리뷰만으로 유지해야 함

---

## 종합 평가

### 벤치마크 포지셔닝

| 차원 | 평가 | Tier 1 대비 |
|------|------|------------|
| 토큰 아키텍처 | CSS variables + Tailwind. Semantic-only 2층. Primitive 레이어 없음 | 단순하지만 확장성 제한 |
| 컴포넌트 인벤토리 | 63개. 폼/네비게이션/오버레이 균형. AI/메시징 신규 카테고리 | 동등한 커버리지 |
| Figma↔Code 매핑 | **공식 Figma 없음. 구조적 한계.** Code-first 철학의 필연적 결과 | 근본적으로 다른 패러다임 |
| API 설계 | Headless + CVA + Tailwind. Full ownership. 높은 유연성 | 가장 개발자 중심적 |
| 접근성 | Radix 위임. WAI-ARIA 준수. 스타일 수정과 무관하게 유지 | 동등하거나 우수 |
| 동기화 거버넌스 | 동기화 자체가 불필요한 아키텍처. Code distribution 모델 | 비교 불가 (다른 축) |

### 핵심 시사점

shadcn/ui는 **"디자인 시스템"의 전통적 정의에 도전하는 시스템**이다. Figma 라이브러리, token 동기화, 디자인-개발 핸드오프라는 Tier 1 시스템의 전제 자체를 거부하고, **코드를 유일한 원본으로 하는 개발자 소유 모델**을 제시한다.

이 관점에서 Figma↔Code 매핑 충실도 점수가 낮은 것은 "결함"이 아니라 **아키텍처 선택의 비용**이다. 반대로, 이 모델은 디자인 시스템의 최종 소비자(개발자)에게 최대의 통제권을 부여하며, 이것이 120k GitHub stars라는 커뮤니티 채택으로 검증되었다.

벤치마크에서 shadcn/ui는 **"Figma↔Code 매핑"이라는 평가 축 자체가 코드-퍼스트 시스템에는 적용 불가능할 수 있음**을 보여주는 대조군(control group) 역할을 한다.
