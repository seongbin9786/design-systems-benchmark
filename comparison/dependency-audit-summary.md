# 컴포넌트 토큰 의존성 전수 조사 — 종합 비교

> 7개 디자인 시스템 × 10개 컴포넌트 실제 소스 코드 라인 단위 분석
> 분석 기준일: 2026-07-26

---

## 1. 시스템별 토큰 의존율 총览

| 시스템 | 평균 토큰 의존율 | 범위 | Hardcoded 총량 | Override 메커니즘 |
|--------|:-------------:|:----:|:------------:|----------------|
| **Spectrum** | **98.9%** | 95.5~100% | 19건 | `--mod-*`, `--highcontrast-*` (3단계 fallback) |
| **Material Web** | **~95%+** | 90~100% | 극소 (gap 8px 등) | `--md-comp-*` CSS vars 직접 설정 |
| **Fluent 2** | **~83%** | 25~96% | 컴포넌트별 5~15종 px | `mergeClasses`, slot className |
| **Ant Design** | **~82%** | 78~87% | 컴포넌트별 4~14건 | `theme.components.*`, CSS vars |
| **Polaris** | **~53%** | 25~86.4% | 19건 (전부 의도적) | **구조적 차단** (override 불가) |
| **Carbon** | **~50%** | 41~59% | 컴포넌트별 38~182건 | className, Sass `!default` (0건 사용) |
| **shadcn/ui** | **18.5%** | 9~39.3% | 205개 클래스 | `cn()` + className (tailwind-merge) |
| **MUI** | **~70%** | 50~90% | 다수 px/문자열 | `sx` prop, `styled()`, theme overrides |

> **주의**: 시스템마다 카운트 기준이 다름. Spectrum/Material Web은 CSS 선언 단위, shadcn은 Tailwind 클래스 단위, Ant Design은 JS style 속성 단위. 절대 수치보다 **패턴과 구조적 차이**에 주목.

---

## 2. 컴포넌트별 토큰 의존율 비교 (10개 컴포넌트)

### Button

| 시스템 | 토큰 의존율 | 고유 토큰 수 | Variant 축 | Hardcoded 특징 |
|--------|:---------:|:---------:|:---------:|-------------|
| Spectrum | 98.3% | 142 | size(3), state(4), style(2) | 4건 (리셋 값) |
| Material Web | ~97% | 42 (comp token) | variant=별도 컴포넌트 (5종) | gap 8px, min-width 64px |
| Fluent 2 | ~87% | 53 | appearance(5), size(3), shape(3) | 15종 px (padding, icon size) |
| Ant Design | ~81% | 58+31 CT | type(6), size(3), shape(3) | 14건 (calc 보정값) |
| Polaris | 70.5% | 66 (--p-*) + 24 (--pc-*) | variant(5), tone(2), size(4) | 1건 (접근성 수정) |
| Carbon | 59% | 33 | kind(7), size(5) | 56건 (to-rem px, 레이아웃) |
| MUI | ~75% | ~20 | variant(4), color(5+), size(3) | 다수 px (padding, minWidth) |
| shadcn/ui | 32.7% | 6 (primary, destructive 등) | variant(6), size(4) | 25개 클래스 (h-9, px-4 등) |

### Input / TextField

| 시스템 | 토큰 의존율 | 고유 토큰 수 | Variant 축 |
|--------|:---------:|:---------:|:---------:|
| Spectrum | 100% | 154 | size(3), state(6), quiet |
| Material Web | ~95% | ~30 | type(filled/outlined) |
| Fluent 2 | ~84% | 30 | size(3), appearance(5+) |
| Ant Design | ~78% | 42+9 CT | variant(4), size(3), status |
| Polaris | 41.3% | 47 | tone(1: magic), state(5) |
| Carbon | 52% | ~25 | size(3), density, invalid, fluid |
| shadcn/ui | 16.7% | 4 | 없음 |

### Card / Tile

| 시스템 | 토큰 의존율 | 비고 |
|--------|:---------:|------|
| Spectrum | 96.8% | 75개 고유 토큰 |
| Fluent 2 | ~91% | appearance(4), size(3) |
| Ant Design | ~83% | size(2), bordered, hoverable |
| Carbon | 49% | Tile: clickable, selectable, expandable |
| Polaris | **CSS 없음** | Box + ShadowBevel의 순수 composition |
| shadcn/ui | 15.0% | bg-card, text-card-foreground, ring-foreground/10 |

### Dialog / Modal

| 시스템 | 토큰 의존율 | 비고 |
|--------|:---------:|------|
| Spectrum | 95.5% | 25개 고유 토큰 (최소) |
| Fluent 2 | ~56% | 레이아웃 상수 하드코딩 다수 |
| Ant Design | ~80% | centered, responsive width |
| Carbon | 49% | size(xs/sm/lg), fluid |
| Polaris | 25.0% | 8 declarations, 대부분 레이아웃 |
| shadcn/ui | 9.2% | 애니메이션/포지셔닝 하드코딩 압도적 |

### DataTable / Table

| 시스템 | 토큰 의존율 | 비고 |
|--------|:---------:|------|
| Spectrum | 98.2% | 206개 고유 토큰 (최대), 48.3KB |
| Fluent 2 | ~25% | 1개 토큰만 참조, 대부분 구조적 |
| Ant Design | ~85% | size(3), bordered, expandable |
| Carbon | 41% | 128 token / 182 hardcoded (최대 규모) |
| Polaris | 35.2% | density, zebra, sticky |
| shadcn/ui | 16.1% | 구조적 클래스 압도적 |

---

## 3. 핵심 발견

### 3.1 토큰 의존율의 3가지 클러스터

```
높음 (90%+)     중간 (50~90%)      낮음 (~50% 이하)
─────────────   ──────────────     ────────────────
Spectrum        Fluent 2           Carbon
Material Web    Ant Design         Polaris
                MUI                shadcn/ui
```

**높은 시스템의 공통점**: CSS custom property 기반. 모든 디자인 값을 var()로 참조. 하드코딩은 레이아웃 리셋(0, transparent)만.

**낮은 시스템의 공통점**: 레이아웃/사이징 값이 하드코딩. Carbon은 `convert.to-rem(Npx)` 패턴, shadcn은 Tailwind 고정 스케일(h-9, px-4).

### 3.2 "토큰 의존율 낮음"의 두 가지 원인

| 원인 | 시스템 | 설명 |
|------|--------|------|
| **레이아웃 값 미토큰화** | Carbon, Polaris | 색상/타이포는 100% 토큰이나, padding/height/width가 px 하드코딩 |
| **철학적 선택** | shadcn/ui | 색상만 토큰(18개), 나머지는 Tailwind 스케일 위임. 의도적 단순함 |

Carbon의 DataTable: 128건 token / 182건 hardcoded. 하드코딩의 대부분은 `convert.to-rem()`으로 변환된 px 값(레이아웃 보정). 색상/간격 토큰은 100% `var(--cds-*)` 경유.

Polaris의 DataTable: 35.2%이나, 색상/간격/타이포만 보면 거의 100%. 낮은 수치는 layout/position 선언 비중 때문.

### 3.3 Hardcoded 값의 성격 분류

| 성격 | 예시 | 시스템 |
|------|------|--------|
| **레이아웃 보정** | `calc(-1px)`, `0`, `100%` | Carbon, Spectrum |
| **사이징 상수** | `h-9`, `min-width: 64px`, `320px` | shadcn, Material Web, Carbon |
| **접근성 수정** | `#898f94` (contrast fix), `3px` focus ring | Polaris |
| **애니메이션** | `translate(-50%, -50%)`, `scale(0.96)` | shadcn, Fluent |
| **CSS 리셋** | `transparent`, `none`, `inherit`, `currentColor` | 모든 시스템 |
| **브라우저 workaround** | `9999px` (border-radius trick) | Polaris |

**Spectrum이 가장 "깨끗"**: 19건 전부 리셋/fallback. 디자인 의도가 하드코딩된 경우 0건.
**Carbon이 가장 "많음"**: DataTable alone 182건. 다만 대부분 to-rem() 레이아웃 값.

### 3.4 Override 메커니즘 비교

| 시스템 | 메커니즘 | 철학 |
|--------|---------|------|
| Spectrum | `--highcontrast-*` > `--mod-*` > `--spectrum-*` 3단계 fallback | 구조화된 override 계층 |
| Material Web | `--md-comp-*` CSS vars 직접 설정 | 공개 API로서의 CSS vars |
| Fluent 2 | `mergeClasses()` 마지막 인자 + slot className | 합성 우선순위 |
| Ant Design | `theme.components.Button.{token}` + CSS vars (`--ant-btn-*`) | 전역/컴포넌트/인스턴스 3단계 |
| MUI | `sx` prop > `styled()` > `theme.components` > `GlobalStyles` | 4단계 커스터마이징 |
| Carbon | className, Sass map override | 빌드 타임 override |
| Polaris | **없음** (구조적 차단) | 일관성 > 유연성 |
| shadcn/ui | `cn()` + className (tailwind-merge) | full ownership, 자유 수정 |

### 3.5 Variant 복잡도 비교

| 시스템 | Button variant 조합 수 | 가장 복잡한 컴포넌트 |
|--------|:-------------------:|-------------------|
| Spectrum | 3 size × 4 state × 2 style = ~24 | Table (8 state × 3 style × 4 size) |
| Fluent 2 | 5 appearance × 3 size × 3 shape = 45 | Badge (4 appearance × 8 color × 6 size = 192) |
| Ant Design | 6 type × 3 size × 3 shape = 54 | Table (size × bordered × expandable × selection) |
| Carbon | 7 kind × 5 size = 35 | DataTable (5 size × zebra × sticky × expandable) |
| Polaris | 5 variant × 2 tone × 4 size = 40 | Badge (11 tone × 2 size) |
| shadcn/ui | 6 variant × 4 size = 24 | Select (position prop만) |
| MUI | 4 variant × 5 color × 3 size = 60 | DataGrid (MUI X, 별도 패키지) |

---

## 4. 양방향 의존성 맵 요약

### 4.1 Component → Token: 컴포넌트별 고유 토큰 수

| 컴포넌트 | Spectrum | Fluent | Carbon | Polaris | Ant | shadcn |
|---------|:-------:|:-----:|:-----:|:------:|:--:|:-----:|
| Button | 142 | 53 | 33 | 66+24 | 58+31 | 6 |
| Input/TextField | 154 | 30 | ~25 | 47 | 42+9 | 4 |
| Card | 75 | 38 | ~30 | — | 38 | 3 |
| Dialog/Modal | 25 | 7 | ~25 | 0 | 40 | 6 |
| Checkbox | 80 | 25 | ~20 | 30 | 28 | 4 |
| Tag/Badge | 140 | 46 | 55 | 40 | 30 | 11 |
| Alert/Notification | 50 | 19 | ~15 | 18 | 32 | 7 |
| Tabs | 103 | 59 | ~30 | 21 | 48 | 8 |
| Table | 206 | 1 | 28 | 25 | 52 | 5 |
| Select/Picker | 146 | 23 | ~20 | 38 | 24 | 9 |

**Spectrum이 압도적으로 많은 고유 토큰 사용** — 모든 상태/variant가 개별 토큰으로 정의.
**Fluent Table은 1개** — Table이 구조만 담당하고 스타일은 하위 컴포넌트(Cell, Row)에 위임.
**shadcn은 전 컴포넌트 합산 18개 고유 토큰** — 의도적 최소주의.

### 4.2 Token → Component: 최다 공유 토큰

| 토큰 (시스템별) | 사용 컴포넌트 수 |
|---------------|:-------------:|
| **Spectrum** `--spectrum-*-content-color-*` | 8/10 |
| **Fluent** `tokens.colorNeutralForeground1` | 9/10 |
| **Fluent** `tokens.borderRadiusMedium` | 8/10 |
| **Carbon** `$text-primary` | 9/10 |
| **Carbon** `$icon-primary` | 7/10 |
| **Polaris** `--p-color-text` | 8/9 |
| **Polaris** `--p-color-bg-fill` | 6/9 |
| **Ant** `colorText` | 10/10 |
| **Ant** `colorBgContainer` | 9/10 |
| **Ant** `borderRadius` | 10/10 |
| **shadcn** `--ring` | 7/10 |
| **shadcn** `--muted-foreground` | 6/10 |

---

## 5. Figma↔Code 매핑 관점 시사점

### 5.1 토큰 의존율이 높을수록 Figma 매핑 용이

| 토큰 의존율 | Figma 매핑 | 시스템 |
|:---------:|:---------:|--------|
| 95%+ | **용이** — 모든 디자인 값이 토큰 = Figma Variables 1:1 대응 | Spectrum, Material Web |
| 80~90% | **양호** — 색상/타이포 매핑 가능, 사이징 일부 갭 | Fluent, Ant Design |
| 50~60% | **부분** — 색상은 매핑, 레이아웃 값은 Figma auto-layout 수치와 직접 대응 | Carbon, Polaris |
| ~20% | **어려움** — 토큰 표면적 자체가 작아 매핑 대상이 적음 | shadcn/ui |

### 5.2 하드코딩 값이 Figma 매핑에 미치는 영향

- **Spectrum**: 하드코딩 19건 전부 리셋 → Figma 매핑 영향 0
- **Carbon**: `convert.to-rem(176px)` 같은 레이아웃 상수 → Figma auto-layout의 min/max constraint에 대응하나 토큰이 아니므로 자동 매핑 불가
- **shadcn**: `h-9`, `px-4` → Figma의 fixed height/padding에 대응하나 Tailwind 스케일 값이라 토큰 매핑 대상 아님
- **Polaris**: 하드코딩 19건 전부 의도적 예외(접근성, workaround) → 매핑 영향 극소

### 5.3 Variant 정합성

| 시스템 | Figma variant ↔ Code variant | 비고 |
|--------|:--------------------------:|------|
| Spectrum | ★★★★☆ | BEM modifier(`--sizeS`, `.is-selected`)가 Figma variant와 직접 매핑 |
| Fluent 2 | ★★★★☆ | appearance/size/shape 완전 일치 (Button 기준 확인) |
| Carbon | ★★★★☆ | v11 kind/size 표준화로 개선 |
| Ant Design | ★★★☆☆ | type/size 대응하나 boolean 조합 과다 |
| Polaris | ★★★☆☆ | variant/tone/size 대응하나 Figma 킷 미확인 |
| shadcn/ui | ★★☆☆☆ | CVA variant는 매핑 가능하나 className 자유도로 drift 가능 |

---

## 6. 파일 인덱스

| 파일 | 시스템 | 줄 수 |
|------|--------|:----:|
| `systems/spectrum-audit.md` | Spectrum | 371 |
| `systems/fluent-audit.md` | Fluent 2 | 733 |
| `systems/carbon-audit.md` | Carbon | 1,072 |
| `systems/polaris-audit.md` | Polaris | 491 |
| `systems/shadcn-audit.md` | shadcn/ui | 641 |
| `systems/antd-audit.md` | Ant Design | 783 |
| `systems/material-audit.md` | Material (Web + MUI) | 989 |
