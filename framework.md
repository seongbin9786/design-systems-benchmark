# 분석 프레임워크

## 1. 토큰 아키텍처

| 항목 | 분석 내용 |
|------|----------|
| 계층 구조 | primitive → semantic → component-level 단계 구분 |
| 네이밍 컨벤션 | 표기법 (dot.notation, --kebab-case, camelCase) |
| 테마 전환 | 다크모드/커스텀 테마 메커니즘 |
| 토큰 포맷 | CSS variables, JSON, Style Dictionary, Figma Variables |
| 동기화 | Figma Variables ↔ Code tokens 파이프라인 유무 |

## 2. 컴포넌트 인벤토리

| 항목 | 분석 내용 |
|------|----------|
| 총 컴포넌트 수 | Figma / Code 각각 |
| 분류 체계 | 카테고리 분류 방식 |
| 커버리지 | 폼, 네비게이션, 데이터 표시, 오버레이, 레이아웃 등 |
| 복합 컴포넌트 | Compound component 패턴 사용 여부 |

## 3. Figma↔Code 매핑 충실도 (핵심)

| 항목 | 분석 내용 |
|------|----------|
| 1:1 대응률 | Figma 컴포넌트 ↔ Code 컴포넌트 매칭 비율 |
| 네이밍 정합성 | 컴포넌트명, props명 일치도 |
| Variant 정합성 | Figma variant properties ↔ Code props 매핑 |
| 토큰 정합성 | Figma styles/variables ↔ Code design tokens |
| 구조적 대응 | Figma auto-layout ↔ Code flex/grid |
| 매핑 방향 | Figma-first? Code-first? 양방향? |

## 4. API 설계 철학

| 항목 | 분석 내용 |
|------|----------|
| 패턴 | Composition vs Configuration |
| 스타일링 | CSS-in-JS / Tailwind / CSS Modules / vanilla CSS |
| Headless 분리 | 로직과 스타일 분리 여부 |
| 커스터마이징 | 테마 오버라이드, slot/recipe 시스템 |

## 5. 접근성

| 항목 | 분석 내용 |
|------|----------|
| ARIA | 내장 ARIA 속성 수준 |
| 키보드 | 키보드 네비게이션 지원 |
| 표준 준수 | WCAG 레벨, WAI-ARIA 패턴 |

## 6. 동기화 거버넌스

| 항목 | 분석 내용 |
|------|----------|
| 프로세스 | Figma↔Code 동기화 방식 (수동/반자동/자동) |
| 도구 | Style Dictionary, Tokens Studio, 자체 도구 |
| 주기 | 릴리스 주기, 동기화 빈도 |
| 기여 모델 | 오픈소스 기여 방식 |
