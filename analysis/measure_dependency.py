#!/usr/bin/env python3
"""컴포넌트 4종(Button/Checkbox/Dialog/TextInput)의 토큰 의존율을 현재 소스에서 재측정한다.

목적: comparison/dependency-audit-summary.md (기준일 2026-07-26) 의 결론이 지금도 성립하는지 확인.

집계 규칙 — 원 감사와 같은 정의를 쓴다
    토큰 의존율 = 토큰 참조 / (토큰 참조 + hardcoded 값) × 100
  토큰 참조:   var(--...), $sass-var, token.x, tokens.x, theme.x, map.get(...), Tailwind 토큰 클래스
  hardcoded:  토큰을 경유하지 않는 raw 치수(px/rem/em/%/vh/vw/deg/ms/s), hex, rgb(a)

⚠️ 한계 (원 감사와 동일)
- 시스템마다 스타일 표현 단위가 달라 절대 수치는 비교할 수 없다. 패턴만 비교한다.
- mixin/함수 내부에서 발생하는 참조는 세지 않는다 (해당 파일에 직접 나타난 것만).
- 4개 컴포넌트(Button/Checkbox/Dialog/TextInput)만 본다. 원 감사는 10개 — 범위가 다르다.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources"
DATA = ROOT / "analysis" / "data"

# component -> {system: (경로, 표기 방식)}
TARGETS = {
 "Button": {
    "Spectrum":     ("spectrum-css/components/button/index.css", "css"),
    "Material Web": ("material-web/button/internal/_filled-button.scss", "scss"),
    "MUI":          ("material-ui/packages/mui-material/src/Button/Button.js", "js"),
    "Fluent 2":     ("fluentui/packages/react-components/react-button/library/src/components/Button/useButtonStyles.styles.ts", "ts"),
    "Carbon":       ("carbon/packages/styles/scss/components/button/_button.scss", "scss"),
    "Polaris":      ("polaris/polaris-react/src/components/Button/Button.module.css", "css"),
    "shadcn/ui":    ("shadcn-ui/apps/v4/registry/new-york-v4/ui/button.tsx", "tailwind"),
    "Ant Design":   ("ant-design/components/button/style/index.ts", "ts"),
 },
 "Checkbox": {
    "Spectrum":     ("spectrum-css/components/checkbox/index.css", "css"),
    "Material Web": ("material-web/checkbox/internal/_checkbox.scss", "scss"),
    "MUI":          ("material-ui/packages/mui-material/src/Checkbox/Checkbox.js", "js"),
    "Fluent 2":     ("fluentui/packages/react-components/react-checkbox/library/src/components/Checkbox/useCheckboxStyles.styles.ts", "ts"),
    "Carbon":       ("carbon/packages/styles/scss/components/checkbox/_checkbox.scss", "scss"),
    "Polaris":      ("polaris/polaris-react/src/components/Checkbox/Checkbox.module.css", "css"),
    "shadcn/ui":    ("shadcn-ui/apps/v4/registry/new-york-v4/ui/checkbox.tsx", "tailwind"),
    "Ant Design":   ("ant-design/components/checkbox/style/index.ts", "ts"),
 },
 "Dialog": {
    "Spectrum":     ("spectrum-css/components/dialog/index.css", "css"),
    "Material Web": ("material-web/dialog/internal/_dialog.scss", "scss"),
    "MUI":          ("material-ui/packages/mui-material/src/Dialog/Dialog.js", "js"),
    "Fluent 2":     ("fluentui/packages/react-components/react-dialog/library/src/components/DialogSurface/useDialogSurfaceStyles.styles.ts", "ts"),
    "Carbon":       ("carbon/packages/styles/scss/components/modal/_modal.scss", "scss"),
    "Polaris":      ("polaris/polaris-react/src/components/Modal/Modal.module.css", "css"),
    "shadcn/ui":    ("shadcn-ui/apps/v4/registry/new-york-v4/ui/dialog.tsx", "tailwind"),
    "Ant Design":   ("ant-design/components/modal/style/index.ts", "ts"),
 },
 "TextInput": {
    "Spectrum":     ("spectrum-css/components/textfield/index.css", "css"),
    "Material Web": ("material-web/textfield/internal/_filled-text-field.scss", "scss"),
    "MUI":          ("material-ui/packages/mui-material/src/TextField/TextField.js", "js"),
    "Fluent 2":     ("fluentui/packages/react-components/react-input/library/src/components/Input/useInputStyles.styles.ts", "ts"),
    "Carbon":       ("carbon/packages/styles/scss/components/text-input/_text-input.scss", "scss"),
    "Polaris":      ("polaris/polaris-react/src/components/TextField/TextField.module.css", "css"),
    "shadcn/ui":    ("shadcn-ui/apps/v4/registry/new-york-v4/ui/input.tsx", "tailwind"),
    "Ant Design":   ("ant-design/components/input/style/index.ts", "ts"),
 },
}

# 원 감사가 보고한 시스템 평균 의존율 (comparison/dependency-audit-summary.md, 2026-07-26)
DOCUMENTED_AVG = {
    "Spectrum": "98.9%", "Material Web": "~95%+", "MUI": "~70%", "Fluent 2": "~83%",
    "Carbon": "~50%", "Polaris": "~53%", "shadcn/ui": "18.5%", "Ant Design": "~82%",
}

# 토큰이 아닌 Sass/JS 변수 — 세면 안 된다.
# Carbon 의 `$prefix` 는 CSS 클래스 접두사(`.#{$prefix}--btn`)로 한 파일에 100회 이상 나온다.
# 이걸 토큰 참조로 세면 의존율이 통째로 부풀어 오른다.
NON_TOKEN_VARS = re.compile(
    r"\$(prefix|css--[\w-]+|self|this|i|j|k|n|key|value|args|rest|map|list|"
    r"name|type|state|size|kind|el|elem|selector|start|end|from|to)\b"
)

TOKEN_PATTERNS = {
    "css":      [r"var\(--[\w-]+"],
    "scss":     [r"\$[\w-]+", r"var\(--[\w-]+", r"map\.get\(", r"custom-property\.get-var\(",
                 r"layout\.(size|density)\(", r"\bz\("],
    "js":       [r"\btheme\.(palette|typography|shape|spacing|shadows|transitions|zIndex)\b",
                 r"\(theme\.vars \|\| theme\)\.", r"theme\.vars\."],
    "ts":       [r"\btokens\.\w+", r"\btoken\.\w+", r"var\(--[\w-]+"],
    # Tailwind: 토큰(테마 스케일)을 참조하는 유틸리티 클래스
    "tailwind": [r"\b(bg|text|border|ring|outline|fill|stroke|shadow|from|to|via)-"
                 r"(background|foreground|primary|secondary|accent|muted|destructive|card|popover|"
                 r"input|border|ring|sidebar|chart)[\w/-]*",
                 r"\b(rounded|gap|p|px|py|pt|pb|pl|pr|m|mx|my|size|w|h|text)-"
                 r"(xs|sm|md|lg|xl|2xl|3xl|full|none|\d+(\.\d+)?)\b"],
}

# ── 느슨한(loose) 기준 vs 엄격한(strict) 기준 ──────────────────────────────────
# 같은 파일이 기준에 따라 2배 차이가 난다. 예: Polaris Button.module.css 는 대부분
# `var(--pc-button-*)` — 이건 *컴포넌트 로컬 변수*이고 그 값이 다시 `var(--p-*)`
# (진짜 디자인 토큰)를 가리킨다. 로컬 변수를 토큰으로 세면 99%, 안 세면 절반 수준.
# 어느 쪽이 맞다기보다, 기준을 밝히지 않은 수치는 비교 불가라는 뜻이다.
LOCAL_INDIRECTION = {
    "Polaris": [r"var\(--pc-[\w-]+"],          # --pc-* = 컴포넌트 로컬
    "Spectrum": [r"var\(--mod-[\w-]+"],        # --mod-* = 오버라이드 훅
}
# strict 기준에서 토큰으로 인정할 패턴 (Tailwind 는 의미 색상 클래스만)
STRICT_TOKEN = {
    "tailwind": [r"\b(bg|text|border|ring|outline|fill|stroke|shadow)-"
                 r"(background|foreground|primary|secondary|accent|muted|destructive|card|popover|"
                 r"input|border|ring|sidebar|chart)[\w/-]*"],
}

HARD_PATTERNS = [
    r"(?<![\w.-])\d+(?:\.\d+)?(?:px|rem|em|%|vh|vw|deg|ms|s)\b",
    r"#[0-9a-fA-F]{3,8}\b",
    r"\brgba?\(",
]
# Tailwind 의 hardcoded = arbitrary value 대괄호 표기
HARD_TAILWIND = [r"\[[^\]]*?(#[0-9a-fA-F]{3,8}|\d+(?:\.\d+)?(px|rem|em|%|vh|vw))[^\]]*?\]"]

STRIP_COMMENTS = [
    (r"/\*.*?\*/", re.S),   # /* */
    (r"^\s*//.*$", re.M),   # //
]


def strip_comments(txt):
    for pat, flags in STRIP_COMMENTS:
        txt = re.sub(pat, " ", txt, flags=flags)
    return txt


def main():
    rows = []
    for comp, per_sys in TARGETS.items():
        for system, (rel, mode) in per_sys.items():
            p = SRC / rel
            if not p.exists():
                rows.append({"component": comp, "system": system, "error": f"경로 없음: {rel}"})
                continue
            txt = strip_comments(p.read_text(encoding="utf-8", errors="replace"))

            refs = sum(len(re.findall(pat, txt)) for pat in TOKEN_PATTERNS[mode])
            refs -= len(NON_TOKEN_VARS.findall(txt))
            hard_pats = HARD_TAILWIND if mode == "tailwind" else HARD_PATTERNS
            hard = sum(len(re.findall(pat, txt)) for pat in hard_pats)
            local = sum(len(re.findall(pat, txt)) for pat in LOCAL_INDIRECTION.get(system, []))
            refs_strict = (sum(len(re.findall(pat, txt)) for pat in STRICT_TOKEN[mode])
                           if mode in STRICT_TOKEN else refs - local)

            total, total_s = refs + hard, refs_strict + hard
            rows.append({
                "component": comp, "system": system, "file": rel, "mode": mode,
                "bytes": p.stat().st_size,
                "token_refs": refs, "token_refs_strict": refs_strict,
                "local_indirection": local, "hardcoded": hard,
                "dependency_pct": round(refs / total * 100, 1) if total else None,
                "dependency_pct_strict": round(refs_strict / total_s * 100, 1) if total_s else None,
                # 0/0 = 그 파일에 스타일 선언이 없다는 뜻 (MUI TextField 는 하위 Input 으로 위임)
                "note": None if total else "스타일 선언 없음 — 하위 컴포넌트로 위임",
            })

    # 시스템별 평균 (측정 성공한 컴포넌트만)
    by_sys = {}
    for r in rows:
        if "error" in r or r["dependency_pct"] is None:
            continue
        by_sys.setdefault(r["system"], []).append(r)
    summary = {}
    for sysname, rs in by_sys.items():
        loose = [r["dependency_pct"] for r in rs]
        strict = [r["dependency_pct_strict"] for r in rs if r["dependency_pct_strict"] is not None]
        summary[sysname] = {
            "components_measured": len(rs),
            "avg_loose": round(sum(loose) / len(loose), 1),
            "avg_strict": round(sum(strict) / len(strict), 1) if strict else None,
            "range_loose": [min(loose), max(loose)],
            "documented_avg": DOCUMENTED_AVG.get(sysname),
        }

    out = {"_note": __doc__.strip().splitlines()[0],
           "_rule": "토큰 의존율 = 토큰 참조 / (토큰 참조 + hardcoded) × 100",
           "_caveat": "시스템 간 절대 수치 비교 불가 — 표현 단위가 다름. 패턴만 비교.",
           "summary": summary, "rows": rows}
    (DATA / "dependency.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))

    print(f"{'시스템':14s} {'측정':>4s} {'느슨평균':>8s} {'엄격평균':>8s} {'범위(느슨)':>14s} {'문서평균':>8s}")
    for sysname, d in sorted(summary.items(), key=lambda kv: -kv[1]["avg_loose"]):
        doc = f"{d['documented_avg']}" if d["documented_avg"] else "-"
        st = f"{d['avg_strict']:.1f}%" if d["avg_strict"] is not None else "-"
        rg = f"{d['range_loose'][0]:.0f}~{d['range_loose'][1]:.0f}%"
        print(f"{sysname:14s} {d['components_measured']:4d} {d['avg_loose']:7.1f}% {st:>8s} {rg:>14s} {doc:>8s}")
    errs = [r for r in rows if "error" in r]
    if errs:
        print("\n측정 실패:")
        for r in errs:
            print(f"  {r['system']:14s} {r['component']:10s} {r['error']}")
    print(f"\n-> {DATA / 'dependency.json'}")


if __name__ == "__main__":
    main()
