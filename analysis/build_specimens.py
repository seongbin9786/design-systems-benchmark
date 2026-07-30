#!/usr/bin/env python3
"""실물 견본 시트 — 8개 시스템의 컴포넌트를 각자의 *실제 값*으로 렌더링한다.

입력: analysis/data/values.json (extract_values.py 출력)
출력: analysis/design-system-specimens.html

앞선 리포트들은 차트로 원리를 보여줬다. 이 문서는 실물을 나란히 놓는다.
색·크기·radius·굵기 전부 각 시스템 소스에서 해석한 값이고, 근거 경로를 함께 적는다.

렌더 방식
  각 견본은 인라인 style 로 그 시스템의 값을 직접 받는다. 공용 CSS 로 모양을 통일하지 않는다 —
  통일하면 비교 대상인 차이가 사라진다.

정직성 표시
  [실측]  Button — 지오메트리를 소스에서 읽어 확인했다 (evidence 경로 표시)
  [구성]  Input · Card · Badge · Alert — 그 시스템의 토큰 값으로 조립했다.
          원본 컴포넌트의 모든 세부(내부 패딩·아이콘·전이)를 재현한 것은 아니다.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "analysis" / "data"
OUT = ROOT / "analysis" / "design-system-specimens.html"

SLOT_LABEL = {
    "surface": "surface", "surface-raised": "surface 상위", "text-primary": "text 주",
    "text-secondary": "text 보조", "border": "border", "brand-bg": "brand 배경",
    "brand-fg": "brand 전경", "danger-bg": "danger", "success-bg": "success",
    "warning-bg": "warning",
}


def e(x):
    return html.escape(str(x), quote=True)


def css_val(v, fallback="transparent"):
    return v if v else fallback


def button_row(system, b):
    """그 시스템의 실제 지오메트리·색으로 버튼 4종을 그린다."""
    up = "text-transform:uppercase;letter-spacing:.02857em;" if b.get("uppercase") else ""
    btns = []
    for v in b["variants"]:
        style = (
            f"height:{b['height']};padding:{b['padding']};"
            f"border-radius:{b['radius']};font-size:{b['font_size']};"
            f"font-weight:{b['font_weight']};"
            f"border:{b['border_width']} solid {css_val(v.get('border'))};"
            f"background:{css_val(v.get('bg'))};color:{css_val(v.get('fg'), 'inherit')};{up}"
        )
        tip = (f"{system} · {v['label']} — bg {v.get('bg') or 'transparent'} · "
               f"fg {v.get('fg') or '-'} · h {b['height']} · r {b['radius']}")
        btns.append(f'<button class="sp-btn" style="{e(style)}" data-tip="{e(tip)}">'
                    f'{e(v["label"])}</button>')
    return (f'<div class="sp-row"><div class="sp-name">{e(system)}'
            f'<code>h {e(b["height"])} · r {e(b["radius"])} · {e(b["font_size"])}/{b["font_weight"]}</code></div>'
            f'<div class="sp-items">{"".join(btns)}</div></div>')


def swatches(system, pal, slots):
    cells = []
    for s in slots:
        v = pal.get(s)
        if not v:
            cells.append(f'<div class="sw none" data-tip="{e(system)} · {e(s)} — 없음">'
                         f'<span class="sw-x">없음</span></div>')
            continue
        cells.append(f'<div class="sw" style="background:{e(v)}" '
                     f'data-tip="{e(system)} · {e(s)} — {e(v)}"><span class="sw-v">{e(v)}</span></div>')
    return (f'<div class="sw-row"><div class="sp-name">{e(system)}</div>'
            f'<div class="sw-cells">{"".join(cells)}</div></div>')


def type_specimen(system, ty, pal):
    if not ty:
        return ""
    lines = []
    for t in ty:
        st = f"font-size:{t['size']};font-weight:{t['weight']};"
        if t.get("line_height"):
            lh = t["line_height"]
            st += f"line-height:{lh};" if not str(lh).replace('.', '').isdigit() or float(lh) < 4 else f"line-height:{lh};"
        lines.append(f'<div class="ty-l"><span class="ty-k">{e(t["name"])}</span>'
                     f'<span class="ty-s" style="{e(st)}" data-tip="{e(system)} · {e(t["name"])} — '
                     f'{e(t["size"])} / {t["weight"]}">다람쥐 헌 쳇바퀴 Ag 123</span>'
                     f'<span class="ty-m">{e(t["size"])} · {t["weight"]}</span></div>')
    return (f'<figure class="card"><figcaption>{e(system)}</figcaption>'
            f'<div class="ty" style="color:{e(css_val(pal.get("text-primary"), "inherit"))}">'
            f'{"".join(lines)}</div></figure>')


def radius_specimen(system, radii, pal):
    boxes = []
    for r in radii:
        boxes.append(f'<div class="rx"><div class="rx-b" style="border-radius:{e(r["value"])};'
                     f'background:{e(css_val(pal.get("brand-bg"), "#888"))}" '
                     f'data-tip="{e(system)} · {e(r["name"])} — {e(r["value"])}"></div>'
                     f'<span class="rx-k">{e(r["value"])}</span></div>')
    return (f'<figure class="card"><figcaption>{e(system)}'
            f'<small>{e(radii[0]["name"].rsplit("-", 1)[0] if radii else "")}</small></figcaption>'
            f'<div class="rxs">{"".join(boxes)}</div></figure>')


def space_specimen(system, spaces, pal):
    bars = []
    for sp in spaces:
        val = sp["value"]
        if val == "—":
            bars.append('<div class="spx"><span class="spx-k">토큰 없음</span></div>')
            continue
        bars.append(f'<div class="spx"><span class="spx-b" style="width:{e(val)};'
                    f'background:{e(css_val(pal.get("brand-bg"), "#888"))}" '
                    f'data-tip="{e(system)} · {e(sp["name"])} — {e(val)}"></span>'
                    f'<span class="spx-k">{e(val)}</span></div>')
    return (f'<figure class="card"><figcaption>{e(system)}</figcaption>'
            f'<div class="spxs">{"".join(bars)}</div></figure>')


def elev_specimen(system, shadows, pal):
    cards = []
    for sh in shadows:
        cards.append(f'<div class="ev" style="box-shadow:{e(sh["value"])};'
                     f'background:{e(css_val(pal.get("surface-raised"), "#fff"))}" '
                     f'data-tip="{e(system)} · {e(sh["name"])} — {e(sh["value"])}">'
                     f'<span>{e(sh["name"])}</span></div>')
    return (f'<figure class="card lifted" style="background:{e(css_val(pal.get("surface"), "#f5f5f5"))}">'
            f'<figcaption style="color:{e(css_val(pal.get("text-primary"), "inherit"))}">{e(system)}</figcaption>'
            f'<div class="evs">{"".join(cards)}</div></figure>')


def ui_specimen(system, d):
    """Input · Card · Badge · Alert — 그 시스템의 토큰으로 조립한 견본."""
    pal, b = d["palette"], d["button"]
    # 버튼 radius 를 카드·입력에 그대로 쓰면 안 된다 — Material Web 의 알약(999px)이 카드를 타원으로 만든다.
    # 컨테이너용으로는 그 시스템 radius 스케일에서 *알약이 아닌* 단계를 고른다.
    def px(v):
        m = re.search(r"([\d.]+)\s*(px|rem)", str(v))
        if not m:
            return None
        n = float(m.group(1))
        return n * 16 if m.group(2) == "rem" else n

    boxy = [r["value"] for r in d["radius"] if (px(r["value"]) or 0) <= 24]
    r_card = boxy[len(boxy) // 2] if boxy else "0"
    r_field = boxy[0] if boxy else "0"
    radius = r_field
    surface = css_val(pal.get("surface"), "#fff")
    raised = css_val(pal.get("surface-raised"), surface)
    ink = css_val(pal.get("text-primary"), "#000")
    ink2 = css_val(pal.get("text-secondary"), ink)
    border = css_val(pal.get("border"), "#ccc")
    brand = css_val(pal.get("brand-bg"), "#888")
    brand_fg = css_val(pal.get("brand-fg"), "#fff")
    danger = css_val(pal.get("danger-bg"), "#c00")
    shadow = d["shadow"][min(1, len(d["shadow"]) - 1)]["value"] if d["shadow"] else "none"

    field = (f'<label class="ui-f" style="color:{e(ink2)};font-size:{e(b["font_size"])}">이메일'
             f'<input class="ui-i" value="name@example.com" readonly'
             f' style="height:{e(b["height"])};border-radius:{e(radius)};'
             f'border:{e(b["border_width"])} solid {e(border)};background:{e(surface)};'
             f'color:{e(ink)};font-size:{e(b["font_size"])}"'
             f' data-tip="{e(system)} · Input — h {e(b["height"])} · r {e(radius)} · border {e(border)}"></label>')
    badges = (f'<div class="ui-bs">'
              f'<span class="ui-bd" style="background:{e(brand)};color:{e(brand_fg)};'
              f'border-radius:{e(radius)}" data-tip="{e(system)} · Badge brand — {e(brand)}">brand</span>'
              f'<span class="ui-bd" style="background:{e(danger)};color:#fff;'
              f'border-radius:{e(radius)}" data-tip="{e(system)} · Badge danger — {e(danger)}">danger</span>'
              + (f'<span class="ui-bd" style="background:{e(pal["success-bg"])};color:#fff;'
                 f'border-radius:{e(radius)}" data-tip="{e(system)} · Badge success — {e(pal["success-bg"])}">'
                 f'success</span>' if pal.get("success-bg") else
                 '<span class="ui-bd none">success 없음</span>')
              + '</div>')
    alert = (f'<div class="ui-al" style="background:{e(raised)};border-left:3px solid {e(danger)};'
             f'border-radius:{e(radius)};color:{e(ink)};font-size:{e(b["font_size"])}"'
             f' data-tip="{e(system)} · Alert — danger {e(danger)}">'
             f'<b>저장하지 못했습니다.</b><span style="color:{e(ink2)}"> 필수 항목을 확인하세요.</span></div>')
    primary = b["variants"][0]
    btn = (f'<button class="sp-btn" style="height:{e(b["height"])};padding:{e(b["padding"])};'
           f'border-radius:{e(b["radius"])};font-size:{e(b["font_size"])};font-weight:{b["font_weight"]};'
           f'border:{e(b["border_width"])} solid {e(css_val(primary.get("border")))};'
           f'background:{e(css_val(primary.get("bg")))};color:{e(css_val(primary.get("fg")))};'
           + ("text-transform:uppercase;" if b.get("uppercase") else "")
           + f'">{e(primary["label"])}</button>')

    return (f'<figure class="ui" style="background:{e(surface)};color:{e(ink)}">'
            f'<figcaption style="border-bottom:1px solid {e(border)}">{e(system)}</figcaption>'
            f'<div class="ui-card" style="background:{e(raised)};border:1px solid {e(border)};'
            f'border-radius:{e(r_card)};box-shadow:{e(shadow)}">'
            f'<h5 style="font-size:{e(b["font_size"])}">계정 설정</h5>'
            f'{field}{badges}{alert}<div class="ui-actions">{btn}</div>'
            f'</div></figure>')


def render(**kw):
    txt = (Path(__file__).resolve().parent / "specimens.tmpl.html").read_text(encoding="utf-8")
    missing = set()

    def sub(m):
        k = m.group(1)
        if k not in kw:
            missing.add(k)
            return m.group(0)
        return str(kw[k])

    out = re.sub(r"\{\{([a-z0-9_]+)\}\}", sub, txt)
    if missing:
        raise KeyError(f"템플릿에 값 없는 자리: {sorted(missing)}")
    return out


def main():
    d = json.loads((DATA / "values.json").read_text())
    slots, systems = d["slots"], d["systems"]
    order = ["Spectrum", "Material Web", "MUI", "Fluent 2", "Carbon", "Polaris",
             "shadcn/ui", "Ant Design"]
    order = [s for s in order if s in systems]

    ev_rows = "".join(
        f'<tr><th scope="row">{e(s)}</th>'
        f'<td class="num">{e(systems[s]["button"]["height"])}</td>'
        f'<td class="num">{e(systems[s]["button"]["radius"])}</td>'
        f'<td class="num">{e(systems[s]["button"]["padding"])}</td>'
        f'<td class="num">{e(systems[s]["button"]["font_size"])} / {systems[s]["button"]["font_weight"]}</td>'
        f'<td class="path">{e(systems[s]["button"]["evidence"])}</td></tr>' for s in order)

    return render(
        buttons="".join(button_row(s, systems[s]["button"]) for s in order),
        btn_table=ev_rows,
        swatch_head="".join(f'<span class="sw-h">{e(SLOT_LABEL.get(x, x))}</span>' for x in slots),
        swatch_rows="".join(swatches(s, systems[s]["palette"], slots) for s in order),
        types="".join(type_specimen(s, systems[s]["type"], systems[s]["palette"]) for s in order),
        radii="".join(radius_specimen(s, systems[s]["radius"], systems[s]["palette"]) for s in order),
        spaces="".join(space_specimen(s, systems[s]["space"], systems[s]["palette"]) for s in order),
        elevs="".join(elev_specimen(s, systems[s]["shadow"], systems[s]["palette"]) for s in order),
        uis="".join(ui_specimen(s, systems[s]) for s in order),
        n_systems=len(order),
        no_status=" · ".join(s for s in order if not systems[s]["palette"].get("success-bg")),
        radius_zero=" · ".join(s for s in order
                              if all(r["value"] in ("0", "0px") for r in systems[s]["radius"])),
        no_space=" · ".join(s for s in order
                            if all(x["value"] == "—" for x in systems[s]["space"])),
    )


if __name__ == "__main__":
    OUT.write_text(main(), encoding="utf-8")
    print(f"-> {OUT}  ({OUT.stat().st_size:,} bytes)")
