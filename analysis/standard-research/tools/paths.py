#!/usr/bin/env python3
"""경로와 입출력 계층의 단일 정의.

모든 도구가 이 모듈만 통해 파일을 읽고 쓴다. 경로 문자열을 스크립트마다 적으면
디렉터리를 옮길 때마다 조용히 깨지고, 어느 산출물이 어느 계층인지도 흐려진다.

계층
  sources/    분석 대상 라이브러리 얕은 클론 (커밋 안 함 — sources/clone.sh 로 재현)
  figma/raw/  Figma API 원본 JSON
  curated/    사람이 관리하는 입력. 소스를 열어 확인한 값 — 스크립트가 덮어쓰지 않는다
  measured/   1차 측정. sources·figma 를 직접 읽어 만든 것
  derived/    2차 파생. measured 를 입력으로 계산한 것
  reports/    최종 생성물. 사람이 편집하지 않는다 (다음 빌드에 덮어써진다)
"""
import json
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
RESEARCH = TOOLS.parent                      # analysis/standard-research
REPO = RESEARCH.parent.parent                # 저장소 루트

SOURCES = REPO / "sources"
FIGMA_RAW = REPO / "figma" / "raw"
CURATED = RESEARCH / "curated"
MEASURED = RESEARCH / "measured"
DERIVED = RESEARCH / "derived"
REPORTS = RESEARCH / "reports"
TEMPLATES = TOOLS / "templates"

# 어느 파일이 어느 계층인지 — 읽기/쓰기 헬퍼가 이 표를 따른다
LAYER = {
    "tokens": MEASURED, "values": MEASURED, "components": MEASURED, "dependency": MEASURED,
    "vocabulary": DERIVED, "naming": DERIVED, "mfi": DERIVED,
    "button-api": CURATED, "button-geometry": CURATED,
}

# 생성물 머리에 붙는 경고 — 사람이 직접 고치면 다음 빌드에 날아간다
BANNER_HTML = ("<!-- 생성물입니다. 직접 편집하지 마세요 — 다음 빌드에 덮어써집니다.\n"
               "     고치려면 analysis/standard-research/tools/ 의 스크립트나 템플릿을 고치고\n"
               "     `python3 analysis/standard-research/run.py` 를 다시 실행하세요. -->\n")
BANNER_MD = ("<!-- 생성물입니다. 직접 편집하지 마세요 — 다음 빌드에 덮어써집니다.\n"
             "     고치려면 analysis/standard-research/tools/ 의 스크립트를 고치고\n"
             "     `python3 analysis/standard-research/run.py` 를 다시 실행하세요. -->\n")


def read_json(name):
    """계층을 자동으로 찾아 JSON 을 읽는다."""
    base = LAYER.get(name)
    if base is None:
        raise KeyError(f"계층이 등록되지 않은 파일: {name} — paths.LAYER 에 추가하세요")
    p = base / f"{name}.json"
    if not p.exists():
        raise FileNotFoundError(f"{p} 가 없습니다. 선행 단계를 먼저 실행하세요 (run.py 참조)")
    return json.loads(p.read_text(encoding="utf-8"))


def write_json(name, data):
    base = LAYER.get(name)
    if base is None:
        raise KeyError(f"계층이 등록되지 않은 파일: {name} — paths.LAYER 에 추가하세요")
    if base is CURATED:
        raise PermissionError(f"{name} 은 curated(수기) 계층입니다 — 스크립트가 덮어쓸 수 없습니다")
    base.mkdir(parents=True, exist_ok=True)
    p = base / f"{name}.json"
    p.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return p


def write_report(filename, body):
    """생성물 저장 — 편집 금지 배너를 앞에 붙인다."""
    REPORTS.mkdir(parents=True, exist_ok=True)
    banner = BANNER_MD if filename.endswith(".md") else BANNER_HTML
    p = REPORTS / filename
    p.write_text(banner + body, encoding="utf-8")
    return p


def src(rel):
    """sources/ 아래 파일 내용. 없으면 빈 문자열."""
    p = SOURCES / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def template(name):
    return (TEMPLATES / name).read_text(encoding="utf-8")
