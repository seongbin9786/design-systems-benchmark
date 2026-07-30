#!/usr/bin/env python3
"""배포용 목차 페이지를 만든다 — reports/index.html.

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
            a = float(str(d.get("documented_avg")).replace("~", "").replace("%", "").replace("+", ""))
        except (TypeError, ValueError):
            continue
        if abs(d["avg_loose"] - a) >= 20:
            flagged.append(s)

    cards = [
        ("design-system-standard-research.html", "📐", "본문 (시각화)",
         "커버리지 히트맵 · 덤벨 차트 · 100% 누적 막대 등 8종. 무엇이 표준화 가능한지 판정한다.",
         ["토큰 어휘 4축 커버리지", "컴포넌트 교집합", "Button variant 축", "재감사: 의존율 · MFI"]),
        ("design-system-standard-research-visual.html", "📊", "확장판",
         "본문의 상위집합. 이름의 *문법* 까지 파고든다.",
         ["토큰 이름 해부 · 어순 진영", "어휘 밀도 히트맵", "variant 조합 폭발", "분해 단위 · 매칭 근거"]),
        ("design-system-specimens.html", "🎨", "실물 견본",
         "차트가 아니라 실물. 각 시스템의 실제 토큰 값으로 컴포넌트를 렌더링했다.",
         ["Button 32개 나란히", "색 팔레트 80칸", "타이포 · radius · 간격 · elevation", "같은 화면을 8개 시스템으로"]),
        ("design-system-standard-research.md", "📄", "본문 (마크다운)",
         "읽기용 원문. 히트맵은 ●/· 표기.", ["GitHub · 에디터에서 그대로", "표 14개"]),
    ]
    card_html = "".join(
        f'<a class="card" href="{e(href)}"><span class="ico">{ico}</span>'
        f'<h2>{e(title)}</h2><p>{e(desc)}</p>'
        f'<ul>{"".join(f"<li>{e(b)}</li>" for b in bullets)}</ul>'
        f'<span class="go">열기 →</span></a>'
        for href, ico, title, desc, bullets in cards)

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

    return TEMPLATE.replace("{{cards}}", card_html) \
                   .replace("{{stats}}", stat_html) \
                   .replace("{{findings}}", find_html) \
                   .replace("{{n}}", str(n)) \
                   .replace("{{tok_total}}", f"{tok_total:,}") \
                   .replace("{{systems}}", " · ".join(systems)) \
                   .replace("{{comp_std}}", " · ".join(comp_std))


TEMPLATE = """<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>디자인 시스템 표준화 연구 — 8개 시스템 소스 실측</title>
<meta name="description" content="Spectrum · Material · MUI · Fluent 2 · Carbon · Polaris · shadcn/ui · Ant Design 의 실제 소스에서 토큰과 컴포넌트를 세어 무엇이 표준화 가능한지 판정한 리포트.">
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
body { margin: 0; background: var(--paper); color: var(--ink); font-family: var(--sans);
  font-size: clamp(.9rem,.87rem + .15vw,.95rem); line-height: 1.65; -webkit-font-smoothing: antialiased; }
.wrap { max-width: 62rem; margin: 0 auto; padding: 4rem 1.5rem 6rem; }
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
h2.sec { font-size: 1.35rem; font-weight: 640; letter-spacing: -.015em; margin: 0 0 1rem;
  padding-top: 1.6rem; border-top: 1px solid var(--rule); }
.cards { display: grid; grid-template-columns: repeat(auto-fit,minmax(17rem,1fr)); gap: 1rem; margin: 0 0 3rem; }
.card { display: flex; flex-direction: column; background: var(--card); border: 1px solid var(--rule);
  border-radius: 6px; padding: 1.2rem 1.25rem 1.1rem; text-decoration: none; color: inherit;
  transition: border-color .12s, transform .12s; }
.card:hover { border-color: var(--accent); transform: translateY(-2px); }
.card:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.card .ico { font-size: 1.5rem; line-height: 1; }
.card h2 { font-size: 1.05rem; font-weight: 640; margin: .55rem 0 .35rem; }
.card p { font-size: .82rem; color: var(--ink-2); margin: 0 0 .7rem; }
.card ul { list-style: none; margin: 0 0 .9rem; padding: 0; }
.card li { font-size: .76rem; color: var(--ink-3); padding-left: .8rem; position: relative; line-height: 1.6; }
.card li::before { content: "·"; position: absolute; left: .15rem; color: var(--accent); }
.card .go { margin-top: auto; font-size: .78rem; color: var(--accent); font-weight: 600; }
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
footer { margin-top: 3rem; padding-top: 1.3rem; border-top: 1px solid var(--rule);
  font-size: .76rem; color: var(--ink-3); }
footer a { color: var(--accent); }
@media (prefers-reduced-motion: reduce) { .card { transition: none; } }
</style>

<div class="wrap">
<p class="eyebrow">design-systems-benchmark · 실측</p>
<h1>디자인 시스템에서 표준화할 수 있는 것</h1>
<p class="lede">{{n}}개 컴포넌트 라이브러리의 <b>실제 소스</b>에서 semantic 토큰 {{tok_total}}개와
컴포넌트 인벤토리를 추출해, 어느 개념이 예외 없이 공통이고 어느 개념이 갈리는지 셌다.
공통인 것만이 표준화 가능하다.</p>
<p class="meta"><b>대상</b> {{systems}} &nbsp;·&nbsp; <b>기준일</b> 2026-07-30 &nbsp;·&nbsp;
<b>소스</b> 고정 커밋 (각 리포트 부록)</p>

<div class="kpis">{{stats}}</div>

<h2 class="sec">리포트</h2>
<div class="cards">{{cards}}</div>

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
"""


if __name__ == "__main__":
    p = paths.write_report(OUT, build())
    print(f"-> {p}  ({p.stat().st_size:,} bytes)")
