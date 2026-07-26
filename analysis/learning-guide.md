# 학습 가이드

> 이 프로젝트의 문서를 효과적으로 읽는 순서와 방법

---

## 빠른 시작: 30분 코스

핵심 결론만 빠르게 파악하고 싶을 때.

1. **`comparison/summary.md`** — "핵심 발견 5가지" (2절)만 읽기
   - Figma↔Code 자동 동기화는 업계 전체 미해결
   - 매핑 충실도는 도구보다 소유 구조가 결정
   - Code-first는 "결함"이 아니라 "선택"

2. **`comparison/component-mapping.md`** — "매핑의 스펙트럼" 다이어그램
   - Design-first ←→ Code-first 스펙트럼에서 각 시스템 위치

3. **`figma/figma-mapping-results.md`** — 실측 매칭률 테이블 (2절)
   - Carbon 97%, Material 92%, Fluent 88%, Spectrum 70%

---

## 표준 코스: 2시간

패턴을 체득하고 싶을 때.

### 전반부 (1시간): 비교 분석

| 순서 | 파일 | 읽을 섹션 | 핵심 질문 |
|:----:|------|----------|----------|
| 1 | `comparison/summary.md` | 전체 | 7개 시스템의 전체 지형도 |
| 2 | `comparison/token-mapping.md` | "계층 구조 비교" + "핵심 차이점" | 토큰 설계의 3가지 분기점 |
| 3 | `comparison/token-usage-patterns.md` | 2.1절 "Button" | 같은 Button, 8가지 철학 |
| 4 | `comparison/dependency-audit-summary.md` | 3절 "핵심 발견" | 토큰 의존율의 3 클러스터 |

### 후반부 (1시간): 개별 시스템

관심 있는 **대비 쌍**을 골라 시스템별 문서를 나란히 읽기:

| 대비 쌍 | 관점 | 파일 |
|---------|------|------|
| Spectrum vs shadcn/ui | Design-first 극단 vs Code-first 극단 | `systems/spectrum.md` vs `systems/shadcn.md` |
| Ant Design vs Carbon | 알고리즘 파생 vs 정적 매핑 | `systems/antd-tokens.md` vs `systems/carbon-tokens.md` |
| Polaris vs MUI | 의도적 제약 vs 무한 유연성 | `systems/polaris-audit.md` vs `systems/material-audit.md` |

각 시스템은 3개 파일로 구성:
- `{name}.md` — 개요 (토큰, 컴포넌트, API, 접근성, 거버넌스)
- `{name}-tokens.md` — 토큰 코드 레벨 분석
- `{name}-audit.md` — 컴포넌트별 토큰 의존성 전수 조사

---

## 심화 코스: 반나절

연구 목적으로 깊게 파고 싶을 때.

### 토큰 아키텍처 트랙

1. `comparison/token-analysis-framework.md` — 분석 프레임워크 (정의/소비/거버넌스 3축)
2. `comparison/token-deep-dive.md` — 7개 시스템 토큰 종합 비교
3. `comparison/token-usage-patterns.md` — 전체 (Button 외 Card, Input, Dialog 등)
4. 관심 시스템의 `{name}-tokens.md` 정독

### Figma↔Code 매핑 트랙

1. `framework.md` — 분석 프레임워크 (6개 차원)
2. `comparison/component-mapping.md` — 매핑 비교 전체
3. `figma/figma-mapping-results.md` — Figma API 실측 데이터
4. `figma/README.md` + `figma/extract.py` — 추출 방법론
5. `figma/raw/*.json` — 원본 데이터

### 감사(audit) 트랙

1. `comparison/dependency-audit-summary.md` — 전체 비교
2. 관심 시스템의 `{name}-audit.md` — 라인 단위 분석
3. 실제 GitHub 저장소 코드와 대조 검증

---

## 읽을 때 주의점

### 별점(★) 해석

- 시스템마다 카운트 기준이 다름. Spectrum은 CSS 선언 단위, shadcn은 Tailwind 클래스 단위, Ant Design은 JS style 속성 단위.
- **절대 수치보다 패턴과 구조적 차이에 주목.**
- 별점은 상대적 우열이지 절대 품질이 아님.

### "Figma 매핑 없음" 해석

- shadcn/ui, Polaris, Ant Design의 Figma 매핑 부재는 품질 문제가 아님.
- Code가 single source of truth인 철학적 선택.
- "매핑 점수가 낮다" ≠ "나쁜 디자인 시스템".

### 토큰 수 해석

- shadcn/ui 32개 vs Material Web 1,700개.
- 적다고 부족한 게 아님. shadcn은 상태 토큰을 opacity modifier로 대체.
- Ant Design은 Seed 1개로 전체 팔레트 자동 파생 — "적은 입력, 많은 출력".

---

## 핵심 개념 사전

| 용어 | 의미 |
|------|------|
| **Seed 토큰** | 알고리즘 파생의 입력값. Ant Design의 `colorPrimary: '#1677ff'` |
| **Semantic 토큰** | 역할을 나타내는 토큰. `--text-primary`, `colorBgContainer` |
| **Component 토큰** | 컴포넌트 전용 토큰. `--spectrum-button-background-color-default` |
| **State Machine 패턴** | Polaris의 `--pc-*` 변수 재할당 방식. CSS 프로퍼티 없이 변수만 변경 |
| **3단계 fallback** | Spectrum의 `--highcontrast-* > --mod-* > --spectrum-*` CSS cascade |
| **DTCG** | W3C Design Tokens Community Group. 토큰 표준 포맷 |
| **MFI** | Mapping Fidelity Index. 이 프로젝트에서 제안하는 정량 매핑 충실도 지수 |
| **Headless** | 로직과 스타일 분리. React Aria, Radix, Base UI |
| **Compound Component** | 부모-자식 조합으로 UI 구성. Spectrum, Fluent 2 |
| **CVA** | Class Variance Authority. shadcn/ui의 variant 관리 도구 |
