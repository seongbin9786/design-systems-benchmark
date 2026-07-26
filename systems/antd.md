# Ant Design (antd) — 벤치마크 분석

> **분석 대상**: Ant Design — Ant Group(구 Ant Financial)의 엔터프라이즈급 UI 디자인 언어 + React 컴포넌트 라이브러리
> **GitHub**: [ant-design/ant-design](https://github.com/ant-design/ant-design) (⭐ 98.8k · forks 54.7k)
> **npm**: `antd` — 최신 **6.5.2** (2026-07-24 발행) · MIT · React ≥ 18
> **Docs**: [ant.design](https://ant.design)
> **주요 버전**: v5.0.0 (2022-11-18, CSS-in-JS 토큰 시스템 도입) · v6.0.0 (2025-11-22, 시맨틱 구조 + CSS Variables 기본화)
> **분석 기준일**: 2026-07-26

---

## 0. 구조적 특수성: Code-first, 디자인 리소스는 Sketch 중심

Ant Design를 분석할 때 가장 먼저 짚어야 할 사실: **공식 Figma kit이 존재하지 않는다.**

공식 리소스 페이지(ant.design/docs/resources)가 "Official"로 분류하는 디자인 리소스는 전부 **Sketch 기반**이다:

| 공식 리소스 | 형태 |
|------------|------|
| Sketch Symbols (v5.0 UI Kit, 2024-01 build, release 5.13.3 동봉) | `.sketch` |
| Mobile Components | `.sketch` |
| Ant Design Pro (템플릿/페이지) | `.sketch` |
| Ant Design Chart | `.sketch` |
| Kitchen (Sketch 플러그인 툴킷) | kitchen.alipay.com |

반면 Figma 리소스는 **전부 서드파티/커뮤니티**로 분류된다:

| 서드파티 Figma 리소스 | 성격 |
|----------------------|------|
| AntUIKit (antuikit.com) — "Ant Design System - v6" 등 | 커뮤니티 제작, 토큰/컴포넌트 1:1 대응 주장 |
| antforfigma.com ("Figma Resources") | 커뮤니티, 상시 업데이트 주장 |
| Figma Open Source Library (community/file/831698976089873405) | 커뮤니티 오픈소스 라이브러리 |
| AntBlocks UI for Figma | 커뮤니티 상용 키트 |
| Ruyi Design Assistant (Figma 플러그인) | antd 코드 컴포넌트로 디자인 → 코드 출력 |

이 구조는 Material Design(spec-first, 다중 구현)이나 shadcn/ui(공식 Figma 없음)와도 다르다. Ant Design는 **단일 Code 라이브러리가 단일 소스**인 Code-first 시스템이며, 디자인 측 공식 파트너는 Sketch이고, Figma 생태계는 커뮤니티에 위임되어 있다. 이 사실은 §3 매핑 충실도 분석의 전제가 된다.

---

## 1. 토큰 아키텍처

### 1.1 계층 구조: Seed → Map → Alias (3-layer derivation)

v5.0에서 도입된 토큰 시스템의 핵심은 **단순 그룹핑이 아닌 파생(derivation) 관계**라는 점이다. 소스(`components/theme/interface/`)에서 타입 구조가 직접 확인된다:

```
Seed Token  ──(Algorithm)──▶  Map Token  ──▶  Alias Token
  디자인 의도의 원점            그라디언트 파생 변수        시맨틱 별칭
```

| 계층 | 소스 위치 | 역할 | 예시 |
|------|----------|------|------|
| **SeedToken** | `theme/interface/seeds` | 모든 디자인 의도의 원점. 알고리즘 입력값 | `colorPrimary`, `borderRadius`, `fontSize`, `sizeUnit` |
| **MapToken** | `theme/interface/maps` | Seed로부터 알고리즘이 파생한 그라디언트 변수 | `colorPrimaryBg`, `colorPrimaryHover`, `colorTextSecondary` |
| **AliasToken** | `theme/interface/alias` | Map의 별칭/특수 처리. 컴포넌트 공통 스타일 일괄 제어 | `colorLink`, `colorTextDescription`, `controlItemBgActive`, `boxShadow` |

`MappingAlgorithm = DerivativeFunc<SeedToken, MapToken>` — 알고리즘은 Seed를 입력받아 Map을 출력하는 순수 함수로 정의된다. MapToken은 다시 `ColorMapToken`, `ColorNeutralMapToken`, `CommonMapToken`, `FontMapToken`, `HeightMapToken`, `SizeMapToken`, `StyleMapToken`의 서브 인터페이스로 구성된다.

**대부분의 커스텀 테마는 Seed Token만으로 충분하다.** `colorPrimary` 하나를 바꾸면 내부 알고리즘이 해당 색상 계열 전체(10단계 팔레트 + hover/active/bg/border 파생)를 자동 계산·적용한다.

### 1.2 Seed Token 인벤토리 (기본값)

| 토큰 | 기본값 | 토큰 | 기본값 |
|------|--------|------|--------|
| `colorPrimary` | `#1677ff` | `colorError` | `#ff4d4f` |
| `colorSuccess` | `#52c41a` | `colorWarning` | `#faad14` |
| `colorInfo` | `#1677ff` | `colorLink` | `#1677ff` |
| `borderRadius` | `6` | `fontSize` | `14` |
| `sizeUnit` | `4` | `sizeStep` | `4` (compact: 2) |
| `controlHeight` | `32` | `lineWidth` | `1` |
| `lineType` | `solid` | `motion` | `true` |
| `wireframe` | `false` | `zIndexPopupBase` | `1000` |
| `colorBgBase` | `#fff` ⚠️ 직접 사용 금지 | `colorTextBase` | `#000` ⚠️ 직접 사용 금지 |

+ motion easing 토큰 8종 (`motionEaseInOut`, `motionEaseOutBack` 등), `fontFamily`/`fontFamilyCode`, `opacityImage`, `sizePopupArrow`, `zIndexBase`

**프리셋 팔레트** (12개 hue × 10단계): `@ant-design/colors` 패키지가 HSB 모델 기반으로 seed 색상에서 10단계 팔레트를 생성:

```js
import { blue } from '@ant-design/colors';
// ['#E6F4FF', '#BAE0FF', '#91CAFF', '#69B1FF', '#4096FF', '#1677FF', '#0958D9', '#003EB3', '#002C8C', '#001D66']
blue.primary // '#1677FF' — 관례상 6번째 단계가 브랜드 메인 컬러
```

12 hue: blue · purple · cyan · green · magenta · pink · red · orange · yellow · volcano · geekblue · lime · gold

### 1.3 네이밍 컨벤션

전 토큰 **camelCase** + 시맨틱 접두/접미사 체계:

| 패턴 | 의미 | 예시 |
|------|------|------|
| `color{Category}` | 색상 계열 | `colorPrimary`, `colorBgContainer`, `colorText`, `colorBorder`, `colorFill` |
| `color{Status}` | 시맨틱 상태 | `colorError`, `colorSuccess`, `colorWarning`, `colorInfo` |
| `…{State}` 접미사 | 인터랙션 상태 | `…Hover`, `…Active`, `…Disabled` |
| `…{Role}` 접미사 | 용도 역할 | `…Bg`, `…Border`, `…Text`, `…Outline`, `…Affix` |
| `{prop}{Size}` 접미사 | 사이즈 스케일 | `fontSizeSM`, `controlHeightLG`, `sizeXXL`, `paddingXS` (XXS~XXL) |
| `font*` / `line*` | 타이포그래피 | `fontSizeHeading1~5`, `lineHeight`, `lineWidthBold` |
| `motion*` | 모션 | `motionDurationFast/Mid/Slow`, `motionEase*` |
| `control*` | 폼 컨트롤 | `controlHeight`, `controlItemBgActive`, `controlOutline` |
| `margin*` / `padding*` | 간격 | `marginLG`, `paddingContentVertical` |
| `screen{BP}(Min/Max)` | 브레이크포인트 | `screenMD`, `screenLGMin` |

**Material Design(`md.sys.color.primary`, dot/kebab)이나 shadcn(`--primary`, kebab)과 달리 camelCase JS 객체 키**가 원본 포맷이다. 이는 토큰의 single source of truth가 TypeScript 타입 시스템에 있음을 의미한다.

### 1.4 테마 전환 / 다크모드: Algorithm 기반

다크모드는 별도 토큰 세트를 수동으로 정의하는 방식이 아니라 **알고리즘 교체**로 구현된다:

```tsx
import { ConfigProvider, theme } from 'antd';
const { defaultAlgorithm, darkAlgorithm, compactAlgorithm } = theme;

<ConfigProvider theme={{
  token: { colorPrimary: '#1890ff' },            // 전역 토큰
  algorithm: [darkAlgorithm, compactAlgorithm],  // 알고리즘 조합 가능
  components: { Button: { colorPrimary: '#00b96b', algorithm: true } },
}}>
  <App />
</ConfigProvider>
```

| 알고리즘 | 역할 |
|----------|------|
| `defaultAlgorithm` | 기본 라이트 테마 (Seed → Map 파생) |
| `darkAlgorithm` | 다크모드 — 동일 Seed에서 어두운 그라디언트 파생 |
| `compactAlgorithm` | 컴팩트 모드 — `sizeStep`을 4→2로 축소 |

- 알고리즘은 **단독 또는 임의 조합** 가능 (`[darkAlgorithm, compactAlgorithm]`)
- **중첩 테마**: ConfigProvider를 중첩하면 하위는 변경되지 않은 토큰을 상위로부터 상속
- **동적 전환**: 런타임에 `theme` prop만 바꾸면 됨 (CSS-in-JS이므로 재렌더로 즉시 반영)
- **컴포넌트별 알고리즘** (≥5.8.0): `components.X.algorithm`으로 특정 컴포넌트만 다른 파생 적용
- `colorBgBase`/`colorTextBase`는 알고리즘이 반전하는 기준점이므로 직접 사용 금지로 문서화됨

### 1.5 컴포넌트 토큰 (Component Token)

각 컴포넌트는 자체 Component Token을 가지며, 전역 토큰과 격리된다. 소스 패턴(`components/button/style/index.ts`)에서 확인:

```ts
export default genStyleHooks(
  'Button',
  (token) => {
    const buttonToken = prepareToken(token);   // 전역 토큰 → Button 토큰 파생
    return [ genSharedButtonStyle(buttonToken), genVariantStyle(buttonToken), ... ];
  },
  prepareComponentToken,                        // 컴포넌트 토큰 기본값 등록
  { unitless: { fontWeight: true, contentLineHeight: true, ... } },
);
```

- `prepareComponentToken`이 컴포넌트별 토큰 기본값을 전역 AliasToken으로부터 파생 (예: `contentFontSize`, `paddingInlineLG`, `defaultBorderColor`)
- `mergeToken`으로 사이즈별(sm/lg) 토큰을 재파생
- 사용자는 `theme.components.Button.{token}`으로 오버라이드 가능
- 컴포넌트 토큰은 해당 컴포넌트 스코프에서만 유효 — 컴포넌트 간 격리 보장

### 1.6 토큰 포맷

| 포맷 | 사용처 | 비고 |
|------|--------|------|
| **TypeScript 객체 (camelCase)** | 원본 source of truth | `SeedToken`/`MapToken`/`AliasToken` 타입 |
| **CSS-in-JS** (`@ant-design/cssinjs`) | v5 기본 런타임 | 해시 className으로 스타일 주입 |
| **CSS Variables** (`--ant-*`) | **v6 기본** (`cssVar` 기본 활성화) | prefix 설정 가능, `hashed`/`zeroRuntime` 옵션 |
| Less variables | v4 호환 경로 | `less-loader` `modifyVars`로 mapToken 주입 |

**v6의 주요 변화**: CSS Variables가 기본 활성화되어, CSS-in-JS 런타임 오버헤드를 줄이면서도 동적 테마 기능을 유지한다. `zeroRuntime` 모드(v6+)는 정적 CSS 추출(`@ant-design/static-style-extract`)로 런타임 스타일 생성을 완전히 생략한다.

### 1.7 Figma Variables ↔ Code token 동기화

**공식 동기화 파이프라인: 없음.**

- 공식 디자인 리소스가 Sketch이므로 Figma Variables와의 공식 연결이 애초에 성립하지 않음
- Style Dictionary, Tokens Studio 등 범용 토큰 변환 도구 공식 사용 없음
- 토큰의 source of truth는 **코드의 TypeScript 타입** — Figma(커뮤니티 키트) 측이 코드 토큰 값을 수동 복제하는 단방향 구조
- 단, 토큰 어휘(`colorPrimary`, `borderRadius` 등)가 공개 문서화되어 있어 서드파티 키트가 동일한 네이밍으로 토큰을 재현하는 것은 가능 (AntUIKit 등이 이를 주장)

---

## 2. 컴포넌트 인벤토리

### 2.1 총 컴포넌트 수

| 소스 | 수 | 비고 |
|------|---:|------|
| `components/index.ts` UI 컴포넌트 export | **73** | `theme`/`version` 제외 순수 UI 컴포넌트 |
| 공식 컴포넌트 오버뷰 페이지 (core) | **72** | List는 DEPRECATED 표기 |
| ProComponents (오버뷰 "Others" 섹션) | **+6** | ProLayout, ProForm, ProTable, ProDescriptions, ProList, EditableProTable |

**70개 초중반으로, 분석 대상 시스템 중 최대 규모급**이다 (MUI 62, shadcn/ui 63, Material Web ~21).

### 2.2 카테고리 분류 (공식 오버뷰 기준)

| 카테고리 | 수 | 주요 컴포넌트 |
|----------|---:|--------------|
| **General** | 4 | Button, FloatButton, Icon, Typography |
| **Layout** | 7 | Divider, Flex, Grid, Layout, Masonry, Space, Splitter |
| **Navigation** | 7 | Anchor, Breadcrumb, Dropdown, Menu, Pagination, Steps, Tabs |
| **Data Entry** | 18 | AutoComplete, Cascader, Checkbox, ColorPicker, DatePicker, Form, Input, InputNumber, Mentions, Radio, Rate, Select, Slider, Switch, TimePicker, Transfer, TreeSelect, Upload |
| **Data Display** | 20 | Avatar, Badge, Calendar, Card, Carousel, Collapse, Descriptions, Empty, Image, List, Popover, QRCode, Segmented, Statistic, Table, Tag, Timeline, Tooltip, Tour, Tree |
| **Feedback** | 11 | Alert, Drawer, Message, Modal, Notification, Popconfirm, Progress, Result, Skeleton, Spin, Watermark |
| **Other** | 5 | Affix, App, BorderBeam, ConfigProvider, Util |

**특징**: Data Entry(18) + Data Display(20)가 전체의 절반을 넘는다. 이는 Ant Design의 정체성이 **엔터프라이즈 백오피스/데이터 집약 애플리케이션**에 있음을 보여준다. Transfer, TreeSelect, Cascader, Mentions, Statistic, Descriptions, Watermark, QRCode 등은 다른 범용 라이브러리에는 없는 엔터프라이즈 특화 컴포넌트다.

### 2.3 커버리지

| 영역 | antd | 비고 |
|------|:----:|------|
| 폼 컨트롤 (text/number/date/time/color/rate/slider) | ✅ | ColorPicker, Rate, Slider 포함 풀세트 |
| 복합 데이터 입력 (Cascader/TreeSelect/Transfer/Mentions) | ✅ | 엔터프라이즈 특화, 타 라이브러리 대비 강점 |
| 테이블 (정렬/필터/고정/가상스크롤/편집) | ✅ | Table + ProTable/EditableProTable |
| 오버레이 (Modal/Drawer/Popover/Tooltip/Dropdown) | ✅ | |
| 피드백 (Message/Notification/Alert/Result/Skeleton) | ✅ | |
| 레이아웃 (Grid/Flex/Splitter/Masonry) | ✅ | v6에서 Masonry, Splitter 추가 |
| 차트 | ❌ (본체) | AntV(G2 등)로 분리 — §6 참조 |
| 모션/이펙트 | ✅ | v6.4 BorderBeam (애니메이션 보더) 신규 |

### 2.4 Compound component 패턴

Ant Design는 **Configuration 중심**이지만 복합 구조에서 compound 패턴을 광범위하게 사용한다:

```jsx
<Form>
  <Form.Item label="Email" name="email" rules={[{ required: true }]}>
    <Input />
  </Form.Item>
</Form>

<Table columns={columns} dataSource={data} />   // Table은 configuration (columns 배열)

<Tabs items={[{ key, label, children }]} />      // v5+ items 기반 API (children 기반 비권장)

<Menu items={menuItems} />                        // items 기반

<Card>
  <Card.Meta title="..." />                       // compound + configuration 혼용
</Card>
```

**v5→v6의 API 방향성**: children 기반 API에서 **`items` 기반 configuration API**로 지속 이동 중. `Tabs`, `Menu`, `Steps`, `Breadcrumb`, `Collapse` 등이 `items` prop을 권장하며, v6는 이를 더 일관되게 정비했다. 이는 "복합 구조도 데이터(configuration)로 표현한다"는 Ant Design의 설계 철학을 보여준다.

---

## 3. Figma↔Code 매핑 충실도 ⭐ (핵심)

### 3.1 매핑 방향: Code-first, Figma는 커뮤니티 위임

```
Ant Design Code (antd, TypeScript)  ← single source of truth
         │
         ├──→ 공식 문서 (ant.design) — 토큰 값/컴포넌트 API 명세
         ├──→ 공식 Sketch kit — 수동 동기화 (Ant Group 디자인팀)
         └──→ 서드파티 Figma kit — 커뮤니티가 코드/문서를 참조해 수동 재현
              (AntUIKit, antforfigma.com, Figma Open Source Library, AntBlocks, Ruyi)
```

**공식 Figma↔Code 동기화 관계가 존재하지 않는다.** 공식 디자인↔코드 관계는 Sketch↔Code이며 이마저도 자동화되지 않은 수동 동기화다. Figma는 완전히 커뮤니티에 위임되어 있다.

> ⚠️ 조사 노트: 일부 자료는 "Ant Design 5.0 UI Kit" / "Ant Design System - v6" 같은 Figma Community 파일을 공식 kit으로 언급하지만, 공식 리소스 페이지(ant.design/docs/resources)는 Figma 리소스를 전부 서드파티로 분류한다. 공식 인증 여부를 판단할 때 공식 리소스 페이지가 권위 있는 출처다.

### 3.2 1:1 대응률

| 비교 쌍 | 대응률 | 근거 |
|---------|-------:|------|
| antd Code ↔ 공식 Sketch kit | **~90%** | 공식팀이 동일 스펙으로 관리. 단 Sketch kit 빌드(5.13.3 동봉, 2024-01)가 코드 최신(6.5.2)보다 뒤처짐 |
| antd Code ↔ 서드파티 Figma kit | **~60-80% (키트별 상이)** | AntUIKit 등은 "토큰/컴포넌트 1:1 대응"을 주장하나 공식 검증 없음. 대표 상태 위주 재현으로 props 전체 순열 미커버 |
| Figma kit ↔ Code 토큰 | **부분 대응** | 토큰 어휘(`colorPrimary` 등)는 공유 가능하나 Figma Variables ↔ TS 토큰 자동 연결 없음 |

### 3.3 네이밍 정합성

**컴포넌트명**: 서드파티 kit이 antd 컴포넌트명(Button, DatePicker, Table...)을 그대로 사용하는 경우 네이밍 정합성은 높다. 이는 antd의 컴포넌트명이 Figma에서도 자연스러운 영문 명사라 재현이 용이하기 때문이다.

**props명 ↔ variant명**: antd의 props는 React 생태계 관례를 따르므로 Figma variant property명과 직접 일치하지 않는 경우가 많다:

| antd prop | 값 | Figma kit의 일반적 variant 표현 |
|-----------|-----|-------------------------------|
| `type` (v5 Button) | `primary`/`default`/`dashed`/`text`/`link` | Type=Primary 등 (근사 대응) |
| `variant` + `color` (v6 Button) | `solid`/`outlined`/`dashed`/`filled`/`text`/`link` × `primary`/`default`/`danger` | 2개 property로 분해 필요 |
| `size` | v5 `large`/`middle`/`small` → **v6 `large`/`medium`/`small`로 통일** | Size property |
| `status` | `error`/`warning` | Status property |
| `disabled` | boolean | Disabled toggle |

v6는 `size` 값을 `large/medium/small`로 통일하고 `bordered`→`variant`, `visible`→`open`, `direction`→`orientation` 등 **시맨틱 일관성 리네이밍**을 대규모로 진행했다. 이는 Code 측 API의 정합성을 높이지만, 기존 Figma kit/문서와의 버전 드리프트를 발생시키는 요인이기도 하다.

### 3.4 Variant 매핑

antd의 variant는 단일 컴포넌트 + props 조합 방식이므로, Figma의 variant matrix와 개념적으로 대응하지만 **공식 매핑 테이블이 존재하지 않는다**:

```jsx
// antd — props 조합
<Button type="primary" size="large" danger ghost block loading disabled>Submit</Button>

// Figma kit — variant property 조합 (커뮤니티 재현)
// [Type=Primary, Size=Large, Danger=True, Ghost=True, Block=True, State=Loading]
```

- antd의 boolean prop 조합 공간은 Figma variant로 완전 열거하기 어려움 (loading × disabled × ghost × block...)
- 서드파티 kit은 대표 조합만 재현하므로, 코드가 지원하는 전체 props 순열 대비 커버리지 낮음
- v6의 `classNames`/`styles` 시맨틱 슬롯(`styles.header`, `classNames.root` 등)은 Figma의 레이어 구조와 개념적으로 대응하나 자동 매핑 없음

### 3.5 토큰 정합성

**잠재력은 높으나 공식 연결은 부재**:

- antd 토큰명(`colorPrimary`, `borderRadius`, `fontSize`)은 camelCase지만 의미론적으로 명확해 Figma Variables명으로 전사하기 용이
- 서드파티 kit(AntUIKit 등)은 코드 토큰 값을 Figma Variables/Styles로 재현해 "동일 어휘"를 주장
- 그러나 **코드 토큰이 변경되면 Figma 측이 수동 추종**해야 하며, 이를 검증하는 공식 프로세스가 없음
- v6의 CSS Variables 기본화(`--ant-color-primary`)로 브라우저 측 토큰 포맷이 표준화되었지만, 이것이 Figma Variables와 연결되는 파이프라인은 없음

### 3.6 구조적 대응

- Figma auto-layout ↔ antd Flex/Grid/Space: 개념적 대응. antd는 `Flex`, `Grid`(Row/Col), `Space`로 레이아웃을 컴포넌트화했으나 Figma auto-layout과의 자동 변환 없음
- Ruyi Design Assistant 같은 서드파티 플러그인이 "antd 코드 컴포넌트로 디자인 → 개발 친화적 코드 출력"을 시도하나 공식 지원 아님

### 3.7 종합 평가

| 항목 | 평가 | 근거 |
|------|:----:|------|
| 1:1 대응률 | ★★☆☆ | 공식 Figma kit 부재. Sketch는 ~90%이나 버전 지연, Figma는 커뮤니티 재현 |
| 네이밍 정합성 | ★★★☆ | 컴포넌트명 재현 용이. 단 props↔variant 공식 매핑 테이블 없음 |
| Variant 매핑 | ★★☆☆ | props 조합 공간을 Figma variant로 완전 열거 불가, 대표 상태만 재현 |
| 토큰 정합성 | ★★☆☆ | 토큰 어휘 공유 가능하나 공식 Variables↔Code 연결 없음, 수동 추종 |
| 구조적 대응 | ★★☆☆ | auto-layout↔Flex 개념 대응만 존재 |

**Ant Design의 Figma↔Code 매핑은 "공식 관계가 성립하지 않는다"는 점에서 구조적으로 가장 약한 차원이다.** 토큰 시스템 자체는 정교하지만(§1), 그것이 Figma라는 도구와 공식적으로 연결되지 않는다. 디자인-개발 핸드오프는 (a) 공식 Sketch kit 또는 (b) 커뮤니티 Figma kit에 의존하며, 어느 쪽도 코드와의 자동 동기화를 보장하지 않는다. 이는 "가장 인기 있는 React UI 라이브러리 중 하나가 Figma 공식 지원을 하지 않는다"는 흥미로운 벤치마크 관찰점이다.

---

## 4. API 설계 철학

### 4.1 Configuration 중심 + 제한적 Composition

Ant Design의 지배적 패턴은 **Configuration (props-driven)** 이다:

```jsx
<Table
  columns={[{ title: 'Name', dataIndex: 'name', sorter: true }]}
  dataSource={data}
  pagination={{ pageSize: 50 }}
  rowSelection={{ type: 'checkbox' }}
/>
```

복잡한 컴포넌트(Table, Form, Menu, Tabs)일수록 **데이터 구조(items/columns/rules)를 props로 주입**하는 방식을 취한다. 이는 엔터프라이즈 환경에서 UI를 서버 응답 데이터로부터 선언적으로 구성하려는 수요와 맞닿아 있다. Composition은 Card, Form.Item, Layout 등 구조적 컴포넌트에 제한적으로 사용된다.

### 4.2 스타일링: CSS-in-JS (@ant-design/cssinjs)

- v5부터 Less → **CSS-in-JS** 전환. `@ant-design/cssinjs` 자체 구현 사용 (styled-components/emotion 아님)
- 스타일은 토큰을 입력받는 **생성기 함수**(`GenerateStyle<Token, CSSObject>`)로 작성 — 컴포넌트별 `style/index.ts`
- 해시 기반 className으로 스타일 중복 제거 및 캐싱
- v6: **CSS Variables 기본** + `zeroRuntime` 정적 추출 옵션으로 런타임 비용 문제 대응

### 4.3 Headless 분리: rc-component 레이어

Ant Design는 핵심 인터랙션 로직을 **`react-component` 조직(111개 저장소)의 `rc-*` / `@rc-component/*` 패키지**로 분리한다:

```
@rc-component/select   (로직: 검색, 비동기, 가상스크롤, 키보드)
        ↓ antd가 스타일/테마를 입힘
antd <Select>
```

npm 의존성에서 확인되는 rc-패키지: `@rc-component/cascader`, `checkbox`, `collapse`, `color-picker`, `dialog`, `drawer`, `dropdown`, `form`, `image`, `input`, `input-number`, `mentions`, `menu`, `motion`, `notification`, `pagination`, `picker`, `progress`, `qrcode`, `rate`, `segmented`, `select`, `slider`, `steps`, `switch`, `table`, `tabs`, `tooltip`, `tour`, `tree`, `tree-select`, `trigger`, `upload` 등 30+개.

**단, Radix UI/shadcn 방식의 "true headless"와는 성격이 다르다**:
- rc-* 패키지는 antd 팀이 antd를 위해 만드는 **내부 기반 레이어**이며, 독립 사용이 가능하더라도 스타일 비종속성을 보장하는 공개 계약이 아님
- 사용자는 rc-*를 직접 소비해 커스텀 스킨을 입히는 것을 권장받지 않음 — antd는 "컴포넌트 라이브러리이자 디자인 규범"으로, 스타일 오버라이드보다 토큰 커스터마이징을 권장 (FAQ에서 컴포넌트 스타일 직접 오버라이드 비권장 명시)
- 즉, 분리는 되어 있으나 **headless를 공개 API로 노출하는 철학이 아니라 내부 구현 분리에 가깝다**

### 4.4 커스터마이징 계층

| 방법 | 범위 | 메커니즘 |
|------|------|----------|
| `theme.token` | 전역 | Seed/Map/Alias 오버라이드 |
| `theme.algorithm` | 전역 | 파생 알고리즘 교체 (dark/compact/커스텀) |
| `theme.components.X` | 컴포넌트 | Component Token + 컴포넌트 스코프 Alias 오버라이드 |
| `classNames`/`styles` 시맨틱 슬롯 (v6) | 인스턴스 | `styles.header`, `classNames.root` 등 구조별 주입 |
| `ConfigProvider` | 서브트리 | 중첩 테마, prefixCls, 전역 컴포넌트 설정 |
| `theme.useToken()` / `theme.getDesignToken()` | 소비 | 컴포넌트 밖에서 토큰 값 읽기 |

**Theme Editor**(ant.design/theme-editor)가 시각적 토큰 디버깅/테마 생성을 공식 지원한다.

---

## 5. 접근성

### 5.1 내장 ARIA

- **네이티브 요소 우선**: Button은 `<button>`/`<a>`를 상황에 맞게 렌더링. anchor 형태 disabled 시 `aria-disabled={true}` + `tabIndex={-1}` + `href` 제거로 접근성적으로 안전한 비활성 처리 (소스 확인)
- **rc-* 레이어에 WAI-ARIA 패턴 내장**: combobox(Select/AutoComplete), listbox, dialog(Modal), tablist(Tabs), tree(Tree), menu(Menu), slider 등 복합 위젯의 ARIA role/state 관리를 rc-패키지가 담당
- Table/List는 ARIA role 및 동적 상태 알림 지원
- `htmlType` 기본값을 `"button"`으로 해 실수에 의한 폼 제출 방지

### 5.2 키보드 네비게이션

- Select/AutoComplete: 방향키 옵션 이동, Enter 선택, Escape 닫기
- Modal/Drawer: focus trap (v6.2 `focusable.trap` 설정 추가), Escape 닫기 (v6.2부터 Tooltip/Popover/Popconfirm도 ESC 닫기 기본)
- Tabs/Menu/Tree: 방향키 내비게이션
- Button: 네이티브 요소에 위임 (Space/Enter 활성화)

### 5.3 표준 준수 수준

- **공식 WCAG 인증 레벨은 선언되어 있지 않다.** 서드파티 자료에서 WCAG 2.1 AA 모범 사례를 따른다고 언급되는 수준
- 중립색 팔레트가 WCAG 2.0 가독성을 고려해 투명도 기반으로 설계됨 (공식 컬러 스펙 문서)
- v6에서 접근성 지속 개선 중: Tree/Icon 접근성 개선(6.3), Image focus-visible + focus-trap(6.4), reduced-motion 지원 확대(6.5.1)
- **알려진 간극**: icon-only Button에 `aria-label`이 자동 부여되지 않음 (소스 확인 — 개발자가 수동 지정 필요), loading 상태에 `aria-busy` 미설정

**평가**: 복합 위젯의 ARIA/키보드 처리를 rc-* 전문 레이어가 담당하므로 기본기는 탄탄하나, 공식 WCAG 레벨 선언이 없고 icon-only 라벨 같은 세밀한 gaps가 남아 있다.

---

## 6. 동기화 거버넌스

### 6.1 프로세스: Code가 단일 소스, 디자인 리소스는 수동 추종

```
Ant Group Ant Design 팀
    │
    ├─ antd 코드 릴리스 (weekly patch / monthly minor)
    ├─ 공식 문서 (ant.design) — 토큰/API 명세
    ├─ 공식 Sketch kit — 수동 동기화 (코드 릴리스 대비 지연, 5.13.3 동봉 이후 별도 갱신 확인 안 됨)
    └─ Figma — 커뮤니티 위임 (공식 파이프라인 없음)
```

### 6.2 릴리스 주기

| 항목 | 주기 |
|------|------|
| Patch | **매주** (정기 버그 수정, 긴급 시 수시) |
| Minor | **매월** (신규 기능) |
| Major | 비정기 (v5 2022-11-18, v6 2025-11-22) |

Semantic Versioning 2.0 준수. v6는 비권장 API를 v6에서 경고만 내고 **v7에서 제거**하는 단계적 폐기 정책을 명시한다. v5 API 폐기 프로세스가 위키로 문서화되어 있다.

### 6.3 도구

| 도구 | 사용 여부 |
|------|----------|
| Style Dictionary | ❌ 공식 사용 없음 |
| Tokens Studio | ❌ 공식 사용 없음 |
| Figma Variables ↔ Code 파이프라인 | ❌ 없음 (공식 Figma kit 자체가 없음) |
| 자체 CSS-in-JS (`@ant-design/cssinjs`) | ✅ 토큰 → 스타일 런타임/정적 생성 |
| `@ant-design/cli` (v6.3.4+) | ✅ 컴포넌트 지식 조회, 사용 분석, 마이그레이션 안내 |
| Theme Editor | ✅ 시각적 테마/토큰 편집 |
| `@ant-design/static-style-extract` | ✅ zeroRuntime용 정적 CSS 추출 |

### 6.4 기여 모델 / 거버넌스

- **Collaborator 제도**: issue #3222에 신청 → 커뮤니티 투표 → 지속적 유지보수 참여 + 주요 기여(신규 컴포넌트, 대형 리팩터링) 요건 충족 시 권한 부여
- **역할 계층**: Collaborator → Maintainer(이슈 배정 가능) → 비활성 시 retirement 팀으로 이동 (권한 축소)
- PR 거버넌스: 기능 추가 PR은 collaborator `+1`/`-1` 코멘트, master/안정 브랜치 직접 push 금지, CI 통과 + 로컬 검증 후 안전 PR 머지
- **Ant Group 소속** — Ant Group(알리바바 계열 핀테크)이 핵심 개발을 주도하나 커뮤니티 기여자 제도 운영

### 6.5 생태계

| 생태계 | 내용 |
|--------|------|
| **AntV** | Ant Group 데이터 시각화 스위트 — G2(차트), G6(그래프), X6(플로우 편집), L7(지도), S2(피벗 테이블), F2(모바일). antd 본체에 차트가 없는 공백을 담당 |
| **ProComponents** | ProLayout, ProForm, ProTable, ProDescriptions, ProList, EditableProTable — 엔터프라이즈 상위 추상 |
| **다중 프레임워크 이식** | NG-ZORRO(Angular), Ant Design Vue, Ant Design Blazor, San, AtomUI(Avalonia) — 커뮤니티 이식 |
| **디자인 언어 문서화** | v6.5에 `DESIGN.md` 추가 — AI 디자인 도구가 Ant Design 시각 언어/컴포넌트 원형/테마 토큰을 이해하도록 지원 |

`DESIGN.md` 추가는 AI 도구 시대에 디자인 언어를 기계 판독 가능하게 문서화하려는 시도로, 토큰/컴포넌트 명세의 단일 소스를 강화하는 방향이다.

---

## 7. 핵심 요약

| 차원 | 평가 | 핵심 근거 |
|------|:----:|----------|
| 토큰 아키텍처 | ★★★★☆ | Seed→Map→Alias 3층 **알고리즘 파생** 구조는 분석 대상 중 가장 정교한 동적 토큰 시스템. camelCase TS 타입이 source of truth, dark/compact 알고리즘 조합, 컴포넌트 토큰 격리. 단 공식 Figma Variables 연결 부재로 -0.5 |
| 컴포넌트 인벤토리 | ★★★★★ | 70+개(73 export + ProComponents 6)로 최대 규모급. Data Entry/Display 중심의 엔터프라이즈 풀커버리지, Transfer/TreeSelect/Cascader 등 독보적 컴포넌트 |
| Figma↔Code 매핑 | ★★☆☆ | **공식 Figma kit 부재** — 공식 디자인 리소스는 Sketch, Figma는 커뮤니티 위임. 토큰 어휘 공유 가능성과 무관하게 공식 동기화 파이프라인/매핑 테이블 없음 |
| API 설계 철학 | ★★★★☆ | Configuration(items/columns) 중심 + CSS-in-JS 토큰 커스터마이징. rc-component로 로직 분리하나 true headless 공개 계약은 아님. v6 시맨틱 슬롯으로 유연성 보강 |
| 접근성 | ★★★☆ | rc-* 레이어의 WAI-ARIA 패턴 + 네이티브 요소 우선. 단 공식 WCAG 레벨 선언 없음, icon-only aria-label 미자동화 등 gaps |
| 동기화 거버넌스 | ★★★☆ | 코드 거버넌스(weekly/monthly 릴리스, collaborator 제도, 단계적 폐기)는 견고. 그러나 디자인↔코드 동기화는 Sketch 수동 추종, Figma는 커뮤니티 의존 |

### 벤치마크 관점에서의 시사점

Ant Design는 **"Code가 압도적으로 강하고, 디자인 도구 연결이 구조적으로 약한"** 시스템의 대표 사례다:

1. **토큰 시스템의 정교함과 Figma 연결 부재의 역설**: Seed→Map→Alias 알고리즘 파생은 동적 테마 생성 측면에서 Material Design의 ref→sys→comp보다 한발 앞선 설계지만, 이 정교한 토큰 체계가 공식적으로 어떤 Figma 아티팩트와도 연결되지 않는다. 토큰 아키텍처의 우수함이 디자인-개발 동기화로 이어지지 않는 사례다.

2. **공식 Figma kit 부재의 의미**: 세계에서 가장 많이 쓰이는 React UI 라이브러리 중 하나가 Figma 공식 지원을 하지 않는다는 것은, (a) Ant Group 내부 디자인 워크플로가 Sketch/Kitchen 중심으로 고착되어 있고, (b) Figma 생태계를 커뮤니티에 위임하는 것이 유지보수 부담 대비 허용 가능하다고 판단했음을 시사한다. 디자인 시스템의 "공식성"이 코드와 디자인 도구 사이에 대칭적으로 존재하지 않을 수 있음을 보여준다.

3. **Code-first 시스템의 매핑 한계**: single source of truth가 코드에 있는 시스템에서 Figma는 항상 2차 재현물이며, 버전 드리프트(Sketch kit이 5.13.3 시점에 멈춰 있는 것 등)가 구조적으로 발생한다. shadcn/ui(공식 Figma 없음)와 유사하지만, antd는 Sketch라는 공식 디자인 파트너가 존재한다는 점에서 "디자인 리소스는 있으나 Figma가 아닌" 독특한 위치를 점한다.

4. **엔터프라이즈 커버리지와 매핑 충실도의 트레이드오프**: 70+ 컴포넌트와 방대한 props 조합 공간은 그 자체로 Figma variant 완전 재현을 어렵게 만든다. 컴포넌트 인벤토리가 클수록 디자인 도구 측의 완전한 동기화가 기하급수적으로 어려워진다는 벤치마크 관찰을 뒷받침한다.
