# Design Systems Benchmark

Figma ↔ Code 매핑 충실도를 중심으로 주요 컴포넌트 라이브러리를 분석하는 프로젝트.

## 분석 대상

### Tier 1 — Figma↔Code 공식 매핑
| 시스템 | 조직 | 코드 라이브러리 | Figma |
|--------|------|----------------|-------|
| Spectrum | Adobe | react-spectrum | 공식 킷 |
| Material Design | Google | MUI / Material Web | 공식 킷 |
| Fluent 2 | Microsoft | fluentui | 공식 킷 |
| Carbon | IBM | carbon | 공식 킷 |
| Polaris | Shopify | polaris | 공식 킷 |

### Tier 2 — Code-first + Figma 매핑
| 시스템 | 조직 | 코드 라이브러리 | Figma |
|--------|------|----------------|-------|
| shadcn/ui | 커뮤니티 | shadcn/ui + Radix | 커뮤니티 킷 |
| Ant Design | Alibaba | antd | 공식 킷 |

## 분석 프레임워크

각 시스템은 아래 차원으로 분석:

1. **토큰 아키텍처** — 계층, 네이밍, 테마 전환
2. **컴포넌트 인벤토리** — 수, 커버리지, 분류
3. **Figma↔Code 매핑 충실도** — 1:1 대응률, 네이밍/변형/토큰 정합성
4. **API 설계 철학** — composition vs config, 스타일링 접근법
5. **접근성** — ARIA, 키보드, 내장 수준
6. **동기화 거버넌스** — Figma↔Code 동기화 프로세스

## 학습 가이드

처음 읽는다면 → [**학습 가이드**](analysis/learning-guide.md)

- **30분 코스**: 핵심 결론 5가지만 빠르게
- **2시간 코스**: 비교 분석 + 시스템 대비 쌍 읽기
- **반나절 코스**: 토큰/매핑/감사 트랙별 심화

실전에 적용하려면 → [**플레이북**](playbook.md) — 오픈 라이브러리 없는 상용 제품에서
디자인 시스템을 추출·확장하는 8단계 절차. 이 벤치마크의 결론과 matchday-saas 구축 사례
(단계별 실물 산출물 대응표 포함)를 근거로 한다.

## 표준화 가능한 요소 (실측 리포트)

"디자인 시스템이 반드시 갖춰야 할 것"을 8개 시스템 소스에서 직접 세어 판정한 결과.
같은 데이터에서 두 형식으로 생성된다 — 읽기용 MD, 시각화용 HTML.

- [**analysis/design-system-standard-research.md**](analysis/design-system-standard-research.md) — 본문
- [**analysis/design-system-standard-research.html**](analysis/design-system-standard-research.html) —
  커버리지 히트맵·덤벨 차트 등 8종, 자기 완결 단일 파일
- [**analysis/design-system-specimens.html**](analysis/design-system-specimens.html) —
  **실물 견본 시트**. 8개 시스템의 Button·팔레트·타이포·radius·간격·elevation·조립 UI 를
  각자의 *실제 토큰 값*으로 렌더링. 원리 설명이 아니라 실물 비교.
- [**analysis/design-system-standard-research-visual.html**](analysis/design-system-standard-research-visual.html) —
  **확장판**. 위의 상위집합 + 네이밍 문법(이름 해부·어순 진영·상태 접미사) · 어휘 밀도 히트맵 ·
  variant 조합 폭발 · 분해 단위 · 컴포넌트별 의존율 히트맵 · MFI 매칭 근거

- 토큰 어휘 4축(값의 종류 / 색이 칠해지는 자리 / 의미 / 상태)별 8/8 교집합
- 정규 컴포넌트 커버리지 + 시스템별 실제 이름 대조표
- Button variant 축 8종 실측 (강조도·의미·크기·형태)
- 재감사: 토큰 의존율 재측정 · MFI-partial

생성: `python3 analysis/{extract_tokens,classify_tokens,extract_naming,extract_components,extract_values,measure_dependency,mfi,build_report,build_report_visual,build_specimens}.py`
(선행: `bash sources/clone.sh` — 분석 대상 소스 얕은 클론)

## 구조

```
├── README.md
├── framework.md          # 분석 프레임워크 상세
├── playbook.md           # 실전 플레이북 (상용 제품 → 추출·확장 8단계 + 사례 대응표)
├── systems/              # 시스템별 분석 (7개 시스템 × 3개 파일)
│   ├── {name}.md         # 개요
│   ├── {name}-tokens.md  # 토큰 코드 레벨 분석
│   └── {name}-audit.md   # 컴포넌트별 토큰 의존성 조사
├── comparison/           # 비교 분석
│   ├── summary.md        # 종합 비교 리포트 (핵심 발견 5가지)
│   ├── token-mapping.md  # 토큰 아키텍처 비교
│   ├── token-deep-dive.md # 토큰 종합 비교 (정의/소비/거버넌스)
│   ├── token-usage-patterns.md # 실제 코드 패턴 레퍼런스
│   ├── token-analysis-framework.md # 토큰 분석 프레임워크
│   ├── component-mapping.md # Figma↔Code 매핑 비교
│   └── dependency-audit-summary.md # 의존성 전수 조사 종합
├── analysis/             # 리뷰, 다음 단계, 실측 스크립트
│   ├── review-and-next-steps.md # 문서 리뷰 (유용성/학습/고도화/심화)
│   ├── learning-guide.md # 학습 가이드
│   ├── advancement-roadmap.md # 고도화 로드맵
│   ├── design-system-standard-research.md   # 표준화 가능 요소 리포트 (생성물)
│   ├── design-system-standard-research.html # 같은 리포트 시각화판 (생성물)
│   ├── design-system-standard-research-visual.html # 확장판 (생성물)
│   ├── design-system-specimens.html # 실물 견본 시트 (생성물)
│   ├── specimens.tmpl.html     # 견본 시트 템플릿
│   ├── extract_values.py      # 토큰 *값* 추출 (alias 체인 → hex/oklch)
│   ├── build_specimens.py     # values.json → 견본 시트 html
│   ├── report_visual.tmpl.html # 확장판 HTML 템플릿
│   ├── extract_naming.py      # 토큰 이름의 문법(표기·어순·깊이) 측정
│   ├── build_report_visual.py # data/*.json → 확장판 html
│   ├── extract_tokens.py      # 소스 → semantic 토큰 이름 추출
│   ├── classify_tokens.py     # 토큰 이름 → 정규 어휘 4축 분류·교집합
│   ├── extract_components.py  # 컴포넌트 인벤토리 + Figma variant 축
│   ├── measure_dependency.py  # 토큰 의존율 재측정 (느슨/엄격 2기준)
│   ├── mfi.py                 # Mapping Fidelity Index (부분)
│   ├── build_report.py        # data/*.json → 리포트 md + html
│   └── data/             # 측정 결과 JSON (스크립트 출력)
├── figma/                # Figma API 추출 데이터
│   ├── extract.py        # 추출 스크립트
│   ├── figma-mapping-results.md # 실측 매핑 분석
│   └── raw/              # 원본 JSON 데이터
└── sources/              # 분석 대상 라이브러리 얕은 클론 (.gitignore)
    ├── clone.sh          # 재현 스크립트
    └── MANIFEST.md       # 고정 커밋 SHA·기준일
```
