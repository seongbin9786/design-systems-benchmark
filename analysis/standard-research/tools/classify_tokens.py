#!/usr/bin/env python3
"""추출된 토큰 이름을 정규 어휘(canonical vocabulary)로 분류하고 시스템 간 교집합을 구한다.

입력: measured/tokens.json
출력: derived/vocabulary.json

분류 축 4개
  category — 값의 종류 (color / spacing / radius / typography / elevation / motion / ...)
  role     — 색이 칠해지는 자리 (surface / foreground / border / icon / overlay / shadow / link)
  intent   — 의미·강조도 (brand / neutral / status:critical / inverse / ...)
  state    — 상호작용 상태 (hover / active / focus / selected / disabled / visited)

판정 기준
  한 축의 값이 N개 시스템 중 몇 개에 등장하는지 센다.
  8/8  → 표준 (standard)      : 어느 시스템에도 빠지지 않음 → 신규 시스템의 필수 요소
  5~7  → 우세 (prevalent)     : 다수가 채택 → 도입 권장
  2~4  → 분기 (divergent)     : 갈림 → 선택 사항
  1    → 고유 (system-specific): 표준화 대상 아님
"""
import json
import re
from collections import defaultdict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402


# ── 축 1: category ──────────────────────────────────────────────────────────
# (canonical, [정규식 조각들]) — 순서가 우선순위. 먼저 맞는 것이 이긴다.
CATEGORY = [
    ("domain",     r"^(ai|chat)-|-aura|ai-gradient"),
    ("typography", r"^component-[a-z]{1,3}-(bold|medium|regular|italic)$|typescale|typography|font|text-style|heading|body|label|display|title|caption|line-height|letter-spacing|char-|cjk|text-(align|transform|decoration|overflow|wrap|indent)"),
    ("elevation",  r"elevation|shadow|box-shadow|depth|drop-shadow"),
    ("motion",     r"motion|duration|easing|curve|transition|animation|delay"),
    ("radius",     r"radius|corner|rounded|shape"),
    ("border",     r"border-width|stroke-width|border-\d|outline-width|thickness"),
    ("z-index",    r"z-index|zindex|layer-\d|stacking"),
    ("breakpoint", r"breakpoint|viewport|screen-"),
    ("opacity",    r"opacity|alpha"),
    ("icon-size",  r"icon-size|icon-\d|workflow-icon"),
    ("blur",       r"blur|backdrop"),
    ("spacing",    r"spacing|space|gap|padding|margin|inset|edge-to|to-text|to-visual|to-icon|to-field|to-component|to-alert|to-validation|to-disclosure|to-control|text-to-|visual-to-"),
    ("sizing",     r"size|height|width|min-|max-|density|track|thumb|scale"),
    ("color",      r"color|bg|background|fg|foreground|surface|border|text|icon|fill|stroke|overlay|scrim|link|divider|split|outline|primary|secondary|accent|brand|neutral|\bring\b|card|popover|input|muted|destructive|sidebar|palette|chart|aura|gradient|swatch|highlight|selection|scrollbar|transparent|compound"),
]

# Fluent 2 는 상태색을 status 가 아니라 *색조* 이름으로 부른다 (statusColorMapping.ts).
# 커버리지에서 누락되지 않도록 매핑하되, 이름 규약이 다르다는 사실은 별도로 기록한다.
HUE_STATUS = {
    "green": "status:success",
    "orange": "status:warning",
    "cranberry": "status:critical",
    "red": "status:critical",
}

# ── 축 2: role (색상 전용) ───────────────────────────────────────────────────
ROLE = [
    ("shadow",     r"shadow"),
    ("overlay",    r"overlay|scrim|backdrop"),
    ("focus-ring", r"focus-(indicator|ring)|ring"),
    ("link",       r"link"),
    ("icon",       r"\bicon\b|-icon|icon-"),
    # `\bline\b` 은 line-height 를 잡는다. Ant Design 의 line-width/line-type 만 인정.
    ("border",     r"border|stroke|outline|divider|split|line-(width|type|color)"),
    # `on-` 은 앞에 하이픈이나 문자열 시작이 와야 한다 (그냥 `on-` 은 motion-path 를 잡는다).
    ("foreground", r"foreground|\bfg\b|\btext\b|text-|(^|-)on-[a-z]|content-color|-content\b|label-color"),
    # `body` 는 타이포그래피 스케일(body01, body1)을 잡으므로 제외.
    ("surface",    r"background|\bbg\b|surface|\bfill\b|container|layer|canvas|elevated|paper"),
]

# ── 축 3: intent ────────────────────────────────────────────────────────────
INTENT = [
    ("status:critical", r"critical|negative|danger|error|destructive|invalid"),
    ("status:warning",  r"warning|caution|notice|alert"),
    ("status:success",  r"success|positive|valid|confirm"),
    ("status:info",     r"informative|\binfo\b|information"),
    ("brand",           r"brand|accent|primary|emphasis|\bkey\b"),
    ("secondary",       r"secondary|subdued|muted|subtle|weak|tertiary|placeholder|quiet"),
    ("inverse",         r"inverse|\bon-\b|invert|contrast-text|-inverted"),
    ("disabled",        r"disabled"),
    ("neutral",         r"neutral|default|\bgray\b|\bgrey\b|standard"),
]

# ── 축 4: state ─────────────────────────────────────────────────────────────
STATE = [
    ("hover",    r"hover"),
    # 경계 없이 `active` 를 쓰면 "interactive" 를 잡는다.
    ("active",   r"\bactive\b|pressed|\bdown\b"),
    ("focus",    r"focus"),
    ("selected", r"selected|checked|current"),
    ("disabled", r"disabled"),
    ("visited",  r"visited"),
    ("loading",  r"loading|pending|skeleton"),
    ("read-only", r"read-?only"),
]


def camel_to_kebab(s):
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", s)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "-", s)
    return s.lower()


def pick_example(entries, axis):
    """대표 예시 1개. 색상 축은 색상 토큰을 우선하고, 그중 가장 짧은 이름을 고른다."""
    pool = [n for n, is_color in entries if is_color] if axis in ("role", "intent", "state") else []
    if not pool:
        pool = [n for n, _ in entries]
    return sorted(pool, key=lambda n: (len(n), n))[0]


def match_axis(name, table):
    for canon, pat in table:
        if re.search(pat, name):
            return canon
    return None


def classify(raw):
    """role 은 category 와 독립으로 계산한다.

    (구버전은 category=='color' 일 때만 role 을 봤다. 그 결과 focus-ring 처럼
    category 가 먼저 가로채는 이름은 role 집계에서 통째로 빠졌다.)
    """
    name = camel_to_kebab(raw)
    cat = match_axis(name, CATEGORY)
    intent = match_axis(name, INTENT)
    hue_named = False
    if intent is None:
        for hue, st in HUE_STATUS.items():
            if re.search(rf"palette-{hue}\b|{hue}-", name):
                intent, hue_named = st, True
                break
    return {
        "category": cat,
        "role": match_axis(name, ROLE),
        "intent": intent,
        "state": match_axis(name, STATE) or "default",
        "_hue_named": hue_named,
    }


def main():
    tokens = paths.read_json("tokens")
    systems = list(tokens)
    n = len(systems)

    # axis -> value -> {system: [예시 토큰...]}
    seen = {a: defaultdict(lambda: defaultdict(list)) for a in ("category", "role", "intent", "state")}
    unclassified = defaultdict(list)
    hue_named = defaultdict(list)  # 색조 이름으로 상태를 표현하는 케이스

    for sys_name, info in tokens.items():
        for tname in info["names"]:
            c = classify(tname)
            if c.pop("_hue_named"):
                hue_named[sys_name].append(tname)
            if c["category"] is None:
                unclassified[sys_name].append(tname)
                continue
            is_color = c["category"] == "color"
            for axis, val in c.items():
                if val is None:
                    continue
                # role/intent/state 의 대표 예시는 색상 토큰에서 뽑아야 읽을 만하다.
                # (그렇지 않으면 role:border 예시로 line-height-100 같은 게 올라온다)
                seen[axis][val][sys_name].append((tname, is_color))

    def tier(k):
        if k == n:
            return "standard"
        if k >= max(5, n * 0.6):
            return "prevalent"
        if k >= 2:
            return "divergent"
        return "system-specific"

    result = {"systems": systems, "system_count": n, "axes": {}}
    for axis, vals in seen.items():
        rows = []
        for val, per_sys in vals.items():
            k = len(per_sys)
            rows.append({
                "value": val,
                "systems": sorted(per_sys),
                "coverage": k,
                "tier": tier(k),
                "missing": sorted(set(systems) - set(per_sys)),
                # 시스템별 대표 예시 1개 = 이름 대조표의 재료
                "examples": {s: pick_example(v, axis) for s, v in per_sys.items()},
                "counts": {s: len(v) for s, v in per_sys.items()},
            })
        rows.sort(key=lambda r: (-r["coverage"], r["value"]))
        result["axes"][axis] = rows

    # 시스템별 category 구성비 — 100% 누적 막대의 재료
    composition = {}
    for sysname in systems:
        counts = {}
        for row in result["axes"]["category"]:
            c = row["counts"].get(sysname)
            if c:
                counts[row["value"]] = c
        total = sum(counts.values())
        composition[sysname] = {
            "total": total,
            "counts": dict(sorted(counts.items(), key=lambda kv: -kv[1])),
            "pct": {k: round(v / total * 100, 1) for k, v in counts.items()} if total else {},
        }
    result["composition"] = composition
    # 전체 볼륨 상위 category (누적 막대의 고정 슬롯 순서)
    vol = {}
    for row in result["axes"]["category"]:
        vol[row["value"]] = sum(row["counts"].values())
    result["category_volume"] = dict(sorted(vol.items(), key=lambda kv: -kv[1]))

    result["unclassified"] = {s: {"count": len(v), "sample": sorted(v)[:15]} for s, v in unclassified.items()}
    result["hue_named_status"] = {s: {"count": len(v), "sample": sorted(v)[:8]} for s, v in hue_named.items()}
    out_path = paths.write_json("vocabulary", result)

    for axis in ("category", "role", "intent", "state"):
        print(f"\n=== {axis} ===")
        for r in result["axes"][axis]:
            print(f"  {r['coverage']}/{n} {r['tier']:16s} {r['value']:18s} 미보유: {', '.join(r['missing']) or '-'}")
    tot_unc = sum(v["count"] for v in result["unclassified"].values())
    tot = sum(t["count"] for t in tokens.values())
    print(f"\n미분류 {tot_unc}/{tot} ({tot_unc / tot * 100:.1f}%)")
    for s, v in result["unclassified"].items():
        if v["count"]:
            print(f"  {s}: {v['count']}  예: {', '.join(v['sample'][:5])}")
    print(f"\n-> {out_path}")


if __name__ == "__main__":
    main()
