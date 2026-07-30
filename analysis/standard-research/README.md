# 표준화 가능 요소 실측 — 파이프라인

8개 디자인 시스템 소스에서 직접 세어 "무엇이 표준화 가능한가"를 판정한다.
**리포트는 전부 생성물이다.** 직접 편집하면 다음 빌드에 날아간다.

## 실행

```bash
bash sources/clone.sh                          # 선행: 분석 대상 소스 얕은 클론 (385MB)
python3 analysis/standard-research/run.py      # 전체 파이프라인
python3 analysis/standard-research/run.py --reports   # 렌더링만
python3 analysis/standard-research/run.py --check     # 재현성 검사 (출력 == 커밋된 것)
```

`run.py` 가 의존 순서를 강제한다. 선행 산출물이 없으면 실행 전에 막는다 —
순서를 틀리게 돌려 낡은 중간 산출물로 리포트를 만드는 사고를 방지한다.

## 계층

입력이 어디서 왔는지, 무엇이 사람 손을 타는지가 디렉터리로 구분된다.

| 계층 | 무엇 | 사람이 편집? | 스크립트가 덮어씀? |
|---|---|---|---|
| `../../sources/` | 분석 대상 라이브러리 얕은 클론 | ✗ | ✗ (clone.sh 로 재현) |
| `../../figma/raw/` | Figma API 원본 JSON | ✗ | ✗ |
| **`curated/`** | 소스를 열어 확인한 수기 입력 | **○** | **✗ (거부됨)** |
| `measured/` | 1차 측정 — sources·figma 를 직접 읽은 것 | ✗ | ○ |
| `derived/` | 2차 파생 — measured 를 입력으로 계산 | ✗ | ○ |
| `reports/` | 최종 생성물 | ✗ | ○ |
| `tools/` | 측정·렌더 스크립트 | ○ | ✗ |

`tools/paths.py` 가 이 표의 단일 출처다. 도구는 경로 문자열을 직접 적지 않고
`paths.read_json("tokens")` 처럼 이름만 쓴다. 계층 판정·쓰기 권한·배너 삽입을 전부
`paths.py` 가 한다 — `curated/` 에 쓰려 하면 `PermissionError` 로 막힌다.

## 의존 그래프

```
sources/ ─┬─ extract_tokens.py     ─→ measured/tokens.json ─┬─ classify_tokens.py ─→ derived/vocabulary.json
          │                                                 └─ extract_naming.py  ─→ derived/naming.json
          ├─ extract_values.py     ─→ measured/values.json
          │      ↑ curated/button-geometry.json (수기 지오메트리)
          ├─ extract_components.py ─→ measured/components.json ── mfi.py ─→ derived/mfi.json
          │      ↑ figma/raw/*.json                                  ↑ figma/raw/*.json
          └─ measure_dependency.py ─→ measured/dependency.json

measured/ + derived/ + curated/ ─┬─ render_research.py  ─→ reports/…research.{md,html}
                                 ├─ render_visual.py    ─→ reports/…research-visual.html
                                 └─ render_specimens.py ─→ reports/…specimens.html
                                          ↑ tools/viz.py (공용 차트 프리미티브)
                                          ↑ tools/templates/*.tmpl.html
```

## 왜 수기 입력이 있는가

전부 자동 추출하고 싶지만 두 곳은 불가능하다. 자동인 척하지 않고 `curated/` 로 분리했다.

- **`curated/button-geometry.json`** — Button 의 높이·패딩·radius. mixin(Carbon SCSS) ·
  Tailwind 유틸리티(shadcn) · cva 를 거치므로 정적 추출로 값이 나오지 않는다.
  `null` 인 항목은 토큰에서 해석 가능한 것이라 스크립트가 채운다 (예: Ant Design 의
  높이는 seed 토큰 `controlHeight`).
- **`curated/button-api.json`** — Button 의 variant 축과 값 목록. 파일을 열어 확인했다.

두 파일 모두 `evidence` 에 근거 경로를 적는다. 소스를 갱신하면 그 경로를 다시 읽고
손으로 고쳐야 한다.

## 산문 수치도 데이터에서 만든다

리포트 본문의 "N개 시스템에서", "최대 N배" 같은 수치는 템플릿에 적지 않고 렌더러가
데이터에서 생성한다. 손으로 적었다가 계수 규칙을 손본 뒤 캡션이 차트와 어긋난 사례가
두 번 있었다 (`gap_txt`, `gran_txt`, `scale_ratio`, `exp1` 등이 그 결과).

렌더러의 `render()` 는 템플릿이 쓰지 않는 값이 남으면 경고하고, 값 없는 자리가 있으면
`KeyError` 로 실패한다.

## 한계

각 스크립트 docstring 에 그 스크립트의 한계를 적었다. 전역 한계는 두 가지다.

- **Figma Variables API 가 403** — `figma/raw/*-variables.json` 전부 error.
  MFI 의 토큰 정합성(가중치 0.20)은 계산할 수 없다.
- **집계 기준에 민감하다** — 토큰 의존율은 느슨/엄격 2기준을 병기한다.
  기준을 밝히지 않은 수치는 비교 불가라는 것이 이 레포의 교훈이고, 그것이 자기
  결론에도 적용된다 (`reports/…research.md` §6-1 참조).
