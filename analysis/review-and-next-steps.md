# 문서화된 내용 리뷰와 다음 단계

> 리뷰 기준일: 2026-07-27
> 대상: systems/ 21개 파일, comparison/ 7개 파일, figma/ 추출 데이터

---

## 1. 가장 유익한 정보 TOP 5

### 1위: "Figma Variables → Code 자동 동기화는 어느 시스템에도 없다"

`comparison/summary.md` 핵심 발견 2.2. 7개 시스템 전수 조사 결과, 완전 자동 토큰 동기화 파이프라인을 운영하는 곳이 **0곳**. 이것은 개별 시스템의 문제가 아니라 **업계 전체의 미해결 문제**라는 결론.

**왜 가장 유익한가**: 이 프로젝트의 핵심 질문("Figma↔Code 매핑 충실도")에 대해 "아직 아무도 해결 못했다"는 답을 내렸기 때문. 이후 모든 분석의 기준점이 됨.

### 2위: 매핑 충실도를 결정하는 것은 도구가 아니라 소유 구조

`comparison/summary.md` 핵심 발견 2.3 + `comparison/component-mapping.md` 핵심 발견 3.

| 소유 구조 | 매핑 충실도 | 시스템 |
|----------|:---------:|--------|
| 동일 조직, 단일 구현 | 높음 | Spectrum, Carbon |
| 동일 조직, 다중 구현 | 높음 (개념적) | Fluent 2 |
| 스펙 + 서드파티 구현 | 낮음 | Material (MUI) |
| Code-first, Figma 부재 | 평가 불가 | Polaris, Ant, shadcn |

**왜 유익한가**: "Style Dictionary를 도입하면 해결된다"는 흔한 가설을 반박. 조직 구조가 기술 도구보다 결정적이라는 통찰.

### 3위: Button 토큰 소비 패턴 8개 시스템 비교

`comparison/token-usage-patterns.md` 2.1절. 동일한 "Button" 컴포넌트가 8개 시스템에서 어떻게 토큰을 소비하는지 실제 코드로 비교.

- Spectrum: 3단계 CSS fallback (`--highcontrast-* > --mod-* > --spectrum-*`)
- Polaris: Custom Property State Machine (변수 재할당만, CSS 프로퍼티 없음)
- shadcn/ui: Tailwind 유틸리티 + opacity modifier (`hover:bg-primary/90`)
- Ant Design: `genStyleHooks` + ComponentToken 알고리즘 파생

**왜 유익한가**: 추상적 "토큰 아키텍처" 개념을 구체적 코드로 보여줌. 각 시스템의 철학 차이가 한 컴포넌트에서 어떻게 나타나는지 직접 비교 가능.

### 4위: Figma API 실측 매칭률 vs 이전 추정

`figma/figma-mapping-results.md`. Community Duplicate 파일에서 실제 COMPONENT_SET을 추출해 Code 컴포넌트와 1:1 대조.

| 시스템 | 이전 추정 | 실측 | 차이 원인 |
|--------|:-------:|:---:|---------|
| Carbon | ~90% | **97%** | 예상이 보수적 |
| Material 3 | ~70% | **92%** | Material Web 기준 |
| Spectrum | ~90% | **70%** | 레이아웃/유틸 컴포넌트가 Figma에 없음 |

**왜 유익한가**: "추정"을 "실측"으로 전환. 특히 Spectrum이 70%로 낮은 이유는 레이아웃 프리미티브(Flex, Grid)가 Figma에 존재하지 않기 때문이라는 발견.

### 5위: 토큰 의존율 3 클러스터

`comparison/dependency-audit-summary.md`. 7개 시스템 × 10개 컴포넌트 라인 단위 분석.

```
높음 (90%+)     중간 (50~90%)      낮음 (~50% 이하)
Spectrum        Fluent 2           Carbon
Material Web    Ant Design         Polaris
                MUI                shadcn/ui
```

**왜 유익한가**: "토큰 의존율 낮음"에도 두 가지 원인이 있음 — Carbon/Polaris는 "레이아웃 값 미토큰화", shadcn은 "철학적 선택". 같은 숫자, 다른 의미.

---

## 2. 어떻게 이해/학습하는 게 유리한가

### 추천 학습 경로 (3단계)

#### 단계 1: 큰 그림 (30분)

1. `comparison/summary.md` — 핵심 발견 5가지만 읽기
2. `comparison/component-mapping.md` — "매핑의 스펙트럼" 다이어그램
3. `comparison/token-mapping.md` — 계층 구조 비교표

**목표**: "Figma↔Code 매핑이 왜 어려운지" 구조적으로 이해.

#### 단계 2: 패턴 체득 (1시간)

4. `comparison/token-usage-patterns.md` — Button 비교 (2.1절) 정독
5. `comparison/token-deep-dive.md` — 5.2절 "다크모드 3가지 패러다임"
6. `comparison/dependency-audit-summary.md` — 3.2절 "토큰 의존율 낮음의 두 가지 원인"

**목표**: 각 시스템의 "철학"이 코드에서 어떻게 나타나는지 체득.

#### 단계 3: 개별 시스템 심화 (시스템당 30분)

7. 관심 시스템의 `systems/{name}.md` → `systems/{name}-tokens.md` → `systems/{name}-audit.md` 순서로 읽기

**추천 대비 쌍**:
- **Spectrum vs shadcn/ui**: Design-first 극단 vs Code-first 극단
- **Ant Design vs Carbon**: 알고리즘 파생 vs 정적 매핑
- **Polaris vs MUI**: 의도적 제약 vs 무한 유연성

### 학습 시 주의점

- **별점(★)에 집착하지 말 것**: 시스템마다 카운트 기준이 다름 (dependency-audit-summary.md 상단 주의 참조). 절대 수치보다 패턴과 구조적 차이에 주목.
- **"Figma 매핑 없음 = 나쁨"이 아님**: shadcn/ui, Polaris는 철학적으로 Figma를 배제. "결함"이 아니라 "선택".
- **토큰 수 ≠ 품질**: shadcn 32개 vs Material 1,700개. 적다고 부족한 게 아님.

---

## 3. 고도화 방법

### 3.1 정량 평가 체계 도입 (우선순위: 높음)

현재 별점(★)은 주관적. 재현 가능한 점수 체계가 필요.

**제안: Figma↔Code 매핑 충실도 지수 (Mapping Fidelity Index)**

```
MFI = w1 × 컴포넌트_매칭률
    + w2 × 네이밍_정합성
    + w3 × Variant_정합성
    + w4 × 토큰_정합성
    + w5 × 구조적_대응

각 항목 0~100점, 가중치는 연구 목적에 따라 조정
```

- 컴포넌트 매칭률: Figma 실측 데이터에서 이미 산출 가능 (figma-mapping-results.md)
- 네이밍 정합성: 자동화 가능 (Figma COMPONENT_SET 이름 vs Code export 이름 편집 거리)
- Variant 정합성: 반자동 (Figma variant properties vs Code props 수동 매핑)
- 토큰 정합성: Figma Variables 데이터 필요 (현재 403으로 미확보)
- 구조적 대응: 수동 평가 (auto-layout ↔ flex/grid)

### 3.2 Figma Variables 데이터 확보 (우선순위: 높음)

현재 가장 큰 갭. 4개 시스템 모두 Community Duplicate 파일이라 Variables API가 403.

**해결 방법**:
1. **원본 파일 접근**: 각 디자인 시스템의 Figma Community 페이지에서 "Duplicate"가 아닌 원본 파일의 file_key 확보. 일부는 공개 팀 프로젝트로 Variables 접근 가능.
2. **Figma UI 수동 추출**: Dev Mode에서 Variables 패널 스크린샷 + 수동 기록
3. **Tokens Studio 플러그인**: 원본 파일에 Tokens Studio가 설치되어 있으면 JSON 내보내기 가능

### 3.3 DTCG 표준 대비 분석 (우선순위: 중간)

W3C Design Tokens Community Group의 표준 포맷과 각 시스템의 토큰 포맷을 비교.

- Carbon이 DTCG JSON을 출력하는 유일한 시스템 (token-deep-dive.md 4.3절)
- 나머지 시스템의 토큰을 DTCG로 변환하면 어떤 정보가 손실되는지 분석
- DTCG가 Figma Variables ↔ Code 브리지의 표준이 될 수 있는지 평가

### 3.4 Figma Dev Mode / MCP 분석 (우선순위: 중간)

Figma의 최근 도구들이 매핑 갭을 얼마나 해소하는지 분석.

- **Dev Mode**: 코드 스니펫 생성, Variables 표시, 측정 도구
- **Figma MCP Server**: AI 에이전트가 Figma 파일에 직접 접근
- **Spectrum MCP 서버 3개**: token-deep-dive.md 4.4절에서 언급만, 상세 분석 없음

### 3.5 대화형 시각화 (우선순위: 낮음)

현재 모든 분석이 마크다운 테이블. 한눈에 비교하기 어려움.

- 토큰 계층 구조 트리 시각화 (시스템별 나란히)
- 매핑 충실도 레이더 차트
- Button 토큰 소비 플로우 다이어그램

---

## 4. 심화 조사 방법

### 4.1 Figma Variables API 심화

**현재 상태**: 4개 시스템 모두 403 (Community Duplicate 제한).

**조사 방법**:
1. Figma Community에서 원본 파일 URL 수집 → file_key 추출
2. `extract.py`의 `FILES` 딕셔너리에 원본 file_key로 교체
3. Variables API 재실행 → `figma/raw/{name}-variables.json` 확보
4. Code 토큰명 vs Figma Variables명 자동 대조 스크립트 작성

**기대 산출물**: 시스템별 "Figma Variables ↔ Code tokens 정합성 테이블"

### 4.2 토큰 동기화 도구 생태계 조사

현재 "어느 시스템도 자동 동기화가 없다"에서 멈춤. **해결을 시도하는 도구들**을 조사.

| 도구 | 조사 내용 |
|------|----------|
| **Tokens Studio** | Figma Variables ↔ JSON 양방향 동기화 능력, DTCG 지원 |
| **Style Dictionary** | Figma 입력 지원 여부, 변환 파이프라인 유연성 |
| **Figma Variables API** | 읽기/쓰기 가능 범위, 웹훅/이벤트 지원 |
| **Specify** | Figma → Code 자동 변환, 컴포넌트 매핑 |
| **Anima / Locofy** | Figma → Code 생성, 토큰 매핑 정확도 |

### 4.3 신규 시스템 추가 조사

현재 7개 시스템 외에 주목할 만한 대상:

| 시스템 | 추가 이유 |
|--------|----------|
| **Base UI (MUI)** | MUI의 headless 전환. Material에서 분리된 새로운 접근 |
| **Radix Themes** | shadcn의 기반인 Radix의 공식 테마 시스템 |
| **Primer (GitHub)** | GitHub의 디자인 시스템. Figma ↔ Code 동기화 사례 |
| **Lightning (Salesforce)** | 엔터프라이즈 규모 Figma ↔ Code 운영 사례 |

### 4.4 실사용 팀 사례 조사

디자인 시스템 "설계"가 아니라 "운영" 관점의 사례:

- Figma ↔ Code 동기화를 실제로 달성한 팀이 있는가?
- 어떤 도구/프로세스를 사용하는가?
- 실패 사례와 원인은?

**조사 채널**: Config (Figma 컨퍼런스) 세션, 디자인 시스템 Slack 커뮤니티, GitHub Discussions

### 4.5 컴포넌트 레벨 구조 매핑 심화

현재 "auto-layout ↔ flex/grid"가 개념적 대응만 존재 (component-mapping.md).

**심화 방법**:
1. Figma 노드 트리에서 auto-layout 속성 추출 (`layoutMode`, `primaryAxisAlignItems`, `paddingLeft` 등)
2. Code 컴포넌트의 CSS flex/grid 속성과 1:1 대조
3. "Figma auto-layout = CSS flexbox" 매핑 규칙 테이블 작성
4. 한계점 분석: Figma에서 표현 불가한 CSS 속성 (grid-template-areas, aspect-ratio 등)

---

## 5. 현재 문서 구조 평가

### 잘 된 점

- **3층 구조** (개요 → 토큰 → 감사)가 일관적
- **비교 문서**가 시스템별 문서를 가로지르는 통찰 제공
- **실제 코드 스니펫**이 추상적 개념을 구체화
- **Figma API 실측**이 추정을 검증으로 전환

### 개선할 점

| 문제 | 위치 | 개선안 |
|------|------|--------|
| 학습 경로 없음 | README.md | 이 문서의 2절을 README에 링크 |
| 별점 기준 불명확 | summary.md | 정량 평가 체계 (3.1절) 도입 |
| Figma Variables 갭 | figma/ | 원본 파일 접근 또는 수동 추출 |
| 시스템별 파일이 3개로 분산 | systems/ | 통합 인덱스 또는 네비게이션 추가 |
| 최신 도구 분석 없음 | — | Figma Dev Mode, MCP, Tokens Studio 추가 |

---

## 6. 우선순위 요약

| 순위 | 항목 | 유형 | 의존성 |
|:----:|------|------|--------|
| 1 | Figma Variables 데이터 확보 | 심화 조사 | 원본 file_key |
| 2 | 정량 평가 체계 (MFI) 도입 | 고도화 | 1번 완료 시 정밀도 향상 |
| 3 | 토큰 동기화 도구 생태계 조사 | 심화 조사 | 없음 |
| 4 | 학습 가이드 README 통합 | 학습 | 없음 |
| 5 | DTCG 표준 대비 분석 | 고도화 | 없음 |
| 6 | Figma Dev Mode / MCP 분석 | 고도화 | 없음 |
| 7 | 신규 시스템 추가 | 심화 조사 | 없음 |
| 8 | 대화형 시각화 | 고도화 | 2번 완료 시 효과적 |
