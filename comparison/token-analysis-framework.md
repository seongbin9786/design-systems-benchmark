# 디자인 토큰 분석 프레임워크

> 핵심 질문: 각 시스템은 디자인 토큰을 **어떻게 정의**하고, **어떻게 소비**하며, **어떻게 관리**하는가?

---

## 축 1: 토큰 정의 (Definition)

### 1.1 계층 구조
- 몇 단계인가? (primitive → semantic → component)
- 각 계층의 역할과 경계는 명확한가?
- 계층 간 참조 방향 (단방향? 순환?)

### 1.2 네이밍 컨벤션
- 표기법 (kebab-case, camelCase, dot.notation)
- 네이밍 패턴: `{category}-{property}-{role}-{state}` 등
- 일관성: 예외가 얼마나 있는가?
- Figma Variables명과의 정합성

### 1.3 Source of Truth
- 원본 포맷 (JSON, TypeScript, SCSS, CSS, Figma)
- 원본 저장 위치 (단일 파일? 분산?)
- 빌드/변환 파이프라인 유무

### 1.4 토큰 카테고리
- Color (primitive palette, semantic roles, component-specific)
- Typography (font family, size, weight, line-height, letter-spacing)
- Spacing / Layout
- Border (radius, width)
- Elevation / Shadow
- Motion (duration, easing)
- 기타 (z-index, breakpoints, opacity)

### 1.5 파생 메커니즘
- 정적 매핑 (수동 참조) vs 알고리즘 파생 (자동 생성)
- 다크모드 토큰: 별도 정의 vs 알고리즘 반전
- 컴포넌트 토큰: 전역에서 파생 vs 독립 정의

---

## 축 2: 토큰 소비 (Consumption)

### 2.1 런타임 포맷
- CSS custom properties (--token-name)
- JS/TS 객체 (theme.palette.primary)
- SCSS/Less 변수 ($token-name)
- 혼합 사용 시 우선순위

### 2.2 컴포넌트 내 소비 패턴
- 컴포넌트 스타일에서 토큰을 어떻게 참조하는가?
- 토큰 참조가 스타일 코드에 분산 vs 중앙 집중?
- Component-level token 격리 여부

### 2.3 테마 전환
- 메커니즘 (CSS vars 교체, JS 객체 재생성, class 토글)
- 런타임 전환 가능 여부 (re-render 필요?)
- 중첩 테마 지원
- 테마 수 (light/dark/HC/custom)

### 2.4 커스터마이징 API
- 사용자가 토큰을 오버라이드하는 방법
- 오버라이드 범위 (전역 / 컴포넌트 / 인스턴스)
- 타입 안전성 (TS 타입으로 토큰명 자동완성?)

### 2.5 다중 포맷 출력
- npm 패키지 배포 포맷 (CSS, JS, JSON, SCSS)
- 프레임워크별 패키지 분리 여부
- Figma Variables 출력 유무

---

## 축 3: 토큰 거버넌스 (Governance)

### 3.1 버전 관리
- 토큰 변경이 시맨틱 버저닝에 반영되는가?
- Breaking change 관리 (토큰 삭제/이름 변경)

### 3.2 비추천(deprecation) 처리
- deprecated 토큰 표시 방법
- 마이그레이션 경로 제공 (alias, codemod)
- 하위 호환 기간

### 3.3 검증 도구
- 토큰 스키마 검증 (JSON Schema, TS types)
- lint 규칙 (stylelint, eslint)
- 스냅샷 테스트 / diff 도구

### 3.4 문서화
- 토큰 레퍼런스 문서 자동 생성?
- 토큰별 설명(description) 포함?
- 시각적 미리보기 (색상 스와치, 타이포그래피 샘플)

### 3.5 Figma 연계
- Figma Variables ↔ Code 토큰 동기화 도구
- Figma Styles/Variables 사용 방식
- 디자인-개발 토큰 핸드오프 프로세스
