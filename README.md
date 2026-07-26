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

## 구조

```
├── README.md
├── framework.md          # 분석 프레임워크 상세
├── systems/              # 시스템별 분석
│   ├── spectrum.md
│   ├── material.md
│   ├── fluent.md
│   ├── carbon.md
│   ├── polaris.md
│   ├── shadcn.md
│   └── antd.md
├── comparison/           # 비교 분석
│   ├── token-mapping.md
│   ├── component-mapping.md
│   └── summary.md
└── figma/                # Figma API 추출 데이터
```
