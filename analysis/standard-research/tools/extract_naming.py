#!/usr/bin/env python3
"""토큰 *이름의 문법*을 측정한다 — 표기법, 구분자, 접두사, 세그먼트 깊이, 어순.

입력: measured/tokens.json (+ 원본 표기를 위해 sources/)
출력: derived/naming.json

왜 따로 재는가
  커버리지(어떤 개념이 있는가)와 별개로, *같은 개념을 어떤 문법으로 적는가*가 표준화의
  실질 장벽이다. 개념이 8/8로 같아도 어순이 다르면 기계적 변환이 불가능하다.

측정 항목
  case        표기법 — kebab / camel / snake / mixed
  depth       하이픈·대문자 경계로 자른 세그먼트 수의 분포
  order       어순 — 역할(surface/text/border)이 의미(brand/critical)보다 앞에 오는가
  prefix      공통 접두사 유무
"""
import json
import re
from collections import Counter
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402


# 원본 표기(추출 전 형태) — tokens.json 은 kebab 정규화를 거쳤으므로 별도로 기록한다
NATIVE = {
    "Spectrum":     ("kebab", "--spectrum-", "`--spectrum-accent-background-color-default`"),
    "Material Web": ("kebab", "--md-sys-",   "`--md-sys-color-on-primary-container`"),
    "MUI":          ("camel", "theme.",      "`theme.palette.primary.contrastText`"),
    "Fluent 2":     ("camel", "--",          "`--colorNeutralForeground2Hover`"),
    "Carbon":       ("kebab", "$",           "`$button-danger-hover`"),
    "Polaris":      ("kebab", "--p-",        "`--p-color-bg-fill-brand-hover`"),
    "shadcn/ui":    ("kebab", "--",          "`--primary-foreground`"),
    "Ant Design":   ("camel", "token.",      "`token.colorErrorBgHover`"),
}

ROLE_WORDS = {"surface", "background", "bg", "foreground", "fg", "text", "border", "stroke",
              "outline", "icon", "fill", "divider", "split", "container", "layer", "shadow"}
INTENT_WORDS = {"brand", "accent", "primary", "secondary", "tertiary", "critical", "negative",
                "danger", "error", "destructive", "warning", "caution", "success", "positive",
                "info", "informative", "neutral", "subtle", "muted", "subdued", "inverse"}
STATE_WORDS = {"hover", "active", "pressed", "down", "focus", "selected", "checked",
               "disabled", "visited", "loading"}


def segs(name):
    return [s for s in re.split(r"[-_.]", name) if s]


def classify_order(parts):
    """역할·의미·상태 단어가 이름 안에서 몇 번째에 오는지 → 어순 패턴 문자열."""
    seq = []
    for p in parts:
        if p in ROLE_WORDS:
            seq.append("R")
        elif p in INTENT_WORDS:
            seq.append("I")
        elif p in STATE_WORDS:
            seq.append("S")
    # 연속 중복 제거 (color-bg-fill → R 한 번)
    out = []
    for c in seq:
        if not out or out[-1] != c:
            out.append(c)
    return "".join(out)


def main():
    tokens = paths.read_json("tokens")
    result = {}
    for system, info in tokens.items():
        names = info["names"]
        depth = Counter(len(segs(n)) for n in names)
        orders = Counter()
        for n in names:
            o = classify_order(segs(n))
            if len(o) >= 2:
                orders[o] += 1
        native_case, native_prefix, native_sample = NATIVE.get(system, ("?", "?", "?"))
        total_order = sum(orders.values())
        # 상태 단어가 이름 끝에 오는 비율 — 접미사 규약인가
        state_named = [n for n in names if any(s in segs(n) for s in STATE_WORDS)]
        state_suffix = sum(1 for n in state_named if segs(n)[-1] in STATE_WORDS)
        result[system] = {
            "native_case": native_case,
            "native_prefix": native_prefix,
            "native_sample": native_sample,
            "total": len(names),
            "depth_avg": round(sum(k * v for k, v in depth.items()) / max(1, len(names)), 2),
            "depth_max": max(depth) if depth else 0,
            "depth_hist": {str(k): v for k, v in sorted(depth.items())},
            "order_top": [{"pattern": p, "count": c,
                           "pct": round(c / total_order * 100, 1) if total_order else 0}
                          for p, c in orders.most_common(4)],
            "state_tokens": len(state_named),
            "state_suffix_pct": round(state_suffix / len(state_named) * 100, 1) if state_named else None,
        }

    order_legend = {
        "RI": "역할 → 의미 (background-brand)",
        "IR": "의미 → 역할 (brand-background)",
        "RS": "역할 → 상태 (background-hover)",
        "RIS": "역할 → 의미 → 상태 (background-brand-hover)",
        "IRS": "의미 → 역할 → 상태 (brand-background-hover)",
        "IS": "의미 → 상태 (brand-hover)",
        "SR": "상태 → 역할 (hover-background)",
        "SI": "상태 → 의미 (hover-brand)",
        "RIR": "역할 → 의미 → 역할",
        "IRI": "의미 → 역할 → 의미",
    }
    out = {"_note": __doc__.strip().splitlines()[0], "order_legend": order_legend, "systems": result}
    out_path = paths.write_json("naming", out)

    print(f"{'시스템':14s} {'표기':6s} {'접두사':12s} {'깊이(평균/최대)':>14s}  어순 1위")
    for s, d in result.items():
        top = d["order_top"][0] if d["order_top"] else {"pattern": "—", "pct": 0}
        print(f"{s:14s} {d['native_case']:6s} {d['native_prefix']:12s} "
              f"{d['depth_avg']:>7.2f}/{d['depth_max']:<6d} {top['pattern']} ({top['pct']}%)")
    print(f"\n-> {out_path}")


if __name__ == "__main__":
    main()
