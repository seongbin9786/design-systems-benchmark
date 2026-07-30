#!/usr/bin/env python3
"""차트 프리미티브와 공용 상수 — 렌더러 3종이 함께 쓴다.

이전에는 render_research.py 가 "기본판 빌더"이면서 동시에 "공용 라이브러리" 역할을
겸했고, 확장판이 그것을 import 했다. 렌더러끼리 결합되면 한쪽을 고칠 때 다른 쪽이
조용히 바뀐다. 공용분은 여기로 분리한다.

색상 — dataviz 레퍼런스 팔레트를 이 문서들의 surface(#f6f7f8 / #14171a)에 맞춰
재검증해 사용한다. categorical 7슬롯 · ordinal 4단계 모두 전 항목 PASS.
"""
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402  — 계층·경로 정의

TIER_LABEL = {
    "standard": "표준",
    "prevalent": "우세",
    "divergent": "분기",
    "system-specific": "고유",
}
AXIS_TITLE = {
    "category": ("값의 종류", "토큰이 무엇을 담는가"),
    "role": ("색이 칠해지는 자리", "같은 색을 어디에 쓰는가"),
    "intent": ("의미와 강조도", "그 색이 무슨 뜻인가"),
    "state": ("상호작용 상태", "상태에 따라 값이 바뀌는가"),
}
# 3글자 코드 — 매트릭스 열 머리글이 8개라 풀네임이 들어가지 않는다
CODE = {
    "Spectrum": "SPE", "Material Web": "MTW", "MUI": "MUI", "Fluent 2": "FLU",
    "Carbon": "CAR", "Polaris": "POL", "shadcn/ui": "SCN", "Ant Design": "ANT",
}
# 누적 막대 고정 슬롯 (전체 볼륨 상위 6개 + 기타). 순서 고정 — 절대 순환시키지 않는다.
COMP_SLOTS = ["color", "typography", "spacing", "sizing", "elevation", "motion", "radius"]
COMP_LABEL = {
    "color": "색상", "typography": "타이포그래피", "spacing": "간격",
    "sizing": "크기", "elevation": "elevation", "motion": "모션", "radius": "radius",
    "기타": "기타", "rest": "미달",
}


def e(x):
    return html.escape(str(x), quote=True)


def load(name):
    """계층 판정은 paths.py 가 한다 — 렌더러는 이름만 안다."""
    return paths.read_json(name)


# ── 차트 프리미티브 ──────────────────────────────────────────────────────────
def hbars(rows, unit="", maxv=None):
    """가로 막대. rows = [(label, value, tip)]. 단일 시리즈이므로 범례 없음."""
    mx = maxv or max((r[1] for r in rows), default=1)
    out = []
    for label, val, tip in rows:
        w = val / mx * 100 if mx else 0
        out.append(f"""<div class="hb" data-tip="{e(tip)}" tabindex="0">
<span class="hb-l">{e(label)}</span>
<span class="hb-t"><i style="width:{w:.2f}%"></i></span>
<span class="hb-v">{e(val)}{e(unit)}</span></div>""")
    return f'<div class="hbars">{"".join(out)}</div>'


def stacked(rows, slots, labels, residual=None):
    """100% 누적 가로 막대. 세그먼트 사이 2px surface 간극, 8% 이상은 직접 라벨.

    residual 로 지정한 슬롯은 *시리즈가 아니다* — 잔여/미달 버킷이므로 중립 트랙 색을 쓰고
    직접 라벨도 붙이지 않는다. 시리즈 색을 주면 없는 계열이 하나 있는 것처럼 읽힌다.
    """
    out = []
    for label, seg, tip in rows:
        parts = []
        for i, k in enumerate(slots):
            pct = seg.get(k, 0)
            if pct <= 0:
                continue
            is_res = k == residual
            cls = "res" if is_res else f"s{i + 1}"
            txt = "" if is_res else (f"{pct:.0f}" if pct >= 8 else "")
            parts.append(
                f'<i class="{cls}" style="flex:{pct}" data-tip="{e(label)} · {e(labels.get(k, k))} {pct}%"'
                f' tabindex="0"><b>{txt}</b></i>')
        out.append(f'<div class="sb" data-row="{e(label)}">'
                   f'<span class="sb-l">{e(label)}</span>'
                   f'<span class="sb-t">{"".join(parts)}</span>'
                   f'<span class="sb-v">{e(tip)}</span></div>')
    return f'<div class="stacks">{"".join(out)}</div>'


def legend(slots, labels):
    items = "".join(
        f'<span class="lg"><i class="s{i + 1}"></i>{e(labels.get(k, k))}</span>'
        for i, k in enumerate(slots))
    return f'<div class="legend-row" role="list">{items}</div>'


def matrix(rows, systems, group_key=None):
    """존재 여부 매트릭스. 행 = 정규 어휘, 열 = 시스템. 채워진 칸 = 이름에 그 개념이 있음."""
    head = "".join(f'<span class="mx-ch" title="{e(s)}">{e(CODE[s])}</span>' for s in systems)
    body = []
    last_group = None
    for r in rows:
        if group_key and r.get("_group") != last_group:
            last_group = r.get("_group")
            body.append(f'<div class="mx-group"><span>{e(last_group)}</span></div>')
        cells = "".join(
            f'<span class="mx-c{" on" if s in r["systems"] else ""}" tabindex="0"'
            f' data-tip="{e(r["value"])} · {e(s)} — {"보유" if s in r["systems"] else "미보유"}'
            f'{(" · " + e(r["examples"][s])) if s in r.get("examples", {}) else ""}"></span>'
            for s in systems)
        tier = r["tier"]
        body.append(f"""<div class="mx-r t-{tier}">
<span class="mx-rl"><b>{e(r['value'])}</b></span>
<span class="mx-cells">{cells}</span>
<span class="mx-n">{r['coverage']}</span>
<span class="mx-t t-{tier}">{TIER_LABEL[tier]}</span></div>""")
    return f"""<div class="mx">
<div class="mx-head"><span></span><span class="mx-chs">{head}</span><span></span><span></span></div>
{"".join(body)}
</div>"""


def dumbbell(rows):
    """문서값 → 재측정값. 두 시리즈이므로 범례 필수. 20pt 이상 벌어진 행은 상태 아이콘+라벨로 표시."""
    out = []
    for label, a, b, gap, big in rows:
        lo, hi = min(a, b), max(a, b)
        out.append(f"""<div class="db{' big' if big else ''}">
<span class="db-l">{e(label)}</span>
<span class="db-t">
  <span class="db-line" style="left:{lo}%;width:{hi - lo}%"></span>
  <span class="db-p a" style="left:{a}%" tabindex="0" data-tip="{e(label)} · 기존 문서값 {a}%"></span>
  <span class="db-p b" style="left:{b}%" tabindex="0" data-tip="{e(label)} · 재측정 {b}%"></span>
</span>
<span class="db-v">{gap:+.0f}pt{' <span class="flag">⚠ 기준 차이</span>' if big else ''}</span></div>""")
    axis = "".join(f'<span style="left:{v}%">{v}</span>' for v in (0, 25, 50, 75, 100))
    return (f'<div class="dbs">{"".join(out)}'
            f'<div class="db-axis"><span class="db-l"></span><span class="db-t">{axis}</span>'
            f'<span class="db-v"></span></div></div>')


def table_view(headers, rows, caption):
    th = "".join(f'<th scope="col">{e(h)}</th>' for h in headers)
    tr = "".join("<tr>" + "".join(
        f'<{"th" if i == 0 else "td"}{" scope=\"row\"" if i == 0 else ""} class="{"" if i == 0 else "num"}">{c}</{"th" if i == 0 else "td"}>'
        for i, c in enumerate(r)) + "</tr>" for r in rows)
    return (f'<details class="tv"><summary>{e(caption)} — 표로 보기</summary>'
            f'<div class="scroll"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div></details>')


