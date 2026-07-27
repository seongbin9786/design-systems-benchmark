# 디자인 시스템 변경 이력

`packages/design-system`의 설계와 토큰이 어떻게 변해왔는지 기록한다.
현재 정본은 `packages/design-system/src/styles/globals.css`이고, 이 문서는 그 이력이다.

## 전체 흐름

```
shadcn 기본 → Coinbase → Spotify dark → 라이트 테마 도입 → Encore 적용 → 3계층 토큰 분리
```

| 순서 | 날짜 | 커밋 | 요약 |
|---|---|---|---|
| 1 | 2026-04-16 | `ea4fc7f` | monorepo 스켈레톤, Storybook 셋업 |
| 2 | 2026-07-13 | `c3c11c3` | shadcn 컴포넌트 30종 일괄 추가, 기본 oklch 토큰 |
| 3 | 2026-07-14 | `d80cccf` | Coinbase 디자인 반영 (blue primary, Inter 폰트) |
| 4 | 2026-07-13 | `29a12d4` | Spotify dark 디자인 반영 (green primary, #121212 캔버스) |
| 5 | 2026-07-19 | `ee1da0e` | 라이트 테마, 테마 전환 도입, 하드코딩 hex 치환 |
| 6 | 2026-07-26 | `8660342` | matchday-design Encore 시스템 적용 (Outfit, JetBrains Mono, 유틸 클래스) |
| 7 | 2026-07-26 | `4117c38` | 리뷰 반영 (이퀄라이저 가시성, 가공 통계 제거) |
| 8 | 2026-07-26 | `4fe0b79` | primitive, semantic 3계층 토큰 분리 |
| 9 | 2026-07-26 | `ad4efa4` | 시각 레퍼런스 HTML 추가 (docs/design-system.html) |

## Phase 1: 스켈레톤 (2026-04-16)

`ea4fc7f` feat: base setup monorepo skeleton

- Storybook, package.json, tsconfig만 존재
- 컴포넌트 없음, 토큰 없음
- `@matchday/design-system` 패키지 등록

## Phase 2: shadcn 기본 컴포넌트 (2026-07-13)

`c3c11c3` feat(frontend): 전체 사용자 화면 구현

컴포넌트 30종 추가:

- shadcn 기반: Alert, AlertDialog, Avatar, Badge, Breadcrumb, Button, Card, Checkbox, Dialog, DropdownMenu, Input, Label, Popover, RadioGroup, ScrollArea, Select, Separator, Sheet, Skeleton, Sonner, Switch, Table, Tabs, Textarea, Tooltip
- 자체 제작: Empty, Field, Page, Scoreboard, Spinner

토큰:

- shadcn 기본 oklch 팔레트 (blue 계열 primary)
- `:root` light, `.dark` dark 분리
- `--brand`, `--brand-foreground` alias 추가
- `--shadow-card`, `--shadow-overlay` 정의
- 폰트: Helvetica Neue 우선, Pretendard/Noto Sans KR fallback

테스트와 Storybook:

- button, checkbox, dialog, dropdown-menu, page, popover, scoreboard, select, sheet, switch, tabs, alert-dialog에 test 파일
- component-library, data-display, overlays, page, scoreboard에 stories

## Phase 3: Coinbase 디자인 (2026-07-14)

`d80cccf` feat(frontend): coinbase 디자인 시스템 반영

토큰 변경:

- primary: oklch blue → `#0052ff` (Coinbase blue)
- surface: white/dark `#0a0b0d`
- 폰트: Inter + Pretendard Variable
- 신규 토큰: `--primary-active`, `--primary-disabled`, `--field-elevated`
- radius: `0.625rem` → `0.75rem`

컴포넌트 변경 (10 파일):

- Button, Badge, Card, Input, Page, Select, Table, Tabs, Textarea
- globals.css 119줄 변경

## Phase 4: Spotify dark 디자인 (2026-07-13)

`29a12d4` feat(design-system): spotify 디자인 반영

토큰 변경:

- primary: `#0052ff` → `#1ed760` (Spotify green)
- background: `#121212`, card: `#181818`, popover: `#282828`
- `:root, .dark` 통합 (dark-only 모드)
- `color-scheme: dark` 고정
- Coinbase 토큰 제거: `--primary-active`, `--primary-disabled`, `--field-elevated`
- radius: `0.75rem` → `0.5rem`
- 폰트: Helvetica Neue 우선 유지

컴포넌트 변경 (16 파일):

- AlertDialog, Badge, Button, Card, Checkbox, Dialog, DropdownMenu, Input, Popover, RadioGroup, Scoreboard, Select, Sheet, Tabs, Textarea
- globals.css 89줄 변경 (순수 hex 전환)

## Phase 5: 라이트 테마와 테마 전환 (2026-07-19)

`ee1da0e` feat(design-system): 라이트 테마와 테마 전환 도입, 하드코딩 컬러 토큰 치환

토큰 변경:

- `:root, .light` (light)와 `.dark` (dark) 분리 복원
- light: `--background: #f6f6f7`, `--primary: #157f3b` (어두운 green)
- dark: 기존 Spotify 팔레트 유지
- 하드코딩 hex → `var()` 참조로 치환

신규 컴포넌트:

- `theme-provider.tsx`: next-themes 기반 ThemeProvider
- `theme-toggle.tsx`: light/dark/system 전환 토글
- `theme-toggle.stories.tsx`

Storybook:

- preview.ts에 테마 전환 decorator 추가
- light/dark/system 3가지 모드 지원

의존성:

- `next-themes` 추가

## Phase 6: Encore 디자인 시스템 적용 (2026-07-26)

`8660342` feat(design): matchday-design Encore 디자인 시스템을 matchday-saas에 적용

matchday-design 프로젝트의 Spotify-inspired "Encore" 디자인 시스템을 competition-web에 적용.
기능은 그대로 유지하고 디자인만 변경.

토큰 변경:

- 폰트 추가
  - `--font-display`: Outfit (500~900), 제목, 점수, 통계 숫자
  - `--font-mono`: JetBrains Mono (400~700), 타이머, 데이터
  - `--font-sans`: Pretendard Variable을 우선순위로 조정
- 신규 radius: `--radius-pill: 9999px`
- 신규 shadow: `--shadow-pop`, `--shadow-brand`

유틸리티 클래스 (globals.css `@layer components`):

| 클래스 | 용도 |
|---|---|
| `.eyebrow` | 11px, bold, uppercase, 0.12em tracking, primary 색 |
| `.font-display` | Outfit 폰트 적용 |
| `.glow-green` | 우상단 green radial glow (::before) |
| `.glow-red` | 우상단 red radial glow (::before) |
| `.live-dot` | 6px pulsing red dot 애니메이션 |
| `.eq` | 4-bar 이퀄라이저 애니메이션 (라이브 인디케이터) |

페이지별 적용 (competition-web 7개 페이지):

- 랜딩: hero glow, eyebrow, display 폰트, eq 애니메이션, feature 번호
- 로그인: 좌측 패널 glow, eyebrow, display 폰트
- 회원가입, 비밀번호 재설정: display 폰트 타이틀
- 공개 hero: display 폰트
- 운영사, 대회 관리 셸: 헤더 glow, eyebrow, display 폰트

검증: typecheck, lint, 스크린 52장 캡처

## Phase 7: 리뷰 반영 (2026-07-26)

`4117c38` fix(design): 리뷰 반영 (이퀄라이저 가시성, 로그인 가공 통계 제거)

- `.eq span` 막대 배경을 `var(--primary)` → `currentColor`로 변경
  - 배지 전경색을 따라 라이트, 다크 모두에서 보이게
- 로그인 페이지 가공 통계 블록 제거 (120+, 800+, 2,400+)
  - 브랜드 패널은 eyebrow, 헤드라인, 설명만 유지

## Phase 8: 3계층 토큰 분리 (2026-07-26)

`4fe0b79` refactor(design): 디자인 토큰 primitive, semantic 3계층 분리

globals.css 인라인 hex를 3계층으로 재편:

```
Tier 1 (Primitive)  :root 블록, 테마 불변 raw 팔레트
  green ramp: --green-400 ~ --green-800
  neutral ramp: --neutral-0 ~ --neutral-1000
  status: --red-400, --red-600, --amber-500, --amber-700

Tier 2 (Semantic)   :root/.light, .dark 블록, 역할 토큰
  --background, --foreground, --primary, --muted 등
  var()로 Tier 1 참조, 다크/라이트 재매핑은 여기서만

Tier 3 (Component)  shadcn CVA variants + @layer components
  semantic 토큰을 직접 소비
```

- 계산값 동일 보존 (라이트, 다크 37개 변수 전수 대조)
- 테마 전략: class 기반 (`.dark` / `.light` on `<html>`)
- next-themes가 class 토글, defaultTheme "system"
- index.html 인라인 스크립트로 FOUC 방지

## Phase 9: 시각 레퍼런스 (2026-07-26)

`ad4efa4` docs(design): 디자인 시스템 시각 레퍼런스 추가 (자기 완결 HTML)

- `docs/design-system.html` 추가 (3,353줄)
- matchday-design/design-system.html을 자기 완결화
- 토큰 CSS 4개, encore.js 인라인, 엠블럼 8종 base64 (144px), 폰트만 CDN

## 현재 구조

### 패키지

```
packages/design-system/
  .storybook/          Storybook 설정 (테마 전환 decorator)
  src/
    components/        32개 컴포넌트 (stories, test 포함)
    styles/globals.css 토큰 정본 (348줄, 3계층)
    lib/utils.ts       cn() 유틸
    index.ts           전체 export
  package.json         @matchday/design-system
```

### 컴포넌트 목록 (32종)

| 분류 | 컴포넌트 |
|---|---|
| 액션 | Button, Checkbox, RadioGroup, Switch |
| 입력 | Input, Textarea, Select, Field, Label |
| 표시 | Badge, Avatar, Card, Table, Separator, Skeleton, Spinner |
| 탐색 | Tabs, Breadcrumb, DropdownMenu |
| 오버레이 | Dialog, AlertDialog, Sheet, Popover, Tooltip, Sonner |
| 레이아웃 | Page, ScrollArea, Empty |
| 도메인 | Scoreboard |
| 테마 | ThemeProvider, ThemeToggle |

### 토큰 체계 (현재)

Tier 1 Primitive (테마 불변):

| 토큰군 | 값 |
|---|---|
| green ramp | `--green-400` #3be477, `--green-500` #1ed760, `--green-700` #157f3b, `--green-800` #12702f |
| neutral ramp | `--neutral-0` #ffffff ~ `--neutral-1000` #000000 (16단계) |
| status | `--red-400` #f3727f, `--red-600` #d02f3a, `--amber-500` #ffa42b, `--amber-700` #b45309 |

Tier 2 Semantic (라이트 / 다크):

| 토큰 | 라이트 | 다크 |
|---|---|---|
| `--background` | neutral-50 | neutral-950 |
| `--foreground` | neutral-950 | neutral-0 |
| `--card` | neutral-0 | neutral-940 |
| `--primary` | green-700 | green-500 |
| `--primary-foreground` | neutral-0 | neutral-1000 |
| `--secondary` | neutral-100 | neutral-925 |
| `--muted` | neutral-150 | neutral-900 |
| `--muted-foreground` | neutral-600 | neutral-400 |
| `--destructive` | red-600 | red-400 |
| `--warning` | amber-700 | amber-500 |
| `--success` | green-700 | green-500 |
| `--field` | neutral-0 | neutral-925 |
| `--border` | rgb(0 0 0 / 12%) | rgb(255 255 255 / 10%) |

Tier 3 Component:

- shadcn CVA variants가 Tier 2를 직접 소비
- `@layer components`의 `.eyebrow`, `.glow-*`, `.live-dot`, `.eq` 등

### 폰트

| 토큰 | 스택 | 용도 |
|---|---|---|
| `--font-sans` | Pretendard Variable, Helvetica Neue, Arial, Noto Sans KR | 본문 |
| `--font-display` | Outfit, Pretendard Variable | 제목, 점수, 통계 |
| `--font-mono` | JetBrains Mono, SFMono-Regular, Menlo | 타이머, 데이터 |

### 의존성

- tailwindcss v4 (CSS-first 설정)
- shadcn v4 (CVA variants)
- next-themes (class 기반 테마 전환)
- sonner (토스트)
- lucide-react (아이콘)
- Storybook (시각 검증)
- vitest + Testing Library (동작 검증)

## 설계 결정 기록

### 왜 Spotify인가

경기 운영 도구의 정보 밀도와 실시간성에 Spotify의 근검정 캔버스, 굵기 대비, pill 조작 요소가 맞음.
콘텐츠가 먼저 보이는 어두운 표면, 초록은 기능 액센트로만 사용.

### 왜 3계층인가

- 인라인 hex가 라이트, 다크 블록에 중복되어 재스킨이 어려웠음
- Tier 1 primitive을 바꾸면 Tier 2 semantic이 따라가도록 var() 참조
- 계산값 동일 보존을 전수 대조로 확인

### 왜 class 기반 테마인가

- tailwind의 `dark:` custom-variant가 `.dark` class에 gate됨
- 팔레트 변수와 유틸 variant가 함께 전환되어야 하므로 media query만으로는 부족
- next-themes + index.html 인라인 스크립트로 FOUC 방지

### 왜 Coinbase에서 Spotify로 전환했나

- Coinbase blue(`#0052ff`)는 SaaS 관리 도구에 적합하지만, 경기 운영의 실시간, 라이브 느낌과 거리
- Spotify dark + green이 LIVE 상태, 스코어보드, 실시간 기록의 시각 언어와 일치
- 전환 후 `--primary-active`, `--primary-disabled` 같은 Coinbase 전용 토큰 제거
