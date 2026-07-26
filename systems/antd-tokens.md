# Ant Design — Design Token 시스템 코드 레벨 분석

> 소스 기준: `github.com/ant-design/ant-design` master (v5/v6)
> 분석 범위: Token 정의(Definition) → 소비(Consumption) → 거버넌스(Governance)

---

## 1. Token 정의 (Definition)

### 1.1 3-Layer Token 아키텍처

Ant Design의 token은 **Seed → Map → Alias** 3단계 derivation pipeline으로 구성된다.

```
SeedToken ──(algorithm)──▶ MapToken ──(aliasFn)──▶ AliasToken ──▶ Component styles
  ~35개                      ~180개                   ~90개 추가
```

각 레이어는 TypeScript interface로 정의되며, 상위 레이어를 `extends`한다:

```
AliasToken extends MapToken
MapToken extends SeedToken, ColorPalettes, ColorMapToken, SizeMapToken,
           HeightMapToken, StyleMapToken, FontMapToken, CommonMapToken
```

**파일 위치**: `components/theme/interface/`

---

### 1.2 SeedToken — 디자인 의도의 원점

**파일**: `components/theme/interface/seeds.ts`

```typescript
export interface SeedToken extends PresetColorType {
  // 색상
  colorPrimary: string;
  colorSuccess: string;
  colorWarning: string;
  colorError: string;
  colorInfo: string;
  colorTextBase: string;
  colorBgBase: string;
  colorLink: string;

  // 타이포그래피
  fontFamily: string;
  fontFamilyCode: string;
  fontSize: number;

  // 라인
  lineWidth: number;
  lineType: string;

  // 반경
  borderRadius: number;

  // 사이즈
  sizeUnit: number;
  sizeStep: number;
  sizePopupArrow: number;
  controlHeight: number;

  // z-index
  zIndexBase: number;
  zIndexPopupBase: number;

  // 이미지
  opacityImage: number;

  // 모션
  motionUnit: number;
  motionBase: number;
  motionEaseOutCirc: string;
  motionEaseInOutCirc: string;
  motionEaseInOut: string;
  motionEaseOutBack: string;
  motionEaseInBack: string;
  motionEaseInQuint: string;
  motionEaseOutQuint: string;
  motionEaseOut: string;

  // 모드
  wireframe: boolean;
  motion: boolean;
}
```

`PresetColorType`은 13개 preset 색상을 포함 (`components/theme/interface/presetColors.ts`):

```typescript
export const PresetColors = [
  'blue', 'purple', 'cyan', 'green', 'magenta', 'pink', 'red',
  'orange', 'yellow', 'volcano', 'geekblue', 'lime', 'gold',
] as const;
```

**Seed 기본값** (`components/theme/themes/seed.ts`):

| Token | 기본값 | 카테고리 |
|-------|--------|----------|
| `colorPrimary` | `'#1677ff'` | 색상 |
| `colorSuccess` | `'#52c41a'` | 색상 |
| `colorWarning` | `'#faad14'` | 색상 |
| `colorError` | `'#ff4d4f'` | 색상 |
| `colorInfo` | `'#1677ff'` | 색상 |
| `colorLink` | `''` (colorInfo 상속) | 색상 |
| `colorTextBase` | `''` (→ `#000`) | 색상 |
| `colorBgBase` | `''` (→ `#fff`) | 색상 |
| `blue` | `'#1677FF'` | Preset |
| `purple` | `'#722ED1'` | Preset |
| `cyan` | `'#13C2C2'` | Preset |
| `green` | `'#52C41A'` | Preset |
| `magenta` | `'#EB2F96'` | Preset |
| `red` | `'#F5222D'` | Preset |
| `orange` | `'#FA8C16'` | Preset |
| `yellow` | `'#FADB14'` | Preset |
| `volcano` | `'#FA541C'` | Preset |
| `geekblue` | `'#2F54EB'` | Preset |
| `gold` | `'#FAAD14'` | Preset |
| `lime` | `'#A0D911'` | Preset |
| `fontFamily` | `-apple-system, BlinkMacSystemFont, 'Segoe UI', ...` | 폰트 |
| `fontFamilyCode` | `'SFMono-Regular', Consolas, ...` | 폰트 |
| `fontSize` | `14` | 폰트 |
| `lineWidth` | `1` | 라인 |
| `lineType` | `'solid'` | 라인 |
| `borderRadius` | `6` | 반경 |
| `sizeUnit` | `4` | 사이즈 |
| `sizeStep` | `4` | 사이즈 |
| `sizePopupArrow` | `16` | 사이즈 |
| `controlHeight` | `32` | 사이즈 |
| `zIndexBase` | `0` | z-index |
| `zIndexPopupBase` | `1000` | z-index |
| `opacityImage` | `1` | 기타 |
| `motionUnit` | `0.1` | 모션 |
| `motionBase` | `0` | 모션 |
| `motionEaseOut` | `'cubic-bezier(0.215, 0.61, 0.355, 1)'` | 모션 |
| `motionEaseInOut` | `'cubic-bezier(0.645, 0.045, 0.355, 1)'` | 모션 |
| `motionEaseOutBack` | `'cubic-bezier(0.12, 0.4, 0.29, 1.46)'` | 모션 |
| `motionEaseInBack` | `'cubic-bezier(0.71, -0.46, 0.88, 0.6)'` | 모션 |
| `motionEaseInQuint` | `'cubic-bezier(0.755, 0.05, 0.855, 0.06)'` | 모션 |
| `motionEaseOutQuint` | `'cubic-bezier(0.23, 1, 0.32, 1)'` | 모션 |
| `motionEaseOutCirc` | `'cubic-bezier(0.08, 0.82, 0.17, 1)'` | 모션 |
| `motionEaseInOutCirc` | `'cubic-bezier(0.78, 0.14, 0.15, 0.86)'` | 모션 |
| `wireframe` | `false` | 모드 |
| `motion` | `true` | 모드 |

**총 Seed 토큰 수**: 약 **48개** (본체 35 + PresetColor 13)

---

### 1.3 Seed → Map Derivation 알고리즘

**파일**: `components/theme/themes/default/index.ts`

```typescript
export default function derivative(token: SeedToken): MapToken {
  const colorPalettes = Object.keys(defaultPresetColors)
    .map((colorKey) => {
      const colors = token[colorKey] === presetPrimaryColors[colorKey]
        ? presetPalettes[colorKey]
        : generate(token[colorKey]);
      return Array.from({ length: 10 }, () => 1).reduce((prev, _, i) => {
        prev[`${colorKey}-${i + 1}`] = colors[i];
        prev[`${colorKey}${i + 1}`] = colors[i];
        return prev;
      }, {});
    })
    .reduce((prev, cur) => ({ ...prev, ...cur }), {} as MapToken);

  return {
    ...token,
    ...colorPalettes,
    ...genColorMapToken(token, { generateColorPalettes, generateNeutralColorPalettes }),
    ...genFontMapToken(token.fontSize),
    ...genSizeMapToken(token),
    ...genControlHeight(token),
    ...genCommonMapToken(token),
  };
}
```

**핵심**: 하나의 `derivative` 함수가 5개의 generator를 조합하여 MapToken을 생성한다.

#### 1.3.1 색상 맵 생성 — `genColorMapToken`

**파일**: `components/theme/themes/shared/genColorMapToken.ts`

각 기능색(primary, success, warning, error, info)에 대해 10단계 팔레트를 생성하고,
이를 시맨틱 token에 매핑한다:

```typescript
const primaryColors = generateColorPalettes(colorPrimaryBase);

return {
  colorPrimaryBg: primaryColors[1],        // 가장 밝은 배경
  colorPrimaryBgHover: primaryColors[2],
  colorPrimaryBorder: primaryColors[3],
  colorPrimaryBorderHover: primaryColors[4],
  colorPrimaryHover: primaryColors[5],      // hover 상태
  colorPrimary: primaryColors[6],           // 기본 (seed와 동일)
  colorPrimaryActive: primaryColors[7],     // active 상태
  colorPrimaryTextHover: primaryColors[8],
  colorPrimaryText: primaryColors[9],
  colorPrimaryTextActive: primaryColors[10], // 가장 어두운 텍스트
  // ... success, warning, error, info 동일 패턴
};
```

**Neutral 색상** (배경/텍스트/보더)은 alpha 기반:

```typescript
// Light 모드 (components/theme/themes/default/colors.ts)
colorText: getAlphaColor(colorTextBase, 0.88),        // rgba(0,0,0,0.88)
colorTextSecondary: getAlphaColor(colorTextBase, 0.65),
colorTextTertiary: getAlphaColor(colorTextBase, 0.45),
colorTextQuaternary: getAlphaColor(colorTextBase, 0.25),

colorFill: getAlphaColor(colorTextBase, 0.15),
colorFillSecondary: getAlphaColor(colorTextBase, 0.06),
colorFillTertiary: getAlphaColor(colorTextBase, 0.04),
colorFillQuaternary: getAlphaColor(colorTextBase, 0.02),

colorBgLayout: getSolidColor(colorBgBase, 4),         // #f5f5f5
colorBgContainer: getSolidColor(colorBgBase, 0),       // #ffffff
colorBgElevated: getSolidColor(colorBgBase, 0),        // #ffffff
colorBorder: getSolidColor(colorBgBase, 15),           // #d9d9d9
colorBorderSecondary: getSolidColor(colorBgBase, 6),   // #f0f0f0
```

**ColorMapToken 총 필드 수**: 약 **80개** (기능색 5 × 10 + neutral ~22 + link 3 + preset hover/active + 기타)

#### 1.3.2 사이즈 맵 생성 — `genSizeMapToken`

**파일**: `components/theme/themes/shared/genSizeMapToken.ts`

```typescript
export default function genSizeMapToken(token: SeedToken): SizeMapToken {
  const { sizeUnit, sizeStep } = token;  // 기본값: 4, 4

  return {
    sizeXXL: sizeUnit * (sizeStep + 8),  // 48
    sizeXL:  sizeUnit * (sizeStep + 4),  // 32
    sizeLG:  sizeUnit * (sizeStep + 2),  // 24
    sizeMD:  sizeUnit * (sizeStep + 1),  // 20
    sizeMS:  sizeUnit * sizeStep,        // 16
    size:    sizeUnit * sizeStep,        // 16
    sizeSM:  sizeUnit * (sizeStep - 1),  // 12
    sizeXS:  sizeUnit * (sizeStep - 2),  // 8
    sizeXXS: sizeUnit * (sizeStep - 3),  // 4
  };
}
```

**공식**: `size = sizeUnit × (sizeStep + offset)` — 단 2개의 seed로 9단계 스케일 생성.

#### 1.3.3 컨트롤 높이 생성 — `genControlHeight`

**파일**: `components/theme/themes/shared/genControlHeight.ts`

```typescript
const genControlHeight = (token: SeedToken): HeightMapToken => {
  const { controlHeight } = token;  // 기본값: 32

  return {
    controlHeightSM: controlHeight * 0.75,   // 24
    controlHeightXS: controlHeight * 0.5,    // 16
    controlHeightLG: controlHeight * 1.25,   // 40
  };
};
```

#### 1.3.4 폰트 맵 생성 — `genFontMapToken`

**파일**: `components/theme/themes/shared/genFontMapToken.ts`

```typescript
const genFontMapToken = (fontSize: number): FontMapToken => {
  const fontSizePairs = genFontSizes(fontSize);  // [12, 14, 16, 20, 24, 30, 38]
  // ...
  return {
    fontSizeSM,                    // 12
    fontSize: fontSizeMD,          // 14
    fontSizeLG,                    // 16
    fontSizeXL: fontSizes[3],      // 20

    fontSizeHeading1: fontSizes[6], // 38
    fontSizeHeading2: fontSizes[5], // 30
    fontSizeHeading3: fontSizes[4], // 24
    fontSizeHeading4: fontSizes[3], // 20
    fontSizeHeading5: fontSizes[2], // 16

    lineHeight, lineHeightLG, lineHeightSM,
    fontHeight, fontHeightLG, fontHeightSM,
    lineHeightHeading1, ..., lineHeightHeading5,
  };
};
```

**FontMapToken**: 19개 필드

#### 1.3.5 공통 맵 생성 — `genCommonMapToken`

**파일**: `components/theme/themes/shared/genCommonMapToken.ts`

```typescript
export default function genCommonMapToken(token: SeedToken): CommonMapToken {
  const { motionUnit, motionBase, borderRadius, lineWidth } = token;

  return {
    // 모션: motionBase + motionUnit * n
    motionDurationFast: `${(motionBase + motionUnit).toFixed(1)}s`,      // 0.1s
    motionDurationMid:  `${(motionBase + motionUnit * 2).toFixed(1)}s`,  // 0.2s
    motionDurationSlow: `${(motionBase + motionUnit * 3).toFixed(1)}s`,  // 0.3s

    // 라인
    lineWidthBold: lineWidth + 1,  // 2

    // 반경 (genRadius)
    ...genRadius(borderRadius),
  };
}
```

#### 1.3.6 반경 스케일 — `genRadius`

**파일**: `components/theme/themes/shared/genRadius.ts`

```typescript
const genRadius = (radiusBase: number) => {
  // borderRadiusLG: base 6 → 8, base 8 → 10, base ≥ 16 → 16 (cap)
  // borderRadiusSM: base 6 → 4, base 8 → 6, base ≥ 16 → 8
  // borderRadiusXS: base < 6 → 1, base ≥ 6 → 2
  // borderRadiusOuter: base < 8 → 4, base ≥ 8 → 6
  return { borderRadius, borderRadiusXS, borderRadiusSM, borderRadiusLG, borderRadiusOuter };
};
```

기본값 `borderRadius: 6` 기준: `XS=2, SM=4, base=6, LG=8, Outer=4`

**StyleMapToken**: 5개 필드 (`lineWidthBold`, `borderRadiusXS`, `borderRadiusSM`, `borderRadiusLG`, `borderRadiusOuter`)

---

### 1.4 @ant-design/colors — HSB 팔레트 생성 알고리즘

**파일**: `@ant-design/colors` 패키지 (`src/generate.ts`)

```typescript
const hueStep = 2;              // 색상환 단계 (도)
const saturationStep = 0.16;    // 채도 단계 (밝은 부분)
const saturationStep2 = 0.05;   // 채도 단계 (어두운 부분)
const brightnessStep1 = 0.05;   // 명도 단계 (밝은 부분)
const brightnessStep2 = 0.15;   // 명도 단계 (어두운 부분)
const lightColorCount = 5;      // 주 색상 위 밝은 색 5개
const darkColorCount = 4;       // 주 색상 아래 어두운 색 4개
```

**알고리즘 구조**:

```typescript
export default function generate(color: ColorInput, opts = {}): string[] {
  const hsv = new FastColor(color).toHsv();
  const patterns = [];

  // 밝은 색 5개 (i = 5 → 1)
  for (let i = lightColorCount; i > 0; i--) {
    patterns.push(new FastColor({
      h: getHue(hsv, i, true),       // hue ± 2° × i
      s: getSaturation(hsv, i, true), // saturation - 0.16 × i
      v: getValue(hsv, i, true),      // brightness + 0.05 × i
    }));
  }

  // 기준색 (입력색 그대로)
  patterns.push(pColor);

  // 어두운 색 4개 (i = 1 → 4)
  for (let i = 1; i <= darkColorCount; i++) {
    patterns.push(new FastColor({
      h: getHue(hsv, i),             // hue ∓ 2° × i
      s: getSaturation(hsv, i),       // saturation + 0.05 × i
      v: getValue(hsv, i),            // brightness - 0.15 × i
    }));
  }

  // dark 테마: 배경색(#141414)과 mix
  if (opts.theme === 'dark') {
    return darkColorMap.map(({ index, amount }) =>
      new FastColor('#141414').mix(patterns[index], amount).toHexString()
    );
  }

  return patterns.map(c => c.toHexString());
}
```

**Hue 방향 로직**:

```typescript
function getHue(hsv, i, light?) {
  // hue 60°~240° (녹~청 범위): 밝은 색은 hue 감소, 어두운 색은 hue 증가
  // 그 외 (적~황 범위): 밝은 색은 hue 증가, 어두운 색은 hue 감소
  if (hsv.h >= 60 && hsv.h <= 240) {
    hue = light ? hsv.h - hueStep * i : hsv.h + hueStep * i;
  } else {
    hue = light ? hsv.h + hueStep * i : hsv.h - hueStep * i;
  }
}
```

**결과**: 10색 팔레트 `[light5, light4, light3, light2, light1, primary, dark1, dark2, dark3, dark4]`

Light/Dark 모드에서 팔레트 인덱스 매핑이 다르다:

```typescript
// Light (default/colors.ts)
{ 1: colors[0], 2: colors[1], ..., 6: colors[5], 7: colors[6], 8: colors[4], 9: colors[5], 10: colors[6] }

// Dark (dark/colors.ts) — 역전 매핑
{ 1: colors[0], 2: colors[1], ..., 5: colors[6], 6: colors[5], 7: colors[4], 8: colors[6], 9: colors[5], 10: colors[4] }
```

Dark 모드에서 **5~10번이 역전**되어, 어두운 배경에 맞는 contrast를 확보한다.

---

### 1.5 darkAlgorithm / compactAlgorithm

#### darkAlgorithm

**파일**: `components/theme/themes/dark/index.ts`

```typescript
const derivative: DerivativeFunc<SeedToken, MapToken> = (token, mapToken) => {
  // 1. dark 옵션으로 팔레트 재생성
  const colors = generate(token[colorKey], { theme: 'dark' });

  // 2. defaultAlgorithm 결과를 base로 사용
  const mergedMapToken = mapToken ?? defaultAlgorithm(token);

  // 3. dark 전용 colorMapToken으로 덮어쓰기
  const colorMapToken = genColorMapToken(token, {
    generateColorPalettes,        // dark 버전
    generateNeutralColorPalettes, // dark 버전
  });

  return {
    ...mergedMapToken,
    ...colorPalettes,
    ...colorMapToken,
    // dark 전용 override
    colorPrimaryBg: colorMapToken.colorPrimaryBorder,
    colorPrimaryBgHover: colorMapToken.colorPrimaryBorderHover,
  };
};
```

**Dark neutral 색상** (Light와 대비):

| Token | Light | Dark |
|-------|-------|------|
| `colorText` | `rgba(0,0,0,0.88)` | `rgba(255,255,255,0.85)` |
| `colorBgBase` | `#fff` | `#000` |
| `colorBgContainer` | `getSolidColor(#fff, 0)` | `getSolidColor(#000, 8)` |
| `colorBgElevated` | `getSolidColor(#fff, 0)` | `getSolidColor(#000, 12)` |
| `colorBorder` | `getSolidColor(#fff, 15)` | `getSolidColor(#000, 26)` |
| `colorBgBlur` | `'transparent'` | `rgba(255,255,255,0.04)` |

#### compactAlgorithm

**파일**: `components/theme/themes/compact/index.ts`

```typescript
const derivative: DerivativeFunc<SeedToken, MapToken> = (token, mapToken) => {
  const mergedMapToken = mapToken ?? defaultAlgorithm(token);

  const fontSize = mergedMapToken.fontSizeSM;       // 14 → 12로 축소
  const controlHeight = mergedMapToken.controlHeight - 4;  // 32 → 28

  return {
    ...mergedMapToken,
    ...genCompactSizeMapToken(mapToken ?? token),  // 전체 사이즈 축소
    ...genFontMapToken(fontSize),                  // 작은 폰트 기준 재생성
    controlHeight,
    ...genControlHeight({ ...mergedMapToken, controlHeight }),
  };
};
```

**알고리즘 합성**: 배열로 전달하면 순차 적용:

```tsx
<ConfigProvider theme={{ algorithm: [darkAlgorithm, compactAlgorithm] }}>
```

---

### 1.6 AliasToken — 시맨틱 매핑 레이어

**파일**: `components/theme/interface/alias.ts`

MapToken을 상속하고, 컴포넌트가 직접 소비하는 시맨틱 token을 추가:

```typescript
export interface AliasToken extends MapToken {
  // 색상 시맨틱
  colorFillContentHover: string;
  colorFillAlter: string;
  colorFillContent: string;
  colorBgContainerDisabled: string;
  colorBgTextHover: string;
  colorBgTextActive: string;
  colorBorderBg: string;
  colorSplit: string;

  // 텍스트 시맨틱
  colorTextPlaceholder: string;
  colorTextDisabled: string;
  colorTextHeading: string;
  colorTextLabel: string;
  colorTextDescription: string;
  colorTextLightSolid: string;

  // 아이콘
  colorIcon: string;
  colorIconHover: string;
  colorHighlight: string;

  // 컨트롤
  controlOutline: string;
  controlOutlineWidth: number;
  controlItemBgHover: string;
  controlItemBgActive: string;
  controlItemBgActiveHover: string;
  controlInteractiveSize: number;
  controlItemBgActiveDisabled: string;
  controlPaddingHorizontal: number;
  controlPaddingHorizontalSM: number;
  lineWidthFocus: number;

  // 간격 — padding
  paddingXXS: number;  // 4
  paddingXS: number;   // 8
  paddingSM: number;   // 12
  padding: number;     // 16
  paddingMD: number;   // 20
  paddingLG: number;   // 24
  paddingXL: number;   // 32

  // 간격 — padding 콘텐츠
  paddingContentHorizontalLG: number;
  paddingContentHorizontal: number;
  paddingContentHorizontalSM: number;
  paddingContentVerticalLG: number;
  paddingContentVertical: number;
  paddingContentVerticalSM: number;

  // 간격 — margin
  marginXXS: number;   // 4
  marginXS: number;    // 8
  marginSM: number;    // 12
  margin: number;      // 16
  marginMD: number;    // 20
  marginLG: number;    // 24
  marginXL: number;    // 32
  marginXXL: number;   // 48

  // 폰트
  fontSizeIcon: number;
  fontWeightStrong: number;

  // 기타
  opacityLoading: number;
  boxShadow: string;
  boxShadowSecondary: string;
  boxShadowTertiary: string;
  linkDecoration: React.CSSProperties['textDecoration'];
  linkHoverDecoration: React.CSSProperties['textDecoration'];
  linkFocusDecoration: React.CSSProperties['textDecoration'];

  // 반응형 브레이크포인트
  screenXS: number; screenXSMin: number; screenXSMax: number;
  screenSM: number; screenSMMin: number; screenSMMax: number;
  screenMD: number; screenMDMin: number; screenMDMax: number;
  screenLG: number; screenLGMin: number; screenLGMax: number;
  screenXL: number; screenXLMin: number; screenXLMax: number;
  screenXXL: number; screenXXLMin: number; screenXXLMax: number;
  screenXXXL: number; screenXXXLMin: number;

  // 그림자
  boxShadowPopoverArrow: string;
  dropShadowPopover: string;
  boxShadowCard: string;
  boxShadowDrawerRight: string;
  boxShadowDrawerLeft: string;
  boxShadowDrawerUp: string;
  boxShadowDrawerDown: string;
  boxShadowTabsOverflowLeft: string;
  boxShadowTabsOverflowRight: string;
  boxShadowTabsOverflowTop: string;
  boxShadowTabsOverflowBottom: string;
}
```

**AliasToken 추가 필드 수**: 약 **90개**

---

### 1.7 Component Token — Button 사례

**파일**: `components/button/style/token.ts`

각 컴포넌트는 고유 `ComponentToken` interface를 정의한다.

```typescript
export interface ComponentToken {
  fontWeight: CSSProperties['fontWeight'];
  iconGap: CSSProperties['gap'];
  defaultShadow: string;
  primaryShadow: string;
  dangerShadow: string;
  primaryColor: string;
  defaultColor: string;
  defaultBg: string;
  defaultBorderColor: string;
  dangerColor: string;
  defaultHoverBg: string;
  defaultHoverColor: string;
  defaultHoverBorderColor: string;
  defaultActiveBg: string;
  defaultActiveColor: string;
  defaultActiveBorderColor: string;
  borderColorDisabled: string;         // @deprecated
  defaultGhostColor: string;
  ghostBg: string;
  defaultGhostBorderColor: string;
  solidTextColor: string;
  textTextColor: string;
  textTextHoverColor: string;
  textTextActiveColor: string;
  paddingInline: CSSProperties['paddingInline'];
  paddingInlineLG: CSSProperties['paddingInline'];
  paddingInlineSM: CSSProperties['paddingInline'];
  paddingBlock: CSSProperties['paddingBlock'];       // @deprecated
  paddingBlockLG: CSSProperties['paddingBlock'];     // @deprecated
  paddingBlockSM: CSSProperties['paddingBlock'];     // @deprecated
  onlyIconSize: number | string;
  onlyIconSizeLG: number | string;
  onlyIconSizeSM: number | string;
  linkHoverBg: string;
  textHoverBg: string;
  contentFontSize: number;
  contentFontSizeLG: number;
  contentFontSizeSM: number;
  contentLineHeight: number;           // @deprecated
  contentLineHeightLG: number;         // @deprecated
  contentLineHeightSM: number;         // @deprecated
  defaultBgDisabled: string;
  dashedBgDisabled: string;
}
```

**Button ComponentToken 필드 수**: 약 **40개** + PresetColor 기반 동적 token (`${colorKey}ShadowColor`, `${colorKey}Hover`, `${colorKey}Active`)

#### `prepareComponentToken` — 글로벌 token → 컴포넌트 token 파생

```typescript
export const prepareComponentToken: GetDefaultToken<'Button'> = (token) => {
  const contentFontSize = token.contentFontSize ?? token.fontSize;
  const solidTextColor = isBright(new AggregationColor(token.colorBgSolid), '#fff')
    ? '#000' : '#fff';

  return {
    fontWeight: 400,
    iconGap: token.marginXS,
    defaultShadow: `0 ${token.controlOutlineWidth}px 0 ${token.controlTmpOutline}`,
    primaryShadow: `0 ${token.controlOutlineWidth}px 0 ${token.controlOutline}`,
    dangerShadow: `0 ${token.controlOutlineWidth}px 0 ${token.colorErrorOutline}`,
    primaryColor: token.colorTextLightSolid,
    dangerColor: token.colorTextLightSolid,
    defaultColor: token.colorText,
    defaultBg: token.colorBgContainer,
    defaultBorderColor: token.colorBorder,
    defaultHoverBg: token.colorBgContainer,
    defaultHoverColor: token.colorPrimaryHover,
    defaultHoverBorderColor: token.colorPrimaryHover,
    defaultActiveBg: token.colorBgContainer,
    defaultActiveColor: token.colorPrimaryActive,
    defaultActiveBorderColor: token.colorPrimaryActive,
    paddingInline: token.paddingContentHorizontal - token.lineWidth,
    paddingInlineLG: token.paddingContentHorizontal - token.lineWidth,
    paddingInlineSM: 8 - token.lineWidth,
    onlyIconSize: 'inherit',
    textHoverBg: token.colorFillTertiary,
    solidTextColor,
    contentFontSize,
    // ... paddingBlock 계산식 포함
  };
};
```

---

### 1.8 Token 총계 및 네이밍 규칙

#### 총 Token 수

| 레이어 | 필드 수 | 설명 |
|--------|---------|------|
| SeedToken | ~48 | 본체 35 + PresetColor 13 |
| MapToken (추가분) | ~130 | ColorMap ~80 + Size 9 + Height 3 + Style 5 + Font 19 + Common 3 + Palette 260(13색×10×2) |
| AliasToken (추가분) | ~90 | 시맨틱 매핑 |
| ComponentToken (Button) | ~40+ | 컴포넌트별 상이 |
| **전체 글로벌 token** | **~270+** | Seed + Map + Alias (Palette 동적 생성 제외) |
| **컴포넌트 token 총합** | **수백 개** | 70+ 컴포넌트 각각 고유 ComponentToken 보유 |

#### 네이밍 규칙 — camelCase 택소노미

```
{category}{Property}{Variant}{State}
```

| 패턴 | 예시 | 설명 |
|------|------|------|
| `color{Role}` | `colorPrimary`, `colorSuccess` | 기능색 seed |
| `color{Role}{Usage}` | `colorPrimaryBg`, `colorPrimaryHover` | 용도별 파생 |
| `color{Role}{Usage}{State}` | `colorPrimaryBgHover`, `colorErrorBorderHover` | 상태 |
| `color{Surface}` | `colorBgContainer`, `colorBgElevated` | 표면 |
| `colorText{Level}` | `colorText`, `colorTextSecondary` | 텍스트 계층 |
| `fontSize{Variant}` | `fontSize`, `fontSizeLG`, `fontSizeHeading1` | 폰트 스케일 |
| `size{Scale}` | `size`, `sizeLG`, `sizeXXS` | 일반 사이즈 |
| `controlHeight{Variant}` | `controlHeight`, `controlHeightSM` | 컨트롤 높이 |
| `borderRadius{Variant}` | `borderRadius`, `borderRadiusLG` | 반경 |
| `padding{Direction}{Scale}` | `paddingContentHorizontalLG` | 간격 |
| `motion{Property}` | `motionDurationFast`, `motionEaseInOut` | 모션 |
| `line{Property}` | `lineWidth`, `lineWidthBold`, `lineType` | 라인 |
| `screen{BP}{Bound}` | `screenMD`, `screenMDMin`, `screenMDMax` | 브레이크포인트 |
| `boxShadow{Context}` | `boxShadow`, `boxShadowCard`, `boxShadowDrawerRight` | 그림자 |

**크기 접미사 스케일**: `XXS < XS < SM < (base) < MD < LG < XL < XXL`

---

## 2. Token 소비 (Consumption)

### 2.1 `genStyleHooks` 패턴 — 컴포넌트 스타일 등록

**파일**: `components/theme/util/genStyleUtils.ts`

```typescript
import { genStyleUtils } from '@ant-design/cssinjs-utils';

export const { genStyleHooks, genComponentStyleHook, genSubStyleComponent } = genStyleUtils<
  ComponentTokenMap, AliasToken, SeedToken
>({
  usePrefix: () => {
    const { getPrefixCls, iconPrefixCls } = useContext(ConfigContext);
    return { rootPrefixCls: getPrefixCls(), iconPrefixCls };
  },
  useToken: () => {
    const [theme, realToken, hashId, token, cssVar, zeroRuntime] = useLocalToken();
    return { theme, realToken, hashId, token, cssVar, zeroRuntime };
  },
  useCSP: () => {
    const { csp } = useContext(ConfigContext);
    return csp ?? {};
  },
  getResetStyles: (token, config) => [genLinkStyle(token), genIconStyle(...)],
  getCommonStyle: genCommonStyle,
  getCompUnitless: (() => unitless),
});
```

`genStyleUtils`는 `@ant-design/cssinjs-utils`에서 제공하며, 내부적으로:
1. `useToken()`으로 현재 테마 token 조회
2. `prepareComponentToken(globalToken)`으로 컴포넌트 기본값 계산
3. 사용자 override(`ConfigProvider.theme.components.Button`) 병합
4. `mergeToken()`으로 글로벌 + 컴포넌트 token 통합
5. 스타일 생성 함수 실행 → CSS-in-JS 객체 생성
6. `useStyleRegister()`로 `<style>` 태그 삽입 (캐싱 + 해시 기반 중복 제거)

### 2.2 Button 스타일 소비 — 실제 코드

**파일**: `components/button/style/index.ts`

```typescript
export default genStyleHooks(
  'Button',
  (token) => {
    const buttonToken = prepareToken(token);
    return [
      genSharedButtonStyle(buttonToken),
      genSizeBaseButtonStyle(buttonToken),
      genSizeSmallButtonStyle(buttonToken),
      genSizeLargeButtonStyle(buttonToken),
      genBlockButtonStyle(buttonToken),
      genVariantStyle(buttonToken),
      genGroupStyle(buttonToken),
    ];
  },
  prepareComponentToken,
  {
    unitless: {
      fontWeight: true,
      contentLineHeight: true,
      contentLineHeightSM: true,
      contentLineHeightLG: true,
    },
  },
);
```

**Token 소비 예시** — `genSharedButtonStyle`:

```typescript
const genSharedButtonStyle: GenerateStyle<ButtonToken, CSSObject> = (token) => {
  const { componentCls, iconCls, fontWeight, opacityLoading,
          motionDurationSlow, motionEaseInOut, iconGap, calc } = token;

  return {
    [componentCls]: {
      outline: 'none',
      display: 'inline-flex',
      gap: iconGap,                              // ← component token
      fontWeight,                                 // ← component token
      transition: `all ${token.motionDurationMid} ${token.motionEaseInOut}`,  // ← global token
      userSelect: 'none',
      cursor: 'pointer',
      // ...
    },
  };
};
```

**사이즈 변형** — `mergeToken`으로 token 재매핑:

```typescript
const genSizeSmallButtonStyle = (token: ButtonToken) => {
  const smallToken = mergeToken<ButtonToken>(token, {
    controlHeight: token.controlHeightSM,          // 32 → 24
    fontSize: token.contentFontSizeSM,
    padding: token.paddingXS,
    buttonPaddingHorizontal: token.paddingInlineSM,
    borderRadius: token.borderRadiusSM,            // 6 → 4
    buttonIconOnlyFontSize: token.onlyIconSizeSM,
  });
  return genButtonStyle(smallToken, `${token.componentCls}-sm`);
};
```

**Token 소비 플로우**:

```
GlobalToken (AliasToken)
        ↓
prepareComponentToken(globalToken) → ComponentToken 기본값
        ↓
ConfigProvider.theme.components.Button override 병합
        ↓
mergeToken(global, component) → FullToken<'Button'>
        ↓
prepareToken(fullToken) → ButtonToken (buttonPaddingHorizontal 등 추가)
        ↓
genXxxStyle(buttonToken) → CSSObject
        ↓
@ant-design/cssinjs → <style> 태그 삽입
```

### 2.3 CSS-in-JS 런타임 — @ant-design/cssinjs

Ant Design v5는 `@ant-design/cssinjs` (Emotion/Stylis 기반 fork)를 사용:

1. **스타일 생성**: 컴포넌트 렌더 시 `useStyleRegister()` 호출
2. **해시 캐싱**: token 값 + 컴포넌트명으로 해시 생성 → 동일 스타일 재삽입 방지
3. **`<style>` 삽입**: `<head>`에 동적 `<style data-token-hash="xxx">` 태그 추가
4. **CSS-in-JS → CSS**: JS 객체가 실제 CSS 텍스트로 직렬화

```typescript
// useToken 내부 (components/theme/useToken.ts)
const [token, hashId, realToken] = useCacheToken<GlobalToken, SeedToken>(
  mergedTheme,
  [defaultSeedToken, rootDesignToken],
  {
    salt: `${version}-${hashed || ''}`,
    override,
    getComputedToken,
    cssVar: { ...cssVar, unitless, ignore, preserve },
    nonce: csp?.nonce,
  },
);
```

### 2.4 CSS Variables 모드 — `--ant-*` 출력

v5.7+에서 `cssVar: true` 설정 시 token이 CSS custom property로 출력:

```tsx
<ConfigProvider
  theme={{
    cssVar: true,
    // 또는 상세 설정:
    // cssVar: { prefix: 'myapp', key: 'theme-dark' },
    token: { colorPrimary: '#1890ff' },
  }}
>
  <App />
</ConfigProvider>
```

**출력 CSS** (개념적):

```css
:where(.css-dev-only-do-not-override-xxxx) {
  --ant-color-primary: #1890ff;
  --ant-color-success: #52c41a;
  --ant-color-warning: #faad14;
  --ant-color-error: #ff4d4f;
  --ant-font-size: 14px;
  --ant-border-radius: 6px;
  --ant-control-height: 32px;
  --ant-motion-duration-fast: 0.1s;
  --ant-motion-duration-mid: 0.2s;
  --ant-motion-duration-slow: 0.3s;
  /* ... 모든 token */
}
```

**v6 변경**: v6에서는 CSS Variables 모드가 **기본 활성화** (IE 지원 중단에 따라).

**장점**:
- 런타임 테마 전환 시 스타일 재생성 없이 CSS 변수값만 변경
- 다중 테마 공존 시 `key`로 변수 네임스페이스 분리
- SSR 하이드레이션 성능 개선

### 2.5 ConfigProvider theme API

```tsx
import { ConfigProvider, theme } from 'antd';

<ConfigProvider
  theme={{
    // 1. 글로벌 Seed/Map/Alias token override
    token: {
      colorPrimary: '#00b96b',
      borderRadius: 4,
      wireframe: true,
    },

    // 2. 알고리즘 선택 (합성 가능)
    algorithm: [theme.darkAlgorithm, theme.compactAlgorithm],

    // 3. 컴포넌트별 token override
    components: {
      Button: {
        colorPrimary: '#00b96b',
        algorithm: true,  // 이 컴포넌트만 팔레트 재파생
        controlHeight: 40,
        fontWeight: 600,
      },
      Input: {
        colorPrimary: '#eb2f96',
        algorithm: true,
      },
    },

    // 4. CSS Variables 모드
    cssVar: true,

    // 5. 해시 className
    hashed: true,

    // 6. 부모 ConfigProvider 상속
    inherit: true,
  }}
>
  <App />
</ConfigProvider>
```

**theme API 속성**:

| 속성 | 타입 | 기본값 | 용도 |
|------|------|--------|------|
| `token` | `AliasToken` (partial) | — | 글로벌 token override |
| `algorithm` | `(seed) => map` \| 배열 | `defaultAlgorithm` | 파생 알고리즘 |
| `components` | `ComponentsConfig` | — | 컴포넌트별 token |
| `cssVar` | `boolean \| { prefix?, key? }` | — | CSS 변수 모드 |
| `hashed` | `boolean` | `true` | 해시 className |
| `inherit` | `boolean` | `true` | 상위 테마 상속 |

### 2.6 런타임 Token 읽기

```tsx
// React 컴포넌트 내부 — Hook
import { theme } from 'antd';

function MyComponent() {
  const { token } = theme.useToken();
  return (
    <div style={{
      color: token.colorPrimary,
      borderRadius: token.borderRadius,
      padding: token.padding,
    }}>
      Token 기반 스타일
    </div>
  );
}

// React 외부 — 정적 호출
const globalToken = theme.getDesignToken({
  token: { colorPrimary: '#1890ff' },
});
// → { colorPrimary: '#1890ff', colorPrimaryBg: '#e6f7ff', ... }
```

`theme.useToken()` 내부 구현 (`components/theme/useToken.ts`):

```typescript
export default function useToken() {
  const { token: rootDesignToken, hashed, theme, override, cssVar } =
    React.useContext(DesignTokenContext);

  const mergedTheme = theme || defaultTheme;

  const [token, hashId, realToken] = useCacheToken<GlobalToken, SeedToken>(
    mergedTheme,
    [defaultSeedToken, rootDesignToken],
    { salt, override, getComputedToken, cssVar: { ...cssVar, unitless, ignore, preserve } },
  );

  return [mergedTheme, realToken, hashed ? hashId : '', token, cssVar, !!zeroRuntime];
}
```

### 2.7 컴포넌트 레벨 Token Override

```tsx
<ConfigProvider
  theme={{
    token: { colorPrimary: '#1677ff' },        // 전체는 파란색
    components: {
      Button: {
        // ComponentToken override
        colorPrimary: '#00b96b',               // Button만 초록색
        controlHeight: 40,
        fontWeight: 600,
        defaultBg: '#f0f0f0',
        paddingInline: 20,

        // algorithm: true → Button 전용 팔레트 재파생
        algorithm: true,
      },
    },
  }}
>
  <Button type="primary">초록 버튼</Button>
</ConfigProvider>
```

`algorithm: true` 설정 시 해당 컴포넌트의 seed override로부터 **전체 팔레트를 재파생**한다.
설정하지 않으면 글로벌 파생 값을 상속하고 지정된 token만 개별 override한다.

---

## 3. Token 거버넌스 (Governance)

### 3.1 TypeScript 타입 = 스키마

Ant Design의 token 거버넌스 핵심은 **TypeScript interface 자체가 스키마**라는 점:

```typescript
// SeedToken에 없는 token은 ConfigProvider에서 타입 에러
<ConfigProvider theme={{ token: { colorPrimaryy: '#fff' } }}>
//                                       ^^^^^^^^^^^^ TS Error: 'colorPrimaryy' does not exist

// ComponentToken도 타입 안전
<ConfigProvider theme={{ components: { Button: { invalidProp: 1 } } }}>
//                                                 ^^^^^^^^^^^ TS Error
```

**타입 계층**:

```typescript
// components/theme/interface/index.ts
export type { SeedToken, MapToken, AliasToken, ... };

// ComponentTokenMap — 모든 컴포넌트 token의 맵
interface ComponentTokenMap {
  Button: ButtonComponentToken;
  Input: InputComponentToken;
  Table: TableComponentToken;
  // ... 70+ 컴포넌트
}

// FullToken<'Button'> = AliasToken & ButtonComponentToken & { componentCls, iconCls, ... }
```

**JSDoc 기반 메타데이터**: 각 token에 `@desc` (중국어) / `@descEN` (영어) 설명 포함:

```typescript
/**
 * @desc 文字字重
 * @descEN Font weight of text
 */
fontWeight: CSSProperties['fontWeight'];
```

이 메타데이터는 Theme Editor와 문서 사이트에 자동 반영된다.

### 3.2 v5 → v6 Token 변경

v6은 **"기술적 업그레이드"** 로, Seed/Map/Alias token 이름 변경은 **없다**.

주요 변경:

| 변경 | 내용 |
|------|------|
| **CSS Variables 기본화** | IE 지원 중단으로 `cssVar` 기본 활성화 |
| **`styles`/`classNames` 통합** | `bodyStyle`, `maskStyle` 등 → `styles.body`, `styles.mask` |
| **`bordered` → `variant`** | Card, Input, Select 등 (deprecated in v6, removed in v7) |
| **`size` 통일** | `"default"` → `"medium"`, `"middle"` → `"medium"` |
| **React 18 필수** | React 17 지원 중단 |
| **DOM 구조 변경** | 내부 셀렉터 기반 커스텀 CSS 깨질 수 있음 |

**Token 관점**: v5 → v6에서 token 이름 변경/삭제 없음.
v4 → v5에서는 Less 변수 → CSS-in-JS token으로 **전면 전환**이 있었음.

### 3.3 Less → CSS-in-JS → CSS Variables 마이그레이션

```
v4 (Less)                    v5 (CSS-in-JS)              v5.7+ / v6 (CSS Variables)
@primary-color: #1890ff  →   token.colorPrimary      →   --ant-color-primary
@border-radius-base: 2px →   token.borderRadius      →   --ant-border-radius
@font-size-base: 14px    →   token.fontSize           →   --ant-font-size
Less 변수 컴파일 타임       런타임 JS 객체               런타임 CSS custom property
```

| 특성 | v4 Less | v5 CSS-in-JS | v5.7+/v6 CSS Vars |
|------|---------|-------------|-------------------|
| 테마 전환 | 재컴파일 필요 | 런타임 가능 | 런타임 가능 (더 빠름) |
| 다중 테마 | 불가 | 가능 | 가능 (key 분리) |
| 번들 영향 | CSS 추출 | JS 번들 포함 | CSS 변수로 분리 |
| SSR | 정적 | 하이드레이션 비용 | 개선됨 |
| 트리 셰이킹 | 불가 | 컴포넌트별 | 컴포넌트별 |

### 3.4 Theme Editor

**URL**: `ant.design/theme-editor`

Theme Editor는 브라우저에서 token을 시각적으로 편집하는 도구:

1. **Seed Token 편집**: colorPrimary, borderRadius, fontSize 등 조절
2. **실시간 프리뷰**: 모든 컴포넌트에 변경 사항 즉시 반영
3. **알고리즘 선택**: default / dark / compact 전환
4. **컴포넌트별 편집**: 특정 컴포넌트의 ComponentToken 개별 조절
5. **설정 내보내기**: `ConfigProvider theme` prop에 붙여넣을 수 있는 JSON/코드 생성

```tsx
// Theme Editor에서 내보낸 설정 예시
const themeConfig = {
  token: {
    colorPrimary: '#00b96b',
    borderRadius: 4,
  },
  components: {
    Button: {
      controlHeight: 40,
    },
  },
};
```

**한계**: Theme Editor는 코드 레벨 도구이며, Figma Variables와 연동되지 않는다.

### 3.5 DESIGN.md — AI 도구용 Token 문서화

**파일**: `github.com/ant-design/ant-design/blob/master/DESIGN.md`

Ant Design은 `DESIGN.md`를 통해 AI 코딩 도구(Cursor, Copilot 등)에 디자인 시스템을 전달:

**구조**:

1. **YAML front-matter** — 기계 판독 가능한 token 맵:
   ```yaml
   version: alpha
   colors:
     primary: '#1677FF'
     primary-hover: '#4096FF'
     primary-active: '#0958D9'
     success: '#52C41A'
     warning: '#FAAD14'
     error: '#FF4D4F'
   typography:
     base-size: 14px
     # ...
   ```

2. **참조 구문 `{colors.primary}`** — 컴포넌트 token이 seed를 참조:
   ```yaml
   components:
     button-primary:
       background: '{colors.primary}'
       text: '#FFFFFF'
     button-primary-hover:
       background: '{colors.primary-hover}'
   ```

3. **컴포넌트 상태 변형**: `button-primary`, `button-primary-hover`, `button-primary-active`를 별도 항목으로 문서화

4. **판단 근거 산문**: 왜 14px 기반인지, 왜 `rgba()` 텍스트인지, 3-layer surface 모델의 이유

5. **커스터마이즈 가드레일**: `ConfigProvider` seed/algorithm/`theme.components` 통해서만 테마 변경, 일회성 CSS 우회 금지

### 3.6 Figma Variables 미연결 — 공식 디자인 도구 스토리

Ant Design은 **Figma Variables API와 공식 연동하지 않는다**.

**현황**:
- 공식 Figma 라이브러리는 Ant Design 팀이 관리하지만, 코드 token과 자동 동기화되지 않음
- Figma의 색상/타이포그래피는 수동으로 코드 token과 일치시킴
- Token Studio (구 Figma Tokens) 같은 서드파티 플러그인 연동도 공식 지원 없음
- `@ant-design/colors` npm 패키지가 팔레트 생성의 single source of truth

**공식 스토리**:
- **디자인 → 코드**: Figma에서 디자인 → 개발자가 ConfigProvider token으로 수동 구현
- **코드 → 디자인**: Theme Editor에서 token 조절 → JSON 내보내기 → Figma에 수동 적용
- **DESIGN.md**: AI 도구가 코드에서 직접 디자인 의도를 읽을 수 있게 함 (Figma 우회)

**의의**: Ant Design은 "코드가 디자인의 원천"이라는 철학. Figma Variables 동기화 대신,
알고리즘 기반 파생으로 seed 몇 개만 관리하면 전체 시스템이 일관되게 유지되는 구조를 선택.

---

## 4. 요약 — Ant Design Token 시스템의 구조적 특징

### 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────┐
│                        ConfigProvider                           │
│  theme={{ token, algorithm, components, cssVar }}               │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  SeedToken (~48개)                                              │
│  colorPrimary, fontSize, borderRadius, sizeUnit, controlHeight  │
│  + 13 PresetColors                                              │
└─────────────────────┬───────────────────────────────────────────┘
                      │ algorithm (default / dark / compact)
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  MapToken (~180개)                                              │
│  genColorMapToken  → colorPrimaryBg/Hover/Active/...            │
│  genSizeMapToken   → sizeXXS~XXL                                │
│  genControlHeight  → controlHeightSM/XS/LG                      │
│  genFontMapToken   → fontSizeSM/LG/XL, Heading1~5              │
│  genCommonMapToken → motionDuration*, borderRadius*, lineWidth* │
│  @ant-design/colors → 13색 × 10단계 팔레트                       │
└─────────────────────┬───────────────────────────────────────────┘
                      │ alias derivation
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  AliasToken (~270개)                                            │
│  colorTextPlaceholder, controlItemBgActive, padding*, margin*   │
│  boxShadow*, screen*, linkDecoration, ...                       │
└─────────────────────┬───────────────────────────────────────────┘
                      │ prepareComponentToken + mergeToken
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  ComponentToken (컴포넌트별 ~20-50개)                             │
│  Button: fontWeight, defaultBg, primaryShadow, paddingInline... │
│  Input: activeBg, hoverBorderColor, activeShadow...             │
└─────────────────────┬───────────────────────────────────────────┘
                      │ genStyleHooks → CSS-in-JS
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│  CSS 출력                                                       │
│  CSS-in-JS: <style data-token-hash="xxx">                       │
│  CSS Vars:  --ant-color-primary: #1677ff;                       │
└─────────────────────────────────────────────────────────────────┘
```

### 핵심 설계 결정

| 결정 | 내용 | 영향 |
|------|------|------|
| **알고리즘 기반 파생** | Seed → Map을 함수로 파생 | seed 몇 개만 바꾸면 전체 테마 일관 변경 |
| **HSB 팔레트 자동 생성** | @ant-design/colors | 13색 × 10단계 = 130색 자동 생성 |
| **TypeScript = 스키마** | interface가 곧 token 스키마 | 컴파일 타임 검증, 자동완성 |
| **CSS-in-JS 런타임** | @ant-design/cssinjs | 동적 테마 전환, 다중 테마 공존 |
| **컴포넌트 격리** | ComponentToken per-component | 컴포넌트별 독립 커스터마이즈 |
| **알고리즘 합성** | `[dark, compact]` 배열 | 테마 조합 자유 |
| **DESIGN.md** | AI 도구용 기계 판독 문서 | Figma 없이 코드에서 디자인 의도 전달 |
| **Figma 미연동** | 코드 = single source of truth | 디자인-코드 동기화는 수동 |
