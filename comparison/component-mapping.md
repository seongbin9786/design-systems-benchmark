# Figma↔Code 매핑 비교 분석

## 종합 매핑 점수

| 시스템 | 1:1 대응률 | 네이밍 정합성 | Variant 정합성 | 토큰 정합성 | 매핑 방향 | Figma 공식 킷 |
|--------|:---------:|:-----------:|:------------:|:---------:|----------|:-----------:|
| Spectrum | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★☆ | Design-first | ✅ |
| Fluent 2 | ★★★★☆ | ★★★★☆ | ★★★★☆ | ★★★★☆ | 양방향 (동일 조직) | ✅ |
| Carbon | ★★★★☆ | ★★★★☆ | ★★★★☆ | ★★★☆☆ | Code-first + 병행 Figma | ✅ |
| Material | ★★☆☆☆ | ★★~★★★★ | ★★~★★★★ | ★~★★★★ | Spec-first (분산) | ✅ |
| Polaris | N/A | N/A | N/A | N/A | Code-first | ❌ 미확인 |
| Ant Design | ★★☆☆☆ | ★★★☆☆ | ★★☆☆☆ | ★★☆☆☆ | Code-first | ❌ (Sketch만) |
| shadcn/ui | N/A | N/A | N/A | N/A | Code-first | ❌ (커뮤니티만) |

## 핵심 발견

### 1. 공식 Figma 킷이 확인된 것은 4개뿐

초기 분류에서 "Tier 1 = Figma 공식 킷"으로 5개를 잡았지만, 실제 리서치 결과:

| 시스템 | 초기 분류 | 실제 |
|--------|----------|------|
| Spectrum | Tier 1 | ✅ 공식 킷 확인 |
| Material | Tier 1 | ✅ 공식 킷 확인 (단, multi-implementation 문제) |
| Fluent 2 | Tier 1 | ✅ 공식 킷 확인 |
| Carbon | Tier 1 | ✅ 공식 킷 확인 |
| Polaris | Tier 1 | ❌ **공식 킷 미확인** — Tools 페이지에 Figma 없음 |
| Ant Design | Tier 2 | ❌ **공식 Figma 없음** — Sketch만 공식 |
| shadcn/ui | Tier 2 | ❌ 공식 없음, 커뮤니티 8개 |

**수정 분류:**
- **Figma 공식 킷 보유**: Spectrum, Material, Fluent 2, Carbon (4개)
- **Code-first (Figma 공식 없음)**: Polaris, Ant Design, shadcn/ui (3개)

### 2. 자동 동기화 파이프라인은 어느 시스템에도 없음

7개 시스템 중 **Style Dictionary, Tokens Studio, 또는 자체 자동 변환 도구로 Figma Variables → Code tokens 완전 자동 파이프라인을 운영하는 곳은 없다.**

| 시스템 | 동기화 수준 | 도구 |
|--------|-----------|------|
| Spectrum | 반자동 (구조화된 계약) | 자체 Figma 플러그인 + Rust CLI + JSON Schema |
| Fluent 2 | 수동/반자동 (추정) | 비공개 |
| Carbon | 수동 | 별도 repo, Figma 라이브러리 퍼블리싱 |
| Material | 수동 (분산) | 없음 — 스펙 문서 참조 |
| Polaris | N/A | Code-first, Figma 연결 없음 |
| Ant Design | 수동 (Sketch) | Kitchen 플러그인 |
| shadcn/ui | N/A | 동기화 자체가 설계상 불필요 |

**Spectrum이 가장 구조화되어 있으나**, 이마저도 Figma Variables에서 Code 토큰으로의 완전 자동 변환이 아니라, JSON Schema 계약을 통한 반자동 정합성 보장이다.

### 3. 매핑 충실도를 결정하는 3가지 구조적 요인

| 요인 | 높은 충실도 | 낮은 충실도 |
|------|-----------|-----------|
| **소유 구조** | 동일 조직이 Figma+Code 소유 (Spectrum, Fluent, Carbon) | 분산/서드파티 (Material-MUI, Ant-커뮤니티) |
| **아키텍처** | 단일 구현 (Spectrum, Carbon) | 다중 구현 (Material), copy-paste (shadcn) |
| **철학** | Design-first (Spectrum) | Code-first (Polaris, shadcn, Ant) |

### 4. Figma↔Code 매핑의 스펙트럼

```
Design-first                                    Code-first
(Spectrum)  (Fluent)  (Carbon)  (Material)  (Ant)  (Polaris)  (shadcn)
    │          │         │         │          │        │          │
    ▼          ▼         ▼         ▼          ▼        ▼          ▼
 Figma가    동일 조직  병행 관리  스펙 중심  Sketch  코드=원본  코드=원본
 코드 선행   정렬      수동 sync  분산 구현  공식     Figma     Figma
                                                    부재      불필요
```

## 시스템별 매핑 상세 비교

### 네이밍 정합성

| 시스템 | 컴포넌트명 | Props/Variant명 | 토큰명 |
|--------|:---------:|:-------------:|:-----:|
| Spectrum | 직접 대응 (Button↔Button) | variant="cta" 등 일치 | --spectrum-* 공유 |
| Fluent 2 | 직접 대응 | appearance/size/shape 완전 일치 | camelCase 공유 |
| Carbon | PascalCase 일치 | kind/size v11 표준화 | Sass $token ↔ Figma Variables |
| Material (Web) | md-filled-button 등 | 스펙 variant = 별도 컴포넌트 | --md-sys-* 직접 대응 |
| Material (MUI) | 이름 다름 (AppBar↔Top App Bar) | variant="contained" ≠ Filled | palette.primary.main ≠ md.sys.color.primary |
| Ant Design | 재현 용이 | props 조합 공간 과대 | camelCase TS, 공식 연결 없음 |
| shadcn/ui | 대체로 일치 | asChild/className 매핑 불가 | CSS vars 수동 복제 |

### Variant 매핑

| 시스템 | Figma variant → Code props | 구조적 차이 |
|--------|--------------------------|-----------|
| Spectrum | 대부분 직접 매핑 | Scale은 Provider 수준 (개별 prop 아님) |
| Fluent 2 | Button 4축 완전 일치 | State는 CSS pseudo-class (Figma는 variant) |
| Carbon | kind/size 직접 매핑 | hasIconOnly는 Figma에서 별도 컴포넌트 |
| Material Web | variant = 별도 컴포넌트 | 1:1이나 구조 다름 |
| MUI | 3/5 variant만 매핑 | M2 기반, M3 variant 미지원 |
| Ant Design | 대표 조합만 재현 | boolean 조합 공간 과대 |
| shadcn/ui | 주요 variant만 | asChild, className 불가 |

### 토큰 매핑

| 시스템 | Figma 측 | Code 측 | 정합도 |
|--------|---------|---------|:-----:|
| Spectrum | Figma Variables (추정) | --spectrum-* CSS vars | ★★★★ |
| Fluent 2 | Figma Variables (Design Language) | @fluentui/tokens TS → CSS vars | ★★★★ |
| Carbon | Figma Variables (color 한정) | Sass $variables | ★★★ |
| Material | Figma styles/variables | --md-sys-* (Web), --mui-* (MUI) | ★~★★★★ |
| Polaris | 미확인 | --p-* CSS vars (TS source) | N/A |
| Ant Design | 서드파티 재현 | camelCase TS → --ant-* (v6) | ★★ |
| shadcn/ui | 커뮤니티 수동 복제 | --primary 등 CSS vars | N/A |
