#!/usr/bin/env python3
"""확장판 리포트 — 기존 리포트의 모든 차트 + 아직 시각화하지 않았던 측정 6종.

입력: measured/ + derived/ + curated/ (계층 판정은 paths.py)
출력: reports/design-system-standard-research-visual.html

기본판(reports/design-system-standard-research.{md,html})은 그대로 둔다. 이 파일은 상위집합이다.

추가된 것
  9  네이밍 문법 — 토큰 이름 해부, 어순 진영, 상태 접미사 규약, 세그먼트 깊이
  10 Figma variant 폭발 — SET 당 조합 수, 분포, 최다 전개 컴포넌트
  11 분해 단위 — 원시 인벤토리 vs 정규 개념 (개념당 파일 수)
  12 컴포넌트별 의존율 히트맵 — 8 시스템 × 4 컴포넌트
  13 어휘 밀도 히트맵 — 존재 여부가 아니라 *토큰 몇 개를 썼는가*
  14 MFI 매칭 근거 — 실제 매칭·미매칭 쌍

색상 — dataviz 레퍼런스 팔레트를 이 문서 surface 로 재검증해 사용 (viz.py 주석 참조).
  sequential 히트맵은 문서화된 blue 램프 100→650 을 그대로 쓴다 (단일 hue, 단조 명도).
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402
from viz import (  # noqa: E402  — 프리미티브는 viz.py 가 단일 출처 (렌더러끼리 결합하지 않는다)
    AXIS_TITLE, CODE, COMP_LABEL, COMP_SLOTS, TIER_LABEL,
    dumbbell, e, hbars, legend, load, matrix, stacked, table_view,
)

OUT = "design-system-standard-research-visual.html"

ROLE_WORDS = {"surface", "background", "bg", "foreground", "fg", "text", "border", "stroke",
              "outline", "icon", "fill", "divider", "split", "container", "layer", "shadow"}
INTENT_WORDS = {"brand", "accent", "primary", "secondary", "tertiary", "critical", "negative",
                "danger", "error", "destructive", "warning", "caution", "success", "positive",
                "info", "informative", "neutral", "subtle", "muted", "subdued", "inverse"}
STATE_WORDS = {"hover", "active", "pressed", "down", "focus", "selected", "checked",
               "disabled", "visited", "loading"}

# 시스템별 대표 토큰 1개의 *원본 표기* — 세그먼트 분류는 위 단어집합으로 계산한다
ANATOMY = {
    "Spectrum":     ("--spectrum-", ["accent", "background", "color", "hover"]),
    "Material Web": ("--md-sys-",   ["color", "on", "primary", "container"]),
    "MUI":          ("theme.",      ["palette", "error", "dark"]),
    "Fluent 2":     ("--",          ["color", "neutral", "foreground", "2", "hover"]),
    # 진영 분류(역할→의미)와 일치하는 실제 토큰. `$button-danger-hover` 는 첫 세그먼트가
    # 역할이 아니라 컴포넌트명이어서 어순 예시로 오해를 준다.
    "Carbon":       ("$",           ["background", "inverse", "hover"]),
    "Polaris":      ("--p-",        ["color", "bg", "fill", "brand", "hover"]),
    "shadcn/ui":    ("--",          ["primary", "foreground"]),
    "Ant Design":   ("token.",      ["color", "error", "bg", "hover"]),
}


def seg_kind(w):
    if w in ROLE_WORDS:
        return "role"
    if w in INTENT_WORDS:
        return "intent"
    if w in STATE_WORDS:
        return "state"
    if w.isdigit():
        return "index"
    return "ns"


# ── 새 차트 프리미티브 ──────────────────────────────────────────────────────
def anatomy(rows):
    """토큰 이름 해부 — 세그먼트를 역할/의미/상태로 색칠해 어순을 눈에 보이게 한다."""
    out = []
    for system, prefix, parts in rows:
        chips = [f'<span class="ana pre">{e(prefix)}</span>']
        for w in parts:
            k = seg_kind(w)
            chips.append(f'<span class="ana k-{k}" data-tip="{e(w)} — {SEG_LABEL[k]}" tabindex="0">'
                         f'{e(w)}</span>')
        order = "".join(dict.fromkeys(
            {"role": "R", "intent": "I", "state": "S"}.get(seg_kind(w), "")
            for w in parts).keys()).replace("", "") or "—"
        out.append(f'<div class="ana-r"><span class="ana-l">{e(system)}</span>'
                   f'<span class="ana-t">{"".join(chips)}</span>'
                   f'<span class="ana-o">{e(order or "—")}</span></div>')
    return f'<div class="anas">{"".join(out)}</div>'


SEG_LABEL = {"role": "역할 — 색이 칠해지는 자리", "intent": "의미 — 무슨 뜻인가",
             "state": "상태 — 상호작용", "index": "단계 번호", "ns": "네임스페이스·분류"}

# sequential 히트맵 — 문서화된 blue 램프 (단일 hue, 단조 명도). 5단계 버킷.
HEAT_STEPS = 5


def heatmap(col_labels, rows, fmt="{:.0f}", unit="", buckets=None, tip_unit=""):
    """숫자 히트맵. rows = [(row_label, {col: value})]. 값 크기를 단일 hue 명도로 인코딩."""
    vals = [v for _, cells in rows for v in cells.values() if v is not None]
    lo, hi = (min(vals), max(vals)) if vals else (0, 1)
    edges = buckets or [lo + (hi - lo) * i / HEAT_STEPS for i in range(1, HEAT_STEPS + 1)]

    def step(v):
        for i, ed in enumerate(edges):
            if v <= ed:
                return i + 1
        return HEAT_STEPS

    head = "".join(f'<span class="hm-ch">{e(c)}</span>' for c in col_labels)
    body = []
    for label, cells in rows:
        cs = []
        for c in col_labels:
            v = cells.get(c)
            if v is None:
                cs.append('<span class="hm-c na" data-tip="측정 없음" tabindex="0">—</span>')
                continue
            cs.append(f'<span class="hm-c h{step(v)}" tabindex="0"'
                      f' data-tip="{e(label)} · {e(c)} — {fmt.format(v)}{e(tip_unit or unit)}">'
                      f'{fmt.format(v)}</span>')
        body.append(f'<div class="hm-r"><span class="hm-rl">{e(label)}</span>'
                    f'<span class="hm-cells">{"".join(cs)}</span></div>')
    scale = "".join(f'<i class="h{i + 1}"></i>' for i in range(HEAT_STEPS))
    return (f'<div class="hm"><div class="hm-head"><span></span>'
            f'<span class="hm-chs">{head}</span></div>{"".join(body)}'
            f'<div class="hm-key"><span>낮음</span>{scale}<span>높음</span></div></div>')


def paired(rows, l1, l2):
    """두 값 비교 막대 (원시 vs 정규). 같은 축, 같은 스케일 — 이중축은 쓰지 않는다."""
    mx = max((max(a, b) for _, a, b, _ in rows), default=1)
    out = []
    for label, a, b, note in rows:
        out.append(f"""<div class="pr">
<span class="pr-l">{e(label)}</span>
<span class="pr-t">
  <span class="pr-b b1" style="width:{a / mx * 100:.1f}%" tabindex="0"
        data-tip="{e(label)} · {e(l1)} {a}"><b>{a}</b></span>
  <span class="pr-b b2" style="width:{b / mx * 100:.1f}%" tabindex="0"
        data-tip="{e(label)} · {e(l2)} {b}"><b>{b}</b></span>
</span>
<span class="pr-v">{e(note)}</span></div>""")
    return f'<div class="prs">{"".join(out)}</div>'


def camps(groups):
    """진영 다이어그램 — 같은 개념을 반대 어순으로 쓰는 두 집단."""
    cards = []
    for title, sub, members, example in groups:
        chips = "".join(f'<span class="camp-m">{e(m)}</span>' for m in members)
        cards.append(f'<div class="camp"><h4>{e(title)}<small>{e(sub)}</small></h4>'
                     f'<code class="camp-ex">{e(example)}</code>'
                     f'<div class="camp-ms">{chips}</div></div>')
    return f'<div class="camps">{"".join(cards)}</div>'


def verify_anatomy(tokens):
    """해부 예시가 실제 추출된 토큰인지 확인 — 손으로 적은 예시는 소스가 바뀌면 조용히 거짓이 된다."""
    known = {n for d in tokens.values() for n in d["names"]}
    bad = []
    for system, (_, parts) in ANATOMY.items():
        joined = "-".join(parts)
        # 숫자 세그먼트는 표시용으로 분리했으므로(foreground·2) 붙인 형태도 후보로 본다
        alt = ""
        for w in parts:
            alt += w if (w.isdigit() and alt) else ("-" + w if alt else w)
        if joined not in known and alt not in known:
            bad.append((system, joined))
    for system, name in bad:
        print(f"경고: {system} 해부 예시 `{name}` 가 tokens.json 에 없다", file=sys.stderr)
    return not bad


def build():
    tokens = load("tokens")
    verify_anatomy(tokens)
    vocab = load("vocabulary")
    comps = load("components")
    mfi = load("mfi")
    dep = load("dependency")
    bapi = load("button-api")
    naming = load("naming")
    manifest = (paths.SOURCES / "MANIFEST.md").read_text().splitlines()
    systems = vocab["systems"]
    n = len(systems)

    # ── 기존 차트 (A~H) ────────────────────────────────────────────────
    tok_sorted = sorted(tokens.items(), key=lambda kv: -kv[1]["count"])
    chart_a = hbars([(s, d["count"], f'{s} — semantic 토큰 {d["count"]}개 · {d["layer"]}')
                     for s, d in tok_sorted], unit="개")
    slots = COMP_SLOTS + ["기타"]
    comp_rows = []
    for s, d in tok_sorted:
        pct = vocab["composition"][s]["pct"]
        seg = {k: pct.get(k, 0) for k in COMP_SLOTS}
        seg["기타"] = round(max(0.0, 100 - sum(seg.values())), 1)
        comp_rows.append((s, seg, f'{vocab["composition"][s]["total"]}개'))
    chart_b = legend(COMP_SLOTS, COMP_LABEL) + stacked(comp_rows, slots, COMP_LABEL, residual="기타")

    mx_rows = []
    for axis in ("category", "role", "intent", "state"):
        title, sub = AXIS_TITLE[axis]
        for r in vocab["axes"][axis]:
            if r["value"] == "default":
                continue
            mx_rows.append({**r, "_group": f"{title} — {sub}"})
    chart_c = matrix(mx_rows, systems, group_key=True)
    table_c = table_view(
        ["정규 어휘", "축", "보유", "판정", "미보유 시스템"],
        [[f'<code>{e(r["value"])}</code>', e(r["_group"].split(" — ")[0]),
          f'{r["coverage"]}/{n}', TIER_LABEL[r["tier"]], e(", ".join(r["missing"]) or "—")]
         for r in mx_rows], "토큰 어휘 커버리지")

    comp_sys = comps["systems"]
    n_cs = len(comp_sys)
    cmx = []
    for r in comps["coverage"]:
        if r["coverage"] < 3:
            continue
        tier = ("standard" if r["coverage"] == n_cs
                else "prevalent" if r["coverage"] >= 5 else "divergent")
        cmx.append({"value": r["component"], "systems": r["systems"], "coverage": r["coverage"],
                    "tier": tier, "missing": r["missing"],
                    "examples": {s: v[0] for s, v in r["aliases"].items()}})
    chart_d = matrix(cmx, comp_sys)
    table_d = table_view(
        ["정규 컴포넌트", "보유", "미보유", "시스템별 실제 이름"],
        [[f'<b>{e(r["value"])}</b>', f'{r["coverage"]}/{n_cs}',
          e(", ".join(r["missing"]) or "—"),
          " ".join(f'<code class="ex" title="{e(s)}">{e(v)}</code>' for s, v in r["examples"].items())]
         for r in cmx], "컴포넌트 커버리지")

    figs = []
    for s, d in comps["figma_variant_axes"].items():
        top = list(d["axes"].items())[:7]
        bars = hbars([(a, v["pct"], f'{s} · {a} — {v["used_in"]}/{d["component_sets"]} SET ({v["pct"]}%)')
                      for a, v in top], unit="%", maxv=100)
        figs.append(f'<figure class="facet"><figcaption>{e(s)}'
                    f'<small>{d["component_sets"]} COMPONENT_SET</small></figcaption>{bars}</figure>')

    b_rows = []
    for s, d in bapi["systems"].items():
        def cell(k):
            v = d.get(k)
            if not v:
                return '<td class="bx none"><span class="glyph">—</span></td>'
            prop = v.get("prop")
            vals = v.get("values") or []
            merged = ((d.get("emphasis") or {}).get("prop")
                      and (d.get("emphasis") or {}).get("prop") == (d.get("intent") or {}).get("prop"))
            cls = "merged" if merged and k in ("emphasis", "intent") else "on"
            pn = f'<code>{e(prop)}</code>' if prop else '<span class="glyph">prop 없음</span>'
            return (f'<td class="bx {cls}" data-tip="{e(s)} · {e(k)} — {e(prop or "prop 없음")}'
                    f'{(": " + e(", ".join(map(str, vals)))) if vals else ""}" tabindex="0">'
                    f'{pn}<b class="cnt">{len(vals)}</b></td>')
        itn = len((d.get("intent") or {}).get("values") or [])
        merged = ((d.get("emphasis") or {}).get("prop")
                  and (d.get("emphasis") or {}).get("prop") == (d.get("intent") or {}).get("prop"))
        shape = ("합침" if merged else "분리" if itn else "의미 축 없음")
        b_rows.append(f'<tr><th scope="row">{e(s)}</th>{cell("emphasis")}{cell("intent")}'
                      f'{cell("size")}{cell("shape")}'
                      f'<td class="bstruct s-{"m" if merged else "s" if itn else "n"}">{shape}</td>'
                      f'<td class="note">{e(d.get("note", ""))}</td></tr>')

    db_rows = []
    for s, d in dep["summary"].items():
        try:
            a = float(str(d.get("documented_avg")).replace("~", "").replace("%", "").replace("+", ""))
        except (TypeError, ValueError):
            continue
        b = d["avg_loose"]
        db_rows.append((s, a, b, b - a, abs(b - a) >= 20))
    db_rows.sort(key=lambda r: -abs(r[3]))
    flagged = [r[0] for r in db_rows if r[4]]
    gap_txt = (f'<b>{len(flagged)}개 시스템({", ".join(flagged)})에서 20pt 이상 벌어졌다.</b>'
               if flagged else '<b>20pt 이상 벌어진 시스템은 없다.</b>')
    chart_g = ('<div class="legend-row"><span class="lg"><i class="dot-a"></i>기존 문서값 (2026-07-26)</span>'
               '<span class="lg"><i class="dot-b"></i>재측정 (2026-07-30)</span></div>' + dumbbell(db_rows))

    W = mfi["weights_measured"]
    tot_w = sum(W.values())
    mfi_rows, mfi_tbl = [], []
    for s, d in sorted(mfi["systems"].items(), key=lambda kv: -kv[1]["mfi_partial"]):
        c1 = W["component_match"] * d["component_match_rate"] / tot_w
        c2 = W["naming"] * d["naming_similarity"] / tot_w
        mfi_rows.append((s, {"match": round(c1, 1), "naming": round(c2, 1),
                             "rest": round(max(0.0, 100 - c1 - c2), 1)}, f'{d["mfi_partial"]}'))
        mfi_tbl.append([e(s), d["figma_component_sets"], d["figma_unique_after_norm"],
                        d["code_components"], d["matched"], f'{d["component_match_rate"]}%',
                        f'{d["naming_similarity"]}%', f'<b>{d["mfi_partial"]}</b>'])
    mslots = ["match", "naming", "rest"]
    mlabel = {"match": "컴포넌트 매칭률 기여 (0.30)", "naming": "네이밍 근접도 기여 (0.20)", "rest": "미달"}
    chart_h = legend(mslots[:2], mlabel) + stacked(mfi_rows, mslots, mlabel, residual="rest")
    table_h = table_view(
        ["시스템", "Figma SET", "정규화 후", "코드", "매칭", "매칭률", "네이밍 근접도", "MFI-partial"],
        mfi_tbl, "MFI-partial")

    # ── 9. 네이밍 문법 (신규) ──────────────────────────────────────────
    chart_ana = anatomy([(s, ANATOMY[s][0], ANATOMY[s][1]) for s in systems if s in ANATOMY])
    nm = naming["systems"]
    ir_camp = [s for s in systems if nm[s]["order_top"] and nm[s]["order_top"][0]["pattern"].startswith("I")]
    ri_camp = [s for s in systems if nm[s]["order_top"] and nm[s]["order_top"][0]["pattern"].startswith("R")]
    chart_camps = camps([
        ("의미 → 역할", f"{len(ir_camp)}개 시스템", ir_camp, "error · background · hover"),
        ("역할 → 의미", f"{len(ri_camp)}개 시스템", ri_camp, "background · error · hover"),
    ])
    chart_suffix = hbars(
        [(s, nm[s]["state_suffix_pct"],
          f'{s} — 상태 토큰 {nm[s]["state_tokens"]}개 중 {nm[s]["state_suffix_pct"]}%가 상태 단어를 맨 끝에 둔다')
         for s in sorted(systems, key=lambda x: -(nm[x]["state_suffix_pct"] or -1))
         if nm[s]["state_suffix_pct"] is not None], unit="%", maxv=100)
    chart_depth = paired(
        [(s, nm[s]["depth_avg"], nm[s]["depth_max"], f'{nm[s]["total"]}개')
         for s in sorted(systems, key=lambda x: -nm[x]["depth_max"])],
        "평균 세그먼트", "최대 세그먼트")
    table_nm = table_view(
        ["시스템", "표기법", "접두사", "예시", "평균 깊이", "최대 깊이", "상태 토큰", "상태=접미사", "어순 1위"],
        [[e(s), e(nm[s]["native_case"]), f'<code>{e(nm[s]["native_prefix"])}</code>',
          f'<code>{e(nm[s]["native_sample"].strip("`"))}</code>',
          nm[s]["depth_avg"], nm[s]["depth_max"], nm[s]["state_tokens"],
          ("—" if nm[s]["state_suffix_pct"] is None else f'{nm[s]["state_suffix_pct"]}%'),
          (f'{nm[s]["order_top"][0]["pattern"]} {nm[s]["order_top"][0]["pct"]}%'
           if nm[s]["order_top"] else "—")] for s in systems],
        "네이밍 문법")

    # ── 10. Figma variant 폭발 (신규) ──────────────────────────────────
    fv = comps["figma_variant_axes"]
    bkeys = ["1-4", "5-12", "13-32", "33-96", "97+"]
    bk_rows = []
    for s, d in fv.items():
        tot = d["component_sets"]
        seg = {k: round(d["variant_buckets"][k] / tot * 100, 1) for k in bkeys}
        bk_rows.append((s, seg, f'{d["variants_total"]:,}개'))
    chart_buckets = (legend(bkeys, {k: f"{k} variant" for k in bkeys})
                     + stacked(bk_rows, bkeys, {k: f"{k} variant" for k in bkeys}))
    chart_perset = hbars([(s, d["variants_per_set"],
                           f'{s} — SET {d["component_sets"]}개가 variant {d["variants_total"]:,}개로 전개 '
                           f'(중앙값 {d["variants_median"]}, 최대 {d["variants_max"]})')
                          for s, d in sorted(fv.items(), key=lambda kv: -kv[1]["variants_per_set"])],
                         unit="개")
    exp_rows = []
    for s, d in fv.items():
        for t in d["top_exploded"][:3]:
            exp_rows.append(f'<tr><th scope="row">{e(s)}</th><td>{e(t["name"])}</td>'
                            f'<td class="num">{t["axes"]}</td>'
                            f'<td class="num strong">{t["variants"]}</td></tr>')

    # ── 11. 분해 단위 (신규) ───────────────────────────────────────────
    gran = []
    for s in comp_sys:
        i = comps["inventory"][s]
        raw, canon = i["raw_count"], len(i["canonical"])
        gran.append((s, raw, canon, f'개념당 {raw / max(1, canon):.1f}'))
    gran.sort(key=lambda r: -(r[1] / max(1, r[2])))
    chart_gran = ('<div class="legend-row"><span class="lg"><i class="b1"></i>원시 인벤토리 (디렉터리·파일)</span>'
                  '<span class="lg"><i class="b2"></i>정규 개념</span></div>'
                  + paired(gran, "원시 인벤토리", "정규 개념"))
    # 캡션 수치도 데이터에서 만든다 — 손으로 적으면 EXCLUDE 규칙을 손볼 때마다 어긋난다
    g_hi, g_lo = gran[0], gran[-1]
    gran_txt = (f'{g_hi[0]} 는 개념 하나를 평균 {g_hi[1] / g_hi[2]:.1f}개 파일로 쪼개고, '
                f'{g_lo[0]} 은 {g_lo[1] / g_lo[2]:.1f}개다. '
                f'"{g_hi[0]} 는 컴포넌트가 {g_hi[1]}개, {g_lo[0]} 은 {g_lo[1]}개"라는 문장은 '
                f'커버리지가 {g_hi[1] / g_lo[1]:.0f}배라는 뜻이 아니다 — <b>분해 단위가 다를 뿐이다.</b> '
                f'정규 개념으로 접으면 {g_hi[2]} 대 {g_lo[2]}이 된다.')
    gran_ratio = f'{(g_hi[1] / g_hi[2]) / (g_lo[1] / g_lo[2]):.0f}'

    # ── 12. 컴포넌트별 의존율 히트맵 (신규) ────────────────────────────
    dcomps = ["Button", "Checkbox", "Dialog", "TextInput"]
    hm_rows = []
    for s in [x[0] for x in sorted(dep["summary"].items(), key=lambda kv: -kv[1]["avg_loose"])]:
        cells = {}
        for r in dep["rows"]:
            if r.get("system") == s and r.get("dependency_pct") is not None:
                cells[r["component"]] = r["dependency_pct"]
        hm_rows.append((s, cells))
    chart_hm_dep = heatmap(dcomps, hm_rows, fmt="{:.0f}", unit="%",
                           buckets=[40, 60, 75, 90, 100], tip_unit="%")

    # ── 13. 어휘 밀도 히트맵 (신규) ────────────────────────────────────
    dense_axes = ["role", "intent", "state"]
    dn_rows = []
    for axis in dense_axes:
        for r in vocab["axes"][axis]:
            if r["value"] == "default" or r["coverage"] < 4:
                continue
            dn_rows.append((f'{axis[:1].upper()}·{r["value"]}',
                            {CODE[s]: r["counts"].get(s) for s in systems}))
    chart_hm_den = heatmap([CODE[s] for s in systems], dn_rows, fmt="{:.0f}", unit="개",
                           buckets=[2, 6, 15, 40, 10 ** 6], tip_unit="개")

    # ── 14. MFI 매칭 근거 (신규) ───────────────────────────────────────
    ev_rows = []
    for s, d in mfi["systems"].items():
        for m in d["matched_sample"][:4]:
            ev_rows.append(f'<tr class="ok"><th scope="row">{e(s)}</th>'
                           f'<td><code>{e(m["code"])}</code></td><td><code>{e(m["figma"])}</code></td>'
                           f'<td class="num">{m["similarity"]}</td><td class="tag t-ok">매칭</td></tr>')
        for u in d["unmatched_sample"][:3]:
            ev_rows.append(f'<tr class="no"><th scope="row">{e(s)}</th>'
                           f'<td><code>{e(u["code"])}</code></td>'
                           f'<td><code class="dim">{e(u["closest"] or "—")}</code></td>'
                           f'<td class="num">{u["similarity"]}</td><td class="tag t-no">미매칭</td></tr>')

    unmeasured = "".join(
        f'<li><code>{e(k)}</code> <span class="w">가중치 {v["weight"]:.2f}</span> — {e(v["reason"])}</li>'
        for k, v in mfi["weights_unmeasured"].items())
    man_html = "\n".join(
        "<tr>" + "".join(f'<td class="{"path" if i == 4 else ""}">{e(c.strip().strip("`"))}</td>'
                         for i, c in enumerate(l.strip("|").split("|")[:5])) + "</tr>"
        for l in manifest if l.startswith("| `"))
    tok_total = sum(d["count"] for d in tokens.values())
    unc_total = sum(v["count"] for v in vocab["unclassified"].values())
    hue_html = "".join(
        f'<li><b>{e(s)}</b> {v["count"]}개 — <code>{e(v["sample"][0])}</code> 같은 이름</li>'
        for s, v in vocab.get("hue_named_status", {}).items())
    std_count = sum(1 for a in vocab["axes"].values() for r in a
                    if r["tier"] == "standard" and r["value"] != "default")
    comp_std = [r["component"] for r in comps["coverage"] if r["coverage"] == n_cs]
    max_exp = max((t["variants"] for d in fv.values() for t in d["top_exploded"]), default=0)

    # 산문에 박히는 수치는 전부 데이터에서 만든다 — 손으로 적은 숫자는 소스가 바뀌면 조용히 거짓이 된다
    scale_ratio = f'{tok_sorted[0][1]["count"] / tok_sorted[-1][1]["count"]:.0f}'
    kebab = [s for s in systems if nm[s]["native_case"] == "kebab"]
    camel = [s for s in systems if nm[s]["native_case"] == "camel"]
    case_split = (f'kebab-case {len(kebab)}개({" · ".join(kebab)}) vs '
                  f'camelCase {len(camel)}개({" · ".join(camel)})')
    # 전개 규모 1·2위 (킷 전체에서)
    all_exp = sorted(((k, t) for k, d in fv.items() for t in d["top_exploded"]),
                     key=lambda kt: -kt[1]["variants"])
    e1, e2 = all_exp[0], all_exp[1] if len(all_exp) > 1 else all_exp[0]
    exp1 = (f'{e1[0]} 의 Figma <code>{e(e1[1]["name"])}</code> 은 '
            f'{e1[1]["axes"]}개 축에서 {e1[1]["variants"]}개 variant 로 전개된다')
    exp2 = (f'{e2[0]} 의 <code>{e(e2[1]["name"])}</code> 은 '
            f'{e2[1]["axes"]}축 {e2[1]["variants"]}개')
    # 표본이 없는 것과 규약이 흔들리는 것은 다르다 — 상태 토큰 10개 미만은 판정에서 제외한다
    MIN_STATE = 10
    sized = [s for s in systems if (nm[s]["state_tokens"] or 0) >= MIN_STATE
             and nm[s]["state_suffix_pct"] is not None]
    suffix_full = [s for s in sized if nm[s]["state_suffix_pct"] == 100]
    weak = min((s for s in sized if nm[s]["state_suffix_pct"] < 100),
               key=lambda x: nm[x]["state_suffix_pct"], default=None)
    suffix_txt = (f'상태 토큰이 {MIN_STATE}개 이상인 시스템만 보면, 규약이 100%인 쪽'
                  f'({" · ".join(suffix_full)})과 '
                  + (f'흔들리는 쪽({weak} {nm[weak]["state_suffix_pct"]}%)' if weak else "그 외")
                  + '의 차이가 검색·자동화 가능성을 가른다')

    return render(
        chart_a=chart_a, chart_b=chart_b, chart_c=chart_c, table_c=table_c,
        chart_d=chart_d, table_d=table_d, figs="\n".join(figs), b_rows="\n".join(b_rows),
        chart_g=chart_g, chart_h=chart_h, table_h=table_h, gap_txt=gap_txt,
        chart_ana=chart_ana, chart_camps=chart_camps, chart_suffix=chart_suffix,
        chart_depth=chart_depth, table_nm=table_nm,
        chart_buckets=chart_buckets, chart_perset=chart_perset,
        exp_rows="\n".join(exp_rows), chart_gran=chart_gran,
        gran_txt=gran_txt, gran_ratio=gran_ratio, chart_hm_dep=chart_hm_dep, chart_hm_den=chart_hm_den, ev_rows="\n".join(ev_rows),
        unmeasured=unmeasured, man_html=man_html,
        tok_total=tok_total, unc_total=unc_total,
        unc_pct=round(unc_total / tok_total * 100, 1),
        hue_html=hue_html, n_systems=n, systems_list=" · ".join(systems),
        std_count=std_count, comp_std_n=len(comp_std), comp_std=" · ".join(comp_std),
        code_key=" · ".join(f'<b>{e(c)}</b> {e(s)}' for s, c in CODE.items()),
        ir_n=len(ir_camp), ri_n=len(ri_camp), max_exp=max_exp,
        scale_ratio=scale_ratio, case_split=case_split,
        exp1=exp1, exp2=exp2, suffix_txt=suffix_txt,
        seg_key="".join(f'<span class="lg"><i class="k-{k}"></i>{e(v)}</span>'
                        for k, v in SEG_LABEL.items()),
    )


TMPL_NAME = "visual.tmpl.html"


def render(**kw):
    """`{{name}}` 치환. str.format 을 쓰면 템플릿의 CSS 중괄호를 전부 이중화해야 해서 위험하다."""
    import re as _re
    txt = paths.template(TMPL_NAME)
    missing = set()

    def sub(m):
        k = m.group(1)
        if k not in kw:
            missing.add(k)
            return m.group(0)
        return str(kw[k])

    out = _re.sub(r"\{\{([a-z0-9_]+)\}\}", sub, txt)
    if missing:
        raise KeyError(f"템플릿에 값 없는 자리: {sorted(missing)}")
    unused = sorted(set(kw) - set(_re.findall(r"\{\{([a-z0-9_]+)\}\}", txt)))
    if unused:
        print(f"경고: 템플릿이 쓰지 않는 값 {unused}", file=sys.stderr)
    return out


if __name__ == "__main__":
    p = paths.write_report(OUT, build())
    print(f"-> {p}  ({p.stat().st_size:,} bytes)")
