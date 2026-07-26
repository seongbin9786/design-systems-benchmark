# shadcn/ui 컴포넌트 레벨 토큰 의존성 감사 (Audit)

> **감사 대상**: shadcn/ui 공식 레지스트리(`ui.shadcn.com/r/styles/new-york/`)에서 가져온 실제 소스 코드
> **감사 날짜**: 2026-07-26
> **스타일 변형**: new-york
> **분류 기준**:
> - **Token-based**: CSS variable에 매핑되는 클래스 (`bg-primary`, `text-muted-foreground`, `border-input`, `ring-ring` 등)
> - **Hardcoded**: Tailwind 고정 스케일 값 (`h-9`, `px-4`, `text-sm`, `rounded-md`, `shadow-sm` 등)
> - **Structural**: 레이아웃/동작 클래스 (`inline-flex`, `items-center`, `w-full`, `transition-colors` 등)

---

## 1. 종합 요약 테이블

| Component | 총 클래스 수 | Token-based | Hardcoded | Structural | Token 의존율 | CVA variants | Override |
|-----------|:-----------:|:-----------:|:---------:|:----------:|:-----------:|:------------:|:--------:|
| **Button** | 52 | 17 | 25 | 10 | 32.7% | variant(6), size(4) | `cn()` + className |
| **Input** | 24 | 4 | 13 | 7 | 16.7% | 없음 | `cn()` + className |
| **Card** | 20 | 3 | 12 | 5 | 15.0% | 없음 | `cn()` + className |
| **Dialog** | 65 | 6 | 41 | 18 | 9.2% | 없음 | `cn()` + className |
| **Checkbox** | 22 | 4 | 8 | 10 | 18.2% | 없음 | `cn()` + className |
| **Badge** | 28 | 11 | 12 | 5 | 39.3% | variant(4) | `cn()` + className |
| **Alert** | 25 | 7 | 14 | 4 | 28.0% | variant(2) | `cn()` + className |
| **Tabs** | 34 | 8 | 15 | 11 | 23.5% | 없음 | `cn()` + className |
| **Table** | 31 | 5 | 12 | 14 | 16.1% | 없음 | `cn()` + className |
| **Select** | 100 | 9 | 53 | 38 | 9.0% | 없음 (position prop) | `cn()` + className |
| **합계** | **401** | **74** | **205** | **122** | **18.5%** | — | — |

> **Token 의존율** = Token-based / 총 클래스 수
> Structural 제외 시 Token/(Token+Hardcoded) = 74/279 = **26.5%**

### 핵심 발견

1. **전체 토큰 의존율 18.5%** — shadcn/ui는 디자인 결정의 대부분을 Tailwind의 고정 스케일(hardcoded)에 위임하고, CSS variable(token)은 색상/시맨틱 레이어에만 사용한다.
2. **Badge가 가장 높은 토큰 의존율(39.3%)** — 변형(variant)이 모두 색상 토큰으로 구성되기 때문.
3. **Dialog, Select가 가장 낮은 토큰 의존율(9%)** — 레이아웃, 애니메이션, 포지셔닝 등 structural/hardcoded 클래스가 압도적으로 많음.
4. **CVA를 사용하는 컴포넌트는 3개뿐** (Button, Badge, Alert) — 나머지는 단일 스타일 + className override.
5. **모든 컴포넌트가 `cn()` (clsx + tailwind-merge) 기반 className override** 를 지원 — 이것이 shadcn/ui의 핵심 커스터마이징 메커니즘.

---

## 2. 컴포넌트별 상세 분석

### 2.1 Button (`button.tsx`)

**아키텍처**: CVA 기반, 2개 variant 축 (variant × size)

#### CVA Base 클래스 (17개)

```
inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md
text-sm font-medium transition-colors focus-visible:outline-none
focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none
disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0
```

| 분류 | 클래스 | 수 |
|------|--------|:--:|
| Token | `focus-visible:ring-ring` | 1 |
| Hardcoded | `gap-2`, `rounded-md`, `text-sm`, `font-medium`, `focus-visible:ring-1`, `disabled:opacity-50`, `[&_svg]:size-4` | 7 |
| Structural | `inline-flex`, `items-center`, `justify-center`, `whitespace-nowrap`, `transition-colors`, `focus-visible:outline-none`, `disabled:pointer-events-none`, `[&_svg]:pointer-events-none`, `[&_svg]:shrink-0` | 9 |

#### variant 축 (6개 값)

| variant | Token-based | Hardcoded | Structural |
|---------|-------------|-----------|------------|
| `default` | `bg-primary`, `text-primary-foreground`, `hover:bg-primary/90` | `shadow` | — |
| `destructive` | `bg-destructive`, `text-destructive-foreground`, `hover:bg-destructive/90` | `shadow-sm` | — |
| `outline` | `border-input`, `bg-background`, `hover:bg-accent`, `hover:text-accent-foreground` | `shadow-sm` | `border` |
| `secondary` | `bg-secondary`, `text-secondary-foreground`, `hover:bg-secondary/80` | `shadow-sm` | — |
| `ghost` | `hover:bg-accent`, `hover:text-accent-foreground` | — | — |
| `link` | `text-primary` | `underline-offset-4`, `hover:underline` | — |

#### size 축 (4개 값)

| size | 클래스 (전부 Hardcoded) |
|------|------------------------|
| `default` | `h-9`, `px-4`, `py-2` |
| `sm` | `h-8`, `rounded-md`, `px-3`, `text-xs` |
| `lg` | `h-10`, `rounded-md`, `px-8` |
| `icon` | `h-9`, `w-9` |

**소계**: Token 17 / Hardcoded 25 / Structural 10 = **52개**

---

### 2.2 Input (`input.tsx`)

**아키텍처**: 단일 클래스 문자열, CVA 없음

```
flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1
text-base shadow-sm transition-colors file:border-0 file:bg-transparent
file:text-sm file:font-medium file:text-foreground
placeholder:text-muted-foreground focus-visible:outline-none
focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed
disabled:opacity-50 md:text-sm
```

| 분류 | 클래스 | 수 |
|------|--------|:--:|
| Token | `border-input`, `file:text-foreground`, `placeholder:text-muted-foreground`, `focus-visible:ring-ring` | 4 |
| Hardcoded | `h-9`, `rounded-md`, `bg-transparent`, `px-3`, `py-1`, `text-base`, `shadow-sm`, `file:bg-transparent`, `file:text-sm`, `file:font-medium`, `focus-visible:ring-1`, `disabled:opacity-50`, `md:text-sm` | 13 |
| Structural | `flex`, `w-full`, `border`, `transition-colors`, `file:border-0`, `focus-visible:outline-none`, `disabled:cursor-not-allowed` | 7 |

**소계**: Token 4 / Hardcoded 13 / Structural 7 = **24개**

---

### 2.3 Card (`card.tsx`)

**아키텍처**: 6개 서브 컴포넌트 (Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter), CVA 없음

| 서브 컴포넌트 | Token | Hardcoded | Structural |
|--------------|-------|-----------|------------|
| Card | `bg-card`, `text-card-foreground` | `rounded-xl`, `shadow` | `border` |
| CardHeader | — | `space-y-1.5`, `p-6` | `flex`, `flex-col` |
| CardTitle | — | `font-semibold`, `leading-none`, `tracking-tight` | — |
| CardDescription | `text-muted-foreground` | `text-sm` | — |
| CardContent | — | `p-6`, `pt-0` | — |
| CardFooter | — | `p-6`, `pt-0` | `flex`, `items-center` |

**소계**: Token 3 / Hardcoded 12 / Structural 5 = **20개**

---

### 2.4 Dialog (`dialog.tsx`)

**아키텍처**: 8개 서브 컴포넌트, Radix Dialog 기반, CVA 없음. 애니메이션 클래스가 대량 포함.

| 서브 컴포넌트 | Token | Hardcoded | Structural |
|--------------|-------|-----------|------------|
| DialogOverlay | — | `z-50`, `bg-black/80`, `animate-in`, `animate-out`, `fade-out-0`, `fade-in-0` | `fixed`, `inset-0` |
| DialogContent | `bg-background` | `left-[50%]`, `top-[50%]`, `z-50`, `max-w-lg`, `translate-x-[-50%]`, `translate-y-[-50%]`, `gap-4`, `p-6`, `shadow-lg`, `duration-200`, 8개 애니메이션, `sm:rounded-lg` | `fixed`, `grid`, `w-full`, `border` |
| Close 버튼 | `ring-offset-background`, `focus:ring-ring`, `data-[state=open]:bg-accent`, `data-[state=open]:text-muted-foreground` | `right-4`, `top-4`, `rounded-sm`, `opacity-70`, `hover:opacity-100`, `focus:ring-2`, `focus:ring-offset-2` | `absolute`, `transition-opacity`, `focus:outline-none`, `disabled:pointer-events-none` |
| X 아이콘 | — | `h-4`, `w-4` | — |
| DialogHeader | — | `space-y-1.5` | `flex`, `flex-col`, `text-center`, `sm:text-left` |
| DialogFooter | — | `sm:space-x-2` | `flex`, `flex-col-reverse`, `sm:flex-row`, `sm:justify-end` |
| DialogTitle | — | `text-lg`, `font-semibold`, `leading-none`, `tracking-tight` | — |
| DialogDescription | `text-muted-foreground` | `text-sm` | — |

**소계**: Token 6 / Hardcoded 41 / Structural 18 = **65개**

> **특이사항**: `bg-black/80` (overlay) — 토큰이 아닌 원시 색상(raw color) 사용. `overlay` 토큰이 존재하지 않음.

---

### 2.5 Checkbox (`checkbox.tsx`)

**아키텍처**: 단일 컴포넌트, Radix Checkbox 기반, CVA 없음

| 분류 | 클래스 | 수 |
|------|--------|:--:|
| Token | `border-primary`, `focus-visible:ring-ring`, `data-[state=checked]:bg-primary`, `data-[state=checked]:text-primary-foreground` | 4 |
| Hardcoded | `h-4`, `w-4`, `rounded-sm`, `shadow`, `focus-visible:ring-1`, `disabled:opacity-50`, `h-4`(icon), `w-4`(icon) | 8 |
| Structural | `grid`, `place-content-center`, `peer`, `shrink-0`, `border`, `focus-visible:outline-none`, `disabled:cursor-not-allowed`, `grid`(indicator), `place-content-center`(indicator), `text-current` | 10 |

**소계**: Token 4 / Hardcoded 8 / Structural 10 = **22개**

---

### 2.6 Badge (`badge.tsx`)

**아키텍처**: CVA 기반, 1개 variant 축

#### CVA Base 클래스 (13개)

| 분류 | 클래스 | 수 |
|------|--------|:--:|
| Token | `focus:ring-ring` | 1 |
| Hardcoded | `rounded-md`, `px-2.5`, `py-0.5`, `text-xs`, `font-semibold`, `focus:ring-2`, `focus:ring-offset-2` | 7 |
| Structural | `inline-flex`, `items-center`, `border`, `transition-colors`, `focus:outline-none` | 5 |

#### variant 축 (4개 값)

| variant | Token-based | Hardcoded |
|---------|-------------|-----------|
| `default` | `bg-primary`, `text-primary-foreground`, `hover:bg-primary/80` | `border-transparent`, `shadow` |
| `secondary` | `bg-secondary`, `text-secondary-foreground`, `hover:bg-secondary/80` | `border-transparent` |
| `destructive` | `bg-destructive`, `text-destructive-foreground`, `hover:bg-destructive/80` | `border-transparent`, `shadow` |
| `outline` | `text-foreground` | — |

**소계**: Token 11 / Hardcoded 12 / Structural 5 = **28개**

---

### 2.7 Alert (`alert.tsx`)

**아키텍처**: CVA 기반 (1개 variant 축) + 2개 서브 컴포넌트 (AlertTitle, AlertDescription)

#### CVA Base 클래스 (13개)

| 분류 | 클래스 | 수 |
|------|--------|:--:|
| Token | `[&>svg]:text-foreground` | 1 |
| Hardcoded | `rounded-lg`, `px-4`, `py-3`, `text-sm`, `[&>svg+div]:translate-y-[-3px]`, `[&>svg]:left-4`, `[&>svg]:top-4`, `[&>svg~*]:pl-7` | 8 |
| Structural | `relative`, `w-full`, `border`, `[&>svg]:absolute` | 4 |

#### variant 축 (2개 값)

| variant | Token-based |
|---------|-------------|
| `default` | `bg-background`, `text-foreground` |
| `destructive` | `border-destructive/50`, `text-destructive`, `dark:border-destructive`, `[&>svg]:text-destructive` |

#### 서브 컴포넌트

| 서브 컴포넌트 | Hardcoded |
|--------------|-----------|
| AlertTitle | `mb-1`, `font-medium`, `leading-none`, `tracking-tight` |
| AlertDescription | `text-sm`, `[&_p]:leading-relaxed` |

**소계**: Token 7 / Hardcoded 14 / Structural 4 = **25개**

---

### 2.8 Tabs (`tabs.tsx`)

**아키텍처**: 3개 서브 컴포넌트 (TabsList, TabsTrigger, TabsContent), Radix Tabs 기반, CVA 없음

| 서브 컴포넌트 | Token | Hardcoded | Structural |
|--------------|-------|-----------|------------|
| TabsList | `bg-muted`, `text-muted-foreground` | `h-9`, `rounded-lg`, `p-1` | `inline-flex`, `items-center`, `justify-center` |
| TabsTrigger | `ring-offset-background`, `focus-visible:ring-ring`, `data-[state=active]:bg-background`, `data-[state=active]:text-foreground` | `rounded-md`, `px-3`, `py-1`, `text-sm`, `font-medium`, `focus-visible:ring-2`, `focus-visible:ring-offset-2`, `disabled:opacity-50`, `data-[state=active]:shadow` | `inline-flex`, `items-center`, `justify-center`, `whitespace-nowrap`, `transition-all`, `focus-visible:outline-none`, `disabled:pointer-events-none` |
| TabsContent | `ring-offset-background`, `focus-visible:ring-ring` | `mt-2`, `focus-visible:ring-2`, `focus-visible:ring-offset-2` | `focus-visible:outline-none` |

**소계**: Token 8 / Hardcoded 15 / Structural 11 = **34개**

---

### 2.9 Table (`table.tsx`)

**아키텍처**: 8개 서브 컴포넌트, CVA 없음. Structural 클래스 비율이 가장 높음 (45.2%).

| 서브 컴포넌트 | Token | Hardcoded | Structural |
|--------------|-------|-----------|------------|
| Table (wrapper) | — | — | `relative`, `w-full`, `overflow-auto` |
| Table | — | `text-sm` | `w-full`, `caption-bottom` |
| TableHeader | — | — | `[&_tr]:border-b` |
| TableBody | — | — | `[&_tr:last-child]:border-0` |
| TableFooter | `bg-muted/50` | `font-medium` | `border-t`, `[&>tr]:last:border-b-0` |
| TableRow | `hover:bg-muted/50`, `data-[state=selected]:bg-muted` | — | `border-b`, `transition-colors` |
| TableHead | `text-muted-foreground` | `h-10`, `px-2`, `font-medium`, `[&:has([role=checkbox])]:pr-0`, `[&>[role=checkbox]]:translate-y-[2px]` | `text-left`, `align-middle` |
| TableCell | — | `p-2`, `[&:has([role=checkbox])]:pr-0`, `[&>[role=checkbox]]:translate-y-[2px]` | `align-middle` |
| TableCaption | `text-muted-foreground` | `mt-4`, `text-sm` | — |

**소계**: Token 5 / Hardcoded 12 / Structural 14 = **31개**

---

### 2.10 Select (`select.tsx`)

**아키텍처**: 10개 서브 컴포넌트, Radix Select 기반, CVA 없음. 가장 복잡한 컴포넌트 (100개 클래스).

| 서브 컴포넌트 | Token | Hardcoded | Structural |
|--------------|-------|-----------|------------|
| SelectTrigger | `border-input`, `ring-offset-background`, `data-[placeholder]:text-muted-foreground`, `focus:ring-ring` | `h-9`, `rounded-md`, `bg-transparent`, `px-3`, `py-2`, `text-sm`, `shadow-sm`, `focus:ring-1`, `disabled:opacity-50` | `flex`, `w-full`, `items-center`, `justify-between`, `whitespace-nowrap`, `border`, `focus:outline-none`, `disabled:cursor-not-allowed`, `[&>span]:line-clamp-1` |
| ChevronDown (trigger) | — | `h-4`, `w-4`, `opacity-50` | — |
| SelectScrollUpButton | — | `py-1` | `flex`, `cursor-default`, `items-center`, `justify-center` |
| ChevronUp | — | `h-4`, `w-4` | — |
| SelectScrollDownButton | — | `py-1` | `flex`, `cursor-default`, `items-center`, `justify-center` |
| ChevronDown | — | `h-4`, `w-4` | — |
| SelectContent | `bg-popover`, `text-popover-foreground` | `z-50`, `min-w-[8rem]`, `rounded-md`, `shadow-md`, 8개 애니메이션, 4개 popper translate | `relative`, `max-h-[--radix-...]`, `overflow-y-auto`, `overflow-x-hidden`, `border`, `origin-[--radix-...]` |
| Viewport | — | `p-1` | `h-[var(--radix-...)]`, `w-full`, `min-w-[var(--radix-...)]` |
| SelectLabel | — | `px-2`, `py-1.5`, `text-sm`, `font-semibold` | — |
| SelectItem | `focus:bg-accent`, `focus:text-accent-foreground` | `rounded-sm`, `py-1.5`, `pl-2`, `pr-8`, `text-sm`, `data-[disabled]:opacity-50` | `relative`, `flex`, `w-full`, `cursor-default`, `select-none`, `items-center`, `outline-none`, `data-[disabled]:pointer-events-none` |
| Indicator span | — | `right-2`, `h-3.5`, `w-3.5` | `absolute`, `flex`, `items-center`, `justify-center` |
| Check icon | — | `h-4`, `w-4` | — |
| SelectSeparator | `bg-muted` | `-mx-1`, `my-1`, `h-px` | — |

**소계**: Token 9 / Hardcoded 53 / Structural 38 = **100개**

---

## 3. View 1: Component → Token 매핑

각 컴포넌트가 참조하는 시맨틱 토큰(CSS variable) 목록.

### Button → 7개 토큰
| 토큰 | 사용 클래스 | 용도 |
|------|-----------|------|
| `--primary` | `bg-primary`, `hover:bg-primary/90`, `text-primary` | 배경, hover, link 텍스트 |
| `--primary-foreground` | `text-primary-foreground` | 기본 variant 텍스트 |
| `--destructive` | `bg-destructive`, `hover:bg-destructive/90` | 파괴적 variant |
| `--destructive-foreground` | `text-destructive-foreground` | 파괴적 variant 텍스트 |
| `--secondary` | `bg-secondary`, `hover:bg-secondary/80` | 보조 variant |
| `--secondary-foreground` | `text-secondary-foreground` | 보조 variant 텍스트 |
| `--accent` / `--accent-foreground` | `hover:bg-accent`, `hover:text-accent-foreground` | outline/ghost hover |
| `--background` | `bg-background` | outline variant 배경 |
| `--input` | `border-input` | outline variant 보더 |
| `--ring` | `focus-visible:ring-ring` | 포커스 링 |

### Input → 4개 토큰
| 토큰 | 사용 클래스 |
|------|-----------|
| `--input` | `border-input` |
| `--foreground` | `file:text-foreground` |
| `--muted-foreground` | `placeholder:text-muted-foreground` |
| `--ring` | `focus-visible:ring-ring` |

### Card → 3개 토큰
| 토큰 | 사용 클래스 |
|------|-----------|
| `--card` | `bg-card` |
| `--card-foreground` | `text-card-foreground` |
| `--muted-foreground` | `text-muted-foreground` |

### Dialog → 5개 토큰
| 토큰 | 사용 클래스 |
|------|-----------|
| `--background` | `bg-background`, `ring-offset-background` |
| `--ring` | `focus:ring-ring` |
| `--accent` | `data-[state=open]:bg-accent` |
| `--muted-foreground` | `data-[state=open]:text-muted-foreground`, `text-muted-foreground` |

### Checkbox → 3개 토큰
| 토큰 | 사용 클래스 |
|------|-----------|
| `--primary` | `border-primary`, `data-[state=checked]:bg-primary` |
| `--primary-foreground` | `data-[state=checked]:text-primary-foreground` |
| `--ring` | `focus-visible:ring-ring` |

### Badge → 6개 토큰
| 토큰 | 사용 클래스 |
|------|-----------|
| `--primary` | `bg-primary`, `hover:bg-primary/80` |
| `--primary-foreground` | `text-primary-foreground` |
| `--secondary` | `bg-secondary`, `hover:bg-secondary/80` |
| `--secondary-foreground` | `text-secondary-foreground` |
| `--destructive` / `--destructive-foreground` | `bg-destructive`, `text-destructive-foreground`, `hover:bg-destructive/80` |
| `--foreground` | `text-foreground` (outline variant) |
| `--ring` | `focus:ring-ring` |

### Alert → 4개 토큰
| 토큰 | 사용 클래스 |
|------|-----------|
| `--background` | `bg-background` |
| `--foreground` | `text-foreground`, `[&>svg]:text-foreground` |
| `--destructive` | `border-destructive/50`, `text-destructive`, `dark:border-destructive`, `[&>svg]:text-destructive` |

### Tabs → 5개 토큰
| 토큰 | 사용 클래스 |
|------|-----------|
| `--muted` | `bg-muted` |
| `--muted-foreground` | `text-muted-foreground` |
| `--background` | `data-[state=active]:bg-background`, `ring-offset-background` |
| `--foreground` | `data-[state=active]:text-foreground` |
| `--ring` | `focus-visible:ring-ring` |

### Table → 2개 토큰
| 토큰 | 사용 클래스 |
|------|-----------|
| `--muted` | `bg-muted/50`, `hover:bg-muted/50`, `data-[state=selected]:bg-muted` |
| `--muted-foreground` | `text-muted-foreground` (×2) |

### Select → 6개 토큰
| 토큰 | 사용 클래스 |
|------|-----------|
| `--input` | `border-input` |
| `--ring` | `focus:ring-ring` |
| `--background` | `ring-offset-background` |
| `--muted-foreground` | `data-[placeholder]:text-muted-foreground` |
| `--popover` / `--popover-foreground` | `bg-popover`, `text-popover-foreground` |
| `--accent` / `--accent-foreground` | `focus:bg-accent`, `focus:text-accent-foreground` |
| `--muted` | `bg-muted` (separator) |

---

## 4. View 2: Token → Component 매핑

각 시맨틱 토큰이 어떤 컴포넌트에서 사용되는지 역추적.

| 토큰 (CSS var) | 사용 컴포넌트 | 총 사용 횟수 | 주요 용도 |
|----------------|-------------|:-----------:|----------|
| `--primary` | Button, Badge, Checkbox | 7 | 배경색, 보더색, hover |
| `--primary-foreground` | Button, Badge, Checkbox | 3 | 텍스트색 |
| `--destructive` | Button, Badge, Alert | 7 | 배경, 보더, 텍스트 |
| `--destructive-foreground` | Button, Badge | 2 | 텍스트색 |
| `--secondary` | Button, Badge | 2 | 배경색 |
| `--secondary-foreground` | Button, Badge | 2 | 텍스트색 |
| `--accent` | Button, Dialog, Select | 4 | hover/focus/active 배경 |
| `--accent-foreground` | Button, Dialog, Select | 4 | hover/focus/active 텍스트 |
| `--background` | Button, Dialog, Alert, Tabs | 5 | 배경, ring-offset |
| `--foreground` | Input, Badge, Alert, Tabs | 5 | 텍스트, 아이콘 |
| `--muted` | Tabs, Table, Select | 5 | 배경 (list, row hover, separator) |
| `--muted-foreground` | Input, Card, Dialog, Tabs, Table, Select | 7 | 보조 텍스트 (placeholder, description, caption) |
| `--card` | Card | 1 | 카드 배경 |
| `--card-foreground` | Card | 1 | 카드 텍스트 |
| `--popover` | Select | 1 | 드롭다운 배경 |
| `--popover-foreground` | Select | 1 | 드롭다운 텍스트 |
| `--input` | Button, Input, Select | 3 | 보더색 |
| `--ring` | Button, Input, Checkbox, Badge, Dialog, Tabs, Select | 7 | 포커스 링 색상 |

### 토큰 사용 빈도 분석

```
--muted-foreground  ████████████████████████████████████  7회 (6개 컴포넌트)
--ring              ████████████████████████████████████  7회 (7개 컴포넌트)
--primary           ████████████████████████████████████  7회 (3개 컴포넌트)
--background        █████████████████████████████        5회 (4개 컴포넌트)
--foreground        █████████████████████████████        5회 (4개 컴포넌트)
--muted             █████████████████████████████        5회 (3개 컴포넌트)
--accent            ████████████████████                 4회 (3개 컴포넌트)
--accent-foreground ████████████████████                 4회 (3개 컴포넌트)
--destructive       ████████████████████████████████████  7회 (3개 컴포넌트)
--input             ███████████████                      3회 (3개 컴포넌트)
--primary-foreground███████████████                      3회 (3개 컴포넌트)
--destructive-fg    ██████████                           2회 (2개 컴포넌트)
--secondary         ██████████                           2회 (2개 컴포넌트)
--secondary-fg      ██████████                           2회 (2개 컴포넌트)
--card              █████                                1회 (1개 컴포넌트)
--card-foreground   █████                                1회 (1개 컴포넌트)
--popover           █████                                1회 (1개 컴포넌트)
--popover-fg        █████                                1회 (1개 컴포넌트)
```

### 토큰 계층별 분류

| 계층 | 토큰 | 특징 |
|------|------|------|
| **Core (7+ 컴포넌트)** | `--ring`, `--muted-foreground` | 거의 모든 인터랙티브 컴포넌트에서 사용 |
| **Wide (4-6 컴포넌트)** | `--primary`, `--destructive`, `--background`, `--foreground`, `--muted`, `--accent`, `--accent-foreground` | 핵심 시맨틱 색상 |
| **Narrow (2-3 컴포넌트)** | `--input`, `--primary-foreground`, `--destructive-foreground`, `--secondary`, `--secondary-foreground` | 특정 패턴에만 사용 |
| **Scoped (1 컴포넌트)** | `--card`, `--card-foreground`, `--popover`, `--popover-foreground` | 단일 컴포넌트 전용 |

---

## 5. Hardcoded 값 인벤토리

### 5.1 Spacing (간격)

| 값 | 사용 위치 | 빈도 |
|----|----------|:----:|
| `gap-2` | Button base | 1 |
| `gap-4` | Dialog content | 1 |
| `px-2` | Table head | 1 |
| `px-2.5` | Badge base | 1 |
| `px-3` | Button sm, Input, Select trigger | 3 |
| `px-4` | Button default, Alert base | 2 |
| `px-8` | Button lg | 1 |
| `py-0.5` | Badge base | 1 |
| `py-1` | Input, Tabs trigger, Select scroll buttons | 4 |
| `py-1.5` | Select label, Select item | 2 |
| `py-2` | Button default, Select trigger | 2 |
| `py-3` | Alert base | 1 |
| `p-1` | Tabs list, Select viewport | 2 |
| `p-2` | Table cell | 1 |
| `p-6` | Card header, Card content, Card footer, Dialog content | 4 |
| `pt-0` | Card content, Card footer | 2 |
| `pl-2` | Select item | 1 |
| `pl-7` | Alert base (svg sibling) | 1 |
| `pr-0` | Table head, Table cell (checkbox) | 2 |
| `pr-8` | Select item | 1 |
| `mt-2` | Tabs content | 1 |
| `mt-4` | Table caption | 1 |
| `mb-1` | Alert title | 1 |
| `-mx-1` | Select separator | 1 |
| `my-1` | Select separator | 1 |
| `space-y-1.5` | Card header, Dialog header | 2 |
| `sm:space-x-2` | Dialog footer | 1 |
| `right-2` | Select indicator | 1 |
| `right-4` | Dialog close | 1 |
| `top-4` | Dialog close, Alert svg | 2 |
| `left-4` | Alert svg | 1 |

> **총 31종, 46회** — spacing이 hardcoded 클래스 중 가장 큰 비중.

### 5.2 Sizing (크기)

| 값 | 사용 위치 | 빈도 |
|----|----------|:----:|
| `h-4` / `w-4` | Checkbox, Dialog close icon, Select icons (×4) | 8 |
| `h-3.5` / `w-3.5` | Select indicator span | 2 |
| `h-8` | Button sm | 1 |
| `h-9` | Button default/icon, Input, Tabs list, Select trigger | 4 |
| `h-10` | Button lg, Table head | 2 |
| `w-9` | Button icon | 1 |
| `size-4` | Button base (svg) | 1 |
| `h-px` | Select separator | 1 |
| `max-w-lg` | Dialog content | 1 |
| `min-w-[8rem]` | Select content | 1 |

> **총 10종, 22회** — `h-9`(36px)가 표준 인터랙티브 높이. `h-4/w-4`(16px)가 표준 아이콘 크기.

### 5.3 Typography (타이포그래피)

| 값 | 사용 위치 | 빈도 |
|----|----------|:----:|
| `text-xs` | Button sm, Badge base | 2 |
| `text-sm` | Button base, Input (md:), Card desc, Dialog desc, Alert (×2), Tabs trigger, Table (×2), Select (×3) | 11 |
| `text-base` | Input | 1 |
| `text-lg` | Dialog title | 1 |
| `font-medium` | Button base, Input file, Tabs trigger, Table footer/head, Alert title | 6 |
| `font-semibold` | Card title, Badge base, Dialog title, Select label | 4 |
| `leading-none` | Card title, Dialog title, Alert title | 3 |
| `leading-relaxed` | Alert description (p) | 1 |
| `tracking-tight` | Card title, Dialog title, Alert title | 3 |
| `underline-offset-4` | Button link | 1 |
| `hover:underline` | Button link | 1 |

> **총 11종, 34회** — `text-sm`(14px)이 지배적. `font-medium`/`font-semibold` 이진 구조.

### 5.4 Radius (둥근 모서리)

| 값 | 사용 위치 | 빈도 |
|----|----------|:----:|
| `rounded-sm` | Checkbox, Dialog close, Select item | 3 |
| `rounded-md` | Button (base/sm/lg), Badge, Tabs trigger, Select (trigger/content) | 7 |
| `rounded-lg` | Alert base, Tabs list, Dialog content (sm:) | 3 |
| `rounded-xl` | Card | 1 |

> **총 4종, 14회** — `rounded-md`(6px)가 표준. 컴포넌트 위계에 따라 sm→md→lg→xl 사용.

### 5.5 Shadow (그림자)

| 값 | 사용 위치 | 빈도 |
|----|----------|:----:|
| `shadow` | Button default, Badge default, Checkbox | 3 |
| `shadow-sm` | Button (destructive/outline/secondary), Input, Select trigger | 5 |
| `shadow-md` | Select content | 1 |
| `shadow-lg` | Dialog content | 1 |

> **총 4종, 10회** — elevation 위계: sm(입력) → default(버튼) → md(드롭다운) → lg(모달)

### 5.6 Opacity / Ring / Border (기타)

| 값 | 사용 위치 | 빈도 |
|----|----------|:----:|
| `opacity-50` | Select chevron, disabled 상태 (×5) | 6 |
| `opacity-70` | Dialog close | 1 |
| `hover:opacity-100` | Dialog close | 1 |
| `ring-1` | Button, Input, Select trigger | 3 |
| `ring-2` | Badge, Dialog close, Tabs (×2) | 4 |
| `ring-offset-2` | Badge, Dialog close, Tabs (×2) | 4 |
| `border` (width) | Button outline, Input, Card, Dialog, Checkbox, Badge, Alert, Select (×2) | 9 |
| `border-b` / `border-t` | Table | 3 |
| `border-transparent` | Badge (×3) | 3 |
| `bg-transparent` | Input, Select trigger | 2 |
| `bg-black/80` | Dialog overlay | 1 |
| `z-50` | Dialog (×2), Select content | 3 |

### 5.7 Animation (애니메이션)

| 값 | 사용 위치 | 빈도 |
|----|----------|:----:|
| `animate-in` / `animate-out` | Dialog, Select | 4 |
| `fade-in-0` / `fade-out-0` | Dialog, Select | 4 |
| `zoom-in-95` / `zoom-out-95` | Dialog, Select | 4 |
| `slide-in-from-*` / `slide-out-to-*` | Dialog (4), Select (4) | 8 |
| `duration-200` | Dialog content | 1 |

> **총 21회** — Dialog와 Select에만 집중. tailwindcss-animate 플러그인 의존.

---

## 6. Override 메커니즘 분석

### 6.1 `cn()` 패턴 (전 컴포넌트 공통)

모든 컴포넌트는 `cn()` 함수를 통해 className을 병합한다:

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

- **clsx**: 조건부 클래스 병합
- **tailwind-merge**: 충돌하는 Tailwind 클래스 자동 해결 (나중 값이 우선)

### 6.2 Override 적용 방식

| 패턴 | 컴포넌트 | 메커니즘 |
|------|---------|---------|
| `cn(baseClasses, className)` | Input, Card (전체), Dialog (전체), Checkbox, Tabs (전체), Table (전체), Select (전체) | className prop → tailwind-merge |
| `cn(cvaVariants({variant, size}), className)` | Button, Badge | CVA variant 선택 후 className merge |
| `cn(cvaVariants({variant}), className)` | Alert | CVA variant 선택 후 className merge |

### 6.3 Override의 구조적 한계

1. **Hardcoded 값은 className으로만 override 가능** — `h-9`를 바꾸려면 `className="h-11"` 전달
2. **Token 값은 CSS variable override 또는 className override** — `bg-primary`를 바꾸려면:
   - CSS: `--primary: new-value` (글로벌/스코프 변경)
   - className: `className="bg-blue-500"` (인스턴스 레벨)
3. **CVA variant는 폐쇄적** — 새로운 variant 추가는 소스 수정 필요
4. **서브 컴포넌트 개별 override** — Card, Dialog, Table, Select는 각 서브 컴포넌트에 독립 className 전달 가능

---

## 7. 구조적 관찰

### 7.1 shadcn/ui의 토큰 철학

shadcn/ui는 **"토큰은 색상만, 나머지는 Tailwind 스케일"** 이라는 명확한 분업을 가진다:

| 디자인 차원 | 결정 방식 | 변경 방법 |
|------------|----------|----------|
| 색상 (color) | CSS variable (token) | `globals.css`에서 variable 재정의 |
| 간격 (spacing) | Tailwind 고정 스케일 | className override 또는 tailwind.config 확장 |
| 크기 (sizing) | Tailwind 고정 스케일 | className override |
| 타이포그래피 | Tailwind 고정 스케일 | className override 또는 tailwind.config |
| 반경 (radius) | Tailwind 고정 스케일 | className override 또는 CSS variable (`--radius`) |
| 그림자 (shadow) | Tailwind 고정 스케일 | className override 또는 tailwind.config |
| 애니메이션 | tailwindcss-animate | className override |

### 7.2 Figma↔Code 매핑 관점에서의 시사점

1. **토큰 매핑 표면적이 작다** — 18개 시맨틱 토큰이 전체 색상 시스템을 구성. Figma Variables와 1:1 매핑이 상대적으로 용이.
2. **Hardcoded 값이 Figma의 "Auto Layout" 수치와 직접 대응** — `px-4` = Figma padding 16px, `gap-2` = Figma gap 8px. Tailwind 스케일(4px 기반)과 Figma의 4px 그리드가 일치.
3. **CVA variant = Figma Component Properties** — Button의 variant/size 축은 Figma의 Property와 구조적으로 동일.
4. **className override = Figma의 Instance Override** — 그러나 shadcn은 코드 레벨에서만 가능하고, 디자인 토큰 시스템에서는 분리됨.
5. **`--radius` 토큰의 부재** — `rounded-md` 등이 CSS variable이 아닌 Tailwind 스케일에 직접 바인딩. 단, shadcn의 `globals.css`에 `--radius: 0.5rem`이 정의되어 있고 tailwind.config에서 참조함.

### 7.3 다른 디자인 시스템과의 비교 포인트

| 특성 | shadcn/ui | Ant Design / Carbon / Fluent / Material |
|------|-----------|----------------------------------------|
| 토큰 범위 | 색상 전용 (18개) | 색상 + 간격 + 타이포 + 반경 + 그림자 (수백~수천 개) |
| Hardcoded 의존 | 높음 (51.1%) | 낮음 (토큰이 대부분 결정) |
| Override 모델 | className (tailwind-merge) | Theme provider, design token override |
| Variant 시스템 | CVA (폐쇄적) | Token-based 동적 테마 |
| Figma 동기화 | 수동 (토큰 표면적 작음) | 자동화 도구 존재 (토큰 표면적 큼) |

---

## 부록: 감사 방법론

1. `ui.shadcn.com/r/styles/new-york/{component}.json` 레지스트리에서 실제 소스 코드 획득
2. 모든 Tailwind utility class를 개별 토큰으로 분해
3. 각 클래스를 Token / Hardcoded / Structural로 3분류:
   - **Token**: shadcn `globals.css`의 CSS variable(`--primary`, `--muted` 등)을 참조하는 클래스
   - **Hardcoded**: Tailwind의 내장 스케일 값 (숫자, 색상 원시값, 애니메이션)
   - **Structural**: 레이아웃, 플렉스, 그리드, 트랜지션, 접근성 등 디자인 결정이 아닌 구조 클래스
4. CVA variant는 모든 variant 값의 클래스를 합산하여 계산
5. 조건부 클래스 (`data-[state=*]:`, `hover:`, `focus:`, `disabled:` 등)는 1개 클래스로 계산
6. `cn()`의 두 번째 인자 `className`은 사용자 override이므로 기본 클래스 수에서 제외
