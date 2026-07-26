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

## 구조

```
├── README.md
├── framework.md          # 분석 프레임워크 상세
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
├── analysis/             # 리뷰와 다음 단계
│   ├── review-and-next-steps.md # 문서 리뷰 (유용성/학습/고도화/심화)
│   ├── learning-guide.md # 학습 가이드
│   └── advancement-roadmap.md # 고도화 로드맵
└── figma/                # Figma API 추출 데이터
    ├── extract.py        # 추출 스크립트
    ├── figma-mapping-results.md # 실측 매핑 분석
    └── raw/              # 원본 JSON 데이터
```
