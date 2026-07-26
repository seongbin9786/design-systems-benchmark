# Figma API 분석 가이드

## 인증

```bash
# Figma Personal Access Token 설정
export FIGMA_TOKEN="your-token-here"
```

토큰 발급: Figma → Settings → Personal access tokens

## 주요 엔드포인트

### 1. 파일 구조 추출
```bash
# 전체 파일 노드 트리
curl -s -H "X-Figma-Token: $FIGMA_TOKEN" \
  "https://api.figma.com/v1/files/{file_key}" | jq '.document'

# 특정 깊이까지 (성능 최적화)
curl -s -H "X-Figma-Token: $FIGMA_TOKEN" \
  "https://api.figma.com/v1/files/{file_key}?depth=3"
```

### 2. 컴포넌트 목록
```bash
# 파일 내 모든 컴포넌트
curl -s -H "X-Figma-Token: $FIGMA_TOKEN" \
  "https://api.figma.com/v1/files/{file_key}/components" | jq '.meta.components'
```

### 3. 스타일 (레거시)
```bash
curl -s -H "X-Figma-Token: $FIGMA_TOKEN" \
  "https://api.figma.com/v1/files/{file_key}/styles" | jq '.meta.styles'
```

### 4. Variables (디자인 토큰)
```bash
# 로컬 변수 컬렉션 + 변수
curl -s -H "X-Figma-Token: $FIGMA_TOKEN" \
  "https://api.figma.com/v1/files/{file_key}/variables/local" | jq '.'
```

### 5. 컴포넌트 세트 (Variants)
```bash
# 특정 컴포넌트의 variant 세트
curl -s -H "X-Figma-Token: $FIGMA_TOKEN" \
  "https://api.figma.com/v1/files/{file_key}/component_sets"
```

## 공개 Figma 파일 키 (분석 대상)

| 시스템 | Figma 파일 | 비고 |
|--------|-----------|------|
| Spectrum | 커뮤니티/Adobe 공개 킷 확인 필요 | spectrum.adobe.com |
| Material Design | 공식 킷 공개 | m3.material.io |
| Fluent 2 | 공식 킷 공개 | fluent2.microsoft.design |
| Carbon | 공식 킷 공개 | carbondesignsystem.com |
| Polaris | 공식 킷 공개 | polaris.shopify.com |
| Ant Design | 공식 킷 공개 | ant.design/docs/spec/download |

> **Note:** 파일 키는 각 디자인 시스템 사이트의 Figma 다운로드 링크에서 추출.
> Figma URL: `figma.com/file/{file_key}/...` 또는 `figma.com/community/file/{file_key}/...`

## 분석 스크립트 (Node.js)

```javascript
// figma/analyze.mjs
// 사용: node figma/analyze.mjs <file_key>

const FIGMA_TOKEN = process.env.FIGMA_TOKEN;
const FILE_KEY = process.argv[2];

async function fetchJSON(url) {
  const res = await fetch(url, {
    headers: { 'X-Figma-Token': FIGMA_TOKEN },
  });
  if (!res.ok) throw new Error(`${res.status}: ${await res.text()}`);
  return res.json();
}

async function main() {
  // 1. 컴포넌트 목록
  const components = await fetchJSON(
    `https://api.figma.com/v1/files/${FILE_KEY}/components`
  );
  console.log(`컴포넌트 수: ${components.meta.components.length}`);
  
  // 2. Variables
  const variables = await fetchJSON(
    `https://api.figma.com/v1/files/${FILE_KEY}/variables/local`
  );
  const collections = Object.values(variables.meta.variableCollections);
  const vars = Object.values(variables.meta.variables);
  console.log(`Variable 컬렉션: ${collections.length}`);
  console.log(`Variables: ${vars.length}`);
  
  // 3. 스타일
  const styles = await fetchJSON(
    `https://api.figma.com/v1/files/${FILE_KEY}/styles`
  );
  console.log(`스타일 수: ${styles.meta.styles.length}`);
  
  // 결과 저장
  const fs = await import('fs');
  fs.writeFileSync(
    `figma/output-${FILE_KEY}.json`,
    JSON.stringify({ components: components.meta, variables: variables.meta, styles: styles.meta }, null, 2)
  );
}

main().catch(console.error);
```

## 추출 데이터 → 분석 매핑

| Figma 데이터 | 분석 차원 | 매핑 대상 (Code) |
|-------------|----------|-----------------|
| components | 컴포넌트 인벤토리, 1:1 대응률 | 코드 컴포넌트 export 목록 |
| component_sets (variants) | Variant 정합성 | 코드 props/variants |
| variables | 토큰 정합성 | CSS variables / theme tokens |
| styles | 토큰 정합성 (레거시) | CSS variables / theme tokens |
| node tree (auto-layout) | 구조적 대응 | flex/grid 레이아웃 |
