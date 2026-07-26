# 고도화 로드맵

> 현재 문서의 갭을 메우고 연구 깊이를 더하기 위한 실행 계획
> 작성일: 2026-07-27

---

## Phase 1: 데이터 갭 해소

### 1.1 Figma Variables 데이터 확보

**현재 상태**: 4개 시스템 모두 Community Duplicate 파일 → Variables API 403.

**실행 단계**:

1. 각 디자인 시스템 공식 사이트에서 원본 Figma 파일 URL 수집
   - Spectrum: spectrum.adobe.com → Figma 링크
   - Material: m3.material.io → Figma Community 링크
   - Fluent 2: fluent2.microsoft.design → Figma 링크
   - Carbon: carbondesignsystem.com → Figma 링크

2. 원본 file_key로 `figma/extract.py`의 `FILES` 딕셔너리 업데이트

3. Variables API 재실행:
   ```bash
   export FIGMA_TOKEN="your-token"
   python3 figma/extract.py
   ```

4. 결과 검증: `figma/raw/{name}-variables.json`에 `error` 대신 실제 데이터가 있는지 확인

**대안**: API 접근이 계속 불가하면 Figma UI에서 Dev Mode → Variables 패널 수동 캡처

### 1.2 Figma Variables ↔ Code 토큰 자동 대조

Variables 데이터 확보 후 실행:

```python
# figma/token-matcher.py (새로 작성)
# Figma Variables 이름 vs Code 토큰 이름 편집 거리 계산
# 출력: 시스템별 정합성 테이블 (CSV)
```

대조 기준:
- 이름 유사도 (Levenshtein distance)
- 값 일치도 (동일 색상/수치)
- 계층 대응 (Figma 컬렉션 ↔ Code 계층)

---

## Phase 2: 정량 평가 체계

### 2.1 Mapping Fidelity Index (MFI) 정의

```
MFI = 0.30 × 컴포넌트_매칭률
    + 0.20 × 네이밍_정합성
    + 0.20 × Variant_정합성
    + 0.20 × 토큰_정합성
    + 0.10 × 구조적_대응
```

각 항목 측정 방법:

| 항목 | 측정 방법 | 데이터 출처 | 자동화 |
|------|----------|-----------|:-----:|
| 컴포넌트 매칭률 | Figma COMPONENT_SET vs Code export 1:1 매칭 | figma-mapping-results.md | ✅ |
| 네이밍 정합성 | 이름 편집 거리 정규화 | Figma API + Code AST | ✅ |
| Variant 정합성 | Figma variant properties 수 vs Code props 수 + 의미 매칭 | 반자동 | ⚠️ |
| 토큰 정합성 | Figma Variables vs Code tokens 이름/값 대조 | Phase 1 데이터 | ✅ |
| 구조적 대응 | auto-layout 속성 vs CSS flex/grid 수동 평가 | 수동 | ❌ |

### 2.2 MFI 산출 스크립트

```python
# analysis/mfi.py (새로 작성)
# 입력: figma/raw/*.json + systems/*-audit.md 데이터
# 출력: 시스템별 MFI 점수 + 레이더 차트 데이터
```

---

## Phase 3: 도구 생태계 조사

### 3.1 토큰 동기화 도구 비교

| 도구 | 조사 항목 |
|------|----------|
| **Tokens Studio** | Figma Variables 양방향 동기화, DTCG 지원, 버전 관리 |
| **Style Dictionary** | Figma 입력 플러그인, 변환 파이프라인, 커뮤니티 규모 |
| **Specify** | Figma → Code 자동 변환 정확도, 컴포넌트 매핑 |
| **Figma Variables API** | 읽기/쓰기 범위, 웹훅, Rate limit |

**산출물**: `analysis/sync-tools-comparison.md`

### 3.2 Figma Dev Mode / MCP 분석

| 항목 | 조사 내용 |
|------|----------|
| Dev Mode | 코드 스니펫 정확도, Variables 표시, CSS 변환 품질 |
| Figma MCP | AI 에이전트 접근 가능 데이터, 컴포넌트 매핑 활용 |
| Spectrum MCP 3개 | token-deep-dive.md 4.4절 언급 내용 상세화 |

**산출물**: `analysis/figma-devmode-mcp.md`

---

## Phase 4: 분석 확장

### 4.1 DTCG 표준 대비

- Carbon의 DTCG JSON 출력 분석
- 나머지 시스템 토큰 → DTCG 변환 시 손실 정보 파악
- DTCG가 Figma↔Code 브리지 표준이 될 수 있는지 평가

**산출물**: `analysis/dtcg-comparison.md`

### 4.2 신규 시스템 추가

| 시스템 | 우선순위 | 이유 |
|--------|:-------:|------|
| Primer (GitHub) | 높음 | Figma↔Code 동기화 실제 운영 사례 |
| Base UI (MUI) | 중간 | MUI headless 전환, Material과 대비 |
| Radix Themes | 중간 | shadcn 기반의 공식 테마 시스템 |
| Lightning (Salesforce) | 낮음 | 엔터프라이즈 규모 참고 |

### 4.3 auto-layout ↔ flex/grid 구조 매핑

1. Figma 노드 트리에서 auto-layout 속성 추출
2. Code CSS와 1:1 대조
3. 매핑 규칙 테이블 + 한계점 분석

**산출물**: `analysis/structure-mapping.md`

---

## Phase 5: 시각화

### 5.1 대화형 비교 대시보드

- 토큰 계층 구조 트리 (시스템별 나란히)
- MFI 레이더 차트
- Button 토큰 소비 플로우 다이어그램
- 매핑 충실도 스펙트럼 시각화

**도구**: 단일 HTML 파일 (Artifact), D3.js 또는 vanilla SVG

---

## 파일 구조 변경안

```
analysis/                          # 신규 디렉터리
├── review-and-next-steps.md       # 이번 리뷰 결과
├── learning-guide.md              # 학습 가이드
├── advancement-roadmap.md         # 이 파일
├── sync-tools-comparison.md       # Phase 3 산출물
├── figma-devmode-mcp.md           # Phase 3 산출물
├── dtcg-comparison.md             # Phase 4 산출물
├── structure-mapping.md           # Phase 4 산출물
└── mfi.py                         # Phase 2 스크립트

figma/
├── token-matcher.py               # Phase 1 스크립트
└── raw/                           # Variables 데이터 추가
```
