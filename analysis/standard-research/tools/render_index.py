#!/usr/bin/env python3
"""배포용 단일 페이지를 만든다 — reports/index.html.

예전에는 리포트마다 카드 링크를 걸어 각각 다른 페이지로 열게 했다. 그러면 읽는 사람이
섹션마다 이동해야 한다. 이제는 한 페이지에 전부 조립한다 — 히어로·KPI·핵심 발견은
그대로 두고, 세 리포트를 스크롤되는 섹션으로 이어 붙인다.

리포트를 한 문서로 합치지 않고 iframe 으로 담는 이유가 있다. 각 리포트는 `:root`,
`body`, `*`, `.wrap`, `h1·h2` 같은 전역 선택자를 쓰는 독립 완결 HTML 이라 한 문서에
쏟아부으면 스타일이 서로 덮어쓴다 (`.wrap` 만 세 종류). iframe 은 문서를 격리해
정교하게 튜닝된 리포트 스타일을 건드리지 않으면서 한 페이지 경험을 준다. 같은 오리진이라
스크립트가 각 iframe 의 실제 높이로 맞춰 연속 스크롤처럼 보인다.

목차를 손으로 관리하면 리포트가 바뀔 때 어긋난다. 핵심 수치도 데이터에서 읽는다.
정적 호스팅(Vercel 등)의 루트가 reports/ 를 가리키면 그대로 사이트가 된다.
"""
import html
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

OUT = "index.html"


def e(x):
    return html.escape(str(x), quote=True)


def build():
    vocab = paths.read_json("vocabulary")
    comps = paths.read_json("components")
    tokens = paths.read_json("tokens")
    naming = paths.read_json("naming")
    dep = paths.read_json("dependency")

    systems = vocab["systems"]
    n = len(systems)
    n_cs = comps["system_count"]
    tok_total = sum(d["count"] for d in tokens.values())
    std = {a: [r["value"] for r in vocab["axes"][a]
               if r["tier"] == "standard" and r["value"] != "default"]
           for a in ("category", "role", "intent", "state")}
    std_count = sum(len(v) for v in std.values())
    comp_std = [r["component"] for r in comps["coverage"] if r["coverage"] == n_cs]
    ir = [s for s in systems if naming["systems"][s]["order_top"]
          and naming["systems"][s]["order_top"][0]["pattern"].startswith("I")]
    ri = [s for s in systems if naming["systems"][s]["order_top"]
          and naming["systems"][s]["order_top"][0]["pattern"].startswith("R")]
    max_exp = max((t["variants"] for d in comps["figma_variant_axes"].values()
                   for t in d["top_exploded"]), default=0)
    flagged = []
    for s, d in dep["summary"].items():
        try:
            a = float(str(d.get("documented_average")).replace("~", "").replace("%", "").replace("+", ""))
        except (TypeError, ValueError):
            continue
        if abs(d["avg_loose"] - a) >= 20:
            flagged.append(s)

    # (앵커 id, 파일, 아이콘, 제목, 설명) — 카드 링크 대신 한 페이지 섹션으로 조립한다.
    sections = [
        ("research", "design-system-standard-research.html", "📐", "본문 (시각화)",
         "커버리지 히트맵 · 덤벨 차트 · 100% 누적 막대 등 8종. 무엇이 표준화 가능한지 판정한다."),
        ("visual", "design-system-standard-research-visual.html", "📊", "확장판",
         "본문의 상위집합. 이름의 *문법* 까지 파고든다."),
        ("specimens", "design-system-specimens.html", "🎨", "실물 견본",
         "차트가 아니라 실물. 각 시스템의 실제 토큰 값으로 컴포넌트를 렌더링했다."),
    ]
    nav_html = "".join(
        f'<a href="#{sid}">{ico} {e(title)}</a>' for sid, _h, ico, title, _d in sections)
    sec_html = "".join(
        f'<section class="rpt" id="{sid}">'
        f'<header class="rpt-h"><span class="ico">{ico}</span>'
        f'<div class="t"><h2>{e(title)}</h2><p>{e(desc)}</p></div>'
        f'<a class="pop" href="{e(href)}" target="_blank" rel="noopener">새 창 ↗</a></header>'
        f'<iframe class="rpt-frame" src="{e(href)}" loading="lazy" '
        f'title="{e(title)}"></iframe></section>'
        for sid, href, ico, title, desc in sections)

    stats = [
        (std_count, "예외 없이 공통인<br>토큰 어휘"),
        (len(comp_std), f"{n}개 시스템 전부에<br>있는 컴포넌트"),
        (f"{len(ri)}<small> vs {len(ir)}</small>", "어순이 갈린<br>두 진영"),
        (max_exp, "Figma 한 컴포넌트의<br>최대 variant 수"),
    ]
    stat_html = "".join(f'<div class="kpi"><div class="k">{v}</div><div class="l">{l}</div></div>'
                        for v, l in stats)

    findings = [
        ("색상은 세 자리로 나뉜다",
         f"면(surface) · 글자(foreground) · 선(border) — {n}개 시스템 예외 없이 전부. "
         "하나로 뭉치면 다크 테마에서 반드시 깨진다."),
        ("어순이 두 진영으로 갈린다",
         f"의미→역할 {len(ir)}개 vs 역할→의미 {len(ri)}개({' · '.join(ri)}). "
         "개념이 같아도 이름 문법이 달라 사전 하나로 변환할 수 없다."),
        ("축을 합치면 값이 곱으로 폭발한다",
         f"강조도와 의미를 한 축에 합친 결과가 Figma 에서 최대 {max_exp} variant 로 전개된다."),
        ("집계 규칙을 밝히지 않은 수치는 비교 불가다",
         f"기존 감사의 토큰 의존율을 다시 재니 {len(flagged)}개 시스템"
         f"({' · '.join(flagged)})에서 20pt 이상 벌어졌다. 소스가 아니라 계수 규칙 때문이다."),
    ]
    find_html = "".join(f'<div class="f"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in findings)

    return TEMPLATE.replace("{{nav}}", nav_html) \
                   .replace("{{sections}}", sec_html) \
                   .replace("{{stats}}", stat_html) \
                   .replace("{{findings}}", find_html) \
                   .replace("{{n}}", str(n)) \
                   .replace("{{tok_total}}", f"{tok_total:,}") \
                   .replace("{{systems}}", " · ".join(systems)) \
                   .replace("{{comp_std}}", " · ".join(comp_std))


TEMPLATE = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>디자인 시스템 표준화 연구 — 8개 시스템 소스 실측</title>
<meta name="description" content="Spectrum · Material · MUI · Fluent 2 · Carbon · Polaris · shadcn/ui · Ant Design 의 실제 소스에서 토큰과 컴포넌트를 세어 무엇이 표준화 가능한지 판정한 리포트. 한 페이지에서 전부 읽는다.">
<style>
:root {
  --ink: #16191d; --ink-2: #4a5157; --ink-3: #767f87;
  --paper: #f6f7f8; --card: #fff; --rule: #dfe3e6; --rule-2: #eceff1;
  --accent: #2f5d8a; --accent-soft: #e8eff6;
  --mono: ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, monospace;
  --sans: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo", "Pretendard",
          "Segoe UI", "Malgun Gothic", system-ui, sans-serif;
}
@media (prefers-color-scheme: dark) {
  :root:where(:not([data-theme="light"])) {
    --ink: #e6eaee; --ink-2: #a8b2bb; --ink-3: #7b858e;
    --paper: #14171a; --card: #1b1f23; --rule: #2c3238; --rule-2: #23282d;
    --accent: #7fb0dd; --accent-soft: #1e2a35;
  }
}
:root[data-theme="dark"] {
  --ink: #e6eaee; --ink-2: #a8b2bb; --ink-3: #7b858e;
  --paper: #14171a; --card: #1b1f23; --rule: #2c3238; --rule-2: #23282d;
  --accent: #7fb0dd; --accent-soft: #1e2a35;
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body { margin: 0; background: var(--paper); color: var(--ink); font-family: var(--sans);
  font-size: clamp(.9rem,.87rem + .15vw,.95rem); line-height: 1.65; -webkit-font-smoothing: antialiased; }
.wrap { max-width: 62rem; margin: 0 auto; padding: 0 1.5rem; }
.hero { padding-top: 4rem; }
.eyebrow { font-family: var(--mono); font-size: .68rem; letter-spacing: .14em; text-transform: uppercase;
  color: var(--accent); margin: 0 0 .9rem; }
h1 { font-size: clamp(1.9rem,1.6rem + 1.4vw,2.9rem); line-height: 1.1; letter-spacing: -.025em;
  font-weight: 660; margin: 0 0 1rem; text-wrap: balance; max-width: 26ch; }
.lede { font-size: clamp(1.05rem,1rem + .3vw,1.2rem); color: var(--ink-2); margin: 0 0 1.4rem; max-width: 58ch; }
.meta { font-size: .8rem; color: var(--ink-3); margin: 0 0 2.4rem; max-width: 62ch; }
.meta b { color: var(--ink-2); font-weight: 600; }
.kpis { display: grid; grid-template-columns: repeat(auto-fit,minmax(9rem,1fr)); gap: 1px;
  background: var(--rule); border: 1px solid var(--rule); border-radius: 5px; overflow: hidden; margin: 0 0 3rem; }
.kpi { background: var(--card); padding: 1.05rem 1.1rem; }
.kpi .k { font-size: 2rem; line-height: 1; font-weight: 600; letter-spacing: -.035em; }
.kpi .k small { font-size: .95rem; font-weight: 500; color: var(--ink-3); letter-spacing: 0; }
.kpi .l { font-size: .78rem; color: var(--ink-2); margin-top: .45rem; }

.topbar { position: sticky; top: 0; z-index: 20; border-bottom: 1px solid var(--rule);
  background: color-mix(in srgb, var(--paper) 86%, transparent);
  -webkit-backdrop-filter: saturate(1.4) blur(8px); backdrop-filter: saturate(1.4) blur(8px); }
.topbar .in { max-width: 90rem; margin: 0 auto; padding: .55rem 1.5rem;
  display: flex; flex-wrap: wrap; gap: .25rem; align-items: center; }
.topbar a { font-size: .8rem; color: var(--ink-2); text-decoration: none;
  padding: .3rem .65rem; border-radius: 4px; }
.topbar a:hover { color: var(--accent); background: var(--accent-soft); }
.topbar .md { margin-left: auto; color: var(--ink-3); font-family: var(--mono); font-size: .72rem; }

.reports { max-width: 90rem; margin: 0 auto; padding: 2.5rem 1.5rem 0; }
.rpt { margin: 0 0 3.5rem; scroll-margin-top: 4.2rem; }
.rpt-h { display: flex; align-items: flex-start; gap: .7rem; margin: 0 0 .8rem; }
.rpt-h .ico { font-size: 1.4rem; line-height: 1.25; }
.rpt-h .t { min-width: 0; }
.rpt-h h2 { font-size: 1.15rem; font-weight: 640; letter-spacing: -.01em; margin: 0; }
.rpt-h p { font-size: .82rem; color: var(--ink-2); margin: .2rem 0 0; max-width: 64ch; }
.rpt-h .pop { margin-left: auto; flex: none; white-space: nowrap; font-size: .76rem; color: var(--accent);
  text-decoration: none; border: 1px solid var(--rule); background: var(--card);
  padding: .28rem .6rem; border-radius: 4px; }
.rpt-h .pop:hover { border-color: var(--accent); }
.rpt-frame { display: block; width: 100%; height: 70vh; min-height: 26rem; border: 0;
  background: var(--paper); border-radius: 6px; }

h2.sec { font-size: 1.35rem; font-weight: 640; letter-spacing: -.015em; margin: 0 0 1rem;
  padding-top: 1.6rem; border-top: 1px solid var(--rule); }
.finds { display: grid; gap: 1px; background: var(--rule); border: 1px solid var(--rule);
  border-radius: 5px; overflow: hidden; margin: 0 0 3rem; }
.f { background: var(--card); padding: 1.05rem 1.15rem; }
.f h3 { font-size: .95rem; font-weight: 640; margin: 0 0 .35rem; }
.f p { font-size: .82rem; color: var(--ink-2); margin: 0; max-width: 68ch; }
.how { background: var(--card); border: 1px solid var(--rule); border-radius: 5px; padding: 1.15rem 1.25rem; }
.how h3 { font-size: .95rem; font-weight: 640; margin: 0 0 .6rem; }
.how p { font-size: .82rem; color: var(--ink-2); margin: 0 0 .6rem; max-width: 68ch; }
.how code { font-family: var(--mono); font-size: .78rem; background: var(--rule-2);
  padding: .1rem .3rem; border-radius: 3px; }
.how pre { font-family: var(--mono); font-size: .74rem; background: var(--rule-2); color: var(--ink-2);
  padding: .7rem .8rem; border-radius: 4px; overflow-x: auto; margin: 0 0 .6rem; }
.tail { padding-bottom: 6rem; }
footer { margin-top: 3rem; padding-top: 1.3rem; border-top: 1px solid var(--rule);
  font-size: .76rem; color: var(--ink-3); }
footer a { color: var(--accent); }
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
</style>

<div class="wrap hero">
<p class="eyebrow">design-systems-benchmark · 실측</p>
<h1>디자인 시스템에서 표준화할 수 있는 것</h1>
<p class="lede">{{n}}개 컴포넌트 라이브러리의 <b>실제 소스</b>에서 semantic 토큰 {{tok_total}}개와
컴포넌트 인벤토리를 추출해, 어느 개념이 예외 없이 공통이고 어느 개념이 갈리는지 셌다.
공통인 것만이 표준화 가능하다. 아래 리포트는 전부 이 페이지에서 이어진다.</p>
<p class="meta"><b>대상</b> {{systems}} &nbsp;·&nbsp; <b>기준일</b> 2026-07-30 &nbsp;·&nbsp;
<b>소스</b> 고정 커밋 (각 리포트 부록)</p>

<div class="kpis">{{stats}}</div>
</div>

<nav class="topbar"><div class="in">
{{nav}}
<a class="md" href="design-system-standard-research.md">마크다운 원문 ↗</a>
</div></nav>

<main class="reports">
{{sections}}
</main>

<div class="wrap tail">
<h2 class="sec">핵심 발견</h2>
<div class="finds">{{findings}}</div>

<h2 class="sec">어떻게 측정했나</h2>
<div class="how">
<p>추정이 아니라 소스를 읽어 센다. 분석 대상 라이브러리를 매니페스트에 적힌 <b>고정 커밋</b>으로
받고, 측정·분류·렌더를 스크립트로 돌린다. 리포트는 전부 생성물이며 데이터에서 만들어지므로
본문 수치와 차트가 어긋날 수 없다.</p>
<pre>bash sources/clone.sh                      # 고정 커밋으로 소스 확보
python3 analysis/standard-research/run.py  # 측정 → 파생 → 렌더
python3 ... run.py --check                 # 재현성 검사 (출력 == 커밋된 것)</pre>
<p>사전 검사가 소스의 커밋 · 로컬 변경 · sparse 경로를 대조해, 일부만 받은 상태나 변조된
상태로는 측정이 시작되지 않는다. 수기로 확인한 값(<code>curated/</code>)은 스크립트가 덮어쓰지 못한다.</p>
<p><b>한계도 문서에 적혀 있다.</b> Figma Variables API 가 403 이라 MFI 의 토큰 정합성은 계산할 수 없고,
토큰 의존율은 집계 기준에 극도로 민감해 느슨·엄격 두 값을 병기한다.</p>
</div>

<footer>
<p>8/8 컴포넌트: {{comp_std}}</p>
<p>측정 대상은 모두 오픈소스 공개 저장소이며, 각 리포트 부록에 커밋 SHA 와 파일 경로를 남겼다.
생성: <code>python3 analysis/standard-research/run.py</code></p>
</footer>
</div>

<script>
// 같은 오리진 iframe 을 실제 내용 높이로 맞춰 한 페이지처럼 연속 스크롤되게 한다.
// 파일이 추가·교체돼도 iframe.rpt-frame 만 찾으면 되므로 목차를 손볼 필요가 없다.
(function () {
  function fit(f) {
    try {
      var d = f.contentDocument || (f.contentWindow && f.contentWindow.document);
      if (!d || !d.documentElement) return;
      var h = Math.max(d.body ? d.body.scrollHeight : 0, d.documentElement.scrollHeight);
      if (h > 0) f.style.height = h + "px";
    } catch (err) { /* cross-origin 이면 그대로 둔다 */ }
  }
  function watch(f) {
    try {
      var d = f.contentDocument;
      if (!d || typeof ResizeObserver === "undefined") return;
      new ResizeObserver(function () { fit(f); }).observe(d.body || d.documentElement);
    } catch (err) { /* ignore */ }
  }
  var frames = Array.prototype.slice.call(document.querySelectorAll("iframe.rpt-frame"));
  frames.forEach(function (f) {
    f.addEventListener("load", function () { fit(f); watch(f); });
    if (f.contentDocument && f.contentDocument.readyState === "complete") { fit(f); watch(f); }
  });
  window.addEventListener("resize", function () { frames.forEach(fit); });
})();
</script>
"""


if __name__ == "__main__":
    p = paths.write_report(OUT, build())
    print(f"-> {p}  ({p.stat().st_size:,} bytes)")
