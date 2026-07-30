#!/usr/bin/env python3
"""Mapping Fidelity Index (부분) 산출.

정의는 analysis/advancement-roadmap.md §2.1:
    MFI = 0.30×컴포넌트_매칭률 + 0.20×네이밍_정합성 + 0.20×Variant_정합성
        + 0.20×토큰_정합성 + 0.10×구조적_대응

이 스크립트가 계산하는 것 / 못 하는 것
  ✅ 컴포넌트_매칭률  — figma/raw/*-components-extracted.json ↔ sources/ 현재 코드 인벤토리
  ✅ 네이밍_정합성    — 전체 코드 컴포넌트의 최근접 Figma 이름 유사도 평균 (무조건부)
  ❌ Variant_정합성   — 코드 prop 축을 전 컴포넌트에서 자동 추출하지 못함 (Button 만 수동 실측)
  ❌ 토큰_정합성      — Figma Variables API 가 403 (figma/raw/*-variables.json). 로드맵 Phase 1 갭
  ❌ 구조적_대응      — auto-layout ↔ flex/grid 수동 평가

따라서 출력은 MFI 전체가 아니라 **가중치 0.50 구간만 재정규화한 부분 지수**다.
비교는 가능하지만 로드맵의 MFI 와 같은 값이 아니다. 이름을 MFI-partial 로 구분한다.
"""
import json
import re
from difflib import SequenceMatcher
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

FIGMA = paths.FIGMA_RAW

KITS = {  # 시스템 -> (figma 파일 접두사, 코드 인벤토리 키)
    "Carbon": "carbon",
    "Fluent 2": "fluent2",
    "Material Web": "material3",
    "Spectrum": "spectrum",
}

WEIGHTS = {"component_match": 0.30, "naming": 0.20}
UNMEASURED = {
    "variant": (0.20, "코드 prop 축 자동 추출 미구현 (Button 만 수동 실측 — button_api.json)"),
    "token": (0.20, "Figma Variables API 403 — figma/raw/*-variables.json 전부 error"),
    "structural": (0.10, "auto-layout ↔ flex/grid 수동 평가 필요"),
}

# Figma 컴포넌트명에 붙는 테마/플랫폼/상태 접미사 — 정규화 시 제거
NOISE = re.compile(
    r"\b(light|dark|darkest|wireframe|desktop|mobile|touch|express|"
    r"default|deprecated|legacy|do|dont|spec|slot|template|example)\b"
)


def norm(s):
    s = s.lower()
    s = re.sub(r"[_/|]", " ", s)
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", s)
    # Figma 는 " - Default" / " - Light" 처럼 *공백-하이픈-공백* 으로 수식어를 붙인다.
    # 임의 하이픈에서 자르면 코드 이름도 잘린다 (context-selector -> context 가 .Text 에 오매칭).
    s = s.split(" - ")[0]
    s = NOISE.sub(" ", s)
    # `Avatar/Avatar` 처럼 같은 단어가 반복되는 Figma 경로형 이름을 접는다
    words = []
    for w in re.split(r"[^a-z0-9]+", s):
        if w and w not in words:
            words.append(w)
    return "".join(words)


def sim(a, b):
    """정규화된 이름끼리의 문자열 유사도.

    ⚠️ 예전에는 "한쪽이 다른 쪽을 포함하면 0.85 이상" 이라는 보정을 넣었다.
    문자 단위 포함은 단어 경계를 무시하므로 무관한 쌍을 매칭했다 —
    `context-selector`↔`.Text` 0.89, `select`↔`Period Selector` 0.88,
    `icon`↔`Icon button`, `datepicker`↔`Picker` 가 전부 매칭으로 집계됐다.
    보정을 제거했다. 그 결과 `radio`↔`Radio buttons` 처럼 사람 눈에는 대응하는 쌍도
    놓치지만, MFI 는 "이름이 얼마나 맞는가" 지표이므로 과대평가보다 과소평가가 정직하다.
    """
    return SequenceMatcher(None, a, b).ratio()


def main():
    comps = paths.read_json("components")
    out = {"note": __doc__.strip().splitlines()[0], "weights_measured": WEIGHTS,
           "weights_unmeasured": {k: {"weight": w, "reason": r} for k, (w, r) in UNMEASURED.items()},
           "systems": {}}

    measured_weight = sum(WEIGHTS.values())

    for system, key in KITS.items():
        fp = FIGMA / f"{key}-components-extracted.json"
        if not fp.exists() or system not in comps["inventory"]:
            continue
        fd = json.loads(fp.read_text())

        # Figma 쪽: COMPONENT_SET 이름을 정규화해 고유 집합으로 축약
        figma_norm = {}
        for cs in fd["component_sets"]:
            n = norm(cs["name"])
            if len(n) < 2:
                continue
            figma_norm.setdefault(n, cs["name"])

        inv = comps["inventory"][system]
        code_names = sorted({r for names in inv["canonical"].values() for r in names} | set(inv["unmapped"]))

        matched, unmatched, sims, all_best = [], [], [], []
        for c in code_names:
            cn = norm(c)
            if not cn:
                continue
            best, score = None, 0.0
            for fn, orig in figma_norm.items():
                s = sim(cn, fn)
                if s > score:
                    best, score = (fn, orig), s
            all_best.append(score)
            if score >= 0.85:
                matched.append({"code": c, "figma": best[1], "similarity": round(score, 3)})
                sims.append(score)
            else:
                unmatched.append({"code": c, "closest": best[1] if best else None,
                                  "similarity": round(score, 3)})

        n_code = len([c for c in code_names if norm(c)])
        match_rate = len(matched) / n_code if n_code else 0.0
        # 매칭된 쌍만 평균하면 임계값 때문에 항상 ~99% 가 나온다(자기충족).
        # 전체 코드 컴포넌트의 최근접 유사도를 평균해 "이름이 얼마나 가까운가"를 본다.
        naming = sum(all_best) / len(all_best) if all_best else 0.0
        naming_matched_only = sum(sims) / len(sims) if sims else 0.0
        partial = (WEIGHTS["component_match"] * match_rate + WEIGHTS["naming"] * naming) / measured_weight

        out["systems"][system] = {
            "figma_component_sets": len(fd["component_sets"]),
            "figma_unique_after_norm": len(figma_norm),
            "code_components": n_code,
            "matched": len(matched),
            "component_match_rate": round(match_rate * 100, 1),
            "naming_similarity": round(naming * 100, 1),
            "naming_similarity_matched_only": round(naming_matched_only * 100, 1),
            "mfi_partial": round(partial * 100, 1),
            "matched_sample": matched[:12],
            "unmatched_sample": unmatched[:12],
        }

    out_path = paths.write_json("mfi", out)

    print("=== MFI-partial (측정 가중치 0.50 재정규화) ===")
    print(f"{'시스템':14s} {'Figma SET':>9s} {'정규화후':>7s} {'코드':>5s} {'매칭':>5s} {'매칭률':>7s} {'네이밍':>7s} {'MFI-p':>7s}")
    for s, d in out["systems"].items():
        print(f"{s:14s} {d['figma_component_sets']:9d} {d['figma_unique_after_norm']:7d} "
              f"{d['code_components']:5d} {d['matched']:5d} {d['component_match_rate']:6.1f}% "
              f"{d['naming_similarity']:6.1f}% {d['mfi_partial']:6.1f}")
    print("\n미측정 항목 (가중치 0.50):")
    for k, (w, r) in UNMEASURED.items():
        print(f"  {k:12s} {w:.2f}  {r}")
    print(f"\n-> {out_path}")


if __name__ == "__main__":
    main()
