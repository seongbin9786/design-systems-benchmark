# 플레이북 — 상용 제품에서 디자인 시스템을 추출해 자사 서비스로 확장하기

> 근거: 이 저장소의 7개 시스템 벤치마크(2026-07-26)와, 그 결과를 실제로 적용한
> matchday-saas `@matchday/design-system` 구축 과정(2026-04-16 ~ 2026-07-27).
> 새 프로젝트에서 "오픈 디자인/컴포넌트 라이브러리가 없는 상용 제품"을 레퍼런스로
> 디자인 시스템을 세울 때 그대로 따라갈 수 있는 절차와, 실제로 밟았던 함정을 기록한다.

---

## 0. 전제 확인 — 이 플레이북이 유효한 상황

- 레퍼런스 제품은 **공식 Figma kit도, 오픈 컴포넌트 라이브러리도 없다** (Spotify가 그랬다).
- 우리는 **code-first**로 간다. 이 저장소의 결론이 그 선택을 정당화한다:
  - "7개 시스템 중 완전 자동 토큰 동기화 파이프라인을 운영하는 곳이 없다" — 업계 최상위도 못 푼 문제를 우리가 풀려고 하지 말 것 (`comparison/summary.md` §2.2).
  - "Figma↔Code 매핑 점수가 낮다는 것은 품질 문제가 아니라 아키텍처 철학의 차이" (§2.4) — shadcn/ui가 증명한 노선.
  - "도구(Style Dictionary 등)보다 조직 구조가 더 결정적" (§2.3) — 1인/소수 팀이면 코드가 곧 단일 소유 조직이다. 이것이 오히려 유리한 조건.
- 따라서 **코드(토큰 CSS + 컴포넌트 소스)가 정본(Single Source of Truth)**이고, 디자인 문서·스크린샷·QA 로그가 그 코드를 검증하는 구조로 간다.

---

## 1. 단계 A — 레퍼런스 제품 실측 감사

상용 제품에는 문서가 없으므로 **실측**이 유일한 입력이다. 추정으로 쓴 결론은 반드시 틀린다.
이 저장소 자체가 두 번 자기 수정했다: "유명 시스템 = Figma 공식 지원" 가정이 틀렸고(7곳 중 4곳만),
Carbon "CSS vars 미사용" 분류가 코드 레벨 검증에서 뒤집혔다(`token-deep-dive.md` §5.3).

### A-1. 수집

- 대상 제품의 대표 화면을 **뷰포트 2종 이상**(데스크톱 1440×900, 모바일 390×844)으로 전량 캡처.
- 브라우저 DevTools로 computed style 실측: 배경/표면/강조색 hex, 폰트 스택(선언이 아니라 **실제 로드된 폰트**), radius, 그림자, 간격 리듬, 포커스 링.
  - matchday의 축구 서비스 32곳 조사에서 "폰트가 선언만 되고 실제 미로드"인 곳들이 실측으로만 드러났다. 선언값을 믿지 말 것.
- 상태(state) 표본: hover/active/disabled/focus, 라이트·다크 각각.
- 서드파티가 만든 명세가 있으면 활용하되 실측으로 재검증 (matchday는 `getdesign.md/spotify/design-md`를 레퍼런스로 쓰고 픽셀 QA로 대조했다).

### A-2. 감사 포맷 — 이 저장소의 3파일 체계를 재사용

시스템(제품)마다 3개 문서:

| 파일 | 내용 | 이 저장소의 예 |
|---|---|---|
| `{name}.md` | 6축 개요: 토큰 아키텍처 / 컴포넌트 인벤토리 / (디자인↔코드 대응) / API 철학 / 접근성 / 거버넌스 | `systems/shadcn.md` |
| `{name}-tokens.md` | 토큰 3축: **정의 / 소비 / 거버넌스** | `systems/polaris-tokens.md` |
| `{name}-audit.md` | 컴포넌트별 토큰 의존율 = 토큰참조 / (토큰참조+하드코딩), 집계 기준 명시 | `systems/carbon-audit.md` §8 부록 |

- 감사 기준일, 소스(URL·커밋), 집계 기준, **한계**(무엇을 못 셌는지)를 반드시 헤더에 남긴다.
- 비교 대상이 여럿이면 컴포넌트 집합을 고정한다 (이 저장소는 Button, Input, Card, Dialog, Checkbox, Badge, Alert, Tabs, Table, Select 10종 고정 — 교차 비교표가 성립하는 이유).

### A-3. 산출물

- 원시 팔레트(램프 후보), 타이포 스케일, radius/그림자/간격 목록 — **아직 이름 붙이지 말 것**. 이름은 단계 C의 일이다.

---

## 2. 단계 B — 스킨 후보는 병렬 실험으로 결정

matchday는 같은 부모 커밋에서 **Coinbase 스킨과 Spotify 스킨 브랜치를 동시에** 만들어 실물로 비교한 뒤 하나를 버렸다. 판정 기준은 취향이 아니라 **도메인 정합**이었다:

> "Coinbase blue(#0052ff)는 SaaS 관리 도구에 적합하지만, 경기 운영의 실시간·라이브 느낌과 거리.
> Spotify dark + green이 LIVE 상태, 스코어보드, 실시간 기록의 시각 언어와 일치."
> — matchday-saas `docs/design-system-changelog.md`

절차:
1. 후보 2~3개를 각각 브랜치로, **토큰 값만 갈아끼워** 실제 화면에 입혀본다 (이게 가능하려면 단계 C의 semantic 토큰이 먼저 있어야 한다 — 최소한 shadcn 기본 토큰이라도).
2. 판정 문장을 "우리 도메인의 핵심 순간(matchday라면 LIVE·기록)에 어느 시각 언어가 맞는가"로 쓴다.
3. 진 브랜치는 삭제하지 말고 origin에 보존한다 (나중에 컨셉 전환 시 재료가 된다).

---

## 3. 단계 C — 시각 언어를 "값"이 아니라 "규칙"으로 번역

상용 제품에서 가져갈 수 있는 것은 hex 코드가 아니라 **절제의 규칙**이다. 그리고 가져가면 안 되는 것을 먼저 못박는다.

### C-1. 법적/윤리적 경계 (문서 첫 줄에)

> "Spotify의 로고, 상표, 전용 서체와 음악 서비스 구조는 복제하지 않는다." — matchday `docs/design.md`

로고·상표·전용 서체·화면 구조(IA)는 복제 금지. 가져가는 것은 색 관계, 밀도, 위계, 모션의 **원리**다.

### C-2. 원칙을 DO/DON'T 문장으로

Encore(matchday 디자인 언어)의 예:

> "Spotify의 절제를 빌려왔다 — 회색조 규율 위에 서고, 그린은 아낄수록 강해진다.
> 색은 콘텐츠에 살고, 크롬은 조용하다."
> "그린은 오직 주요 액션 · 활성 · 라이브에만. DON'T — 장식 그라디언트, 시리즈마다 새 색을 칠한 차트, 그린 본문/제목"

이 문장들이 이후 모든 코드리뷰의 판정 기준이 된다. 값은 바뀌어도 규칙은 남는다.

### C-3. 도메인 확장 지점을 명시

레퍼런스 제품에 없는 우리 도메인 요소(matchday: LIVE 도트, 스코어보드, 상태색 success/warning)를
**레퍼런스의 문법 안에서** 정의한다. 예: LIVE = 강조색의 가장 강한 사용처, 이퀄라이저 애니메이션은 `currentColor`로 그려 어떤 문맥에도 이식 가능하게.

---

## 4. 단계 D — 토큰 아키텍처: 2계층으로 시작해서 3계층으로 성장

### D-1. 시작은 semantic 단층 (shadcn 방식)

- "shadcn/ui의 32개 토큰은 '부족'이 아니라 '철학'이다" (`token-deep-dive.md` §5.1). "토큰 수 ≠ 토큰 품질" — Material 1,700개는 반면교사.
- 역할 기반 네이밍 컨벤션을 그대로 차용: `--<role>` / `--<role>-foreground` / `--<role>-hover` (background, card, popover, primary, muted, accent, destructive, border, input, ring …). fg/bg **쌍**은 항상 함께 정의한다 (Polaris·shadcn 교훈).
- 다크/라이트는 **별도 값 정의** 패러다임 (Spectrum·Fluent·Carbon·Polaris·shadcn 방식). 알고리즘 반전(Ant)은 세밀 제어가 어렵다.

### D-2. primitive 계층은 "리팩터할 근거가 생겼을 때" 분리

matchday는 semantic에 hex를 직접 넣고 3개월을 달린 뒤, 벤치마크 학습 당일에 primitive→semantic으로 재편했다. 재편 커밋의 계약이 중요하다:

> "globals.css 인라인 hex를 primitive(:root) + semantic(var 참조)로 재편
> — 계산값 동일 보존 (라이트/다크 37개 변수 전수 대조)"

- **Tier 1 primitive**: 테마 불변 원시 램프 (`--green-400/500/700/800`, `--neutral-0…1000`, 상태색). 한 번 정의, 테마 안 탄다.
- **Tier 2 semantic**: 다크/라이트 리매핑이 일어나는 **유일한** 장소. 전부 `var(--primitive)` 참조.
- **Tier 3 component**: 별도 계층을 만들지 않고 CVA variant + 인라인 컴포넌트 변수(`[--card-spacing:…]`)에 위임한다. Spectrum처럼 수백 개 component 토큰을 만드는 건 우리 규모에 과잉 (YAGNI).
- 재편 시 검증 계약: **변수 전수 대조로 계산값 바이트 동일**을 증명하고 커밋 메시지에 남긴다. 이것이 이 저장소의 "도구보다 구조화된 계약과 검증이 정답" (Spectrum 4.5점의 비결) 결론의 실전 적용이다.

### D-3. 브랜드 주입 훅

전역 토큰을 덮지 않고 국소 재정의할 별칭을 마련한다: `--brand: var(--primary)`를 루트에 두고,
테넌트/주최자 브랜딩이 필요한 서브트리 루트에서만 `--brand`를 재할당. Spectrum의 `--mod-*` 오버라이드 훅의 축소판.

---

## 5. 단계 E — 구현 스택 (code-first 기준 레시피)

matchday가 실제 조합한 스택. 각 선택의 이유와 함께:

| 선택 | 이유 |
|---|---|
| **Tailwind v4 CSS-first** (`@theme inline`, tailwind.config 없음) | 토큰 정본이 CSS 한 파일(`globals.css`)로 수렴. `--color-*: var(--*)` 매핑으로 semantic 토큰이 곧 유틸리티 이름이 됨 (`bg-background`, `text-muted-foreground`) |
| **shadcn 구조로 시작** (30 컴포넌트 일괄 생성) | 컴포넌트를 npm 의존이 아닌 **소유한 소스**로 확보 — 스킨 실험·도메인 확장이 자유로움. 모노레포 패키지에 중앙화하고 앱의 `components.json`이 패키지를 가리키게 해 `shadcn add`가 공용 패키지에 떨어지게 함 |
| **headless 프리미티브** (Base UI) | 접근성(ARIA·키보드)은 직접 만들지 않는다. 스타일은 전부 우리 토큰 |
| **CVA + data-attribute variant** | 열거형 variant는 CVA, 단순 변형은 `data-size` → `data-[size=sm]:…` 셀렉터. 모든 요소에 `data-slot` 마킹 → 교차 컴포넌트 스타일링을 셀렉터로 해결 |
| **class 기반 테마** (`.dark`/`.light` + next-themes + first-paint 인라인 스크립트) | 팔레트 변수와 `dark:` 유틸리티 변형이 **같은 스위치**로 동시에 전환돼야 하므로 media query가 아닌 class. FOUC는 인라인 스크립트로 차단 |
| **패키지는 빌드 없이 소스 배포** (`exports`가 `.ts` 직접) | 소비 앱의 Vite가 컴파일. 빌드 파이프라인 유지비 제로 |

앱 쪽 규칙: 앱의 CSS는 디자인 시스템 globals.css **re-import 한 줄 + 자기 `@source`** 만. 앱은 토큰을 하나도 정의하지 않는다. 이 규칙이 "룩앤필을 토큰 교체만으로 갈아끼운다"는 목표의 물리적 보장이다.

---

## 6. 단계 F — 검증과 강제

### F-1. 검증: 실측 QA + 전량 캡처 (비주얼 리그레션 도구 대신)

- **픽셀 QA 로그**: 레퍼런스와 나란히 놓고 뷰포트별로 대조, 발견-수정-재검증을 문서로 남긴다 (matchday `design-qa.md`: 포커스 링이 흰색 2px inset → `var(--primary)`로 수정, computed `rgb(30,215,96)` 재확인, `final result: passed`).
- **전량 스크린샷 갤러리**: Playwright로 전 화면 × 역할 × (뷰포트 × 테마) 캡처 + index.html 리포트. 스토리 단위로도 동일하게 (story-shots). 사람이 훑는 갤러리가 스냅샷 diff보다 이 규모에선 유효하다는 판단 — "Story DOM 스냅샷과 비주얼 리그레션은 사용하지 않는다"를 명시적 정책으로 문서화.
- **커버리지 게이트**: 디자인 시스템 패키지에 별도 임계값 (matchday: line/func/stmt 65%, branch 60%) + CI에 전용 job (lint → typecheck → test:coverage).

### F-2. 강제: 되는 것과 안 되는 것을 정직하게

- `eslint-plugin-better-tailwindcss`의 `no-unknown-classes`: 오타 난 토큰 유틸리티(`bg-brnad`)는 잡는다. 커스텀 클래스(`eyebrow`, `live-dot` 등)는 allowlist로.
- **한계**: arbitrary value(`bg-[#FEE500]`)는 lint로 못 잡는다. 하드코딩 컬러 금지는 결국 **코드리뷰 원칙**이다 — 원칙 문서(C-2)가 판정 기준. 의도적 예외(서드파티 브랜드 버튼 등)는 예외임을 주석으로 남긴다.
- 컴포넌트 중복 방지: "shadcn에 이미 있는 것을 다시 만들지 않는다"를 문서 원칙으로. 반대로 앱에서 반복 패턴이 **셀 수 있게** 쌓이면 (matchday: `border bg-card` 30+ 사용처 → Card variant, 에러 알림 13곳 → QueryErrorAlert) variant/공용 컴포넌트로 승격한다. 승격 근거는 사용처 카운트.

---

## 7. 단계 G — 시각 레퍼런스 HTML: "사람이 보는 정본"을 출력한다

code-first 노선에는 Figma가 없다. 그래서 **디자인 시스템 전체를 사람이 한눈에 열람할 산출물**을
코드에서 직접 뽑아야 한다. 이것이 벤치마크 결론 — "Code-first 시스템의 대안은 코드 문서 자체가
디자인 명세" (`comparison/summary.md` §6) — 의 구현체이며, 이 플레이북에서 가장 중요한 최종 출력물이다.

matchday의 실물: `docs/design-system.html` (3,353줄, 자기 완결 단일 파일, PR #126).

### G-1. 구성 — 11개 섹션 뼈대 (재사용 가능)

1. **개요** — 디자인 언어 이름(ENCORE)과 선언
2. **3계층 아키텍처** — 토큰 계층 다이어그램
3. **네이밍 규칙**
4. **색상** / 5. **타이포그래피** / 6. **간격 · 도형 · Elevation · 모션** / 7. **아이콘** (53종 · stroke 1.8 · round caps — 수치 스펙 포함)
8. **컴포넌트 라이브러리** — 전 컴포넌트 실렌더링
9. **도메인 패턴** — 매치 센터, 레코더 콘솔 (새 프로젝트에서는 자기 도메인으로 교체)
10. **적용 화면** — "이 시스템으로 만든 29개 화면"
11. **테마 — 역할 반전** / 12. **거버넌스 — 벤치마크에서 가져온 것, 다음에 할 것**

### G-2. 제작 규칙 — 자기 완결(single-file)

커밋 메시지가 곧 레시피다:

> "matchday-design/design-system.html 을 자기 완결화해 docs/에 추가
> — 토큰 CSS 4개·encore.js 인라인, 엠블럼 8종 base64(144px 리사이즈), 폰트만 CDN"

- **실제 토큰 CSS를 인라인**한다 — 명세와 구현이 같은 파일이므로 어긋날 수 없다. 문서용 사본 CSS를 따로 만들면 그 순간부터 썩는다.
- 이미지는 base64(리사이즈해서), 외부 의존은 폰트 CDN 정도만. 파일 하나로 이동·공유·아카이브가 된다.
- 저장 위치는 서비스 repo `docs/` — 디자인 워크스페이스에서 만들었더라도 자기 완결화해 서비스 repo로 옮긴다.

### G-3. 왜 이 출력이 중요한가

- **Storybook과 역할이 다르다.** Storybook은 컴포넌트 단위 개발 도구, 이 HTML은 토큰→컴포넌트→도메인 패턴→적용 화면→거버넌스를 **하나의 서사**로 보여주는 계약 문서다. 디자이너·신규 합류자·외부 공유에 쓰는 건 이쪽이다.
- **"적용 화면 N개" 섹션이 증명 책임을 진다.** 컴포넌트 나열만 있는 쇼케이스는 시스템이 실제 화면을 감당하는지 말해주지 않는다. 실 화면 수십 장이 붙어야 명세가 아니라 실적이 된다.
- **거버넌스 섹션이 감사 추적을 겸한다.** "어디서 가져왔고(벤치마크 교훈), 다음에 뭘 할지"를 문서 안에 남기면 이 파일 하나가 의사결정 기록이 된다.

생성 시점: 토큰·컴포넌트가 안정된 뒤(D~F 완료 후). 스킨 실험(B) 단계에서 만들면 두 번 만들게 된다.

---

## 8. 단계 H — 도메인 확장 단계 (시스템이 레퍼런스를 넘어서는 지점)

시간이 지나면 레퍼런스 모방이 아니라 자기 문법이 생긴다. matchday의 경우:

1. **도메인 컴포넌트**: Scoreboard, Page 같은 compound 컴포넌트 (`Root/Team/Score/Meta` 네이밍, context는 진짜 공유 상태가 있을 때만).
2. **사용자 모드별 프리미티브**: "조회는 모바일, 기록은 콕핏" — 카드 남용 진단("한 화면에 Card 8개") 후 규칙선·타이포그래피 기반 프리미티브 6종(Section, DataList, StatComparison, Timeline, NavStrip, Cockpit) 신설. 각각 story + test 동반.
3. 이 단계의 판단 기준도 원칙 문장이다: "상자 대신 선", "정보 두 줄마다 테두리가 한 겹씩 붙으면 안 된다".

---

## 9. 사례 대응표 — 각 단계가 matchday-saas에서 실제로 출력한 것

이 플레이북으로 프롬프팅했을 때 기대할 출력물과, 원본 사례의 실물 대응:

| 단계 | 기대 출력물 | matchday-saas의 실물 |
|---|---|---|
| **A. 실측 감사** | 레퍼런스별 감사 문서 3종 + 전량 캡처 + 원시 팔레트 | 아키텍처 레퍼런스: 이 repo(`systems/` 21파일, `comparison/` 7파일, `figma/raw`). 시장 레퍼런스: football-ux-research(32곳 수집물). 시각 레퍼런스(Spotify)는 3종 감사 대신 getdesign.md 명세 + 픽셀 실측으로 대체 |
| **B. 병렬 스킨 실험** | 스킨 브랜치 N개 + 도메인 정합 판정 기록 | `feat/coinbase-design`(폐기, origin 보존) vs `feat/spotify-design`(채택) + 판정문이 담긴 `docs/design-system-changelog.md` |
| **C. 규칙 번역** | 법적 경계 + DO/DON'T 원칙 문서 | `docs/design.md`(복제 금지 경계, 8개 컴포넌트 원칙, 밀도·모션 규칙), `matchday-design/README.md`(Encore 언어 + 벤치마크 교훈→적용 대응표) |
| **D. 토큰** | semantic 토큰 CSS 1파일 → 성장 후 primitive 분리 커밋(전수 대조 증명) | `packages/design-system/src/styles/globals.css`(정본, 298줄) + 3계층 재편 PR #125("37개 변수 전수 대조" 명시) |
| **E. 스택 구현** | 컴포넌트 패키지 + 앱 CSS re-import 한 줄 | `@matchday/design-system` 32개 모듈(story/test 동반), theme-provider/toggle, FOUC 인라인 스크립트, 앱 globals.css 2줄 |
| **F. 검증·강제** | 픽셀 QA 로그, 전량 캡처 갤러리, 커버리지 게이트, lint | `design-qa.md`(`final result: passed`), `screenshots/` 52장×7역할 + index.html, story-shots 스크립트, CI design-system job(65/60%), better-tailwindcss `no-unknown-classes` |
| **G. 시각 레퍼런스** | 자기 완결 단일 HTML (토큰 인라인 + 적용 화면 + 거버넌스) | `docs/design-system.html` 3,353줄, 11개 섹션, 적용 화면 29개 (PR #126) |
| **H. 도메인 확장** | 도메인 compound 컴포넌트, 카운트 기반 variant 승격, 자기 진단 문서 | Scoreboard·Page compound, Badge/Card/Empty variant 승격(30+·13곳 카운트 근거), 모바일 프리미티브 6종 + `mobile-first-redesign.md` 진단서, `docs/design-system-changelog.md`(9단계 이력) |

새 프로젝트에서의 기대 출력 트리:

```
연구 repo(또는 docs/research/)
  audit/{제품}.md, {제품}-tokens.md, {제품}-audit.md    ← A
  captures/…                                           ← A
서비스 repo
  (브랜치) skin/{후보A}, skin/{후보B} + 판정 기록         ← B
  docs/design.md                                        ← C
  packages/design-system/src/styles/globals.css         ← D
  packages/design-system/src/components/*               ← E
  design-qa.md, screenshots/, CI 게이트                  ← F
  docs/design-system.html                               ← G
  (성장 후) 도메인 컴포넌트 · 변경 이력 문서               ← H
```

플레이북이 자동으로 출력하지 **못하는** 것 두 가지: B의 스킨 판정(도메인 정합은 사람의 결정이다 —
matchday에서도 최종 채택은 사용자 판단이었다)과 A의 실측 실행(DevTools/Playwright를 실제로 돌리는 작업).
나머지는 문서·코드 생성이므로 에이전트가 이 문서만 보고 산출할 수 있는 형태다.

---

## 10. 함정 목록 (실제로 밟았거나 벤치마크가 경고한 것)

1. **추정 금지, 실측만** — 이 저장소는 docs 레벨 결론 2건이 코드 레벨 검증에서 뒤집혔고, Figma 매칭률 추정치(Spectrum ~90%)가 실측(70%)과 크게 어긋났다.
2. **자동 동기화 환상** — Figma Variables↔코드 자동 동기화는 업계 미해결. 파이프라인 구축에 시간 쓰지 말고 계약+검증 문서에 써라.
3. **토큰 수 ≠ 품질** — 계층·네이밍·의존율이 품질이다. 램프부터 만들지 말고 semantic부터.
4. **레퍼런스의 숫자를 그대로 옮기지 말 것** — 라이트 테마의 `--primary`는 다크의 그린을 그대로 못 쓴다 (matchday: `#1ed760` → 라이트에서 `#157f3b`, 대비 확보).
5. **가공 데이터 노출 주의** — 시안에 넣은 그럴듯한 수치("120+/800+")가 실 화면까지 살아남는다. 리뷰에서 잡혔다.
6. **lint가 다 못 잡는다** — arbitrary value는 통과한다. 원칙 문서 + 리뷰가 최종 방어선.
7. **집계 기준을 명시하지 않은 감사는 비교 불가** — 시스템마다 카운트 기준이 다르면 절대 수치가 아니라 패턴만 비교하라.

---

## 11. 체크리스트 (새 프로젝트 착수용)

- [ ] A. 레퍼런스 제품 실측: 화면 전량 캡처(2 뷰포트), computed style 팔레트/타이포/radius/그림자, 상태·테마 표본
- [ ] A. 감사 문서 3종 작성 (개요 6축 / 토큰 정의·소비·거버넌스 / 의존율, 기준일·소스·한계 명시)
- [ ] B. 스킨 후보 2+개 병렬 브랜치, 도메인 정합 문장으로 판정, 진 브랜치 보존
- [ ] C. 원칙 문서: 법적 경계 → DO/DON'T 규칙 → 도메인 확장 요소
- [ ] D. semantic 토큰 (role/-foreground/-hover 쌍, 다크·라이트 별도 값, `--brand` 주입 훅)
- [ ] E. 스택: Tailwind v4 CSS-first + 소유형 컴포넌트(shadcn류) + headless 프리미티브 + class 테마 + FOUC 스크립트
- [ ] E. 앱 CSS = re-import 한 줄, 앱 토큰 0개
- [ ] F. 픽셀 QA 로그 + 전량 캡처 갤러리 + 커버리지 게이트 + no-unknown-classes lint
- [ ] G. 시각 레퍼런스 HTML: 자기 완결 단일 파일, 실제 토큰 CSS 인라인, 적용 화면 갤러리, 거버넌스 섹션 (D~F 완료 후 생성)
- [ ] (성장 후) D-2. primitive 계층 분리 — 변수 전수 대조로 계산값 보존 증명
- [ ] (성장 후) H. 사용처 카운트 기반 variant 승격, 도메인 프리미티브
