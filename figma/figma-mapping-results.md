# Figma 실측 데이터 기반 컴포넌트 매핑 분석

> Figma API로 실제 파일에서 추출한 데이터 + 코드 컴포넌트 1:1 대조
> 분석 기준일: 2026-07-26
> Figma 파일: 프로젝트 630597477 (Community Duplicate)

---

## 1. Figma 파일 정보

| 시스템 | file_key | 페이지 | COMPONENT_SET | 총 variant |
|--------|----------|:-----:|:-----------:|:--------:|
| Spectrum | VN27jZQKq2YTR9kavQH27p | 20 | 462 | 8,039 |
| Material 3 | jFqFUx2lt37lQJX6v80Xpc | 33 | 171 | 5,354 |
| Carbon v11 | qitdRY9kvVF80IwfFOd6dh | 54 | 177 | 4,211 |
| Fluent 2 | zh53bUlnsBwTu61rP9Wc1q | 51 | 104 | 2,376 |

### Spectrum COMPONENT_SET 462개의 실체

Spectrum은 **컴포넌트 × 플랫폼 × 테마**의 곱으로 SET이 폭발함:

```
Action Button × (Desktop, Mobile) × (Light, Dark, Darkest, Wireframe) = 8 SET
```

테마/플랫폼 접미사 제거 시 **61개 고유 컴포넌트**로 축소.

---

## 2. Code ↔ Figma 매칭률 (실측)

| 시스템 | Code 컴포넌트 | Figma 매칭 | 매칭률 | 비고 |
|--------|:-----------:|:--------:|:-----:|------|
| **Carbon** | 39 | 38 | **97%** | InlineNotification만 미매칭 |
| **Material 3** | 25 | 23 | **92%** | TimePicker, Divider 미매칭 |
| **Fluent 2** | 41 | 36 | **88%** | Table, Calendar, Combobox, Overflow, Toast 미매칭 |
| **Spectrum** | 43 | 30 | **70%** | 테마 정규화 후. 레이아웃/유틸 컴포넌트 미매칭 |

---

## 3. 시스템별 매칭 상세

### Carbon (97% — 38/39)

**거의 완벽한 1:1 대응.** Figma 컴포넌트명이 코드명과 직접 매핑.

| Code | Figma COMPONENT_SET |
|------|-------------------|
| Button | Button |
| TextInput | Text input - Default |
| Checkbox | Checkbox |
| Tag | Tag - Operational |
| DataTable | Data table |
| Tabs | Tabs |
| Modal | Form modal - Default |
| Select | Select |

미매칭: `InlineNotification` (Figma에서 "Notification"으로 존재하나 문자열 매칭 실패)

### Material 3 (92% — 23/25)

| Code | Figma COMPONENT_SET |
|------|-------------------|
| Button | .Building Blocks/Menu button |
| FAB | .Building Blocks/FAB Menu/Primary/FAB |
| TextField | Text field |
| Card | .Building Blocks/Card states/Elevated |
| Dialog | Basic dialog |
| Checkbox | Checkboxes |
| Chip | Assistive chip |
| Tabs | Primary tabs/Icon and label |
| Switch | Switch |
| Slider | Centered slider |

미매칭: `TimePicker`, `Divider`

**특징**: Figma에서 ".Building Blocks/" 접두사가 붙은 내부 빌딩블록과 실제 컴포넌트가 혼재.

### Fluent 2 (88% — 36/41)

| Code | Figma COMPONENT_SET |
|------|-------------------|
| Button | .Info button |
| Input | Input |
| Dialog | Dialog |
| Checkbox | Checkbox |
| Badge | Badge |
| MessageBar | Message bar |
| Tab | Horizontal Tab |
| Accordion | Accordion |
| Avatar | Avatar/Avatar |
| Breadcrumb | .Breadcrumb Item |

미매칭: `Table`, `Calendar`, `Combobox`, `Overflow`, `Toast`

**특징**: "." 접두사가 붙은 내부 컴포넌트(.Card body, .Breadcrumb Item 등)가 다수.

### Spectrum (70% — 30/43, 정규화 후)

| Code | Figma (테마 제거 후) |
|------|-------------------|
| Button / ActionButton | Action Button |
| TextField | Text Field |
| Card | Card |
| Checkbox | Checkbox |
| Tag | Tag |
| Picker | Picker |
| ActionBar | Action Bar |
| AlertDialog | Alert Dialog |
| ComboBox | Combo Box |
| ProgressBar | Progress Bar |
| ProgressCircle | Progress Circle |
| StatusLight | Status Light |
| Switch | Switch |
| Toast | Toast |

미매칭 (13개):
- **레이아웃/유틸** (Figma에 존재하지 않는 코드 전용): Flex, Grid, Well, IllustratedMessage
- **네이밍 불일치**: RadioGroup ↔ "Radio Button", NumberField ↔ 미포함, SearchField ↔ 미포함
- **복합 컴포넌트**: Calendar, ContextualHelp, DropZone, ListBox, ListView, TreeView

---

## 4. Figma Variant 구조 분석

### Spectrum: 테마 × 플랫폼 매트릭스

```
컴포넌트 1개 = 2(플랫폼) × 4(테마) = 8개 COMPONENT_SET
462 SET ÷ 8 ≈ 58개 고유 컴포넌트 (실측 61개)
```

Variant properties (COMPONENT_SET 내부):
- State: Default, Hover, Down, Focus, Disabled
- Size: S, M, L, XL (컴포넌트별 상이)
- Selected: True/False

### Material 3: 계층적 네이밍

```
.Building Blocks/  → 내부 빌딩블록 (코드에 직접 대응 안 함)
Primary tabs/      → 실제 컴포넌트
Text field         → 실제 컴포넌트
```

Variant properties:
- State: Default, Hover, Pressed, Disabled, Focused
- Type/Style: Filled, Outlined, Elevated, Tonal
- Size: Small, Medium, Large
- Leading/Trailing icon: True/False

### Carbon: 상태 × 종류

Variant properties:
- Kind: Primary, Secondary, Tertiary, Ghost, Danger
- Size: xs, sm, md, lg, 2xl
- State: Default, Hover, Active, Disabled, Focus
- Selected: True/False

### Fluent 2: Appearance × Size

Variant properties:
- Appearance: Primary, Secondary, Outline, Subtle, Transparent
- Size: Small, Medium, Large
- Shape: Rounded, Circular, Square
- State: Rest, Hover, Pressed, Disabled

---

## 5. API 접근 제한 사항

| 엔드포인트 | 결과 | 원인 |
|-----------|------|------|
| `/files/:key` (노드 트리) | ✅ 성공 | — |
| `/files/:key/components` | ❌ 빈 배열 | Community 복제 파일은 published library 아님 |
| `/files/:key/variables/local` | ❌ 403 | Community 복제 파일 Variables 접근 불가 |
| `/files/:key/styles` | ❌ 빈 배열 | 동일 |

**Variables/Styles를 보려면**: 원본 파일의 팀 권한이 필요하거나, Figma UI에서 직접 확인해야 함.

---

## 6. 핵심 결론

### 이전 추정 vs 실측

| 시스템 | 이전 추정 매핑률 | 실측 매핑률 | 차이 원인 |
|--------|:-------------:|:---------:|---------|
| Carbon | ~90% (추정) | **97%** | 예상이 보수적이었음 |
| Material 3 | ~70% (추정) | **92%** | Material Web 기준. MUI 포함 시 낮아짐 |
| Fluent 2 | ~90% (추정) | **88%** | 거의 일치 |
| Spectrum | ~90% (추정) | **70%** | 레이아웃/유틸 컴포넌트가 Figma에 없음 |

### Figma에 없고 Code에만 있는 컴포넌트 유형

1. **레이아웃 프리미티브**: Flex, Grid, Well, Box (코드 전용)
2. **복합/동적 컴포넌트**: TreeView, ListView, Calendar (Figma에서 정적 표현 한계)
3. **유틸리티**: DropZone, ContextualHelp (상호작용 중심)

### Figma에 있고 Code에 없는 컴포넌트 유형

1. **내부 빌딩블록**: ".Building Blocks/*" (Material), "._Card - Footer" (Spectrum)
2. **테마 변형**: Spectrum의 Desktop/Mobile × Light/Dark/Darkest/Wireframe
3. **와이어프레임/스크린**: Carbon "Screens" 페이지

---

## 7. 원본 데이터

```
figma/raw/
├── carbon-components-extracted.json    (177 SET, 4241 COMPONENT)
├── spectrum-components-extracted.json  (462 SET, 9012 COMPONENT)
├── material3-components-extracted.json (171 SET, 5599 COMPONENT)
├── fluent2-components-extracted.json   (104 SET, 2396 COMPONENT)
├── carbon-variables.json               (403 - 접근 불가)
├── spectrum-variables.json             (403 - 접근 불가)
├── material3-variables.json            (403 - 접근 불가)
└── fluent2-variables.json              (403 - 접근 불가)
```
