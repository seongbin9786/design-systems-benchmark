# shadcn/ui 디자인 토큰 시스템 — 코드 레벨 딥다이브

> **분석 대상**: shadcn/ui v4 (Tailwind CSS v4 + oklch 기반)
> **소스**: [github.com/shadcn-ui/ui](https://github.com/shadcn-ui/ui) · [ui.shadcn.com/docs/theming](https://ui.shadcn.com/docs/theming) · 공식 registry (`ui.shadcn.com/r/styles/new-york-v4/*.json`)
> **분석 범위**: 토큰의 정의(Definition) → 소비(Consumption) → 거버넌스(Governance) 3축
> **핵심 결론**: shadcn/ui의 토큰은 **npm 패키지가 아니라 사용자의 `globals.css`에 존재하는 ~32개의 semantic CSS custom properties**이다. primitive 계층이 없고, 버전 관리가 없으며, Figma 동기화 파이프라인이 존재하지 않는다. 이는 결함이 아니라 "코드를 유일한 원본으로 하는 개발자 소유 모델"이라는 아키텍처 선택의 직접적 결과이다.

---

## 축 1: 토큰 정의 (Definition)

### 1.1 실제 토큰 인벤토리 — 전체 ~32개 semantic 변수

shadcn/ui의 토큰은 `globals.css`의 `:root`(light)와 `.dark`(dark) 셀렉터에 정의된다. 아래는 **neutral base color 기준 v4 기본 스캐폴드의 실제 oklch 값 전체**이다.

#### Core surfaces (6개)

| 토큰 | Light (`:root`) | Dark (`.dark`) |
|------|-----------------|----------------|
| `--background` | `oklch(1 0 0)` | `oklch(0.145 0 0)` |
| `--foreground` | `oklch(0.145 0 0)` | `oklch(0.985 0 0)` |
| `--card` | `oklch(1 0 0)` | `oklch(0.205 0 0)` |
| `--card-foreground` | `oklch(0.145 0 0)` | `oklch(0.985 0 0)` |
| `--popover` | `oklch(1 0 0)` | `oklch(0.205 0 0)` |
| `--popover-foreground` | `oklch(0.145 0 0)` | `oklch(0.985 0 0)` |

#### Emphasis & actions (9개)

| 토큰 | Light (`:root`) | Dark (`.dark`) |
|------|-----------------|----------------|
| `--primary` | `oklch(0.205 0 0)` | `oklch(0.922 0 0)` |
| `--primary-foreground` | `oklch(0.985 0 0)` | `oklch(0.205 0 0)` |
| `--secondary` | `oklch(0.97 0 0)` | `oklch(0.269 0 0)` |
| `--secondary-foreground` | `oklch(0.205 0 0)` | `oklch(0.985 0 0)` |
| `--muted` | `oklch(0.97 0 0)` | `oklch(0.269 0 0)` |
| `--muted-foreground` | `oklch(0.556 0 0)` | `oklch(0.708 0 0)` |
| `--accent` | `oklch(0.97 0 0)` | `oklch(0.269 0 0)` |
| `--accent-foreground` | `oklch(0.205 0 0)` | `oklch(0.985 0 0)` |
| `--destructive` | `oklch(0.577 0.245 27.325)` | `oklch(0.704 0.191 22.216)` |

#### Borders, inputs, focus (3개)

| 토큰 | Light (`:root`) | Dark (`.dark`) |
|------|-----------------|----------------|
| `--border` | `oklch(0.922 0 0)` | `oklch(1 0 0 / 10%)` |
| `--input` | `oklch(0.922 0 0)` | `oklch(1 0 0 / 15%)` |
| `--ring` | `oklch(0.708 0 0)` | `oklch(0.556 0 0)` |

#### Charts (5개)

| 토큰 | Light (`:root`) | Dark (`.dark`) |
|------|-----------------|----------------|
| `--chart-1` | `oklch(0.646 0.222 41.116)` | `oklch(0.488 0.243 264.376)` |
| `--chart-2` | `oklch(0.6 0.118 184.704)` | `oklch(0.696 0.17 162.48)` |
| `--chart-3` | `oklch(0.398 0.07 227.392)` | `oklch(0.769 0.188 70.08)` |
| `--chart-4` | `oklch(0.828 0.189 84.429)` | `oklch(0.627 0.265 303.9)` |
| `--chart-5` | `oklch(0.769 0.188 70.08)` | `oklch(0.645 0.246 16.439)` |

#### Sidebar (8개)

| 토큰 | Light (`:root`) | Dark (`.dark`) |
|------|-----------------|----------------|
| `--sidebar` | `oklch(0.985 0 0)` | `oklch(0.205 0 0)` |
| `--sidebar-foreground` | `oklch(0.145 0 0)` | `oklch(0.985 0 0)` |
| `--sidebar-primary` | `oklch(0.205 0 0)` | `oklch(0.488 0.243 264.376)` |
| `--sidebar-primary-foreground` | `oklch(0.985 0 0)` | `oklch(0.985 0 0)` |
| `--sidebar-accent` | `oklch(0.97 0 0)` | `oklch(0.269 0 0)` |
| `--sidebar-accent-foreground` | `oklch(0.205 0 0)` | `oklch(0.985 0 0)` |
| `--sidebar-border` | `oklch(0.922 0 0)` | `oklch(1 0 0 / 10%)` |
| `--sidebar-ring` | `oklch(0.708 0 0)` | `oklch(0.556 0 0)` |

#### Radius (1개 — 색상 토큰 아님)

| 토큰 | 값 | 비고 |
|------|-----|------|
| `--radius` | `0.625rem` | light 전용. `.dark`에서 재정의되지 않음 |

**합계: 색상 31개 + radius 1개 = 32개.** 이 중 `--destructive`는 기본 테마에서 `--destructive-foreground` 쌍을 갖지 않는 유일한 emphasis 토큰이다 (button의 destructive variant가 `text-white`를 하드코딩하는 이유와 연결됨 — §2.2 참고).

### 1.2 foreground/background 쌍(pair) 패턴

shadcn/ui 토큰의 가장 특징적인 네이밍 구조는 **`--X`(surface) / `--X-foreground`(text/icon) 쌍**이다. surface 토큰에는 `-background` 접미사를 붙이지 않는다 (`--primary-background`가 아니라 `--primary`).

| Surface 토큰 | Foreground 토큰 | 제어 대상 | 주요 소비자 |
|--------------|-----------------|-----------|-------------|
| `background` | `foreground` | 앱 기본 배경 + 본문 텍스트 | 페이지 셸, `body` |
| `card` | `card-foreground` | Elevated surface | `Card`, 대시보드 패널 |
| `popover` | `popover-foreground` | Floating surface | `Popover`, `DropdownMenu`, `ContextMenu` |
| `primary` | `primary-foreground` | 최고 강조 액션/브랜드 | 기본 `Button`, 선택 상태, badge |
| `secondary` | `secondary-foreground` | 저강도 filled 액션 | secondary button/badge |
| `muted` | `muted-foreground` | 약한 surface + 저강도 텍스트 | 설명문, placeholder, helper text |
| `accent` | `accent-foreground` | hover/focus/active surface | ghost button, 메뉴 하이라이트, hover된 행 |
| `sidebar` | `sidebar-foreground` | 사이드바 surface + 텍스트 | `Sidebar` 컨테이너 |
| `sidebar-primary` | `sidebar-primary-foreground` | 사이드바 강조 액션 | 활성 아이템, CTA |
| `sidebar-accent` | `sidebar-accent-foreground` | 사이드바 hover/selected | 메뉴 hover 상태 |

**쌍을 갖지 않는 standalone 토큰**: `destructive`(기본 테마 기준), `border`, `input`, `ring`, `chart-1`~`chart-5`, `sidebar-border`, `sidebar-ring`, `radius`.

이 쌍 구조의 실용적 의미: 컴포넌트는 `bg-primary text-primary-foreground`처럼 **두 클래스만 쓰면 어떤 테마에서도 대비가 보장되는 조합**을 얻는다. light에서 `primary`가 어두운 색(`oklch(0.205 0 0)`)이면 `primary-foreground`는 밝은 색(`oklch(0.985 0 0)`)이고, dark에서는 둘이 반전된다. 즉 **대비 관계가 토큰 쌍 자체에 인코딩**되어 있다.

### 1.3 Primitive 계층이 없는 이유와 함의

shadcn/ui에는 `--color-neutral-900`, `--blue-500` 같은 **primitive(원시) 토큰 계층이 존재하지 않는다.** `--primary`가 곧바로 `oklch(0.205 0 0)`이라는 raw 값을 가진다.

```
전통적 3층 (Spectrum/Material/Carbon):
  primitive (--blue-500: #0070f3)
      ↓ 참조
  semantic (--primary: var(--blue-500))
      ↓ 참조
  component (--button-background: var(--primary))

shadcn/ui (2층, 실질 1.5층):
  semantic (--primary: oklch(0.205 0 0))   ← raw 값 직접 보유
      ↓ Tailwind @theme alias
  utility class (bg-primary)               ← 컴포넌트가 직접 소비
```

**왜 없는가:**

1. **추적할 원본 팔레트가 없다.** Tier 1 시스템은 디자인 조직이 Figma에서 팔레트를 관리하고 그것이 primitive 계층으로 흘러들어온다. shadcn/ui는 디자인 조직이 아니라 개발자(shadcn)가 코드로 만드는 시스템이며, 팔레트라는 중간 산출물 자체가 불필요하다.
2. **토큰 수가 극도로 적다.** 32개는 primitive→semantic 2단 간접 참조를 정당화할 만큼 복잡하지 않다. Material Web의 sys 토큰만 70+개, Spectrum은 수백 개다. 32개에 2층을 씌우면 얻는 것보다 추상화 비용이 크다.
3. **소비자가 곧 소유자다.** 토큰을 재정의하려는 사용자는 `--primary: oklch(...)` 한 줄만 바꾸면 된다. primitive 계층이 있으면 "어떤 primitive를 바꿔야 primary가 변하는가"를 알아야 한다. shadcn/ui는 그 인지 비용을 없앴다.

**함의 (trade-off):**

| 장점 | 단점 |
|------|------|
| 토큰 구조를 5분 만에 이해 가능 | 브랜드 팔레트 확장이 어려움 — `--brand-500` 같은 체계를 추가하려면 사용자가 직접 설계해야 함 |
| 재정의가 단일 지점에서 일어남 | light/dark 간 값의 관계가 암묵적 — `--primary` dark 값이 light 값과 어떤 규칙으로 연결되는지 토큰이 표현하지 못함 |
| 빌드 파이프라인 불필요 | 토큰 간 일관성을 검증할 스키마/도구가 없음 |
| — | `--secondary`, `--muted`, `--accent`가 light에서 모두 `oklch(0.97 0 0)`로 **동일한 값**을 갖는 등 의미 구분과 값의 분리가 일어남 — primitive가 있었다면 이 셋이 같은 토큰을 참조한다는 사실이 명시적으로 드러났을 것 |

### 1.4 oklch 색상 공간 — 왜 선택되었나

v4는 v3의 HSL에서 **oklch**로 전환했다. 기본 스캐폴드의 모든 색상 값이 oklch 포맷이다.

```css
--primary: oklch(0.205 0 0);              /* L=0.205, C=0, H=0 → 거의 검은색 */
--destructive: oklch(0.577 0.245 27.325); /* L=0.577, C=0.245, H=27.3° → 채도 높은 빨강 */
--chart-1: oklch(0.646 0.222 41.116);     /* L=0.646, H=41° → 주황 계열 */
```

**선택 이유:**

1. **지각적 균일성 (perceptual uniformity).** oklch에서 같은 L 값은 사람이 느끼기에 같은 밝기다. HSL의 `hsl(210 100% 50%)`(파랑)과 `hsl(60 100% 50%)`(노랑)은 L이 같아도 체감 밝기가 크게 다르다. 테마를 만들 때 "primary를 파랑에서 초록으로 바꾸고 싶은데 대비는 유지하고 싶다"면 oklch에서는 L과 C만 고정하고 H만 돌리면 된다.
2. **테마 생성 도구와의 궁합.** shadcn/ui는 [ui.shadcn.com/themes](https://ui.shadcn.com/themes)와 tweakcn 같은 커뮤니티 테마 생성기를 통해 base color(neutral, stone, zinc, mauve, olive, mist, taupe)를 제공한다. oklch의 균일성 덕분에 이들 도구는 hue 회전만으로도 일관된 대비의 팔레트를 기계적으로 생성할 수 있다.
3. **gamut 활용.** oklch는 sRGB보다 넓은 색 표현이 가능하고, CSS 네이티브 지원(`oklch()` 함수)으로 폴리필이 불필요하다.
4. **alpha 합성.** dark 모드의 `--border: oklch(1 0 0 / 10%)`처럼 "흰색 10%" 표현이 자연스럽다. neutral 테마는 chroma(C)가 전부 0이라 순수 회색이지만, 브랜드 테마에서는 chroma를 살린 채 명도만 조정할 수 있다.

**실제 값에서 읽히는 패턴:** neutral 테마는 모든 색의 chroma(C)가 `0`이다. 즉 완전한 무채색 그레이스케일이며, 색상은 오직 `--destructive`(빨강)와 `--chart-1~5`에만 존재한다. 이는 "shadcn/ui 기본 테마 = 중성 캔버스, 브랜드 색은 사용자가 입힌다"는 철학을 값 자체로 보여준다.

### 1.5 Tailwind `@theme` 통합 — CSS 변수가 유틸리티가 되는 메커니즘

shadcn/ui의 토큰은 그 자체로는 아무것도 하지 않는 평범한 CSS custom properties이다. 이것이 Tailwind utility class로 연결되는 다리가 **`@theme inline` 블록**이다.

```css
@import "tailwindcss";
@import "shadcn/tailwind.css";

@custom-variant dark (&:is(.dark *));

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --color-chart-1: var(--chart-1);
  /* ... chart-2 ~ chart-5 ... */
  --color-sidebar: var(--sidebar);
  --color-sidebar-foreground: var(--sidebar-foreground);
  --color-sidebar-primary: var(--sidebar-primary);
  --color-sidebar-primary-foreground: var(--sidebar-primary-foreground);
  --color-sidebar-accent: var(--sidebar-accent);
  --color-sidebar-accent-foreground: var(--sidebar-accent-foreground);
  --color-sidebar-border: var(--sidebar-border);
  --color-sidebar-ring: var(--sidebar-ring);
}
```

**동작 원리:**

1. Tailwind v4는 `--color-*` 네임스페이스의 변수를 색상 유틸리티의 소스로 사용한다. `--color-primary`가 정의되면 `bg-primary`, `text-primary`, `border-primary`, `ring-primary` 등이 자동 생성된다.
2. `@theme inline`의 `inline` 키워드가 핵심이다. 일반 `@theme`이면 Tailwind가 빌드 시 값을 **정적으로 인라인**하지만, `inline`이면 생성된 유틸리티가 `background-color: var(--color-primary)` → 다시 `var(--background)`를 가리키는 **런타임 참조 체인**을 유지한다.
3. 따라서 `.dark`에서 `--background` 값을 바꾸면 `bg-background`를 쓰는 모든 요소가 **재빌드 없이 런타임에** 즉시 반응한다. 다크모드가 CSS 변수 재정의만으로 동작하는 구조적 근거다.

**Radius 스케일 — 단일 소스에서 파생:**

```css
@theme inline {
  --radius-sm:  calc(var(--radius) * 0.6);
  --radius-md:  calc(var(--radius) * 0.8);
  --radius-lg:  var(--radius);
  --radius-xl:  calc(var(--radius) * 1.4);
  --radius-2xl: calc(var(--radius) * 1.8);
  --radius-3xl: calc(var(--radius) * 2.2);
  --radius-4xl: calc(var(--radius) * 2.6);
}
```

`--radius: 0.625rem` 하나를 바꾸면 `rounded-sm`~`rounded-4xl` 전체 스케일이 비례적으로 바뀐다. 이는 shadcn/ui 토큰 체계에서 **유일하게 파생(derivation) 메커니즘이 존재하는 지점**이다. 색상 토큰에는 이런 파생이 전혀 없고 전부 독립적 raw 값이다.

**Base layer — 토큰의 전역 적용:**

```css
@layer base {
  * {
    @apply border-border outline-ring/50;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

모든 요소의 기본 border 색이 `--border`로, body의 배경/텍스트가 `--background`/`--foreground`로 설정된다. 컴포넌트가 border 색을 명시하지 않아도 테마를 따르는 이유다.

### 1.6 Source of Truth

| 항목 | 상태 |
|------|------|
| 원본 포맷 | **CSS** (`globals.css`의 `:root` / `.dark` 블록) |
| 원본 저장 위치 | **사용자 프로젝트** — `shadcn init`이 스캐폴드를 생성해 줌 |
| 빌드/변환 파이프라인 | ❌ 없음 (Style Dictionary 미사용) |
| JSON 토큰 파일 | ❌ 없음 |
| Figma Variables | ❌ 공식 파이프라인 없음 |
| TypeScript 토큰 타입 | ❌ 없음 (토큰명은 문자열로만 존재) |

**토큰의 single source of truth는 사용자의 `globals.css`이다.** shadcn/ui 저장소에는 "기본값 스캐폴드"만 있을 뿐, 런타임에 참조되는 권위 있는 토큰 파일은 각 프로젝트에 존재한다.

---

## 축 2: 토큰 소비 (Consumption)

### 2.1 소비 경로 개요

```
globals.css (:root / .dark)
    │  --primary: oklch(0.205 0 0)
    ▼
@theme inline
    │  --color-primary: var(--primary)
    ▼
Tailwind 유틸리티 생성
    │  bg-primary / text-primary / ring-primary ...
    ▼
CVA variant (button.tsx)  ←  컴포넌트가 유틸리티 클래스 문자열로 소비
    │  default: "bg-primary text-primary-foreground hover:bg-primary/90"
    ▼
cn() (clsx + tailwind-merge)  ←  사용자 className과 병합
    ▼
DOM (className)
```

컴포넌트는 토큰을 **CSS 변수로 직접 참조하지 않는다.** 반드시 Tailwind 유틸리티 클래스를 거쳐 소비한다. 즉 토큰 소비의 최소 단위는 `bg-primary` 같은 클래스 문자열이다.

### 2.2 실제 컴포넌트 코드 — button.tsx

공식 registry(`ui.shadcn.com/r/styles/new-york-v4/button.json`)에서 배포되는 **실제 소스**이다:

```tsx
import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { Slot } from "radix-ui"

import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex shrink-0 items-center justify-center gap-2 rounded-md text-sm font-medium whitespace-nowrap transition-all outline-none focus-visible:border-ring focus-visible:ring-[3px] focus-visible:ring-ring/50 disabled:pointer-events-none disabled:opacity-50 aria-invalid:border-destructive aria-invalid:ring-destructive/20 dark:aria-invalid:ring-destructive/40 [&_svg]:pointer-events-none [&_svg]:shrink-0 [&_svg:not([class*='size-'])]:size-4",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive:
          "bg-destructive text-white hover:bg-destructive/90 focus-visible:ring-destructive/20 dark:bg-destructive/60 dark:focus-visible:ring-destructive/40",
        outline:
          "border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground dark:border-input dark:bg-input/30 dark:hover:bg-input/50",
        secondary:
          "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost:
          "hover:bg-accent hover:text-accent-foreground dark:hover:bg-accent/50",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2 has-[>svg]:px-3",
        xs: "h-6 gap-1 rounded-md px-2 text-xs has-[>svg]:px-1.5 [&_svg:not([class*='size-'])]:size-3",
        sm: "h-8 gap-1.5 rounded-md px-3 has-[>svg]:px-2.5",
        lg: "h-10 rounded-md px-6 has-[>svg]:px-4",
        icon: "size-9",
        "icon-xs": "size-6 rounded-md [&_svg:not([class*='size-'])]:size-3",
        "icon-sm": "size-8",
        "icon-lg": "size-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

function Button({
  className,
  variant = "default",
  size = "default",
  asChild = false,
  ...props
}: React.ComponentProps<"button"> &
  VariantProps<typeof buttonVariants> & {
    asChild?: boolean
  }) {
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

export { Button, buttonVariants }
```

**토큰 소비 관점에서 읽기:**

| variant | 소비하는 토큰 | 패턴 |
|---------|--------------|------|
| `default` | `primary`, `primary-foreground` | `bg-{X} text-{X}-foreground` — 쌍 구조의 정석 |
| `destructive` | `destructive` (+ `text-white` 하드코딩) | `--destructive-foreground` 토큰이 없으므로 흰색을 직접 지정 |
| `outline` | `background`, `accent`, `accent-foreground`, `input` | hover 시 accent 쌍으로 전환. dark에서는 `input` 토큰을 반투명(`bg-input/30`)으로 사용 |
| `secondary` | `secondary`, `secondary-foreground` | 쌍 구조 |
| `ghost` | `accent`, `accent-foreground` | 배경 없이 시작, hover 시 accent 쌍 |
| `link` | `primary` | 텍스트 색만 소비 |

주목할 점:

1. **톆큰 참조가 클래스 문자열에 분산되어 있다.** "Button이 어떤 토큰을 쓰는가"를 알려면 CVA 정의의 문자열을 읽어야 한다. 토큰 의존성을 기계적으로 추출하려면 문자열 파싱이 필요하다.
2. **opacity modifier가 토큰과 결합한다.** `hover:bg-primary/90`, `dark:bg-input/30`처럼 토큰 색에 투명도를 입히는 것이 hover/dark 상태 표현의 기본 문법이다. 별도의 `--primary-hover` 상태 토큰이 존재하지 않는다. **상태 토큰 부재**는 shadcn/ui 토큰 체계의 중요한 특징이다 — 상태 변형이 토큰이 아니라 유틸리티 조합으로 해결된다.
3. **`focus-visible:ring-ring/50`** — focus ring 색이 `--ring` 토큰에서 나온다. 접근성 상태까지 토큰화되어 있다.
4. **`data-variant` / `data-size` 속성** — 토큰은 아니지만, 외부에서 컴포넌트 상태를 CSS 셀렉터로 타겟팅할 수 있는 훅을 제공한다.

### 2.3 실제 컴포넌트 코드 — card.tsx

Card는 CVA 대신 **composition + CSS 변수 지역화** 패턴으로 토큰을 소비한다:

```tsx
function Card({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card"
      className={cn(
        "group/card flex flex-col gap-(--card-spacing) overflow-hidden rounded-xl bg-card py-(--card-spacing) text-sm text-card-foreground ring-1 ring-foreground/10 [--card-spacing:--spacing(4)] has-data-[slot=card-footer]:pb-0 has-[>img:first-child]:pt-0 data-[size=sm]:[--card-spacing:--spacing(3)] data-[size=sm]:has-data-[slot=card-footer]:pb-0 *:[img:first-child]:rounded-t-xl *:[img:last-child]:rounded-b-xl",
        className
      )}
      {...props}
    />
  )
}

function CardContent({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-content"
      className={cn("px-(--card-spacing)", className)}
      {...props}
    />
  )
}

function CardFooter({ className, ...props }: React.ComponentProps<"div">) {
  return (
    <div
      data-slot="card-footer"
      className={cn(
        "flex items-center rounded-b-xl border-t bg-muted/50 p-(--card-spacing)",
        className
      )}
      {...props}
    />
  )
}
```

**토큰 소비 관점에서 읽기:**

1. **`bg-card text-card-foreground`** — card/foreground 쌍을 그대로 소비.
2. **`ring-foreground/10`** — `--foreground` 토큰을 10% 투명도로 ring에 재활용. foreground 토큰이 텍스트 외에 border/ring 용도로도 쓰이는 유연한 소비 사례다.
3. **`bg-muted/50`** (CardFooter) — `--muted` 토큰을 반투명으로 소비해 시각적 계층을 만든다.
4. **`[--card-spacing:--spacing(4)]`** — 컴포넌트 **지역 CSS 변수**를 정의하고 `gap-(--card-spacing)`, `px-(--card-spacing)`으로 소비한다. 전역 토큰은 아니지만, 컴포넌트 내부 스페이싱을 하나의 변수로 통일한 "컴포넌트 토큰"의 경량 버전으로 볼 수 있다. `data-[size=sm]`이 이 지역 변수 값만 바꾸면 모든 자식의 간격이 함께 변한다.

### 2.4 cn() 유틸리티 — clsx + tailwind-merge

모든 컴포넌트의 className 병합은 `cn()`을 통과한다. registry의 `lib/utils.ts` 실제 소스:

```ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

**토큰 소비와의 관계:**

1. **`clsx`**: 조건부 클래스 병합. `cn(isActive && "bg-accent", className)`처럼 불리언/객체/배열을 받아 클래스 문자열로 정규화한다.
2. **`tailwind-merge`**: **같은 CSS 속성을 건드리는 Tailwind 클래스 간 충돌을 해결**한다. `cn("bg-primary", "bg-destructive")` → `"bg-destructive"` (뒤가 이김). `cn("px-4", "px-2")` → `"px-2"`.
3. 이것이 토큰 소비에 미치는 영향: 컴포넌트의 기본 토큰 소비(`bg-primary`)가 **사용자가 전달한 className으로 안전하게 오버라이드**된다. `<Button className="bg-chart-2">`를 전달하면 tailwind-merge가 `bg-primary`를 제거하고 `bg-chart-2`를 남긴다. 즉 **인스턴스 레벨 토큰 오버라이드가 className prop 하나로 구현**되어 있다.
4. 한계: tailwind-merge는 **클래스 문자열 레벨**에서만 동작한다. `--primary` 변수 자체를 바꾸는 것이 아니라 해당 인스턴스의 클래스를 교체하는 방식이므로, "이 앱의 모든 primary를 바꾸는" 전역 변경에는 적합하지 않다 (그것은 globals.css 수정의 영역).

### 2.5 다크모드 — `.dark` 클래스 토글과 변수 재정의

다크모드는 **동일한 변수명을 `.dark` 셀렉터에서 다른 값으로 재정의**하는 방식이다:

```css
:root {
  --background: oklch(1 0 0);        /* 흰색 */
  --foreground: oklch(0.145 0 0);    /* 거의 검은색 */
  --primary: oklch(0.205 0 0);       /* 어두운 색 */
  --primary-foreground: oklch(0.985 0 0);
}

.dark {
  --background: oklch(0.145 0 0);    /* light의 foreground 값과 동일 */
  --foreground: oklch(0.985 0 0);    /* light의 background 값과 동일 */
  --primary: oklch(0.922 0 0);       /* 반전: 밝은 색이 primary가 됨 */
  --primary-foreground: oklch(0.205 0 0);
}
```

**토글 메커니즘:**

```css
@custom-variant dark (&:is(.dark *));
```

이 한 줄이 Tailwind의 `dark:` variant를 "`.dark` 클래스의 자손"으로 재정의한다. 이후 `<html class="dark">`를 토글하면:

1. `.dark` 셀렉터의 변수 재정의가 cascade로 모든 요소에 적용 → `bg-background` 등이 런타임에 즉시 변색
2. `dark:bg-input/30`처럼 `dark:` 접두 클래스가 붙은 유틸리티가 활성화

실제 토글은 보통 `next-themes` 라이브러리가 담당한다. **re-render 없이 CSS cascade만으로 전환**되며, 이는 JS 테마 객체를 재생성하는 MUI/Fluent 방식과 대비된다.

**dark 모드 값에서 읽히는 설계 규칙:**

- light/dark 값 사이에 **공식화된 파생 규칙은 없다.** `--background`의 dark 값이 light `--foreground` 값과 같은 것은 우연이 아니라 의도된 반전이지만, 이것이 코드나 문서에 규칙으로 명시되어 있지는 않다. 사용자가 dark 값을 임의로 바꿔도 아무도 막지 않는다.
- `--border`/`--input`은 dark에서 고정 회색이 아니라 **흰색 + alpha**(`oklch(1 0 0 / 10%)`)로 정의된다. 어떤 배경 위에서도 자연스럽게 겹치는 semi-transparent border 전략이다.
- `--radius`는 `.dark`에서 재정의되지 않는다 — 형태 토큰은 테마와 무관하다.

### 2.6 런타임 테마 변경 API의 부재 — 제약 분석

shadcn/ui에는 `ThemeProvider`의 `theme` prop, `createTheme()`, `ConfigProvider` 같은 **런타임 테마 변경 API가 존재하지 않는다.** 있는 것은:

| 가능한 것 | 불가능한 것 |
|-----------|-------------|
| `.dark` 클래스 토글 (light ↔ dark) | JS에서 토큰 값을 읽고 쓰는 API |
| CSS로 `.dark` 변수 재정의 | "blue 테마" "compact 테마" 같은 복수 테마의 런타임 전환 (CSS를 직접 추가하면 가능하지만 API는 없음) |
| `className`으로 인스턴스별 토큰 오버라이드 | 타입 안전한 토큰 참조 (토큰명이 문자열이라 오타를 컴파일러가 잡지 못함) |
| DOM에서 `getComputedStyle`으로 변수 읽기 | 토큰 변경 시 컴포넌트가 반응하는 구독 메커니즘 |

**제약의 실제 의미:**

1. **테마 = CSS 파일.** 새 테마를 만들려면 CSS 변수 묶음을 직접 작성해야 한다. 테마가 코드가 아니라 선언이기 때문에, 테마 간 전환도 CSS 클래스 추가/제거로만 가능하다.
2. **타입 안전성 부재.** `bg-primayr` 같은 오타는 빌드를 통과하고, 해당 클래스는 단순히 적용되지 않는다. Tier 1 시스템의 TS 토큰 타입(MUI의 `theme.palette.primary.main` 자동완성)과 대비되는 지점이다.
3. **토큰 검증 도구 없음.** 대비 부족, 미정의 토큰 참조, light/dark 불일치를 검사하는 공식 lint가 없다.

### 2.7 사용자 커스터마이징 — globals.css 직접 편집

토큰을 바꾸는 공식 경로는 **`globals.css`를 직접 편집**하는 것이다:

```css
:root {
  --primary: oklch(0.6 0.2 250);  /* 브랜드 파랑으로 교체 */
}
.dark {
  --primary: oklch(0.7 0.18 250);
}
```

한 줄 수정이 `bg-primary`를 소비하는 **모든 컴포넌트에 전역 반영**된다. 컴포넌트 코드를 한 줄도 건드리지 않고 브랜드 컬러를 입힐 수 있는 것이 이 모델의 핵심 가치다.

**새 토큰 추가도 같은 방식이다** (공식 문서 예시):

```css
:root {
  --warning: oklch(0.84 0.16 84);
  --warning-foreground: oklch(0.28 0.07 46);
}
.dark {
  --warning: oklch(0.41 0.11 46);
  --warning-foreground: oklch(0.99 0.02 95);
}
@theme inline {
  --color-warning: var(--warning);
  --color-warning-foreground: var(--warning-foreground);
}
```

이후 `<div className="bg-warning text-warning-foreground" />`처럼 사용한다. **토큰 추가가 3개 블록(`:root`, `.dark`, `@theme inline`) 편집으로 완료**되며, 빌드 설정이나 코드 생성이 전혀 필요 없다.

**함의:**

| 장점 | 단점 |
|------|------|
| 진입 장벽이 극도로 낮음 — CSS만 알면 됨 | 토큰 변경이 git diff에 남을 뿐, 리뷰/승인 프로세스가 없음 |
| 컴포넌트 코드와 토큰이 완전히 분리 | 토큰명 변경 시 전역 검색/치환 필요 (alias/비추천 메커니즘 없음) |
| 빌드 파이프라인 제로 | 토큰이 "문서"되지 않음 — 각 토큰의 용도 설명이 코드에 존재하지 않음 |

---

## 축 3: 토큰 거버넌스 (Governance)

### 3.1 npm 패키지가 아니다 — 토큰의 소유권 구조

shadcn/ui의 토큰은 **npm으로 배포되지 않는다.** `node_modules`에 shadcn/ui 토큰 파일이 존재하지 않는다. 대신:

```
shadcn/ui 저장소 (upstream)
    │  apps/www/registry/.../globals.css  ← "기본 스캐폴드"일 뿐
    │
    │  pnpm dlx shadcn@latest init
    ▼
사용자 프로젝트의 globals.css  ← "권위 있는 복사본"이 됨
    │
    │  이후 모든 변경은 사용자가 직접
    ▼
프로젝트별 토큰 (upstream과 독립적으로 진화)
```

`init`은 토큰 스캐폴드를 **복사**해 줄 뿐, 이후 사용자 프로젝트의 토큰과 upstream은 **완전히 분리**된다. 이는 MUI(`@mui/material/styles`), Chakra(`@chakra-ui/react` theme), Ant Design(less/cssinjs 토큰)처럼 토큰이 패키지에 들어있고 버전이 매겨지는 모델과 근본적으로 다르다.

**이 구조의 거버넌스적 의미:**

- 토큰의 **소유자는 shadcn(조직)이 아니라 각 프로젝트의 개발자**다.
- upstream이 토큰 값을 바꿔도 사용자 프로젝트에는 아무 영향이 없다 (opt-in 하지 않는 한).
- 반대로 사용자 프로젝트의 토큰 커스터마이징을 upstream이 알 방법도, 지원할 의무도 없다.

### 3.2 토큰 버전 관리의 부재

**토큰에는 시맨틱 버저닝이 적용되지 않는다.**

| 전통적 시스템 | shadcn/ui |
|---------------|-----------|
| 토큰 변경이 패키지 버전에 반영됨 (v5.1 → v6.0) | 토큰 스캐폴드는 저장소 커밋으로만 추적 |
| Breaking change가 CHANGELOG/migration guide로 안내 | 토큰 이름 변경 시 공식 마이그레이션 경로 없음 |
| deprecated 토큰에 alias 제공 | alias 메커니즘 없음 — 이름이 바뀌면 구버전 컴포넌트는 새 토큰을 참조하지 못해 스타일이 깨짐 |
| 하위 호환 기간 유지 | 호환성 개념 자체가 없음 |

**업데이트는 어떻게 처리되는가:**

1. **컴포넌트 코드**: `shadcn add button --overwrite` 또는 `--diff`로 upstream 변경을 수동 반영. 하지만 이것은 **컴포넌트 TSX 코드**의 업데이트이지 토큰의 업데이트가 아니다.
2. **토큰**: 사용자가 upstream의 새 globals.css를 직접 diff해서 수동 머지해야 한다. 공식 토큰 마이그레이션 도구는 없다.
3. **`migrate` 명령어**: 아이콘 교체, RTL, Radix 패키지 통합 같은 **코드 레벨** 일괄 변환을 제공하지만 토큰 값 변환은 다루지 않는다.

실제로 v3(HSL) → v4(oklch) 전환 당시, 기존 사용자의 HSL 토큰을 oklch로 자동 변환해 주는 공식 도구는 없었고, 사용자는 새 스캐폴드를 참고해 직접 값을 옮겼다.

### 3.3 Registry 시스템 — 토큰 변경의 전파 메커니즘

shadcn/ui의 배포 단위인 **registry**는 컴포넌트 코드와 메타데이터를 JSON으로 서빙한다. 실제 registry item의 구조:

```json
{
  "$schema": "https://ui.shadcn.com/schema/registry-item.json",
  "name": "button",
  "dependencies": ["radix-ui"],
  "files": [
    {
      "path": "registry/new-york-v4/ui/button.tsx",
      "content": "import * as React from \"react\"\nimport { cva ... }",
      "type": "registry:ui"
    }
  ],
  "type": "registry:ui"
}
```

**토큰과 registry의 관계:**

1. **registry item은 토큰을 포함하지 않는다.** 위 button.json에는 `button.tsx` 코드만 있고, `--primary` 값은 들어있지 않다. 컴포넌트는 토큰을 **이름으로만 참조**(`bg-primary`)하므로, 토큰 값이 무엇이든 컴포넌트 코드는 변하지 않는다.
2. **톆큰 변경이 전파되는 경로**: registry가 토큰을 나르지 않으므로, upstream의 토큰 변경이 사용자에게 전파되는 **자동 경로가 없다.** 사용자가 `init` 시점에 받은 스캐폴드가 그 프로젝트의 토큰 최종 상태가 된다.
3. **registry는 확장 가능하다.** `components.json`의 `registries` 필드로 서드파티/프라이빗 registry를 연결할 수 있다:

```json
{
  "registries": {
    "@shadcn": "https://ui.shadcn.com/r/{name}.json",
    "@acme": "https://registry.acme.com/{name}.json",
    "@private": {
      "url": "https://api.company.com/registry/{name}.json",
      "headers": { "Authorization": "Bearer ${REGISTRY_TOKEN}" }
    }
  }
}
```

이것은 **컴포넌트** 배포의 확장이지 토큰 배포의 확장은 아니다. 다만 registry가 `registry:theme` / config 타입의 파일을 나르도록 구성하면 토큰 스캐폴드도 배포 가능해진다 — 즉 토큰 전파를 원하면 **사용자가 직접 registry를 설계**해야 한다.

4. **`components.json`의 불변 설정**: `style`, `tailwind.baseColor`, `tailwind.cssVariables`는 init 이후 변경 불가하다. 바꾸려면 컴포넌트를 삭제하고 재설치해야 한다. 이는 토큰 체계의 근간(base color, CSS 변수 사용 여부)이 프로젝트 생명주기 동안 고정됨을 의미한다.

### 3.4 커뮤니티 Figma 키트의 토큰 복제 방식

공식 Figma 라이브러리가 없으므로, 커뮤니티 키트들이 `globals.css`의 토큰을 **수동으로 복제**한다:

| 키트 | 토큰 복제 방식 (일반적) |
|------|------------------------|
| Pietro Schirano kit | 코드 구현과 1:1 매칭 표방 — CSS 변수값을 Figma color styles/variables에 수동 입력 |
| Sitsiilia Bergmann kit | 정기 유지보수 — upstream 토큰 변경 시 수동 추적 |
| Matt Wierzbicki (shadcndesign.com) | 8가지 스타일 통합 — 각 스타일별 토큰 세트를 Figma variables로 수동 구성 |
| tweakcn 연동 키트 | 테마 생성기 출력값을 Figma에 반영하는 반자동 워크플로우 시도 |

**구조적 문제:**

1. **동기화 보장이 없다.** upstream이 `--primary` 값을 바꾸면 모든 커뮤니티 키트가 각자 수동으로 따라가야 하며, 시차와 누락이 불가피하다.
2. **검증 수단이 없다.** 어떤 키트가 현재 upstream 토큰과 일치하는지 확인할 공식 방법이 없다.
3. **복제의 방향이 단방향이다.** Figma → Code 방향의 토큰 파이프라인(Style Dictionary, Tokens Studio 등)이 없으므로, 디자이너가 Figma에서 토큰을 조정해도 그것이 코드로 흘러가지 않는다.

### 3.5 "정상적인" 토큰 파이프라인과의 대비

Tier 1 시스템이 구축하는 토큰 파이프라인과 shadcn/ui의 실제 구조를 나란히 놓으면:

```
[정상적 파이프라인 — Spectrum/Carbon/Material]

Figma Variables (디자이너 편집)
    │  Tokens Studio / 자체 플러그인
    ▼
JSON 토큰 파일 (W3C Design Tokens 포맷)
    │  Style Dictionary 빌드
    ▼
다중 포맷 출력 (CSS / TS / SCSS / iOS / Android)
    │  스키마 검증 + diff + 버전 관리
    ▼
npm 패키지로 배포 (semver, changelog, deprecation)
    │
    ▼
컴포넌트가 패키지의 토큰을 소비


[shadcn/ui의 실제 구조]

globals.css (개발자가 직접 편집)  ← Figma 연결 없음, JSON 없음, 빌드 없음
    │  @theme inline (수동 alias)
    ▼
Tailwind 유틸리티
    │
    ▼
복사된 컴포넌트 코드가 클래스 문자열로 소비  ← 버전 없음, 검증 없음
```

| 거버넌스 항목 | 정상적 파이프라인 | shadcn/ui |
|---------------|-------------------|-----------|
| Source of Truth | Figma 또는 중앙 토큰 저장소 | 사용자의 globals.css |
| 변환 파이프라인 | Style Dictionary 등 자동 빌드 | 없음 (CSS가 곧 최종 산출물) |
| 다중 포맷 출력 | CSS/TS/SCSS/플랫폼별 | CSS 단일 포맷 |
| 스키마 검증 | JSON Schema, TS 타입 | 없음 |
| 버전 관리 | semver + changelog | 없음 (git 커밋만) |
| 비추천 처리 | deprecated alias + codemod | 없음 |
| 토큰 문서 | 자동 생성 레퍼런스 | 문서 페이지의 수동 표 |
| Figma 동기화 | Tokens Studio / Variables API | 없음 (커뮤니티 수동 복제) |
| 변경 전파 | 패키지 업데이트 (자동) | 없음 (수동 머지) |

### 3.6 거버넌스 부재는 실패인가, 선택인가

이 모든 "없음"은 shadcn/ui의 핵심 철학 — **"컴포넌트를 설치하는 것이 아니라 복사하여 소유한다"** — 와 일관된다.

**선택의 논리:**

1. 토큰을 패키지로 만들면 **토큰의 소유권이 사용자에게서 다시 라이브러리 조직으로 넘어간다.** shadcn/ui는 그것을 의도적으로 거부한다.
2. 토큰 버전 관리는 **업데이트를 강제하는 메커니즘**이다. shadcn/ui는 업데이트를 opt-in으로 유지함으로써 사용자가 자신의 디자인 시스템을 완전히 통제하게 한다.
3. 거버넌스 파이프라인의 부재는 **의존성의 부재**이기도 하다. Style Dictionary도, Tokens Studio도, Figma 라이선스도 필요 없다. 유지보수할 인프라가 없으므로 깨질 인프라도 없다.

**대가는 명확하다:**

- 대규모 조직에서 디자인 일관성을 코드 리뷰만으로 유지해야 함
- 디자이너가 토큰을 소유할 수 있는 공식 경로가 없음 (CSS를 편집할 수 있는 디자이너만 참여 가능)
- 토큰 drift를 감지할 자동화가 없음
- Figma↔Code 매핑 충실도가 구조적으로 낮을 수밖에 없음

---

## 종합: 프레임워크 3축 요약

| 축 | shadcn/ui의 답변 |
|----|------------------|
| **정의** | ~32개 semantic CSS custom properties, primitive 계층 없음, oklch 색상 공간, foreground/background 쌍 구조, `@theme inline`으로 Tailwind 유틸리티에 연결, radius만 단일 소스에서 파생 |
| **소비** | Tailwind 유틸리티 클래스 문자열로 소비 (CVA variant 내부), `cn()`(clsx + tailwind-merge)으로 인스턴스 오버라이드, `.dark` 클래스 토글로 런타임 테마 전환, 상태 토큰 부재 (opacity modifier로 대체), 런타임 테마 API 없음 |
| **거버넌스** | npm 패키지 없음, 버전 관리 없음, 토큰은 사용자 globals.css에 존재, registry는 컴포넌트만 전파하고 토큰은 전파하지 않음, Figma 동기화 없음 (커뮤니티 수동 복제), 모든 거버넌스 메커니즘의 부재는 "소유권 이전" 철학의 일관된 결과 |

### 벤치마크적 시사점

shadcn/ui는 **"토큰 시스템의 최소 viable 형태"**를 보여준다. 32개의 semantic 토큰, 1개의 CSS 파일, 0개의 빌드 단계로 수만 개의 프로젝트가 일관된 테마를 운용한다. 이는 토큰 아키텍처가 반드시 다층 파이프라인을 요구하지 않는다는 증거이자, 동시에 그 단순함이 **규모와 협업(특히 디자인-개발 협업)의 한계**로 직결된다는 증거이기도 하다.

Figma↔Code 매핑 충실도라는 본 벤치마크의 중심 질문에서, shadcn/ui의 토큰 시스템은 **"Code 쪽 원본은 완벽하게 단순하지만, Figma 쪽 원본이 존재하지 않는"** 극단적 사례다. 매핑의 한쪽 끝이 비어 있는 이 시스템은, 역으로 다른 시스템들이 Figma↔Code 동기화에 들이는 비용이 무엇을 위한 것인지 묻는 기준점이 된다.
