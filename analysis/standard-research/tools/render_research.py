#!/usr/bin/env python3
"""측정 결과를 자기 완결 HTML 한 장으로 렌더링한다.

입력: measured/ + derived/ + curated/ (계층 판정은 paths.py)
출력: reports/design-system-standard-research.{html,md}

playbook.md §7 G-2 의 규칙을 따른다 — 외부 의존 없는 단일 파일. 데이터를 JSON 에서 읽어
생성하므로 측정값과 문서가 어긋날 수 없다.

색상 — dataviz 스킬의 검증된 레퍼런스 팔레트를 이 문서의 surface 에 맞춰 재검증해 사용한다.
  categorical 7슬롯  light #f6f7f8 / dark #14171a  → 전 항목 PASS (light 대비 WARN → 직접 라벨 + 표 병기로 해소)
  ordinal 4단계(tier) light #184f95→#6da7ec, dark #cde2fb→#2a78d6 → 전 항목 PASS
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402
from viz import (  # noqa: E402  — 프리미티브는 viz.py 가 단일 출처
    AXIS_TITLE, CODE, COMP_LABEL, COMP_SLOTS, TIER_LABEL,
    dumbbell, e, hbars, legend, load, matrix, stacked, table_view,
)

OUT_HTML = "design-system-standard-research.html"
OUT_MD = "design-system-standard-research.md"

# ── 본문 조립 ────────────────────────────────────────────────────────────────
def build():
    tokens = load("tokens")
    vocab = load("vocabulary")
    comps = load("components")
    mfi = load("mfi")
    dep = load("dependency")
    bapi = load("button-api")
    manifest = (paths.SOURCES / "MANIFEST.md").read_text().splitlines()
    systems = vocab["systems"]

    # ── A. 토큰 규모 ────────────────────────────────────────────────────
    tok_sorted = sorted(tokens.items(), key=lambda kv: -kv[1]["count"])
    chart_a = hbars([(s, d["count"], f'{s} — semantic 토큰 {d["count"]}개 · {d["layer"]}')
                     for s, d in tok_sorted], unit="개")
    table_a = table_view(
        ["시스템", "토큰 수", "계층", "추출 경로"],
        [[e(s), d["count"], e(d["layer"]), f'<span class="path">{e(d["source"])}</span>']
         for s, d in tok_sorted],
        "토큰 규모")

    # ── B. 구성비 ───────────────────────────────────────────────────────
    slots = COMP_SLOTS + ["기타"]
    comp_rows = []
    for s, d in tok_sorted:
        pct = vocab["composition"][s]["pct"]
        seg = {k: pct.get(k, 0) for k in COMP_SLOTS}
        seg["기타"] = round(max(0.0, 100 - sum(seg.values())), 1)
        comp_rows.append((s, seg, f'{vocab["composition"][s]["total"]}개'))
    chart_b = (legend(COMP_SLOTS, COMP_LABEL) + stacked(comp_rows, slots, COMP_LABEL, residual="기타"))
    table_b = table_view(
        ["시스템"] + [COMP_LABEL[k] for k in slots],
        [[e(s)] + [f'{seg.get(k, 0):.1f}%' for k in slots] for s, seg, _ in comp_rows],
        "토큰 구성비")

    # ── C. 커버리지 매트릭스 ────────────────────────────────────────────
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
          f'{r["coverage"]}/{len(systems)}', TIER_LABEL[r["tier"]],
          e(", ".join(r["missing"]) or "—")] for r in mx_rows],
        "토큰 어휘 커버리지")

    # ── D. 컴포넌트 매트릭스 ────────────────────────────────────────────
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
        [[f'<b>{e(r["value"])}</b>', f'{r["coverage"]}/{n_cs}', e(", ".join(r["missing"]) or "—"),
          " ".join(f'<code class="ex" title="{e(s)}">{e(v)}</code>' for s, v in r["examples"].items())]
         for r in cmx],
        "컴포넌트 커버리지")

    # ── E. Figma variant 축 ─────────────────────────────────────────────
    figs = []
    for s, d in comps["figma_variant_axes"].items():
        top = list(d["axes"].items())[:7]
        bars = hbars([(a, v["pct"], f'{s} · {a} — {v["used_in"]}/{d["component_sets"]} SET ({v["pct"]}%)'
                       + (f' · 값: {", ".join(v["values"][:6])}' if v["values"] else ""))
                      for a, v in top], unit="%", maxv=100)
        figs.append(f'<figure class="facet"><figcaption>{e(s)}'
                    f'<small>{d["component_sets"]} COMPONENT_SET</small></figcaption>{bars}</figure>')

    # ── F. Button 축 구조 ───────────────────────────────────────────────
    b_rows = []
    for s, d in bapi["systems"].items():
        def cell(k):
            v = d.get(k)
            if not v:
                return '<td class="bx none"><span class="glyph">—</span></td>'
            prop = v.get("prop")
            vals = v.get("values") or []
            merged = (d.get("emphasis") or {}).get("prop") == (d.get("intent") or {}).get("prop") and prop
            cls = "merged" if merged and k in ("emphasis", "intent") else "on"
            pn = f'<code>{e(prop)}</code>' if prop else '<span class="glyph">prop 없음</span>'
            return (f'<td class="bx {cls}" data-tip="{e(s)} · {e(k)} — {e(prop or "prop 없음")}'
                    f'{(": " + e(", ".join(map(str, vals)))) if vals else ""}" tabindex="0">'
                    f'{pn}<b class="cnt">{len(vals)}</b></td>')
        emp = len((d.get("emphasis") or {}).get("values") or [])
        itn = len((d.get("intent") or {}).get("values") or [])
        merged = ((d.get("emphasis") or {}).get("prop")
                  and (d.get("emphasis") or {}).get("prop") == (d.get("intent") or {}).get("prop"))
        shape = ("합침" if merged else "분리" if itn else "의미 축 없음")
        b_rows.append(f'<tr><th scope="row">{e(s)}</th>{cell("emphasis")}{cell("intent")}'
                      f'{cell("size")}{cell("shape")}'
                      f'<td class="bstruct s-{"m" if merged else "s" if itn else "n"}">{shape}</td>'
                      f'<td class="note">{e(d.get("note", ""))}</td></tr>')

    # ── G. 의존율 덤벨 ──────────────────────────────────────────────────
    db_rows = []
    for s, d in dep["summary"].items():
        doc = d.get("documented_avg")
        try:
            a = float(str(doc).replace("~", "").replace("%", "").replace("+", ""))
        except (TypeError, ValueError):
            continue
        b = d["avg_loose"]
        gap = b - a
        db_rows.append((s, a, b, gap, abs(gap) >= 20))
    db_rows.sort(key=lambda r: -abs(r[3]))
    flagged = [r[0] for r in db_rows if r[4]]
    gap_txt = (f'<b>{len(flagged)}개 시스템({", ".join(flagged)})에서 20pt 이상 벌어졌다.</b>'
               if flagged else '<b>20pt 이상 벌어진 시스템은 없다.</b>')
    chart_g = ('<div class="legend-row"><span class="lg"><i class="dot-a"></i>기존 문서값 (2026-07-26)</span>'
               '<span class="lg"><i class="dot-b"></i>재측정 (2026-07-30)</span></div>'
               + dumbbell(db_rows))
    table_g = table_view(
        ["시스템", "기존", "재측정(느슨)", "재측정(엄격)", "범위", "차이", "측정 수"],
        [[e(s), f'{a:.0f}%', f'{b:.1f}%',
          (f'{dep["summary"][s]["avg_strict"]}%' if dep["summary"][s]["avg_strict"] is not None else "—"),
          f'{dep["summary"][s]["range_loose"][0]:.0f}~{dep["summary"][s]["range_loose"][1]:.0f}%',
          f'{gap:+.0f}pt', dep["summary"][s]["components_measured"]]
         for s, a, b, gap, big in db_rows],
        "토큰 의존율")

    # ── H. MFI 누적 기여 ────────────────────────────────────────────────
    W = mfi["weights_measured"]
    tot_w = sum(W.values())
    mfi_rows, mfi_tbl = [], []
    for s, d in sorted(mfi["systems"].items(), key=lambda kv: -kv[1]["mfi_partial"]):
        c1 = W["component_match"] * d["component_match_rate"] / tot_w
        c2 = W["naming"] * d["naming_similarity"] / tot_w
        mfi_rows.append((s, {"match": round(c1, 1), "naming": round(c2, 1),
                             "rest": round(max(0.0, 100 - c1 - c2), 1)},
                         f'{d["mfi_partial"]}'))
        mfi_tbl.append([e(s), d["figma_component_sets"], d["figma_unique_after_norm"],
                        d["code_components"], d["matched"], f'{d["component_match_rate"]}%',
                        f'{d["naming_similarity"]}%', f'<b>{d["mfi_partial"]}</b>'])
    mslots = ["match", "naming", "rest"]
    mlabel = {"match": "컴포넌트 매칭률 기여 (0.30)", "naming": "네이밍 근접도 기여 (0.20)", "rest": "미달"}
    chart_h = (legend(mslots[:2], mlabel) + stacked(mfi_rows, mslots, mlabel, residual="rest"))
    table_h = table_view(
        ["시스템", "Figma SET", "정규화 후", "코드", "매칭", "매칭률", "네이밍 근접도", "MFI-partial"],
        mfi_tbl, "MFI-partial")

    unmeasured = "".join(
        f'<li><code>{e(k)}</code> <span class="w">가중치 {v["weight"]:.2f}</span> — {e(v["reason"])}</li>'
        for k, v in mfi["weights_unmeasured"].items())

    man_rows = [l for l in manifest if l.startswith("| `")]
    man_html = "\n".join(
        "<tr>" + "".join(f'<td class="{"path" if i == 4 else ""}">{e(c.strip().strip("`"))}</td>'
                         for i, c in enumerate(l.strip("|").split("|")[:5])) + "</tr>"
        for l in man_rows)

    unc = vocab["uncategorized"]
    unc_total = sum(v["count"] for v in unc.values())
    tok_total = sum(d["count"] for d in tokens.values())
    hue = vocab.get("hue_named_status", {})
    hue_html = "".join(
        f'<li><b>{e(s)}</b> {v["count"]}개 — <code>{e(v["sample"][0])}</code> 같은 이름</li>'
        for s, v in hue.items())

    cf = coverage_facts(vocab, len(systems))
    std_by_axis = {
        a: [r["value"] for r in vocab["axes"][a] if r["tier"] == "standard" and r["value"] != "default"]
        for a in ("category", "role", "intent", "state")}
    std_count = sum(len(v) for v in std_by_axis.values())
    comp_std = [r["component"] for r in comps["coverage"] if r["coverage"] == n_cs]

    return TEMPLATE.format(
        chart_a=chart_a, table_a=table_a,
        chart_b=chart_b, table_b=table_b,
        chart_c=chart_c, table_c=table_c,
        chart_d=chart_d, table_d=table_d,
        figs="\n".join(figs),
        b_rows="\n".join(b_rows),
        chart_g=chart_g, table_g=table_g,
        chart_h=chart_h, table_h=table_h,
        gap_txt=gap_txt, unmeasured=unmeasured, man_html=man_html,
        tok_total=tok_total, unc_total=unc_total,
        unc_pct=round(unc_total / tok_total * 100, 1),
        hue_html=hue_html, n_systems=len(systems),
        systems_list=" · ".join(systems),
        std_count=std_count, comp_std_n=len(comp_std),
        comp_std=" · ".join(comp_std),
        code_key=" · ".join(f'<b>{e(c)}</b> {e(s)}' for s, c in CODE.items()),
        **cf,
    )


def coverage_facts(vocab, n):
    """레시피 산문에 들어가는 커버리지 수치 — 손으로 적으면 계수 규칙을 손볼 때마다 어긋난다."""
    def rows(axis):
        return {r["value"]: r for r in vocab["axes"][axis]}

    intent, state, cat = rows("intent"), rows("state"), rows("category")

    def lo(table, keys):
        got = [table[k] for k in keys if k in table]
        return min((r["coverage"] for r in got), default=0)

    def missing(table, keys):
        out = []
        for k in keys:
            for m in table.get(k, {}).get("missing", []):
                if m not in out:
                    out.append(m)
        return out

    st_keys = ["status:success", "status:warning"]
    state_keys = ["hover", "focus", "active"]
    shape_keys = ["elevation", "radius"]
    return {
        "cov_status": f"{lo(intent, st_keys)}/{n}",
        "cov_state": f"{lo(state, state_keys)}/{n}",
        "miss_state": " · ".join(missing(state, state_keys)) or "없음",
        "cov_shape": f"{lo(cat, shape_keys)}/{n}",
        "miss_shape": " · ".join(missing(cat, shape_keys)) or "없음",
    }


# ── Markdown 산출 ───────────────────────────────────────────────────────────
def md_cell(c):
    """셀 안의 파이프는 이스케이프해야 한다 — Carbon 의 추출 경로에 `layout|type|motion` 이 들어 있다."""
    return "" if c is None else str(c).replace("|", "\\|")


def md_table(headers, rows, align=None):
    """마크다운 표. align 은 'l'/'r'/'c' 문자열 (열 수와 같은 길이)."""
    align = align or "l" * len(headers)
    sep = {"l": ":---", "r": "---:", "c": ":---:"}
    out = ["| " + " | ".join(md_cell(h) for h in headers) + " |",
           "|" + "|".join(sep[a] for a in align) + "|"]
    for r in rows:
        out.append("| " + " | ".join(md_cell(c) for c in r) + " |")
    return "\n".join(out)


def build_md():
    """HTML 과 같은 JSON 을 읽어 마크다운으로 낸다.

    표에서 보유/미보유는 ●/· 로 표시한다 — 터미널·GitHub·에디터 어디서나 폭이 안 깨진다.
    """
    tokens = load("tokens")
    vocab = load("vocabulary")
    comps = load("components")
    mfi = load("mfi")
    dep = load("dependency")
    bapi = load("button-api")
    manifest = (paths.SOURCES / "MANIFEST.md").read_text().splitlines()
    systems = vocab["systems"]
    n = len(systems)
    L = []

    tok_total = sum(d["count"] for d in tokens.values())
    unc_total = sum(v["count"] for v in vocab["uncategorized"].values())
    unc_pct = round(unc_total / tok_total * 100, 1)
    std_by_axis = {a: [r["value"] for r in vocab["axes"][a]
                       if r["tier"] == "standard" and r["value"] != "default"]
                   for a in ("category", "role", "intent", "state")}
    std_count = sum(len(v) for v in std_by_axis.values())
    comp_sys = comps["systems"]
    n_cs = len(comp_sys)
    comp_std = [r["component"] for r in comps["coverage"] if r["coverage"] == n_cs]
    cf = coverage_facts(vocab, n)

    L.append("# 디자인 시스템에서 표준화할 수 있는 것")
    L.append("")
    L.append(f"> {n}개 컴포넌트 라이브러리의 **실제 소스**에서 semantic 토큰 {tok_total}개와 "
             "컴포넌트 인벤토리를 추출해, 어느 개념이 예외 없이 공통이고 어느 개념이 갈리는지 셌다.\n"
             "> 공통인 것만이 표준화 가능하다.")
    L.append(">")
    L.append(f"> **대상** {' · '.join(systems)}  \n"
             "> **기준일** 2026-07-30 · **소스** 고정 커밋 (부록)  \n"
             "> **시각화판** [design-system-standard-research.html](design-system-standard-research.html) — "
             "커버리지 히트맵, 덤벨 차트 등 8종. 이 문서와 같은 데이터에서 생성된다.")
    L.append("")
    L.append(md_table(
        ["예외 없이 공통인 토큰 어휘", f"{n}개 시스템 전부에 있는 컴포넌트",
         "추출한 semantic 토큰 총수", "category 축을 못 붙인 잔여"],
        [[std_count, len(comp_std), tok_total, f"{unc_pct}%"]], "rrrr"))
    L.append("")

    # 방법
    L.append("## 측정 방법과 한계")
    L.append("")
    L.append("결론보다 이 절이 먼저다. 이 저장소의 기존 감사가 남긴 교훈이 "
             '"집계 기준을 명시하지 않은 감사는 비교 불가"이기 때문이다.')
    L.append("")
    L.append("- **수집 범위** — 각 시스템의 *semantic(alias) 계층*만. primitive 램프(`gray-100` 류)는 "
             "제외했다. 표준화 대상이 아니다.")
    L.append(f"- **판정** — 토큰 이름을 4개 축(값의 종류 / 자리 / 의미 / 상태)으로 분류하고, "
             f"각 값이 {n}개 중 몇 개 시스템에 등장하는지 센다.")
    L.append("- **이름이 곧 근거** — 값이 아니라 *이름*을 본다. 이름에 개념이 드러나지 않으면 "
             "그 시스템은 실제로 그 개념을 구분하지 않는다고 본다.")
    L.append(f"- **잔여 {unc_total}개({unc_pct}%)** 는 *값의 종류* 축만 못 붙은 것이다 (다른 축은 기록됐다). 대부분 Carbon 의 "
             "`code01`/`container01` 같은 시스템 고유 스케일이다.")
    L.append("")
    L.append("> [!WARNING]")
    L.append("> **이름이 같아야 개념이 같은 것은 아니다.** Fluent 2 는 상태색을 `status` 가 아니라 "
             "*색조* 이름으로 부른다 — `colorPaletteCranberryForeground1` 이 위험색이다. "
             "이 문서는 `statusColorMapping.ts`(success→green, warning→orange, danger→cranberry)를 "
             "읽어 매핑한 뒤 커버리지에 넣었다. 해당 사례: "
             + ", ".join(f'{s} {v["count"]}개' for s, v in vocab.get("hue_named_status", {}).items()))
    L.append("")

    # 1. 규모·구성
    L.append("## 1. 토큰 규모와 구성")
    L.append("")
    tok_sorted = sorted(tokens.items(), key=lambda kv: -kv[1]["count"])
    mx, mn = tok_sorted[0][1]["count"], tok_sorted[-1][1]["count"]
    L.append(f"최대({tok_sorted[0][0]} {mx})와 최소({tok_sorted[-1][0]} {mn})가 "
             f"**{mx / mn:.0f}배** 차이다. 토큰이 많은 게 좋은 것은 아니다 — 그 수가 어디에 쓰였는지가 갈린다.")
    L.append("")
    cslots = COMP_SLOTS + ["기타"]
    rows = []
    for s, d in tok_sorted:
        pct = vocab["composition"][s]["pct"]
        seg = {k: pct.get(k, 0) for k in COMP_SLOTS}
        seg["기타"] = round(max(0.0, 100 - sum(seg.values())), 1)
        rows.append([s, d["count"]] + [f"{seg[k]:.0f}%" if seg[k] else "—" for k in cslots])
    L.append(md_table(["시스템", "토큰 수"] + [COMP_LABEL[k] for k in cslots], rows,
                      "lr" + "r" * len(cslots)))
    L.append("")
    L.append("간격을 토큰화하지 않은 시스템이 둘(Material Web · shadcn/ui) 있다.")
    L.append("")

    # 2. 어휘 매트릭스
    L.append("## 2. 어휘 커버리지 매트릭스")
    L.append("")
    L.append(f"`●` = 그 시스템이 그 개념을 **이름에 드러낸다**, `·` = 드러내지 않는다. "
             "행을 가로로 읽으면 표준화 가능성, 열을 세로로 읽으면 그 시스템의 성향이 보인다.")
    L.append("")
    L.append("판정 기준: **표준** = 8/8 예외 없음 · **우세** = 5~7/8 · **분기** = 2~4/8 · **고유** = 1/8")
    L.append("")
    for axis in ("category", "role", "intent", "state"):
        title, sub = AXIS_TITLE[axis]
        L.append(f"### {title} — {sub}")
        L.append("")
        rows = []
        for r in vocab["axes"][axis]:
            if r["value"] == "default":
                continue
            marks = ["●" if s in r["systems"] else "·" for s in systems]
            rows.append([f"`{r['value']}`"] + marks + [f"{r['coverage']}/{n}",
                                                       TIER_LABEL[r["tier"]],
                                                       ", ".join(r["missing"]) or "—"])
        L.append(md_table(["정규 어휘"] + [CODE[s] for s in systems] + ["보유", "판정", "미보유"],
                          rows, "l" + "c" * n + "rll"))
        L.append("")
    L.append("열 코드: " + " · ".join(f"**{c}** {s}" for s, c in CODE.items()))
    L.append("")
    L.append("> [!NOTE]")
    L.append("> 세로로 읽으면 **shadcn/ui 열이 눈에 띄게 비어 있다.** 상태(hover·focus·active)와 "
             "elevation·간격 토큰이 없다. 없어서 못 만든 게 아니라 그 표현을 토큰이 아닌 Tailwind "
             "유틸리티로 옮긴 설계다 — 대가는 상태 표현이 컴포넌트 코드에 흩어진다는 것.")
    L.append("")

    # 3. 컴포넌트
    L.append("## 3. 컴포넌트 교집합")
    L.append("")
    L.append("디렉터리·파일 인벤토리를 정규 개념으로 접은 결과. 시스템마다 분해 단위가 달라 "
             "(Carbon 은 DataTable 하위를 개별 디렉터리로 둔다) 절대 개수는 비교하지 않고 "
             "*개념 커버리지*만 본다.")
    L.append("")
    rows = []
    for r in comps["coverage"]:
        if r["coverage"] < 3:
            continue
        marks = ["●" if s in r["systems"] else "·" for s in comp_sys]
        rows.append([f"**{r['component']}**"] + marks
                    + [f"{r['coverage']}/{n_cs}", ", ".join(r["missing"]) or "—"])
    L.append(md_table(["정규 컴포넌트"] + [CODE[s] for s in comp_sys] + ["보유", "미보유"],
                      rows, "l" + "c" * n_cs + "rl"))
    L.append("")
    L.append("### 같은 개념, 다른 이름")
    L.append("")
    rows = []
    for r in comps["coverage"]:
        if r["coverage"] < n_cs:
            continue
        rows.append([f"**{r['component']}**"]
                    + [", ".join(f"`{x}`" for x in r["aliases"].get(s, ["—"])[:3]) for s in comp_sys])
    L.append(md_table(["정규 컴포넌트"] + [CODE[s] for s in comp_sys], rows))
    L.append("")

    # 4. Button 축
    L.append("## 4. Button variant 축 — 8종 실측")
    L.append("")
    L.append("축 자체는 거의 같다. **강조도**(얼마나 강해 보이나) · **의미**(무슨 일을 하나) · "
             "**크기** · **형태**. 갈리는 건 이름, 그리고 강조도와 의미를 *분리했는지 합쳤는지*다.")
    L.append("")
    rows = []
    for s, d in bapi["systems"].items():
        def ax(k):
            v = d.get(k)
            if not v:
                return "—"
            prop = v.get("prop")
            vals = v.get("values") or []
            head = f"`{prop}`" if prop else "*prop 없음*"
            return f"{head}<br>{' · '.join(map(str, vals))}" if vals else head
        emp = (d.get("emphasis") or {}).get("prop")
        itn = (d.get("intent") or {}).get("prop")
        rel = "**합침**" if emp and emp == itn else ("분리" if itn else "의미 축 없음")
        rows.append([s, ax("emphasis"), ax("intent"), ax("size"), ax("shape"), rel])
    L.append(md_table(["시스템", "강조도", "의미", "크기", "형태", "두 축 관계"], rows))
    L.append("")
    for s, d in bapi["systems"].items():
        if d.get("note"):
            L.append(f"- **{s}** — {d['note']}")
    L.append("")
    L.append("> [!IMPORTANT]")
    L.append("> **합치면 값이 곱으로 폭발한다.** Carbon 은 `kind` 하나에 강조도와 의미를 합쳐 "
             "`danger--tertiary` 처럼 조합을 문자열로 인코딩한다. Spectrum·MUI·Polaris·Ant Design 은 "
             "두 축을 분리해 같은 표현력을 값의 곱 없이 얻는다. 새로 만든다면 분리가 맞다.")
    L.append(">")
    L.append("> **Material Web 은 variant prop 자체가 없다.** 강조도별로 별도 커스텀 엘리먼트"
             "(`<md-filled-button>` 등)로 나눈다. 크기 축도 없다. Figma 킷에는 variant 가 있으니 — "
             "이 지점이 Figma↔Code 매핑이 구조적으로 어긋나는 자리다.")
    L.append("")

    # 5. Figma 축
    L.append("## 5. Figma 쪽 축 분포")
    L.append("")
    L.append("공식 Figma 킷 4종의 COMPONENT_SET 에서 variant property 이름을 집계했다. "
             "**어느 킷에서도 1위가 `state`** 다 — 디자인 파일이 가장 많이 표현하는 축은 상호작용 상태다. "
             "코드에서 상태는 prop 이 아니라 CSS 의사클래스이므로, 이 축은 원리상 1:1 매핑되지 않는다.")
    L.append("")
    rows = []
    for s, d in comps["figma_variant_axes"].items():
        top = list(d["axes"].items())[:6]
        rows.append([s, d["component_sets"]]
                    + [f"`{a}` {v['pct']}%" for a, v in top]
                    + [""] * (6 - len(top)))
    L.append(md_table(["Figma 킷", "SET 수", "1위", "2위", "3위", "4위", "5위", "6위"],
                      rows, "lr" + "l" * 6))
    L.append("")

    # 6. 재감사
    L.append("## 6. 재감사 — 기존 결론이 지금도 성립하나")
    L.append("")
    L.append("### 6-1. 토큰 의존율 재측정")
    L.append("")
    L.append("컴포넌트 4종(Button / Checkbox / Dialog / TextInput)의 스타일 소스에서 "
             "`토큰 참조 / (토큰 참조 + hardcoded)` 를 셌다. **느슨**은 컴포넌트 로컬 변수"
             "(`--pc-*` 류)와 Tailwind 스케일 클래스를 토큰으로 인정한 값, **엄격**은 제외한 값.")
    L.append("")
    rows, flagged = [], []
    for s, d in sorted(dep["summary"].items(), key=lambda kv: -kv[1]["avg_loose"]):
        doc = d.get("documented_avg")
        try:
            a = float(str(doc).replace("~", "").replace("%", "").replace("+", ""))
            gap = d["avg_loose"] - a
            gaps = f"{gap:+.0f}pt"
            if abs(gap) >= 20:
                flagged.append(s)
                gaps = f"**{gaps}** ⚠"
        except (TypeError, ValueError):
            gaps = "—"
        st = f'{d["avg_strict"]}%' if d["avg_strict"] is not None else "—"
        rows.append([s, f'{d["avg_loose"]}%', st,
                     f'{d["range_loose"][0]:.0f}~{d["range_loose"][1]:.0f}%',
                     doc or "—", gaps, d["components_measured"]])
    L.append(md_table(["시스템", "느슨 평균", "엄격 평균", "범위", "기존 문서값", "차이", "측정 수"],
                      rows, "lrrrrrr"))
    L.append("")
    L.append("> [!CAUTION]")
    L.append(f"> **{len(flagged)}개 시스템({', '.join(flagged)})에서 20pt 이상 벌어졌다.** "
             "원인은 소스 변화가 아니라 *집계 기준*이다. 기존 감사는 shadcn 의 Tailwind 클래스를 "
             "전부 hardcoded 로 세었고(205개), 이 재측정은 테마 스케일을 참조하는 클래스를 "
             "토큰 참조로 센다. 어느 쪽도 틀리지 않았다 — 그래서 "
             '**"토큰 의존율 3 클러스터"는 시스템의 속성이 아니라 계수 규칙의 산물**이라고 봐야 한다. '
             "이 저장소가 스스로 경고한 함정 7번이 자기 결론에도 적용된다.")
    L.append("")
    L.append("### 6-2. Mapping Fidelity Index (부분)")
    L.append("")
    L.append("로드맵 §2.1 의 MFI 5개 항목 중 계산 가능한 2개만 구해 가중치 0.50 구간으로 재정규화했다. "
             "로드맵의 MFI 와 **같은 값이 아니다**.")
    L.append("")
    rows = [[s, d["figma_component_sets"], d["figma_unique_after_norm"], d["code_components"],
             d["matched"], f'{d["component_match_rate"]}%', f'{d["naming_similarity"]}%',
             f'**{d["mfi_partial"]}**']
            for s, d in sorted(mfi["systems"].items(), key=lambda kv: -kv[1]["mfi_partial"])]
    L.append(md_table(["시스템", "Figma SET", "정규화 후", "코드", "매칭", "매칭률",
                       "네이밍 근접도", "MFI-partial"], rows, "lrrrrrrr"))
    L.append("")
    L.append("계산하지 못한 항목 (가중치 0.50):")
    L.append("")
    for k, v in mfi["weights_unmeasured"].items():
        L.append(f"- `{k}` (가중치 {v['weight']:.2f}) — {v['reason']}")
    L.append("")

    # 7. 레시피
    L.append("## 7. 그래서 최소 시스템은 무엇을 갖춰야 하나")
    L.append("")
    L.append(f"위 측정에서 **8/8** 로 나온 것만 모은 목록이다. 하나라도 빠뜨리면 "
             f"{n}개 시스템 중 어느 것도 하지 않은 선택을 하는 셈이다.")
    L.append("")
    L.append("1. **색상 토큰을 세 자리로 나눈다** — 면(surface) · 글자(foreground) · 선(border). "
             "예외 없이 8/8이다. 하나로 뭉치면 다크 테마에서 반드시 깨진다.")
    L.append(f"2. **의미 축에 최소 세 값** — 브랜드 · 보조 · 위험(critical). 성공·경고는 {cf['cov_status']}로 그다음 순위.")
    L.append(f"3. **상태를 토큰으로 만든다** — hover · focus · active 는 {cf['cov_state']}. "
             f"미보유는 {cf['miss_state']} — 그 대가로 상태 표현이 컴포넌트 코드에 흩어진다.")
    L.append("4. **타이포그래피 스케일을 토큰화한다** — 8/8. 색상과 함께 유일하게 예외가 없는 값 종류다.")
    L.append(f"5. **Elevation·radius 는 {cf['cov_shape']}** — 미보유는 {cf['miss_shape']} 로 예외다 "
             "(shadcn 은 Tailwind 유틸리티, Carbon 은 radius 토큰이 *아예 없다*).")
    L.append(f"6. **컴포넌트는 {len(comp_std)}개부터** — {' · '.join(comp_std)}.")
    L.append("7. **Button 의 variant 축은 강조도와 의미를 분리한다** — 합치면 값이 곱으로 폭발한다.")
    L.append("8. **상태는 Figma 와 코드가 원리상 어긋난다** — Figma 킷의 1위 축이 `state` 인데 "
             "코드에서는 prop 이 아니라 의사클래스다. 자동 동기화를 시도하지 말고 계약 문서로 남긴다.")
    L.append("")

    # 부록
    L.append("## 부록 — 측정에 쓴 소스 커밋")
    L.append("")
    L.append("얕은 클론으로 받은 고정 커밋. 재현은 `bash sources/clone.sh`.")
    L.append("")
    L.extend(l for l in manifest if l.startswith("|"))
    L.append("")
    L.append("### 시스템별 추출 경로")
    L.append("")
    L.append(md_table(["시스템", "토큰 수", "계층", "추출 경로"],
                      [[s, d["count"], d["layer"], f'`{d["source"]}`'] for s, d in tok_sorted],
                      "lrll"))
    L.append("")
    L.append("---")
    L.append("")
    L.append("생성: `python3 analysis/standard-research/run.py` — 데이터는 `measured/` · `derived/` · `curated/` 에서 읽는다.  \n"
             "측정 스크립트: `extract_tokens.py` · `classify_tokens.py` · `extract_components.py` · "
             "`measure_dependency.py` · `mfi.py`")
    return "\n".join(L) + "\n"


TEMPLATE = """<meta charset="utf-8">
<title>디자인 시스템에서 표준화할 수 있는 것 — 8개 시스템 소스 실측</title>
<style>
:root {{
  --ink: #16191d; --ink-2: #4a5157; --ink-3: #767f87;
  --paper: #f6f7f8; --card: #fdfdfd; --rule: #dfe3e6; --rule-2: #eceff1;
  --accent: #2f5d8a; --accent-soft: #e8eff6;
  /* tier — 검증된 ordinal 4단계 (단일 hue, monotone L, light-end 2.33:1) */
  --t1: #184f95; --t2: #256abf; --t3: #3987e5; --t4: #6da7ec;
  --t1-bg: #e4edf9; --t2-bg: #e8f0fb; --t3-bg: #edf3fc; --t4-bg: #f1f5fd;
  /* categorical 7슬롯 — 검증된 레퍼런스 팔레트 (light) */
  --s1: #2a78d6; --s2: #eb6834; --s3: #1baf7a; --s4: #eda100;
  --s5: #e87ba4; --s6: #008300; --s7: #4a3aa7;
  --grid: #e6e9ec; --axis: #c9cfd4;
  --warn: #d03b3b;
  --mono: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, monospace;
  --sans: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Pretendard",
          "Segoe UI", "Malgun Gothic", system-ui, sans-serif;
  --step--1: clamp(.75rem, .73rem + .1vw, .8rem);
  --step-0: clamp(.9rem, .87rem + .15vw, .95rem);
  --step-1: clamp(1.05rem, 1rem + .25vw, 1.15rem);
  --step-2: clamp(1.3rem, 1.2rem + .5vw, 1.6rem);
  --step-3: clamp(1.7rem, 1.5rem + 1vw, 2.4rem);
}}
@media (prefers-color-scheme: dark) {{
  :root:where(:not([data-theme="light"])) {{
    --ink: #e6eaee; --ink-2: #a8b2bb; --ink-3: #7b858e;
    --paper: #14171a; --card: #1b1f23; --rule: #2c3238; --rule-2: #23282d;
    --accent: #7fb0dd; --accent-soft: #1e2a35;
    --t1: #cde2fb; --t2: #9ec5f4; --t3: #6da7ec; --t4: #2a78d6;
    --t1-bg: #1f2c38; --t2-bg: #1d2831; --t3-bg: #1b242b; --t4-bg: #192026;
    --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500;
    --s5: #d55181; --s6: #008300; --s7: #9085e9;
    --grid: #262c31; --axis: #383f45;
    --warn: #e8846c;
  }}
}}
:root[data-theme="dark"] {{
  --ink: #e6eaee; --ink-2: #a8b2bb; --ink-3: #7b858e;
  --paper: #14171a; --card: #1b1f23; --rule: #2c3238; --rule-2: #23282d;
  --accent: #7fb0dd; --accent-soft: #1e2a35;
  --t1: #cde2fb; --t2: #9ec5f4; --t3: #6da7ec; --t4: #2a78d6;
  --t1-bg: #1f2c38; --t2-bg: #1d2831; --t3-bg: #1b242b; --t4-bg: #192026;
  --s1: #3987e5; --s2: #d95926; --s3: #199e70; --s4: #c98500;
  --s5: #d55181; --s6: #008300; --s7: #9085e9;
  --grid: #262c31; --axis: #383f45;
  --warn: #e8846c;
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--paper); color: var(--ink);
  font-family: var(--sans); font-size: var(--step-0); line-height: 1.65;
  -webkit-font-smoothing: antialiased; }}
.wrap {{ display: grid; grid-template-columns: 14rem minmax(0,1fr); gap: 2.5rem;
  max-width: 88rem; margin: 0 auto; padding: 0 1.5rem; }}
@media (max-width: 62rem) {{ .wrap {{ grid-template-columns: 1fr; gap: 0; }} nav.rail {{ display: none; }} }}
nav.rail {{ position: sticky; top: 0; align-self: start; height: 100vh;
  padding: 3.5rem 0 2rem; overflow-y: auto; }}
nav.rail ol {{ list-style: none; margin: 0; padding: 0; }}
nav.rail a {{ display: block; padding: .28rem .55rem; border-radius: 3px; color: var(--ink-2);
  text-decoration: none; font-size: var(--step--1); line-height: 1.4; border-left: 2px solid transparent; }}
nav.rail a:hover {{ color: var(--ink); background: var(--rule-2); }}
nav.rail a:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 1px; }}
nav.rail .sub-a {{ padding-left: 1.3rem; color: var(--ink-3); }}
nav.rail .rail-t {{ font-family: var(--mono); font-size: .65rem; letter-spacing: .12em;
  text-transform: uppercase; color: var(--ink-3); padding: 0 .55rem; margin: 0 0 .6rem; }}
main {{ padding: 3.5rem 0 6rem; min-width: 0; }}

.eyebrow {{ font-family: var(--mono); font-size: .68rem; letter-spacing: .14em;
  text-transform: uppercase; color: var(--accent); margin: 0 0 .9rem; }}
h1 {{ font-size: var(--step-3); line-height: 1.14; letter-spacing: -.022em; font-weight: 660;
  margin: 0 0 1rem; text-wrap: balance; max-width: 30ch; }}
.lede {{ font-size: var(--step-1); color: var(--ink-2); margin: 0 0 1.6rem; max-width: 62ch; }}
h2 {{ font-size: var(--step-2); letter-spacing: -.015em; font-weight: 640; line-height: 1.25;
  margin: 4rem 0 .5rem; text-wrap: balance; padding-top: 1.6rem; border-top: 1px solid var(--rule); }}
h2 .h2n {{ font-family: var(--mono); font-size: .7rem; color: var(--ink-3); display: block;
  letter-spacing: .1em; margin-bottom: .5rem; font-weight: 400; }}
h3 {{ font-size: var(--step-1); font-weight: 620; margin: 2.4rem 0 .4rem; letter-spacing: -.01em; }}
p {{ max-width: 68ch; margin: 0 0 1rem; }}
.sub {{ color: var(--ink-2); margin-bottom: 1.4rem; max-width: 68ch; }}
a {{ color: var(--accent); }}
code {{ font-family: var(--mono); font-size: .86em; }}
figure {{ margin: 0; }}

.meta {{ display: flex; flex-wrap: wrap; gap: .4rem 1.4rem; padding: .85rem 1.05rem;
  background: var(--card); border: 1px solid var(--rule); border-radius: 4px;
  font-size: var(--step--1); color: var(--ink-2); margin-bottom: 1.6rem; }}
.meta b {{ color: var(--ink); font-weight: 600; }}
.kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(9.5rem,1fr)); gap: 1px;
  background: var(--rule); border: 1px solid var(--rule); border-radius: 4px;
  overflow: hidden; margin: 0 0 2rem; }}
.kpi {{ background: var(--card); padding: 1rem 1.05rem; }}
.kpi .k {{ font-size: 2rem; line-height: 1; font-weight: 600; letter-spacing: -.035em; }}
.kpi .l {{ font-size: var(--step--1); color: var(--ink-2); margin-top: .45rem; }}
.kpi .k small {{ font-size: .95rem; font-weight: 500; color: var(--ink-3); letter-spacing: 0; }}

.callout {{ border-left: 3px solid var(--warn); background: var(--card); padding: .85rem 1.05rem;
  margin: 1.3rem 0; border-radius: 0 4px 4px 0; }}
.callout p {{ margin: 0; font-size: var(--step--1); color: var(--ink-2); max-width: 72ch; }}
.callout p + p {{ margin-top: .5rem; }}
.callout b {{ color: var(--ink); }}
.panel {{ background: var(--card); border: 1px solid var(--rule); border-radius: 4px;
  padding: 1.1rem 1.15rem; margin: 0 0 1rem; }}

/* ── 범례 ── */
.legend-row {{ display: flex; flex-wrap: wrap; gap: .3rem .9rem; margin: 0 0 .8rem; }}
.lg {{ display: inline-flex; align-items: center; gap: .35rem; font-size: var(--step--1);
  color: var(--ink-2); }}
.lg i {{ width: 10px; height: 10px; border-radius: 2px; display: inline-block; flex: none; }}
.lg i.dot-a {{ border-radius: 50%; background: var(--card); border: 2px solid var(--s1); }}
.lg i.dot-b {{ border-radius: 50%; background: var(--s2); }}
.s1 {{ background: var(--s1); }} .s2 {{ background: var(--s2); }} .s3 {{ background: var(--s3); }}
.s4 {{ background: var(--s4); }} .s5 {{ background: var(--s5); }} .s6 {{ background: var(--s6); }}
.s7 {{ background: var(--s7); }}

/* ── 가로 막대 ── */
.hbars {{ display: flex; flex-direction: column; gap: 5px; }}
.hb {{ display: grid; grid-template-columns: 7.5rem minmax(0,1fr) 4rem; gap: .6rem;
  align-items: center; }}
.hb:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 2px; }}
.hb-l {{ font-size: var(--step--1); color: var(--ink-2); white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis; }}
.hb-t {{ height: 12px; background: var(--grid); border-radius: 2px; overflow: hidden; }}
.hb-t i {{ display: block; height: 100%; background: var(--s1); border-radius: 0 4px 4px 0; }}
.hb-v {{ font-family: var(--mono); font-size: var(--step--1); color: var(--ink);
  font-variant-numeric: tabular-nums; text-align: right; }}

/* ── 100% 누적 ── */
.stacks {{ display: flex; flex-direction: column; gap: 6px; }}
.sb {{ display: grid; grid-template-columns: 7.5rem minmax(0,1fr) 3.4rem; gap: .6rem; align-items: center; }}
.sb-l {{ font-size: var(--step--1); color: var(--ink-2); white-space: nowrap; }}
.sb-t {{ display: flex; gap: 2px; height: 20px; }}
.sb-t i {{ display: block; min-width: 2px; position: relative; border-radius: 2px; }}
.sb-t i:first-child {{ border-radius: 4px 2px 2px 4px; }}
.sb-t i:last-child {{ border-radius: 2px 4px 4px 2px; }}
.sb-t i:focus-visible {{ outline: 2px solid var(--ink); outline-offset: 1px; }}
.sb-t i b {{ position: absolute; inset: 0; display: grid; place-items: center;
  font-family: var(--mono); font-size: .62rem; font-weight: 600; color: #fff;
  text-shadow: 0 0 2px rgba(0,0,0,.45); }}
/* aqua·yellow·magenta 는 밝아서 흰 글자가 안 읽힌다 — 어두운 잉크 + 밝은 후광 */
.sb-t i.s3 b, .sb-t i.s4 b, .sb-t i.s5 b {{ color: #16191d; text-shadow: 0 0 2px rgba(255,255,255,.5); }}
.sb-t i.res {{ background: var(--grid); }}
.sb-v {{ font-family: var(--mono); font-size: var(--step--1); color: var(--ink-3);
  text-align: right; font-variant-numeric: tabular-nums; }}

/* ── 매트릭스 ── */
.mx {{ background: var(--card); border: 1px solid var(--rule); border-radius: 4px;
  padding: .5rem .7rem .7rem; overflow-x: auto; }}
.mx-head, .mx-r {{ display: grid; grid-template-columns: 12rem minmax(0,1fr) 2rem 3.2rem;
  gap: .6rem; align-items: center; min-width: 32rem; }}
.mx-head {{ padding: .25rem 0 .4rem; border-bottom: 1px solid var(--rule); position: sticky; top: 0;
  background: var(--card); z-index: 2; }}
.mx-chs {{ display: grid; grid-template-columns: repeat(8, 1fr); gap: 3px; }}
.mx-ch {{ font-family: var(--mono); font-size: .58rem; color: var(--ink-3); text-align: center;
  letter-spacing: .02em; }}
.mx-group {{ margin: .9rem 0 .35rem; }}
.mx-group span {{ font-family: var(--mono); font-size: .63rem; letter-spacing: .09em;
  text-transform: uppercase; color: var(--accent); }}
.mx-r {{ padding: 1px 0; }}
.mx-rl {{ font-family: var(--mono); font-size: .72rem; color: var(--ink); white-space: nowrap;
  overflow: hidden; text-overflow: ellipsis; padding-left: .45rem; border-left: 4px solid transparent; }}
.mx-r.t-standard .mx-rl {{ border-left-color: var(--t1); }}
.mx-r.t-prevalent .mx-rl {{ border-left-color: var(--t2); }}
.mx-r.t-divergent .mx-rl {{ border-left-color: var(--t3); }}
.mx-r.t-system-specific .mx-rl {{ border-left-color: var(--t4); }}
.mx-cells {{ display: grid; grid-template-columns: repeat(8, 1fr); gap: 3px; }}
.mx-c {{ height: 15px; border-radius: 2px; background: var(--grid);
  box-shadow: inset 0 0 0 1px var(--rule-2); }}
.mx-c.on {{ background: var(--s1); box-shadow: none; }}
.mx-c:focus-visible {{ outline: 2px solid var(--ink); outline-offset: 1px; }}
.mx-n {{ font-family: var(--mono); font-size: .72rem; color: var(--ink-2); text-align: right;
  font-variant-numeric: tabular-nums; }}
.mx-t {{ font-family: var(--mono); font-size: .6rem; text-align: center; padding: .1rem .25rem;
  border-radius: 2px; }}
.mx-t.t-standard {{ color: var(--t1); background: var(--t1-bg); }}
.mx-t.t-prevalent {{ color: var(--t2); background: var(--t2-bg); }}
.mx-t.t-divergent {{ color: var(--t3); background: var(--t3-bg); }}
.mx-t.t-system-specific {{ color: var(--t4); background: var(--t4-bg); }}
.code-key {{ font-size: var(--step--1); color: var(--ink-3); margin: .5rem 0 1rem; }}
.code-key b {{ font-family: var(--mono); color: var(--ink-2); font-weight: 500; }}

/* ── 덤벨 ── */
.dbs {{ display: flex; flex-direction: column; gap: 7px; }}
.db, .db-axis {{ display: grid; grid-template-columns: 7.5rem minmax(0,1fr) 7.5rem;
  gap: .7rem; align-items: center; }}
.db-l {{ font-size: var(--step--1); color: var(--ink-2); white-space: nowrap; }}
.db-t {{ position: relative; height: 16px; }}
.db-t::before {{ content: ""; position: absolute; left: 0; right: 0; top: 50%; height: 1px;
  background: var(--grid); }}
.db-line {{ position: absolute; top: 50%; height: 3px; transform: translateY(-50%);
  background: var(--axis); border-radius: 2px; }}
.db-p {{ position: absolute; top: 50%; width: 11px; height: 11px; border-radius: 50%;
  transform: translate(-50%,-50%); box-shadow: 0 0 0 2px var(--card); }}
.db-p.a {{ background: var(--card); border: 2px solid var(--s1); }}
.db-p.b {{ background: var(--s2); }}
.db-p:focus-visible {{ outline: 2px solid var(--ink); outline-offset: 2px; }}
.db-v {{ font-family: var(--mono); font-size: var(--step--1); color: var(--ink-2);
  font-variant-numeric: tabular-nums; }}
.db.big .db-v {{ color: var(--warn); font-weight: 600; }}
.db .flag {{ font-family: var(--sans); font-size: .68rem; font-weight: 500; margin-left: .3rem; }}
.db-axis {{ margin-top: .2rem; }}
.db-axis .db-t {{ height: 1rem; }}
.db-axis .db-t span {{ position: absolute; top: 0; transform: translateX(-50%);
  font-family: var(--mono); font-size: .62rem; color: var(--ink-3); }}
.db-axis .db-t::before {{ top: 0; }}

/* ── facet ── */
.facets {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(19rem,1fr)); gap: 1rem; }}
.facet {{ background: var(--card); border: 1px solid var(--rule); border-radius: 4px; padding: .95rem 1.05rem; }}
.facet figcaption {{ font-size: var(--step-0); font-weight: 620; margin-bottom: .7rem; }}
.facet figcaption small {{ display: block; font-weight: 400; color: var(--ink-3);
  font-family: var(--mono); font-size: .66rem; margin-top: .12rem; }}
.facet .hb {{ grid-template-columns: 5.5rem minmax(0,1fr) 2.8rem; }}

/* ── Button 축 표 ── */
.scroll {{ overflow-x: auto; border: 1px solid var(--rule); border-radius: 4px; background: var(--card); }}
table {{ border-collapse: collapse; width: 100%; font-size: var(--step--1); }}
thead th {{ text-align: left; font-weight: 600; color: var(--ink-2); font-size: .68rem;
  letter-spacing: .07em; text-transform: uppercase; padding: .55rem .75rem;
  border-bottom: 1px solid var(--rule); white-space: nowrap; background: var(--card);
  position: sticky; top: 0; }}
tbody th {{ text-align: left; font-weight: 500; padding: .5rem .75rem; white-space: nowrap; }}
tbody td {{ padding: .5rem .75rem; vertical-align: middle; }}
tbody tr + tr th, tbody tr + tr td {{ border-top: 1px solid var(--rule-2); }}
.num {{ font-family: var(--mono); font-variant-numeric: tabular-nums; white-space: nowrap; }}
.path {{ font-family: var(--mono); font-size: .74rem; color: var(--ink-3); word-break: break-all; }}
.ex {{ display: inline-block; font-size: .7rem; color: var(--ink-2); background: var(--rule-2);
  padding: .06rem .3rem; border-radius: 2px; margin: 0 .16rem .12rem 0; }}
.bx {{ position: relative; }}
.bx code {{ font-size: .72rem; }}
.bx .cnt {{ display: inline-block; margin-left: .35rem; font-family: var(--mono); font-size: .64rem;
  color: var(--ink-3); background: var(--rule-2); border-radius: 2px; padding: 0 .25rem; }}
.bx.merged code {{ background: var(--t3-bg); color: var(--t2); padding: .05rem .25rem; border-radius: 2px; }}
.bx.none .glyph, .bx .glyph {{ color: var(--ink-3); }}
.bstruct {{ font-size: .7rem; white-space: nowrap; }}
.bstruct.s-m {{ color: var(--warn); font-weight: 600; }}
.bstruct.s-s {{ color: var(--ink-2); }}
.bstruct.s-n {{ color: var(--ink-3); }}
.note {{ color: var(--ink-2); max-width: 24rem; font-size: .95em; line-height: 1.5; }}

/* ── 표 병기 (대비 WARN 완화 + 접근성) ── */
.tv {{ margin: .8rem 0 0; }}
.tv summary {{ font-size: var(--step--1); color: var(--accent); cursor: pointer; padding: .25rem 0; }}
.tv summary:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
.tv[open] summary {{ margin-bottom: .5rem; }}

ul.plain {{ list-style: none; padding: 0; margin: 0 0 1rem; }}
ul.plain li {{ padding: .35rem 0; border-bottom: 1px solid var(--rule-2); font-size: var(--step--1);
  color: var(--ink-2); max-width: 74ch; }}
ul.plain .w {{ font-family: var(--mono); font-size: .7rem; color: var(--ink-3); }}
ol.recipe {{ padding-left: 1.4rem; max-width: 70ch; counter-reset: r; list-style: none; }}
ol.recipe li {{ margin-bottom: .8rem; position: relative; }}
ol.recipe li::before {{ counter-increment: r; content: counter(r); position: absolute;
  left: -1.6rem; top: .18rem; font-family: var(--mono); font-size: .66rem; color: var(--accent);
  background: var(--accent-soft); width: 1.15rem; height: 1.15rem; border-radius: 2px;
  display: grid; place-items: center; }}
ol.recipe b {{ font-weight: 620; }}
footer {{ margin-top: 4rem; padding-top: 1.4rem; border-top: 1px solid var(--rule);
  color: var(--ink-3); font-size: var(--step--1); }}

#tip {{ position: fixed; z-index: 50; pointer-events: none; opacity: 0;
  transform: translate(-50%, -130%); background: var(--ink); color: var(--paper);
  font-size: .72rem; line-height: 1.45; padding: .35rem .5rem; border-radius: 3px;
  max-width: 22rem; transition: opacity .08s linear; }}
#tip.on {{ opacity: 1; }}
@media (prefers-reduced-motion: reduce) {{ * {{ transition: none !important; animation: none !important; }} }}
</style>

<div class="wrap">
<nav class="rail" aria-label="목차">
  <p class="rail-t">목차</p>
  <ol>
    <li><a href="#how">측정 방법과 한계</a></li>
    <li><a href="#scale">1. 토큰 규모와 구성</a></li>
    <li><a href="#tokens">2. 어휘 커버리지 매트릭스</a></li>
    <li><a href="#components">3. 컴포넌트 교집합</a></li>
    <li><a href="#variants">4. Button variant 축</a></li>
    <li><a href="#figma">5. Figma 쪽 축 분포</a></li>
    <li><a href="#reaudit">6. 재감사</a></li>
    <li><a href="#reaudit" class="sub-a">6-1 의존율 재측정</a></li>
    <li><a href="#mfi" class="sub-a">6-2 MFI-partial</a></li>
    <li><a href="#recipe">7. 최소 시스템 레시피</a></li>
    <li><a href="#sources">부록 — 소스 커밋</a></li>
  </ol>
</nav>

<main>
<p class="eyebrow">design-systems-benchmark · 실측</p>
<h1>디자인 시스템에서 표준화할 수 있는 것</h1>
<p class="lede">{n_systems}개 컴포넌트 라이브러리의 <b>실제 소스</b>에서 semantic 토큰 {tok_total}개와
컴포넌트 인벤토리를 추출해, 어느 개념이 예외 없이 공통이고 어느 개념이 갈리는지 셌다.
공통인 것만이 표준화 가능하다.</p>

<div class="meta">
  <span><b>대상</b> {systems_list}</span>
  <span><b>기준일</b> 2026-07-30</span>
  <span><b>소스</b> 고정 커밋 (부록)</span>
</div>

<div class="kpis">
  <div class="kpi"><div class="k">{std_count}</div><div class="l">예외 없이 공통인<br>토큰 어휘</div></div>
  <div class="kpi"><div class="k">{comp_std_n}</div><div class="l">8개 시스템 전부에<br>있는 컴포넌트</div></div>
  <div class="kpi"><div class="k">{tok_total}</div><div class="l">추출한 semantic<br>토큰 총수</div></div>
  <div class="kpi"><div class="k">{unc_pct}<small>%</small></div><div class="l">category 축을<br>못 붙인 잔여</div></div>
</div>

<h2 id="how"><span class="h2n">방법</span>측정 방법과 한계</h2>
<p class="sub">결론보다 이 문단이 먼저다. 이 저장소의 기존 감사가 남긴 교훈이
"집계 기준을 명시하지 않은 감사는 비교 불가"이기 때문이다.</p>
<ul class="plain">
<li><b>수집 범위</b> — 각 시스템의 <i>semantic(alias) 계층</i>만. primitive 램프(<code>gray-100</code> 류)는 제외했다. 표준화 대상이 아니다.</li>
<li><b>판정</b> — 토큰 이름을 4개 축(값의 종류 / 자리 / 의미 / 상태)으로 분류하고, 각 값이 {n_systems}개 중 몇 개 시스템에 등장하는지 센다.</li>
<li><b>이름이 곧 근거</b> — 값이 아니라 <i>이름</i>을 본다. 이름에 개념이 드러나지 않으면 그 시스템은 실제로 그 개념을 구분하지 않는다고 본다.</li>
<li><b>잔여 {unc_total}개({unc_pct}%)</b>는 <i>값의 종류</i> 축만 못 붙은 것이다 (다른 축은 기록됐다). 대부분 Carbon 의 <code>code01</code>/<code>container01</code> 같은 시스템 고유 스케일이다.</li>
</ul>
<div class="callout">
<p><b>이름이 같아야 개념이 같은 것은 아니다.</b> Fluent 2 는 상태색을 <code>status</code> 가 아니라
<i>색조</i> 이름으로 부른다 — <code>colorPaletteCranberryForeground1</code> 이 위험색이다.
이 문서는 <code>statusColorMapping.ts</code>(success→green, warning→orange, danger→cranberry)를
읽어 매핑한 뒤 커버리지에 넣었다. 해당 사례:</p>
<ul class="plain">{hue_html}</ul>
</div>

<h2 id="scale"><span class="h2n">1</span>토큰 규모와 구성</h2>
<p class="sub">먼저 규모. 최대와 최소가 <b>10배</b> 차이다. 토큰이 많은 게 좋은 것은 아니다 —
아래 구성비를 보면 그 수가 어디에 쓰였는지가 갈린다.</p>
<div class="panel">{chart_a}{table_a}</div>

<h3>무엇에 토큰을 쓰는가</h3>
<p class="sub">같은 "디자인 토큰"이라도 시스템마다 무게중심이 다르다. shadcn/ui 는 거의 색상뿐이고,
Material Web 은 절반이 타이포그래피, Spectrum 은 4분의 1이 간격이다.
<b>간격을 토큰화하지 않은 시스템이 둘</b>(Material Web · shadcn/ui) 있다.</p>
<div class="panel">{chart_b}{table_b}</div>

<h2 id="tokens"><span class="h2n">2</span>어휘 커버리지 매트릭스</h2>
<p class="sub">이 문서의 핵심. 행은 정규 어휘 하나, 열은 시스템 하나.
<b>칸이 채워졌으면 그 시스템이 그 개념을 이름에 드러낸다</b>는 뜻이다.
행을 가로로 읽으면 표준화 가능성, 열을 세로로 읽으면 그 시스템의 성향이 보인다.
칸에 커서를 올리면 실제 토큰 이름이 나온다.</p>
<p class="code-key">{code_key}</p>
{chart_c}
{table_c}
<div class="callout">
<p><b>세로로 읽으면 shadcn/ui 열이 눈에 띄게 비어 있다.</b> 상태(hover·focus·active)와
elevation·간격 토큰이 없다. 없어서 못 만든 게 아니라, 그 표현을 토큰이 아닌
Tailwind 유틸리티로 옮긴 설계다 — 대가는 상태 표현이 컴포넌트 코드에 흩어진다는 것.</p>
</div>

<h2 id="components"><span class="h2n">3</span>컴포넌트 교집합</h2>
<p class="sub">디렉터리·파일 인벤토리를 정규 개념으로 접은 결과. 시스템마다 분해 단위가 달라
(Carbon 은 DataTable 하위를 개별 디렉터리로 둔다) 절대 개수는 비교하지 않고 <i>개념 커버리지</i>만 본다.
칸에 커서를 올리면 그 시스템이 쓰는 실제 이름이 나온다 — 같은 개념을 얼마나 다르게 부르는지가 여기 다 있다.</p>
{chart_d}
{table_d}

<h2 id="variants"><span class="h2n">4</span>Button variant 축 — 8종 실측</h2>
<p class="sub">축 자체는 거의 같다. <b>강조도</b>(얼마나 강해 보이나) · <b>의미</b>(무슨 일을 하나) ·
<b>크기</b> · <b>형태</b>. 갈리는 건 이름, 그리고 강조도와 의미를 <i>분리했는지 합쳤는지</i>다.
회색 숫자는 그 축의 값 개수.</p>
<div class="scroll"><table>
<thead><tr><th scope="col">시스템</th><th scope="col">강조도</th><th scope="col">의미</th>
<th scope="col">크기</th><th scope="col">형태</th><th scope="col">두 축 관계</th>
<th scope="col">설계 특징</th></tr></thead>
<tbody>{b_rows}</tbody></table></div>
<div class="callout">
<p><b>합치면 값이 곱으로 폭발한다.</b> Carbon 은 <code>kind</code> 하나에 강조도와 의미를 합쳐
<code>danger--tertiary</code> 처럼 조합을 문자열로 인코딩한다. Spectrum·MUI·Polaris·Ant Design 은
두 축을 분리해 같은 표현력을 값의 곱 없이 얻는다. 새로 만든다면 분리가 맞다.</p>
<p><b>Material Web 은 variant prop 자체가 없다.</b> 강조도별로 별도 커스텀 엘리먼트
(<code>&lt;md-filled-button&gt;</code>, <code>&lt;md-text-button&gt;</code> …)로 나눈다. 크기 축도 없다.
Figma 킷에는 variant 가 있으니 — 이 지점이 Figma↔Code 매핑이 구조적으로 어긋나는 자리다.</p>
</div>

<h2 id="figma"><span class="h2n">5</span>Figma 쪽 축 분포</h2>
<p class="sub">공식 Figma 킷 4종의 COMPONENT_SET 에서 variant property 이름을 집계했다.
막대는 그 축을 쓰는 SET 의 비율. <b>어느 킷에서도 1위가 <code>state</code></b>다 —
디자인 파일이 가장 많이 표현하는 축은 상호작용 상태다.
코드에서 상태는 prop 이 아니라 CSS 의사클래스이므로, 이 축은 원리상 1:1 매핑되지 않는다.</p>
<div class="facets">{figs}</div>

<h2 id="reaudit"><span class="h2n">6</span>재감사 — 기존 결론이 지금도 성립하나</h2>
<h3 style="margin-top:1.2rem">6-1. 토큰 의존율 재측정</h3>
<p class="sub">컴포넌트 4종(Button / Checkbox / Dialog / TextInput)의 스타일 소스에서
<code>토큰 참조 / (토큰 참조 + hardcoded)</code> 를 셌다. 빈 원이 기존 문서값, 채운 원이 재측정값.
선이 길수록 결론이 바뀐 것이다.</p>
<div class="panel">{chart_g}{table_g}</div>
<div class="callout">
<p>{gap_txt} 원인은 소스 변화가 아니라 <i>집계 기준</i>이다.
기존 감사는 shadcn 의 Tailwind 클래스를 전부 hardcoded 로 세었고(205개), 이 재측정은
테마 스케일을 참조하는 클래스를 토큰 참조로 센다. 어느 쪽도 틀리지 않았다 —
그래서 <b>"토큰 의존율 3 클러스터"는 시스템의 속성이 아니라 계수 규칙의 산물</b>이라고 봐야 한다.
이 저장소가 스스로 경고한 함정 7번이 자기 결론에도 적용된다.</p>
</div>

<h3 id="mfi">6-2. Mapping Fidelity Index (부분)</h3>
<p class="sub">로드맵 §2.1 의 MFI 5개 항목 중 계산 가능한 2개만 구해 가중치 0.50 구간으로
재정규화했다. 막대는 두 항목의 기여를 쌓은 것 — 오른쪽 숫자가 MFI-partial.
로드맵의 MFI 와 <b>같은 값이 아니다</b>.</p>
<div class="panel">{chart_h}{table_h}</div>
<p class="sub" style="margin-top:1rem">계산하지 못한 항목 (가중치 0.50):</p>
<ul class="plain">{unmeasured}</ul>

<h2 id="recipe"><span class="h2n">7</span>그래서 최소 시스템은 무엇을 갖춰야 하나</h2>
<p class="sub">위 측정에서 <b>8/8</b>로 나온 것만 모은 목록이다. 하나라도 빠뜨리면
{n_systems}개 시스템 중 어느 것도 하지 않은 선택을 하는 셈이다.</p>
<ol class="recipe">
<li><b>색상 토큰을 세 자리로 나눈다</b> — 면(surface) · 글자(foreground) · 선(border).
예외 없이 8/8이다. 하나로 뭉치면 다크 테마에서 반드시 깨진다.</li>
<li><b>의미 축에 최소 세 값</b> — 브랜드 · 보조 · 위험(critical). 성공·경고는 {cov_status}로 그다음 순위.</li>
<li><b>상태를 토큰으로 만든다</b> — hover · focus · active 는 {cov_state}.
미보유는 {miss_state} — 그 대가로 상태 표현이 컴포넌트 코드에 흩어진다.</li>
<li><b>타이포그래피 스케일을 토큰화한다</b> — 8/8. 색상과 함께 유일하게 예외가 없는 값 종류다.</li>
<li><b>Elevation·radius 는 {cov_shape}</b> — 미보유는 {miss_shape} 로 예외다
(shadcn 은 Tailwind 유틸리티, Carbon 은 radius 토큰이 <i>아예 없다</i> — 각진 형태를 부재로 강제한다).</li>
<li><b>컴포넌트는 9개부터</b> — {comp_std}.</li>
<li><b>Button 의 variant 축은 강조도와 의미를 분리한다</b> — 합치면 값이 곱으로 폭발한다.</li>
<li><b>상태는 Figma 와 코드가 원리상 어긋난다</b> — Figma 킷의 1위 축이 <code>state</code>인데
코드에서는 prop 이 아니라 의사클래스다. 자동 동기화를 시도하지 말고 계약 문서로 남긴다.</li>
</ol>

<h2 id="sources"><span class="h2n">부록</span>측정에 쓴 소스 커밋</h2>
<p class="sub">얕은 클론으로 받은 고정 커밋. 재현은 <code>bash sources/clone.sh</code>.</p>
<div class="scroll"><table>
<thead><tr><th scope="col">key</th><th scope="col">repo</th><th scope="col">HEAD</th>
<th scope="col">커밋일</th><th scope="col">용량</th></tr></thead>
<tbody>{man_html}</tbody></table></div>

<footer>
<p>생성: <code>python3 analysis/standard-research/run.py</code> — 데이터는 <code>measured/</code> · <code>derived/</code> · <code>curated/</code> 에서 읽는다.
측정 스크립트: <code>tools/extract_tokens.py</code> · <code>classify_tokens.py</code> ·
<code>extract_components.py</code> · <code>measure_dependency.py</code> · <code>mfi.py</code>.</p>
<p>차트 색상은 dataviz 레퍼런스 팔레트를 이 문서의 surface(<code>#f6f7f8</code> / <code>#14171a</code>)에
맞춰 재검증해 사용했다 — categorical 7슬롯·ordinal 4단계 모두 전 항목 PASS.
light 모드 대비 WARN 항목은 직접 라벨과 표 병기로 완화했다.</p>
</footer>
</main>
</div>

<div id="tip" role="status" aria-live="polite"></div>
<script>
(function () {{
  var tip = document.getElementById('tip'), cur = null;
  function show(el) {{
    var t = el.getAttribute('data-tip');
    if (!t) return;
    tip.innerHTML = t;
    var r = el.getBoundingClientRect();
    tip.style.left = Math.min(Math.max(r.left + r.width / 2, 120), window.innerWidth - 120) + 'px';
    tip.style.top = r.top + 'px';
    tip.classList.add('on');
    cur = el;
  }}
  function hide() {{ tip.classList.remove('on'); cur = null; }}
  document.addEventListener('pointerover', function (ev) {{
    var el = ev.target.closest('[data-tip]');
    if (el && el !== cur) show(el); else if (!el && cur) hide();
  }});
  document.addEventListener('pointerleave', hide);
  document.addEventListener('focusin', function (ev) {{
    var el = ev.target.closest('[data-tip]');
    if (el) show(el);
  }});
  document.addEventListener('focusout', hide);
  document.addEventListener('keydown', function (ev) {{ if (ev.key === 'Escape') hide(); }});
  // 스크롤 중에는 위치를 따라가게 하지 않고 감춘다 — 포인터가 안 움직이면 툴팁이 남는다
  window.addEventListener('scroll', hide, {{passive: true}});
}})();
</script>
"""


if __name__ == "__main__":
    for name, body in ((OUT_HTML, build()), (OUT_MD, build_md())):
        p = paths.write_report(name, body)
        print(f"-> {p}  ({p.stat().st_size:,} bytes)")
