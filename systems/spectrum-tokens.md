# Adobe Spectrum Design Token 시스템 — 코드 레벨 심층 분석

> 분석 기준: `@adobe/spectrum-tokens@14.15.0` (2026-07 기준), `adobe/spectrum-design-data` monorepo `main` branch
>
> **참고**: 기존 `adobe/spectrum-tokens` repo는 `adobe/spectrum-design-data`로 이름 변경됨. Spectrum 2 token data는 `main` branch, S1 legacy data는 `s1-legacy` branch + `v12.x.x` npm package에 위치.

---

## 1. Token 정의 (Definition)

### 1.1 소스 포맷 및 저장 구조

Token의 source of truth는 **JSON**이다. 두 가지 병행 포맷이 존재한다:

| 포맷 | 위치 | 구조 | 용도 |
|------|------|------|------|
| **Flat format** | `packages/tokens/src/*.json` | `{ "token-name": { ... } }` 객체 | npm 배포, Style Dictionary 소비 |
| **Cascade format** | `packages/design-data/tokens/*.tokens.json` | `[{ name: {...}, value, uuid }]` 배열 | SDK/도구 소비, 정규화된 메타데이터 |

> `packages/tokens/src/`는 `packages/design-data/`에서 **자동 생성**된다. 직접 편집 금지.

#### Flat format 디렉토리 구조

```
packages/tokens/
├── schemas/
│   └── token-types/          # 19개 JSON Schema 파일
│       ├── alias.json
│       ├── alignment.json
│       ├── color.json
│       ├── color-set.json
│       ├── dimension.json
│       ├── drop-shadow.json
│       ├── font-family.json
│       ├── font-size.json
│       ├── font-style.json
│       ├── font-weight.json
│       ├── gradient-stop.json
│       ├── multiplier.json
│       ├── opacity.json
│       ├── scale-set.json
│       ├── set.json
│       ├── system-set.json
│       ├── text-transform.json
│       ├── token.json        # 모든 token type의 base schema
│       └── typography.json
├── snapshots/
│   └── validation-snapshot.json
├── src/                      # 8개 token 소스 파일
│   ├── color-palette.json        # 283 KB — raw palette (blue-100~1400, gray, red, etc.)
│   ├── color-aliases.json        # 104 KB — semantic alias (accent-background-color-*)
│   ├── color-component.json      #  25 KB — component별 color (avatar-border-color, etc.)
│   ├── semantic-color-palette.json # 23 KB — accent/negative/informative 매핑
│   ├── typography.json           #  96 KB — font-family, font-size, line-height, etc.
│   ├── layout.json               # 184 KB — global spacing/dimension
│   ├── layout-component.json     # 587 KB — component별 spacing (가장 큰 파일)
│   └── icons.json                #  55 KB — icon color token
├── index.js                  # JS 헬퍼 (getAllTokens, getTokensByFile, etc.)
├── manifest.json             # 8개 파일 목록
├── naming-exceptions.json    # 72 KB — legacy naming 예외 추적
└── package.json
```

#### Cascade format 디렉토리 구조

```
packages/design-data/
├── tokens/
│   ├── color-palette.tokens.json      # 483 KB
│   ├── color-aliases.tokens.json
│   ├── color-component.tokens.json
│   ├── semantic-color-palette.tokens.json
│   ├── typography.tokens.json
│   ├── layout.tokens.json
│   ├── layout-component.tokens.json
│   └── icons.tokens.json
├── components/       # component 메타데이터
├── fields/           # taxonomy 필드 정의
├── guidelines/       # 디자인 가이드라인
├── mode-sets/        # mode/theme 정의
├── registry/         # 레지스트리 데이터
└── scripts/          # 빌드/검증 스크립트
```

### 1.2 Token 계층 구조 (Hierarchy)

Spectrum은 **3단계 계층**을 사용한다. 각 단계의 실제 토큰 예시:

#### Layer 1: Palette (원시 값)

`color-palette.json` — 하드코딩된 RGB 값. `private: true`로 표시되어 직접 사용 비권장.

```json
{
  "blue-100": {
    "$schema": "https://opensource.adobe.com/spectrum-design-data/schemas/token-types/color-set.json",
    "uuid": "482037db-2e5c-4deb-bfa5-986a46cdcf33",
    "private": true,
    "sets": {
      "light": {
        "$schema": ".../color.json",
        "value": "rgb(245, 249, 255)",
        "uuid": "bb610367-a43d-4ba9-b667-84b4d8da69b2"
      },
      "dark": {
        "$schema": ".../color.json",
        "value": "rgb(14, 23, 63)",
        "uuid": "7d56ac58-fd58-41b3-9bbd-448ae0a7dd85"
      },
      "wireframe": {
        "$schema": ".../color.json",
        "value": "rgb(246, 248, 252)",
        "uuid": "05ffb7a9-8bd9-46cd-bfb0-66217d52ceb1"
      }
    }
  }
}
```

**핵심 패턴**: 하나의 token name(`blue-100`)이 `sets` 안에 `light`, `dark`, `wireframe` 3개 theme variant를 보유. 이것이 **color-set** token type이다.

#### Layer 2: Semantic Alias (의미 기반 매핑)

`semantic-color-palette.json` — palette token을 `{curly-brace}` alias 구문으로 참조.

```json
{
  "accent-color-100": {
    "$schema": ".../alias.json",
    "value": "{blue-100}",
    "uuid": "2e080bb5-6f2c-4fd9-96a2-bf9fc19d2649"
  },
  "accent-color-1000": {
    "$schema": ".../alias.json",
    "value": "{blue-1000}",
    "uuid": "9bf3fa2f-75d3-44d3-ae30-d88893665366"
  }
}
```

`color-aliases.json` — 상태(state)별 semantic alias. theme variant별로 다른 palette 값을 매핑.

```json
{
  "accent-background-color-default": {
    "$schema": ".../color-set.json",
    "uuid": "e05251ac-d64a-4157-9b20-224f0392269e",
    "sets": {
      "light": {
        "$schema": ".../alias.json",
        "value": "{accent-color-900}",
        "uuid": "d9d8488d-9b38-47e0-9660-dcad040f3ca8"
      },
      "dark": {
        "$schema": ".../alias.json",
        "value": "{accent-color-800}",
        "uuid": "f24eb871-6419-4cef-88a2-cca8548ae31e"
      },
      "wireframe": {
        "$schema": ".../alias.json",
        "value": "{accent-color-900}",
        "uuid": "1f4f6c48-633c-4eb5-b7d6-bf5a9a7fde18"
      }
    }
  },
  "accent-background-color-hover": {
    "$schema": ".../color-set.json",
    "sets": {
      "light": { "value": "{accent-color-1000}" },
      "dark":  { "value": "{accent-color-700}" },
      "wireframe": { "value": "{accent-color-1000}" }
    }
  }
}
```

**해석**: light theme에서 `accent-background-color-default`은 `accent-color-900` → `blue-900` → `rgb(39, 77, 234)`로 해석. dark theme에서는 `accent-color-800`으로 다른 값.

#### Layer 3: Component Token

`color-component.json` — component 이름이 token name prefix + `component` 필드로 명시.

```json
{
  "avatar-border-color": {
    "$schema": ".../alias.json",
    "component": "avatar",
    "value": "{gray-25}",
    "uuid": "bae79ea7-2b3e-4d43-af42-7deab67acc7c"
  },
  "avatar-opacity-disabled": {
    "$schema": ".../alias.json",
    "component": "avatar",
    "value": "{opacity-disabled}",
    "uuid": "84d25d1b-f9e4-4a9e-8cd0-92367ff00637"
  },
  "action-bar-border-color": {
    "$schema": ".../color-set.json",
    "component": "action-bar",
    "uuid": "1f180759-7dbe-4ac3-80f6-78433659d52c",
    "sets": {
      "light": { "value": "{transparent-white-25}" },
      "dark":  { "value": "{gray-400}" },
      "wireframe": { "value": "{transparent-white-25}" }
    }
  },
  "table-selected-row-background-color": {
    "$schema": ".../alias.json",
    "component": "table",
    "value": "{informative-background-color-default}",
    "uuid": "b7537f50-bd49-44b6-a171-19943d443d24"
  }
}
```

`layout-component.json` — component별 spacing/dimension token. **desktop/mobile** scale variant.

```json
{
  "accordion-bottom-to-text-compact-extra-large": {
    "$schema": ".../scale-set.json",
    "component": "accordion",
    "uuid": "92fef7e7-45bc-4dcd-91c2-c42e696263a8",
    "deprecated": true,
    "deprecated_comment": "Use semantic token base-padding-vertical-extra-large instead",
    "renamed": "base-padding-vertical-extra-large",
    "sets": {
      "desktop": { "value": "8px", "uuid": "7a576841-..." },
      "mobile":  { "value": "10px", "uuid": "70e6d9e7-..." }
    }
  }
}
```

#### 전체 해석 체인 예시

```
Button background (light, default)
  └─ --spectrum-button-background-color-default     [component token, CSS]
       └─ var(--spectrum-neutral-background-color-default)  [semantic alias, CSS]
            └─ {gray-800}                                   [alias → palette 참조]
                 └─ rgb(50, 50, 50)                          [palette 원시 값, light]
```

### 1.3 Token 규모 및 카테고리별 분포

8개 소스 파일의 크기 기준 추정:

| 파일 | 크기 | 카테고리 | 추정 token 수 |
|------|------|----------|--------------|
| `layout-component.json` | 587 KB | component spacing | ~3,000+ |
| `color-palette.json` | 283 KB | raw color palette | ~1,500+ (×3 theme sets) |
| `layout.json` | 184 KB | global spacing/dimension | ~1,000+ |
| `color-aliases.json` | 104 KB | semantic color alias | ~500+ |
| `typography.json` | 96 KB | font/typography | ~500+ |
| `icons.json` | 55 KB | icon color | ~300+ |
| `color-component.json` | 25 KB | component color | ~150+ |
| `semantic-color-palette.json` | 23 KB | accent/negative/informative | ~100+ |

**총 추정: 7,000~8,000+ token** (theme variant sets 포함 시 더 많음)

### 1.4 Naming Convention

**기본 패턴**: `kebab-case`, 계층적 의미를 이름에 인코딩.

```
{component}-{property}-{state}-{size}
```

실제 예시:
- `accent-background-color-default` — semantic: 역할 + 속성 + 상태
- `avatar-opacity-disabled` — component: 컴포넌트 + 속성 + 상태
- `accordion-bottom-to-text-compact-extra-large` — component: 컴포넌트 + 해부학 + density + 크기
- `body-cjk-emphasized-font-weight` — typography: 역할 + 스크립트 + 강조 + 속성
- `icon-color-blue-primary-hover` — icon: 컴포넌트 + 속성 + 색상 + 역할 + 상태

**크기 체계**: t-shirt sizing (`small`, `medium`, `large`, `extra-large`, `2x-large`)

**Naming exceptions**: `naming-exceptions.json` (72 KB)에 legacy 이름 불일치를 추적.

```json
{
  "exceptions": [
    {
      "token": "gradient-stop-1-avatar",
      "file": "color-palette.json",
      "category": "component-ordering",
      "reason": "Legacy name is property-then-component; canonical generation order is component-then-property"
    },
    {
      "token": "drop-shadow-emphasized-default-color",
      "file": "color-aliases.json",
      "category": "compound-state",
      "reason": "Does not roundtrip through canonical generation rules"
    }
  ]
}
```

카테고리: `component-ordering`, `compound-state`, `state-position`, `anatomy-decomposition`

### 1.5 Deprecation 처리

Token schema(`token.json`)에 deprecation 관련 필드가 명시적으로 정의됨:

```json
{
  "deprecated": {
    "type": ["boolean", "string"],
    "default": false,
    "description": "Boolean (legacy) or version string (cascade). Truthy = deprecated."
  },
  "deprecated_comment": {
    "type": "string"
  },
  "renamed": {
    "type": "string",
    "description": "Legacy format: new token name. Use replaced_by (UUID) in cascade format instead."
  },
  "replaced_by": {
    "oneOf": [
      { "type": "string", "format": "uuid" },
      { "type": "array", "items": { "type": "string", "format": "uuid" }, "minItems": 1 }
    ],
    "description": "UUID(s) of the replacement token(s). Array form requires deprecated_comment."
  },
  "plannedRemoval": {
    "type": "string",
    "description": "Spec version when token will be removed."
  }
}
```

**실제 deprecation 예시** (`layout-component.json`):

```json
{
  "accordion-bottom-to-text-compact-extra-large": {
    "deprecated": true,
    "deprecated_comment": "Use semantic token base-padding-vertical-extra-large instead. Major refactor necessary",
    "renamed": "base-padding-vertical-extra-large",
    "sets": {
      "desktop": { "value": "8px" },
      "mobile": { "value": "10px" }
    }
  }
}
```

**Deprecation 라이프사이클** (README 문서화):
1. 기존 token에 `deprecated: true` 설정
2. `renamed: "new-token-name"`으로 대체 token 명시
3. `deprecated_comment`에 마이그레이션 가이드 추가
4. 기존 token의 value를 새 token의 alias로 변경
5. 다음 major release에서 제거

### 1.6 Cascade Format vs Flat Format 비교

동일 token `blue-100`의 두 포맷:

**Flat format** (`packages/tokens/src/color-palette.json`):
```json
{
  "blue-100": {
    "$schema": ".../color-set.json",
    "uuid": "482037db-...",
    "private": true,
    "sets": {
      "light": { "value": "rgb(245, 249, 255)", "uuid": "bb610367-..." },
      "dark":  { "value": "rgb(14, 23, 63)",    "uuid": "7d56ac58-..." },
      "wireframe": { "value": "rgb(246, 248, 252)", "uuid": "05ffb7a9-..." }
    }
  }
}
```

**Cascade format** (`packages/design-data/tokens/color-palette.tokens.json`):
```json
[
  {
    "name": {
      "property": "color",
      "colorFamily": "blue",
      "scaleIndex": 100,
      "colorScheme": "light"
    },
    "$schema": ".../color.json",
    "value": "rgb(245, 249, 255)",
    "uuid": "bb610367-...",
    "set_uuid": "482037db-...",
    "set_schema": ".../color-set.json",
    "private": true
  },
  {
    "name": {
      "property": "color",
      "colorFamily": "blue",
      "scaleIndex": 100,
      "colorScheme": "dark"
    },
    "value": "rgb(14, 23, 63)",
    "uuid": "7d56ac58-...",
    "set_uuid": "482037db-..."
  }
]
```

**차이점**:
- Flat: token name이 문자열 key, variant가 `sets` 객체 안에 중첩
- Cascade: `name`이 구조화된 객체(`property`, `colorFamily`, `scaleIndex`, `colorScheme`), 각 variant가 독립 레코드, `set_uuid`로 그룹핑

---

## 2. Token 소비 (Consumption)

### 2.1 npm 패키지 배포

**패키지**: `@adobe/spectrum-tokens@14.15.0` (337개 버전, 주간 ~12,925 다운로드)

```
@adobe/spectrum-tokens/
├── dist/              # 1.16 MB — 빌드 산출물
├── schemas/           # 22.3 kB — JSON Schema
├── snapshots/         # 80.9 kB — validation snapshot
├── src/               # 1.36 MB — 8개 JSON token 소스
├── tasks/             # 8.82 kB — moon task 정의
├── test/              # 31 kB
├── index.js           # 2.24 kB — JS 헬퍼 함수
├── manifest.json      # 223 B — token 파일 목록
├── naming-exceptions.json  # 65.5 kB
└── package.json
```

**의존성 0개** — 순수 데이터 패키지.

#### index.js — 프로그램매틱 접근 API

```js
// 모든 token 파일 이름 목록
export const tokenFileNames = await glob(`${resolve(__dirname, "./src")}/**/*.json`);

// 특정 파일의 token 로드
export const getFileTokens = async (tokenFileName) =>
  await readJson(resolve(__dirname, "src", tokenFileName));

// 파일별 token 객체 반환
export const getTokensByFile = async () => { /* ... */ };

// 전체 token 병합 반환
export const getAllTokens = async () => { /* ... */ };

// deprecation 체크 유틸
export const isDeprecated = (token) =>
  (Object.hasOwn(token, "deprecated") && token.deprecated == true) ||
  (Object.hasOwn(token, "sets") &&
    Object.values(token.sets).every(
      (setValue) => Object.hasOwn(setValue, "deprecated") && setValue.deprecated == true
    ));
```

**소비 방식**: 정적 import가 아닌 **async 함수**를 통해 JSON을 동적 로드.

### 2.2 CSS Custom Property 소비

Spectrum CSS(`adobe/spectrum-css` repo)에서 component는 `--spectrum-*` namespace의 CSS custom property로 token을 소비.

#### Button 컴포넌트 실제 코드 (`components/button/index.css`)

**사이즈 매핑** — global token → component-local variable:

```css
.spectrum-Button {
  --spectrum-button-sized-height: var(--spectrum-component-height-100);
  --spectrum-button-sized-font-size: var(--spectrum-font-size-100);
  --spectrum-button-sized-edge-to-visual: calc(
    var(--spectrum-component-pill-edge-to-visual-100) - var(--spectrum-button-border-width)
  );
  --spectrum-button-sized-padding-label-to-icon: var(--spectrum-text-to-visual-100);
  --spectrum-button-intended-icon-size: var(--spectrum-workflow-icon-size-100);
}

.spectrum-Button--sizeS {
  --spectrum-button-sized-height: var(--spectrum-component-height-75);
  --spectrum-button-sized-font-size: var(--spectrum-font-size-75);
  /* ... 75 scale token 참조 */
}

.spectrum-Button--sizeL {
  --spectrum-button-sized-height: var(--spectrum-component-height-200);
  --spectrum-button-sized-font-size: var(--spectrum-font-size-200);
  /* ... 200 scale token 참조 */
}
```

**Variant/State별 색상 매핑** — semantic token → component-local variable:

```css
.spectrum-Button {
  --spectrum-button-content-color-default: var(--spectrum-neutral-content-color-default);
  --spectrum-button-content-color-hover: var(--spectrum-neutral-content-color-hover);
  --spectrum-button-content-color-down: var(--spectrum-neutral-content-color-down);
  --spectrum-button-content-color-focus: var(--spectrum-neutral-content-color-key-focus);
  --spectrum-button-content-color-disabled: var(--spectrum-disabled-content-color);
}

.spectrum-Button--accent {
  --spectrum-button-background-color-default: var(--spectrum-accent-background-color-default);
  --spectrum-button-background-color-hover: var(--spectrum-accent-background-color-hover);
  --spectrum-button-background-color-down: var(--spectrum-accent-background-color-down);
  --spectrum-button-background-color-focus: var(--spectrum-accent-background-color-key-focus);
  --spectrum-button-border-color-default: transparent;
  --spectrum-button-content-color-default: var(--spectrum-white);
}

.spectrum-Button--negative {
  --spectrum-button-background-color-default: var(--spectrum-negative-background-color-default);
  --spectrum-button-background-color-hover: var(--spectrum-negative-background-color-hover);
  /* ... */
}
```

**3단계 fallback 체인** — 최종 속성 적용 시 override hook 제공:

```css
.spectrum-Button {
  background-color: var(
    --highcontrast-button-background-color-default,
    var(--mod-button-background-color-default,
      var(--spectrum-button-background-color-default)
    )
  );
}
```

해석 우선순위: `--highcontrast-*` > `--mod-*` > `--spectrum-*` (design token)

### 2.3 React Spectrum의 Token 소비

React Spectrum(`adobe/react-spectrum`)은 자체 CSS 파일이 **없다**.

**파이프라인**:
```
@spectrum-css/button (CSS source, --spectrum-* token 참조)
    ↓ @adobe/spectrum-css-workflow (빌드 시 변환)
@react-spectrum/theme (JS style object로 컴파일)
    ↓ Provider가 theme context 제공
@react-spectrum/button (useStyleProps()로 소비)
```

- `@react-spectrum/button/src/`에는 `index.ts` **하나만** 존재 — CSS 파일 없음
- 스타일은 `useStyleProps()` / `useProviderProps()` 훅을 통해 JS 객체로 주입
- 실제 token 참조는 `@spectrum-css/button`의 CSS에 있고, 빌드 시 JS로 변환됨

### 2.4 Theming 구조

**Theme variant 축**:

| 축 | 값 | token에서의 표현 |
|----|-----|-----------------|
| Color scheme | `light`, `dark`, `wireframe` | `sets.light`, `sets.dark`, `sets.wireframe` |
| Scale | `desktop`, `mobile` | `sets.desktop`, `sets.mobile` (scale-set type) |
| Density | `compact`, `regular` | token name에 인코딩 (`-compact-`) |

**React Spectrum Provider**:
- `Provider` 컴포넌트가 `colorScheme`, `scale`, `theme` props를 받아 context 제공
- CSS class(`.spectrum--light`, `.spectrum--dark`, `.spectrum--medium`, `.spectrum--large`)로 theme 적용
- 실제 CSS variable 값은 `@spectrum-css` token 패키지에서 로드

### 2.5 사용자 Token Override

3가지 override 경로:

1. **`--mod-*` custom property** — component 레벨 override
   ```css
   .my-button {
     --mod-button-background-color-default: hotpink;
   }
   ```

2. **`--highcontrast-*` custom property** — high-contrast 모드 override
   ```css
   .my-button {
     --highcontrast-button-background-color-default: black;
   }
   ```

3. **React Spectrum `styles` prop** — JS 레벨 override
   ```jsx
   <Button styles={{ backgroundColor: 'red' }}>Click</Button>
   ```

4. **`UNSAFE_className` / `UNSAFE_style`** — escape hatch (비권장)

---

## 3. Token 거버넌스 (Governance)

### 3.1 버전 관리

**Semver + Changesets + Conventional Commits** 3중 체계:

| 변경 유형 | Semver | 예시 |
|-----------|--------|------|
| 버그 수정, 오타 | `x.x.n+1` (patch) | `detail-margin-top-mulitplier` → `detail-margin-top-multiplier` |
| 새 token 추가, 의도적 값 변경, deprecation 추가 | `x.n+1.0` (minor) | 새 token 추가, alias 추가 |
| token 삭제, value type 변경 | `n+1.0.0` (major) | color → dimension type 변경 |

**Release 자동화**:
- `main` branch merge → `latest` tag로 자동 배포
- `next`, `next-major` branch → `next` tag로 pre-release
- Changesets로 변경 이력 관리

### 3.2 Token Diff 도구

**`@adobe/token-diff-generator`** — library + CLI (`tdiff`):

```bash
# 두 release 버전 비교
tdiff report \
  --otv "@adobe/spectrum-tokens@13.0.0-beta.46" \
  --ntv "@adobe/spectrum-tokens@13.0.0-beta.47" \
  --format markdown \
  --output logs/output.md

# branch 간 비교 + 특정 파일만
tdiff report \
  --otb main --ntb feature-branch \
  -n color-aliases.json color-component.json
```

**핵심 기능**:
- `@adobe/optimized-diff`로 일반 JSON diff 수행
- token 특화 후처리: **UUID 기반 rename 감지** — 일반 diff는 "삭제 + 추가"로 보이는 것을 UUID 매칭으로 "이름 변경"으로 보고
- `renamed` property도 함께 추적
- 출력 포맷: `cli`, `markdown`, `handlebars` (내장 템플릿: `cli`, `default`, `json`, `plain`, `summary`)
- **제약**: `@adobe/spectrum-tokens@12.26.0` 이전 버전은 UUID가 없어 사용 불가

**`tools/optimized-diff`** — 대규모 token dataset용 고성능 diff 엔진 (별도 패키지)

**`tools/token-changeset-generator`** — token diff 분석에서 changeset 파일 자동 생성

### 3.3 JSON Schema 검증

**2층 검증 구조**:

```
Layer 1: JSON Schema (구조적 검증)
  └─ Draft 2020-12
  └─ schemas/token-types/ 의 19개 스키마
  └─ moon run tokens:validateDesignData

Layer 2: Rule Catalog (의미론적 검증)
  └─ packages/design-data-spec/rules/rules.yaml
  └─ SPEC-001 ~ SPEC-006 규칙
  └─ conformance fixtures (유효/무효 예시 + 기대 진단)
```

**Base token schema** (`token.json`):

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://opensource.adobe.com/spectrum-design-data/schemas/token-types/token.json",
  "title": "Token",
  "type": "object",
  "properties": {
    "value": { "anyOf": ["number", "string", "object", "array"] },
    "component": { "type": "string" },
    "private": { "type": "boolean", "default": false },
    "deprecated": { "type": ["boolean", "string"] },
    "deprecated_comment": { "type": "string" },
    "renamed": { "type": "string" },
    "replaced_by": { "oneOf": ["uuid-string", "uuid-array"] },
    "plannedRemoval": { "type": "string" },
    "description": { "type": "string" },
    "uuid": { "type": "string", "format": "uuid" }
  },
  "required": ["value", "uuid"]
}
```

**Color token schema** (`color.json`) — base schema 상속 + value 패턴 제약:

```json
{
  "allOf": [{ "$ref": "token.json" }],
  "properties": {
    "$schema": {
      "const": "https://opensource.adobe.com/spectrum-design-data/schemas/token-types/color.json"
    },
    "value": {
      "type": "string",
      "pattern": "^rgba\\(...\\)|rgb\\(...\\)$"
    }
  }
}
```

**Snapshot 검증**: `snapshots/validation-snapshot.json`과 비교하여 검증 결과 회귀 감지.

```bash
moon run tokens:verifyDesignDataSnapshot
# 변경 시: design-data migrate snapshot
```

### 3.4 Rust CLI 도구 (`@adobe/design-data`)

`sdk/cli/` — Rust로 작성, npm으로 prebuilt binary 배포 (Node.js ≥ 20.12, Rust 불필요).

```bash
npm install -g @adobe/design-data
# 또는
npx @adobe/design-data <command>
```

| 명령어 | 기능 |
|--------|------|
| `design-data primer --format json` | 데이터셋 구조 개요 (AI 에이전트 세션용) |
| `design-data query "property=color*"` | 이름/속성으로 token 검색 |
| `design-data suggest "primary background color"` | AI 기반 token 추천 |
| `design-data resolve color-background-layer-1 --color-scheme light` | mode-set context에서 token 값 해석 |
| `design-data component button` | component schema 출력 |
| `design-data validate ./my-tokens` | design-data 디렉토리 검증 |

**설정** (`.design-data.toml`):
```toml
[source]
type = "github"
repo = "adobe/spectrum-design-data"
tag = "@adobe/spectrum-tokens@14.11.0"
```

미설정 시 내장된 Spectrum snapshot 사용 (오프라인, 무설정).

**TUI 모드**: `design-data` 명령어만 실행하면 인터랙티브 TUI 실행 — command palette, cascade resolver, validator, 4-screen authoring wizard 포함.

### 3.5 Figma Plugin (`component-options-editor`)

`tools/component-options-editor/` — Figma 플러그인.

**역할**: raw design token 편집기가 아닌, **component option schema** 작성/편집 도구.

- Visual Form Editor: string, boolean, size, color, icon 등 option type별 폼
- JSON Editor: CodeMirror 기반, syntax highlighting + validation
- Real-time Validation: Ajv 2020-12 JSON Schema validator
- Import/Export: component schema 파일 로드/다운로드

**Token과의 관계**: component option의 허용 값(color, size, icon 등)이 design token에 의해 제약되므로, token 생태계의 상류 도구. `packages/component-schemas/`의 JSON schema를 편집.

**기술 스택**: Lit/Web Components + Spectrum Web Components + TypeScript + Webpack + AVA

### 3.6 Token 문서화

- **S1 Visualizer**: `opensource.adobe.com/spectrum-design-data/visualizer/` — 정적 사이트
- **S2 Visualizer**: `opensource.adobe.com/spectrum-design-data/s2-visualizer/`
- **S2 Tokens Viewer**: `opensource.adobe.com/spectrum-design-data/s2-tokens-viewer/` — component usage 분석 포함
- **Release Timeline**: `opensource.adobe.com/spectrum-design-data/release-timeline/` — 릴리스 빈도 차트
- **CHANGELOG.md**: 580 KB — changeset 기반 자동 생성

### 3.7 추가 도구 생태계

| 도구 | 위치 | 기능 |
|------|------|------|
| `transform-tokens-json` | `tools/` | token 데이터 포맷 간 변환/병합 |
| `token-manifest-builder` | `tools/` | token 배포용 manifest 생성 |
| `release-analyzer` | `tools/` | 릴리스 이력 분석, 변경 빈도 시각화 데이터 생성 |
| `spectrum-design-data-mcp` | `tools/` | MCP 서버 — AI 어시스턴트에 구조화된 design data 접근 제공 |
| `design-data-agent-mcp` | `tools/` | 에이전트 전용 MCP 서버 |
| `design-data-skill` | `tools/` | Claude Code 에이전트 스킬 패키지 |
| `s2-docs-mcp` | `tools/` | S2 component 문서 MCP 서버 |

---

## 4. 종합 평가

### 강점

1. **엄격한 계층 분리**: palette → semantic → component 3단계가 명확하며, alias `{curly-brace}` 구문으로 참조 체인이 추적 가능
2. **UUID 기반 추적**: 모든 token에 UUID 부여 → rename 감지, diff, 마이그레이션이 기계적으로 가능
3. **다중 theme 내장**: `sets` 구조로 light/dark/wireframe + desktop/mobile variant가 단일 token 정의에 통합
4. **강력한 검증**: JSON Schema (Draft 2020-12) + rule catalog + snapshot 회귀 감지 3중 검증
5. **전문 도구 체인**: Rust CLI, diff generator, changeset generator, MCP 서버 등 token lifecycle 전반을 도구화
6. **Deprecation 거버넌스**: `deprecated` → `renamed` → `replaced_by` → `plannedRemoval`까지 구조화된 수명 주기

### 약점 / 주의점

1. **복잡도**: flat + cascade 2개 포맷 병행, 19개 token type schema, naming exceptions 등 학습 곡선 높음
2. **CSS 직접 배포 부재**: npm 패키지에 CSS custom property 파일이 직접 포함되지 않음 — `@spectrum-css` 패키지를 별도로 소비해야 함
3. **token 규모**: layout-component.json alone 587 KB, 총 7,000~8,000+ token으로 대규모 — 전체를 파악하기 어려움
4. **S1 → S2 마이그레이션 진행 중**: v11 → v12 → v14로 오면서 token 구조 대폭 변경, legacy 호환성 부담
5. **React Spectrum의 간접 소비**: CSS-in-JS 변환 파이프라인을 거쳐야 하므로 token 변경이 React 컴포넌트에 반영되기까지 여러 빌드 단계 필요

### 다른 디자인 시스템과의 차별점

| 측면 | Spectrum | 일반적 DS |
|------|----------|-----------|
| Token 저장 | JSON (전용 monorepo) | JSON/YAML (Style Dictionary) |
| Theme variant | `sets` 객체 내장 | 별도 파일 또는 빌드 시 생성 |
| UUID 추적 | 모든 token에 UUID | 보통 없음 |
| 검증 | JSON Schema + rule catalog + snapshot | JSON Schema 또는 lint |
| CLI 도구 | Rust 기반 전용 CLI | Node.js 스크립트 |
| Diff 도구 | UUID 기반 rename 감지 전용 도구 | 일반 diff 또는 수동 |
| AI 통합 | MCP 서버 3개 + AI suggest 명령 | 대부분 없음 |
