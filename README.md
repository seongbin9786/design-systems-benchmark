# Design Systems Benchmark

Figma ↔ Code 매핑 충실도를 중심으로 주요 컴포넌트 라이브러리를 분석하는 프로젝트.

📊 **리포트 웹판 → https://design-systems-benchmark.vercel.app**
(목차 · 본문 · 확장판 · 실물 견본. `analysis/standard-research/reports/` 를 그대로 배포한다)

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
파이프라인과 계층 구조는 → [**analysis/standard-research/README.md**](analysis/standard-research/README.md)

리포트 (전부 생성물 — 직접 편집하지 말 것). 웹판은 각 항목의 🌐 링크:

- [**본문**](analysis/standard-research/reports/design-system-standard-research.md) — 읽기용 MD ·
  [🌐](https://design-systems-benchmark.vercel.app/design-system-standard-research.md)
- [**시각화**](analysis/standard-research/reports/design-system-standard-research.html) — 커버리지 히트맵·덤벨 차트 등 8종 ·
  [🌐](https://design-systems-benchmark.vercel.app/design-system-standard-research)
- [**확장판**](analysis/standard-research/reports/design-system-standard-research-visual.html) —
  위의 상위집합 + 네이밍 문법(이름 해부·어순 진영) · 어휘 밀도 · variant 폭발 · 분해 단위 ·
  [🌐](https://design-systems-benchmark.vercel.app/design-system-standard-research-visual)
- [**실물 견본**](analysis/standard-research/reports/design-system-specimens.html) —
  Button 32개·팔레트 80칸·타이포·radius·간격·elevation·조립 UI 를 각 시스템의 *실제 값*으로 렌더링 ·
  [🌐](https://design-systems-benchmark.vercel.app/design-system-specimens)

```bash
bash sources/clone.sh                        # 선행: 분석 대상 소스 얕은 클론
python3 analysis/standard-research/run.py    # 전체 재생성 (index.html 포함)
vercel deploy --prod                         # 웹판 갱신 (vercel.json 이 reports/ 를 가리킨다)
```

## 구조

```
├── README.md
├── vercel.json           # 정적 배포 설정 (outputDirectory = reports/)
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
├── analysis/             # 리뷰·다음 단계 문서 + 실측 연구
│   ├── review-and-next-steps.md # 문서 리뷰 (유용성/학습/고도화/심화)
│   ├── learning-guide.md # 학습 가이드
│   ├── advancement-roadmap.md # 고도화 로드맵
│   └── standard-research/ # 표준화 가능 요소 실측 (계층 분리)
│       ├── README.md     # 파이프라인·의존 그래프·계층 규칙
│       ├── run.py        # 전체 실행 (의존 순서 강제)
│       ├── tools/        # 측정·렌더 스크립트 + paths.py + viz.py + templates/
│       ├── curated/      # 수기 입력 (스크립트가 덮어쓰지 않음)
│       ├── measured/     # 1차 측정 (sources·figma 직접)
│       ├── derived/      # 2차 파생 (measured 입력)
│       └── reports/      # 최종 생성물 (편집 금지) — index.html 이 배포 루트
├── figma/                # Figma API 추출 데이터
│   ├── extract.py        # 추출 스크립트
│   ├── figma-mapping-results.md # 실측 매핑 분석
│   └── raw/              # 원본 JSON 데이터
└── sources/              # 분석 대상 라이브러리 얕은 클론 (.gitignore)
    ├── clone.sh          # 재현 스크립트
    └── MANIFEST.md       # 고정 커밋 SHA·기준일
```
