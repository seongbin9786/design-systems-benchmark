# Encore — Matchday Design System

매치데이의 디자인 언어. Spotify의 절제를 빌려왔다 — 회색조 규율 위에 서고,
그린은 아낄수록 강해진다. 색은 콘텐츠에 살고, 크롬은 조용하다.

시각 레퍼런스(스와치 · 타이포 샘플 · 전체 컴포넌트 · 도메인 컴포넌트)는
**[`design-system.html`](./design-system.html)** 을 브라우저로 열어 본다.

---

## 아키텍처 — 3계층 토

값은 한 방향으로만 흐른다. 상위 계층이 바뀌면 하위 전체가 따라간다.

```
design-tokens/
├── spotify.css                  호환 번들 (@import 4개) — 기존 화면 29 + 갤러리는 그대로 동작
├── components.css               클래스 계층 (Tier 2·3만 소비)
└── tokens/
    ├── primitives.css           TIER 1  원시 값 · 테마 불변        (77)
    ├── semantic.css             TIER 2  역할 앨리어스 · dark/light  (115)
    └── component-tokens.css     TIER 3  컴포넌트 큰 · 오버라이드 훅 (176)
```

| 계층 | 역할 | 참조 규칙 |
|---|---|---|
| **Tier 1 · Primitives** | 그린 · 차콜 · 상태 팔레트, 타입 스케일, 4-베이스 간격, 반경, elevation, 모션 | 리터럴만. 테마가 바뀌어도 값 불변 |
| **Tier 2 · Semantic** | `--bg-card`, `--text-muted`, `--line` 등 역할 앨리어스 | Tier 1만. **dark/light 매핑의 유일한 소유지** |
| **Tier 3 · Component** | `--button-bg-primary-hover`, `--player-bg-selected` 등 | Tier 2가 원칙, 앨리어스가 없을 때만 Tier 1 |
| **components.css** | 모든 클래스 | **Tier 3·2만. Tier 1 직접 참조 0건** |

### 계층 계약
- 하향 참조만 허용. 상향 참조 금지.
- 테마 분기는 오직 Tier 2(`semantic.css`)에서만 일어난다.
  라이트 테마는 neutral 래더의 **값이 아니라 역할**을 뒤집는다 —
  낮은 칸이 잉크가 되고 높은 칸이 표면이 된다.
  그래서 Tier 3와 클래스 계층에는 **테마 코드가 0줄**이다.
- `fg/bg` 쌍을 반드시 함께 정의한다 (`--badge-bg-live` ↔ `--badge-fg-live`) —
  대비를 토큰 수준에서 보증한다.

---

## 네이밍

계층마다 하나의 패턴. 전부 kebab-case.

- **Tier 1** — `{hue}-{step}` / `{scale}-{step}` → `--green-500`, `--space-4`, `--fs-title-2`
- **Tier 2** — `{category}-{role}[-{state}]` → `--bg-card-hover`, `--text-muted`, `--line-strong`
- **Tier 3** — `{component}-{property}-{variant}-{state}` → `--cardbtn-bg-red-on`
  (variant/state는 필요할 때만)

규칙:
1. 이름 변경은 breaking change. 비추천은 새 이름 추가 + 주석, 삭제는 다음 메이저에서.
2. 표시형 도메인 컴포넌트(듀얼 바 · 타임라인 · 순위표)는 Tier 2를 직접 소비해도 된다 —
   오버라이드 훅이 필요 없는 컴포넌트까지 Tier 3를 만들지 않는다(절제).

---

## 쓰기

**새 작업** — 4개 파일을 직접 링크한다 (계층이 명시적으로 보인다):

```html
<link rel="stylesheet" href="design-tokens/tokens/primitives.css">
<link rel="stylesheet" href="design-tokens/tokens/semantic.css">
<link rel="stylesheet" href="design-tokens/tokens/component-tokens.css">
<link rel="stylesheet" href="design-tokens/components.css">
<script src="templates/encore.js"></script>
```

**기존 화면 29 + 갤러리** — `design-tokens/spotify.css` 한 줄 그대로.
번들이 4개 파일을 올바른 순서로 `@import` 하므로 변경 불필요.

### 오버라이드 훅 (Spectrum식)
셀렉터 수술 없이, 스코프 변수로 컴포넌트를 리스킨한다:

```css
.score-recorder {
  --action-bg-goal:        var(--green-400);
  --button-padding-inline: 36px;
}
/* 클래스 수정 0줄 · specificity 전쟁 없음 · 테마 안전 */
```

---

## 그린은 소중하다

그린은 오직 **주요 액션 · 활성 · 라이브**에만. 나머지는 회색조가 책임진다.
- DO — 한 화면에 그린 버튼 하나, 라이브 닷/이퀄라이저, 단색 데이터 바
- DON'T — 장식 그라디언트, 시리즈마다 새 색을 칠한 차트, 그린 본문/제목

---

## 벤치마크 출처

`~/studyspaces/design-systems-benchmark` (Spectrum · Material · Fluent 2 · Carbon ·
Polaris · shadcn · Ant, 7개 시스템 분석)의 처방을 적용했다.

| 교훈 | 출처 | 적용 |
|---|---|---|
| primitive → semantic → component 3계층 | Spectrum · Material · Carbon · Ant | `tokens/` 3파일 물리 분리 |
| 네이밍 패턴 통일 | Polaris · Spectrum | Tier 3 전체 + R1–R6 |
| 모든 값 `var()` 소비, hardcoded 제거 | 전 시스템 | 클래스 계층 원시 색상 0건 |
| 오버라이드 훅 (`--mod-*`) | Spectrum (536개) | 2단계 fallback 패턴 문서화 |
| 토큰별 description | Polaris | 인라인 주석 + 시각 레퍼런스 |
| fg/bg 쌍 | Polaris · shadcn | 상태 컴포넌트 전부에 쌍 정의 |
| 테마 = 앨리어스 계층에서만 | 전 시스템 | Tier 3 · 클래스 테마 코드 0줄 |
| "토큰 수 ≠ 품질" | Material (1,700개, 동결) | 368개로 절제 |

가장 강한 결론 — 완전 자동 동기화는 업계 어디에도 없고,
도구보다 **구조화된 계약과 검증**이 정답이다 (Spectrum 4.5점의 비결).
다음 단계: 토큰 계약 스키마(JSON Schema) · 스냅샷 회귀 검증 · Figma Variables 1:1 정렬.

---

## 검증

3계층 분리가 렌더링을 바꾸지 않았음을 헤드리스 스크린으로 확인했다:
- `score-recorder`, `standings` — 리팩토링 전후 **픽셀 동일** (해시 일치)
- `match-live`, `auth`, `landing` — 전후 차이가 실행 간 노이즈(라이브 시계/애니메이션)와
  통계적으로 동일 (각 642 vs 643 픽셀, 0.022%)

---

## 경쟁/레거시 언어 (참고)

이 워크스페이스에는 Encore 외에 과거 산출물이 남아 있다 —
Encore가 정답이며, 아래는 화해 또는 정리 대상이다.

- `spotify-design-system.html` — **v2.1 쇼케이스 (2계층 시기, superseded)**.
  최신 3계층 시각 레퍼런스는 [`design-system.html`](./design-system.html) (v3.0).
  구형 파일 상단에 레거시 배너를 표시해 최종본으로 유도한다 (비파괴).
- `design-tokens/colors_and_type.css` — Coinbase CDS 기반 라이트 토큰 (미사용)
- `design/` + `매치데이 랜딩 페이지.html` — navy/orange/lime 라이트 랜딩 탐구
