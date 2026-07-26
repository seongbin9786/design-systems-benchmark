# Design Systems Benchmark — 종합 비교 리포트

> 분석 기준일: 2026-07-26
> 분석 대상: 7개 디자인 시스템 (Spectrum, Material, Fluent 2, Carbon, Polaris, shadcn/ui, Ant Design)
> 핵심 질문: **Figma ↔ Code 매핑 충실도**

---

## 1. 종합 평가 매트릭스

| 시스템 | 토큰 | 컴포넌트 | Figma↔Code | API 설계 | 접근성 | 거버넌스 | 종합 |
|--------|:----:|:------:|:---------:|:------:|:----:|:------:|:----:|
| **Spectrum** | ★★★★ | ★★★★★ | ★★★★☆ | ★★★★★ | ★★★★★ | ★★★★☆ | **4.5** |
| **Fluent 2** | ★★★★ | ★★★★ | ★★★★☆ | ★★★★ | ★★★★★ | ★★★☆☆ | **4.1** |
| **Carbon** | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★★★★ | ★★★☆☆ | **4.0** |
| **Material** | ★★★★ | ★★★ | ★★☆☆☆ | ★★★★ | ★★★☆☆ | ★★☆☆☆ | **3.1** |
| **Ant Design** | ★★★★ | ★★★★★ | ★★☆☆☆ | ★★★★ | ★★★☆☆ | ★★★☆☆ | **3.5** |
| **Polaris** | ★★★★ | ★★★★ | N/A | ★★★★ | ★★★★ | ★★☆☆☆ | **3.6*** |
| **shadcn/ui** | ★★★ | ★★★★ | N/A | ★★★★★ | ★★★★ | ★★★★ | **4.0*** |

> *Polaris, shadcn/ui는 Figma↔Code 매핑 평가 불가 (공식 Figma 킷 부재). 종합 점수는 해당 차원 제외.

---

## 2. 핵심 발견 5가지

### 2.1 공식 Figma 킷이 있는 시스템은 4개뿐

초기 분류에서 5개를 "Figma 공식"으로 잡았으나, 실제 검증 결과:

| 공식 Figma 킷 확인 | 공식 Figma 킷 없음 |
|-------------------|-------------------|
| Spectrum, Material, Fluent 2, Carbon | Polaris (미확인), Ant Design (Sketch만), shadcn/ui (커뮤니티만) |

**"유명 디자인 시스템 = Figma 공식 지원"이라는 가정이 틀렸다.** Polaris는 Tools 페이지에 Figma가 없고, Ant Design은 공식 리소스가 전부 Sketch이며, shadcn/ui는 철학적으로 Figma를 배제한다.

### 2.2 Figma Variables → Code 자동 동기화는 어느 시스템에도 없음

7개 시스템 중 **완전 자동 토큰 동기화 파이프라인을 운영하는 곳이 없다.**

- Spectrum이 가장 구조화 (JSON Schema 계약 + Rust CLI + Figma 플러그인)
- 그러나 이마저도 "반자동 정합성 보장"이지 "자동 변환"이 아님
- Style Dictionary, Tokens Studio를 공식 사용하는 곳도 없음

**이것은 업계 전체의 미해결 문제이다.** Figma Variables API(2023~)가 비교적 새로우며, 디자인↔코드 동기화는 여전히 수동/반자동에 머문다.

### 2.3 매핑 충실도는 "소유 구조"가 결정

| 소유 구조 | 시스템 | 매핑 충실도 |
|----------|--------|:---------:|
| 동일 조직, 단일 구현 | Spectrum, Carbon | 높음 |
| 동일 조직, 다중 구현 | Fluent 2 | 높음 (개념적) |
| 스펙 + 서드파티 구현 | Material (MUI) | 낮음 |
| Code-first, Figma 부재 | Polaris, Ant, shadcn | 평가 불가 |

**디자인 팀과 개발 팀이 같은 조직에서 같은 시스템을 소유할 때 매핑 충실도가 높아진다.** 도구(Style Dictionary 등)보다 조직 구조가 더 결정적이다.

### 2.4 Code-first 시스템은 Figma 매핑이 "결함"이 아니라 "선택"

shadcn/ui, Polaris, Ant Design은 Code가 single source of truth이다:

- **shadcn/ui**: copy-paste 아키텍처 → 코드 단일 원본 부재 → Figma 매핑 대상 자체가 유동적
- **Polaris**: className/style 탈출구 제거 → 코드가 디자인 규범 → Figma 불필요
- **Ant Design**: 정교한 토큰 알고리즘이 공식 Figma 아티팩트와 연결되지 않는 역설

이들에게 "Figma↔Code 매핑 점수가 낮다"는 것은 품질 문제가 아니라 **아키텍처 철학의 차이**이다.

### 2.5 토큰 아키텍처의 우수함 ≠ 디자인 동기화

| 시스템 | 토큰 정교함 | Figma 동기화 |
|--------|:---------:|:---------:|
| Ant Design | ★★★★★ (알고리즘 파생) | ★☆☆☆☆ |
| Spectrum | ★★★★☆ | ★★★★☆ |
| shadcn/ui | ★★★☆☆ | N/A |

Ant Design의 Seed→Map→Alias 알고리즘 파생은 동적 테마 생성에서 가장 정교하지만, 이 토큰 체계가 공식 Figma 아티팩트와 전혀 연결되지 않는다. **토큰 설계의 우수함과 디자인-개발 동기화는 독립 변수이다.**

---

## 3. API 설계 철학 스펙트럼

```
Configuration 중심                              Composition 중심
(Ant Design)  (MUI)  (Carbon)  (Polaris)  (Fluent)  (Spectrum)  (shadcn)
     │          │       │        │          │         │           │
     ▼          ▼       ▼        ▼          ▼         ▼           ▼
  items/     sx prop  props   config+    slot-based  React Aria  CVA +
  columns    + theme  기반    comp 분리  compound    compound    Radix
  데이터     4단계            (원자/구조)  3-layer     3단계      full ownership
  주입                                                      
```

| 시스템 | Headless 분리 | 스타일링 | 커스터마이징 자유도 |
|--------|:-----------:|---------|:----------------:|
| Spectrum | ✅ React Aria (54개) | CSS Modules → CSS (s2) | 중간 (의도적 제약) |
| Fluent 2 | ⚠️ preview | Griffel atomic CSS-in-JS | 중간 |
| Carbon | ❌ | SCSS Modules | 낮음 |
| Material (MUI) | ⚠️ hooks | sx/styled/theme | 높음 |
| Polaris | ❌ | CSS Modules + custom props | 매우 낮음 (의도적) |
| Ant Design | ⚠️ rc-* (내부) | CSS-in-JS → CSS vars | 중간 (토큰 중심) |
| shadcn/ui | ✅ Radix/Base UI | Tailwind CSS | 매우 높음 (full ownership) |

---

## 4. 접근성 비교

| 시스템 | 수준 | 핵심 메커니즘 | 고유 패턴 |
|--------|:----:|-------------|---------|
| Spectrum | ★★★★★ | React Aria (WAI-ARIA APG) | 54개 headless 패키지, 30+ 언어, 13 캘린더 |
| Fluent 2 | ★★★★★ | tabster + react-aria | disabledFocusable, High Contrast 전용 테마 |
| Carbon | ★★★★★ | IBM Accessibility Checklist | iconDescription 강제, Layer 시스템 |
| Polaris | ★★★★☆ | props 기반 ARIA 자동화 | on-bg-fill 페어링 토큰 (대비율 구조적 보장) |
| shadcn/ui | ★★★★☆ | Radix 위임 | 스타일 수정과 무관하게 접근성 유지 |
| Material | ★★★☆☆ | WAI-ARIA 패턴 | 기본 contrast 3:1 (WCAG AA 미달) |
| Ant Design | ★★★☆☆ | rc-* 내부 레이어 | 공식 WCAG 선언 없음, icon-only aria-label 미자동 |

---

## 5. 컴포넌트 커버리지

| 시스템 | 수 | 강점 영역 | 고유 컴포넌트 |
|--------|:--:|---------|-------------|
| Carbon | 100+ | 엔터프라이즈, Fluid 변형 | FluidForm, ChatButton, AILabel |
| Spectrum | 82+ | Color(7종), Date/DnD | ColorWheel, DropZone, LogicButton |
| Ant Design | 73+6 | Data Entry/Display | Transfer, TreeSelect, Cascader, Mentions, QRCode |
| MUI | 62 | 범용 + 스펙 외 확장 | DataGrid (MUI X), Masonry |
| shadcn/ui | 63 | AI/메시징 (신규) | Bubble, Message, Attachment, Marker |
| Polaris | 89 (docs) | 커머스, 레이아웃 프리미티브 | IndexTable, IndexFilters, Box/Stack 계열 |
| Fluent 2 | ~50 | Microsoft 생태계 | TeachingPopover, Persona, SwatchPicker |
| Material Web | ~21 | 스펙 충실 | — (maintenance mode) |

---

## 6. 벤치마크 시사점

### Figma↔Code 매핑을 개선하려면

1. **도구보다 조직**: Style Dictionary 도입보다 디자인-개발 동일 조직 소유가 더 효과적
2. **계약(Contract) 기반**: Spectrum의 JSON Schema처럼 양쪽이 공유하는 구조화된 계약이 핵심
3. **토큰 네이밍 통일**: Figma Variables명과 Code 토큰명이 다르면 자동화 불가
4. **Component API 정렬**: Fluent 2처럼 "Figma properties map to code"를 명시적 목표로 설정

### Code-first 시스템을 위한 대안

Figma 매핑이 철학적으로 불필요한 시스템(shadcn, Polaris)에는:
- 코드 문서 자체가 디자인 명세 (Storybook, 문서 사이트)
- v0.dev, DESIGN.md(Ant) 등 AI/기계 판독 가능 명세
- Figma MCP/Dev Mode보다 **코드 → 디자인 역방향** 도구가 적합

### 미해결 문제

- Figma Variables → Code tokens 완전 자동 동기화는 업계 전체 미해결
- Component-level 매핑 (auto-layout → flex/grid)은 개념적 대응만 존재
- 다중 구현(Material) 또는 copy-paste(shadcn) 아키텍처에서 "단일 매핑 대상" 정의 불가

---

## 7. 파일 인덱스

| 파일 | 내용 |
|------|------|
| `systems/spectrum.md` | Adobe Spectrum 상세 분석 (705줄) |
| `systems/material.md` | Material Design 상세 분석 (564줄) |
| `systems/fluent.md` | Fluent 2 상세 분석 (543줄) |
| `systems/carbon.md` | Carbon 상세 분석 (517줄) |
| `systems/polaris.md` | Polaris 상세 분석 (578줄) |
| `systems/shadcn.md` | shadcn/ui 상세 분석 |
| `systems/antd.md` | Ant Design 상세 분석 (487줄) |
| `comparison/component-mapping.md` | Figma↔Code 매핑 비교 |
| `comparison/token-mapping.md` | 토큰 아키텍처 비교 |
| `comparison/summary.md` | 종합 비교 테이블 |
| `figma/README.md` | Figma API 분석 가이드 |
| `framework.md` | 분석 프레임워크 |
