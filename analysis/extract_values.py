#!/usr/bin/env python3
"""토큰의 *값*을 추출한다 — 이름이 아니라 실제 색·크기. 실물 컴포넌트를 그리기 위한 재료.

입력: sources/<repo>/...
출력: analysis/data/values.json

앞선 스크립트들은 이름만 봤다. 실물을 렌더링하려면 값이 필요하다.
각 시스템의 alias 체인을 원시 팔레트까지 따라가 hex/oklch 로 해석한다.

수집 항목 (시스템별)
  palette  semantic 색 8~10칸 — surface / text / border / brand / danger …
  type     타이포 스케일 (size · weight · line-height)
  radius   corner radius 스케일
  space    간격 스케일
  shadow   elevation 스케일
  button   Button 지오메트리 + variant 별 색 (실제 렌더링용)

⚠️ button 지오메트리는 소스를 읽어 확인한 값이다 (mixin·유틸리티 클래스를 거치므로 자동 추출 불가).
   근거 경로를 evidence 에 남긴다. 색은 위 palette 와 같은 해석기를 통과한 값이다.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "sources"
OUT = ROOT / "analysis" / "data"

# 우리가 그릴 정규 슬롯 — 8개 시스템에서 같은 자리를 찾아 채운다
SLOTS = ["surface", "surface-raised", "text-primary", "text-secondary", "border",
         "brand-bg", "brand-fg", "danger-bg", "success-bg", "warning-bg"]


def txt(rel):
    p = SRC / rel
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def _num(s):
    m = re.match(r"\d+", str(s))
    return int(m.group(0)) if m else 10 ** 6


def js_consts(source, pattern=r"export const (\w+)\s*=\s*'([^']+)'"):
    return dict(re.findall(pattern, source))


# ─────────────────────────────────────────────────────────── Carbon
def carbon():
    prim = js_consts(txt("carbon/packages/colors/src/colors.ts"))  # gray10 -> #f4f4f4
    theme = json.loads(txt("carbon/packages/themes/src/dtcg/white.json") or "{}")

    def leaf(*path):
        node = theme
        for p in path:
            node = node.get(p, {}) if isinstance(node, dict) else {}
        return node.get("$value") if isinstance(node, dict) else None

    def resolve(v):
        """`{gray.100}` / `{white.default}` → hex"""
        if not isinstance(v, str):
            return None
        m = re.fullmatch(r"\{(\w+)\.(\w+)\}", v)
        if not m:
            return v if v.startswith("#") else None
        fam, step = m.group(1), m.group(2)
        if fam == "white":
            return "#ffffff"
        if fam == "black":
            return "#000000"
        return prim.get(f"{fam}{step}") or prim.get(f"{fam}{step.replace('Hover', '')}")

    # 버튼 색은 테마 파일이 아니라 dtcg/components/button.json 에 있고,
    # 값이 $extensions["carbon.themes"]["white"] 아래 테마별로 들어 있다.
    bt = json.loads(txt("carbon/packages/themes/src/dtcg/components/button.json") or "{}")

    def btn(key):
        node = bt.get("button", {}).get(key, {})
        ext = node.get("$extensions", {}).get("carbon.themes", {})
        return resolve(ext.get("white"))

    pal = {
        "surface": resolve(leaf("background")),
        "surface-raised": resolve(leaf("layer", "01")) or resolve(leaf("layer-01")),
        "text-primary": resolve(leaf("text", "primary")),
        "text-secondary": resolve(leaf("text", "secondary")),
        "border": resolve(leaf("border", "subtle-01")),
        "brand-bg": btn("primary") or resolve(leaf("background-brand")),
        "brand-fg": resolve(leaf("text", "on-color")),
        "danger-bg": btn("danger-primary") or resolve(leaf("support", "error")),
        "success-bg": resolve(leaf("support", "success")),
        "warning-bg": resolve(leaf("support", "warning")),
    }
    # 타이포: type/src/styles.ts 의 리터럴
    # 타이포: styles.ts 의 fontSize 는 `rem(scale[N])` — scale 배열(px)을 따라가야 값이 나온다
    scale_src = txt("carbon/packages/type/src/scale.ts")
    sm = re.search(r"export const scale = \[(.*?)\];", scale_src, re.S)
    scale = [int(x) for x in re.findall(r"\d+", sm.group(1))] if sm else []
    ts = txt("carbon/packages/type/src/styles.ts")
    ty = []
    for m in re.finditer(r"export const (\w+) = \{(.*?)\n\};", ts, re.S):
        body = m.group(2)
        idx = re.search(r"fontSize:\s*rem\(scale\[(\d+)\]\)", body)
        lit = re.search(r"fontSize:\s*'([^']+)'", body)
        fw = re.search(r"fontWeight:\s*fontWeights\.(\w+)", body)
        lh = re.search(r"lineHeight:\s*([\d.]+)", body)
        size = None
        if idx and int(idx.group(1)) < len(scale):
            size = f"{scale[int(idx.group(1))]}px"
        elif lit:
            size = lit.group(1)
        if size:
            ty.append({"name": m.group(1), "size": size,
                       "weight": {"regular": 400, "semibold": 600, "light": 300}.get(
                           fw.group(1) if fw else "", 400),
                       "line_height": lh.group(1) if lh else None})
    return {
        "palette": pal, "type": ty[:8],
        # Carbon 은 radius 토큰이 없다 — 각진 형태를 부재로 강제한다 (앞선 측정에서 확인)
        "radius": [{"name": "(없음)", "value": "0px"}],
        "space": [{"name": f"spacing-{i:02d}", "value": v} for i, v in enumerate(
            ["0.125rem", "0.25rem", "0.5rem", "0.75rem", "1rem", "1.5rem", "2rem", "2.5rem"], 1)],
        "shadow": [{"name": "overlay", "value": "0 0 0 rgba(0,0,0,0)"}],
        "button": {
            "evidence": "carbon/packages/styles/scss/components/button/_button.scss",
            "height": "48px", "padding": "0 63px 0 15px", "radius": "0",
            "font_size": "14px", "font_weight": 400, "border_width": "1px",
            "variants": [
                {"label": "Primary", "bg": pal["brand-bg"], "fg": pal["brand-fg"], "border": "transparent"},
                {"label": "Secondary", "bg": btn("secondary"), "fg": pal["brand-fg"],
                 "border": "transparent"},
                {"label": "Tertiary", "bg": "transparent", "fg": btn("tertiary"),
                 "border": btn("tertiary")},
                {"label": "Danger", "bg": pal["danger-bg"], "fg": pal["brand-fg"], "border": "transparent"},
            ],
        },
    }


# ─────────────────────────────────────────────────────────── shadcn/ui
def shadcn():
    css = txt("shadcn-ui/apps/v4/app/globals.css")
    root = re.search(r":root\s*\{(.*?)\n\}", css, re.S)
    v = dict(re.findall(r"--([a-z0-9-]+):\s*([^;]+);", root.group(1))) if root else {}
    pal = {
        "surface": v.get("background"), "surface-raised": v.get("card"),
        "text-primary": v.get("foreground"), "text-secondary": v.get("muted-foreground"),
        "border": v.get("border"), "brand-bg": v.get("primary"),
        "brand-fg": v.get("primary-foreground"), "danger-bg": v.get("destructive"),
        "success-bg": None, "warning-bg": None,
    }
    return {
        "palette": pal,
        # Tailwind 기본 스케일을 쓴다 — 자체 타이포 토큰이 없다
        "type": [{"name": n, "size": s, "weight": 400, "line_height": lh} for n, s, lh in [
            ("text-xs", "0.75rem", "1rem"), ("text-sm", "0.875rem", "1.25rem"),
            ("text-base", "1rem", "1.5rem"), ("text-lg", "1.125rem", "1.75rem"),
            ("text-xl", "1.25rem", "1.75rem"), ("text-2xl", "1.5rem", "2rem")]],
        "radius": [{"name": n, "value": f"calc({v.get('radius', '0.625rem')} {o})"} for n, o in [
            ("--radius-sm", "- 4px"), ("--radius-md", "- 2px"), ("--radius-lg", "+ 0px"),
            ("--radius-xl", "+ 4px")]],
        "space": [{"name": f"p-{i}", "value": f"{i * 0.25}rem"} for i in (1, 2, 3, 4, 6, 8, 10, 12)],
        "shadow": [{"name": "shadow-xs", "value": "0 1px 2px 0 rgb(0 0 0 / 0.05)"},
                   {"name": "shadow-sm", "value": "0 1px 3px 0 rgb(0 0 0 / 0.1)"},
                   {"name": "shadow-md", "value": "0 4px 6px -1px rgb(0 0 0 / 0.1)"}],
        "button": {
            "evidence": "shadcn-ui/apps/v4/registry/new-york-v4/ui/button.tsx (cva)",
            "height": "36px", "padding": "0 16px", "radius": "calc(0.625rem - 2px)",
            "font_size": "0.875rem", "font_weight": 500, "border_width": "1px",
            "variants": [
                {"label": "default", "bg": pal["brand-bg"], "fg": pal["brand-fg"], "border": "transparent"},
                {"label": "secondary", "bg": v.get("secondary"), "fg": v.get("secondary-foreground"),
                 "border": "transparent"},
                {"label": "outline", "bg": v.get("background"), "fg": v.get("foreground"),
                 "border": v.get("border")},
                {"label": "destructive", "bg": pal["danger-bg"], "fg": v.get("destructive-foreground"),
                 "border": "transparent"},
            ],
        },
    }


# ─────────────────────────────────────────────────────────── Fluent 2
def fluent():
    grey = dict(re.findall(r"\b(\d+):\s*'?`?(#[0-9a-fA-F]{6})", txt("fluentui/packages/tokens/src/global/colors.ts")))
    brand_src = txt("fluentui/packages/tokens/src/global/brandColors.ts")
    first = brand_src.split("export const", 2)
    brand = dict(re.findall(r"\b(\d+):\s*`?(#[0-9a-fA-F]{6})", first[1] if len(first) > 1 else brand_src))
    light = txt("fluentui/packages/tokens/src/alias/lightColor.ts")

    def alias(key):
        m = re.search(rf"^\s+{re.escape(key)}:\s*([^,]+),\s*(?://\s*(#[0-9a-fA-F]{{6}}))?", light, re.M)
        if not m:
            return None
        if m.group(2):
            return m.group(2)
        expr = m.group(1).strip()
        if expr == "white":
            return "#ffffff"
        if expr == "black":
            return "#000000"
        g = re.fullmatch(r"(grey|brand)\[(\d+)\]", expr)
        if g:
            return (grey if g.group(1) == "grey" else brand).get(g.group(2))
        return None

    pal = {
        "surface": alias("colorNeutralBackground1"),
        "surface-raised": alias("colorNeutralBackground2"),
        "text-primary": alias("colorNeutralForeground1"),
        "text-secondary": alias("colorNeutralForeground2"),
        "border": alias("colorNeutralStroke1"),
        "brand-bg": alias("colorBrandBackground"),
        "brand-fg": alias("colorNeutralForegroundOnBrand"),
        "danger-bg": alias("colorPaletteRedBackground3") or "#c50f1f",
        "success-bg": alias("colorPaletteGreenBackground3") or "#107c10",
        "warning-bg": alias("colorPaletteYellowBackground3") or "#fde300",
    }
    fonts = txt("fluentui/packages/tokens/src/global/fonts.ts")
    fs = dict(re.findall(r"(fontSizeBase\d+):\s*'([^']+)'", fonts))
    lh = dict(re.findall(r"(lineHeightBase\d+):\s*'([^']+)'", fonts))
    br = dict(re.findall(r"(borderRadius\w+):\s*'([^']+)'", txt("fluentui/packages/tokens/src/global/borderRadius.ts")))
    sp = dict(re.findall(r"\b(\w+):\s*'([\d.]+px)'", txt("fluentui/packages/tokens/src/global/spacings.ts")))
    return {
        "palette": pal,
        "type": [{"name": k, "size": v, "weight": 400, "line_height": lh.get(k.replace("fontSize", "lineHeight"))}
                 for k, v in sorted(fs.items())][:8],
        "radius": [{"name": k, "value": v} for k, v in br.items()][:6],
        "space": [{"name": k, "value": v} for k, v in list(sp.items())[:8]],
        "shadow": [{"name": "shadow4", "value": "0 2px 4px rgba(0,0,0,.14), 0 0 2px rgba(0,0,0,.12)"},
                   {"name": "shadow8", "value": "0 4px 8px rgba(0,0,0,.14), 0 0 2px rgba(0,0,0,.12)"},
                   {"name": "shadow16", "value": "0 8px 16px rgba(0,0,0,.14), 0 0 2px rgba(0,0,0,.12)"}],
        "button": {
            "evidence": "fluentui/.../react-button/library/src/components/Button/useButtonStyles.styles.ts",
            "height": "32px", "padding": "0 12px", "radius": br.get("borderRadiusMedium", "4px"),
            "font_size": fs.get("fontSizeBase300", "14px"), "font_weight": 600, "border_width": "1px",
            "variants": [
                {"label": "primary", "bg": pal["brand-bg"], "fg": pal["brand-fg"], "border": "transparent"},
                {"label": "secondary", "bg": pal["surface"], "fg": pal["text-primary"], "border": pal["border"]},
                {"label": "outline", "bg": "transparent", "fg": pal["text-primary"], "border": pal["border"]},
                {"label": "subtle", "bg": "transparent", "fg": pal["text-primary"], "border": "transparent"},
            ],
        },
    }


# ─────────────────────────────────────────────────────────── Spectrum
def spectrum():
    base = SRC / "spectrum-tokens/packages/tokens/src"
    store = {}
    for f in ["color-palette.json", "color-aliases.json", "semantic-color-palette.json"]:
        p = base / f
        if p.exists():
            store.update(json.loads(p.read_text()))

    def val(name, depth=0):
        if depth > 6 or name not in store:
            return None
        node = store[name]
        v = node.get("sets", {}).get("light", {}).get("value") if "sets" in node else node.get("value")
        if not isinstance(v, str):
            return None
        m = re.fullmatch(r"\{([^}]+)\}", v)
        return val(m.group(1), depth + 1) if m else v

    pal = {
        "surface": val("background-base-color") or "#ffffff",
        "surface-raised": val("background-layer-2-color"),
        "text-primary": val("neutral-content-color-default"),
        "text-secondary": val("neutral-subdued-content-color-default"),
        "border": val("gray-300"),
        "brand-bg": val("accent-background-color-default"),
        "brand-fg": "#ffffff",
        "danger-bg": val("negative-background-color-default"),
        "success-bg": val("positive-background-color-default"),
        "warning-bg": val("notice-background-color-default"),
    }
    ty = json.loads((base / "typography.json").read_text()) if (base / "typography.json").exists() else {}

    def tval(name):
        n = ty.get(name, {})
        v = n.get("sets", {}).get("desktop", {}).get("value") or n.get("value")
        return v if isinstance(v, str) else None

    return {
        "palette": pal,
        "type": [{"name": k, "size": tval(k), "weight": 400, "line_height": None}
                 for k in ["font-size-50", "font-size-75", "font-size-100", "font-size-200",
                           "font-size-300", "font-size-400"] if tval(k)],
        "radius": [{"name": k, "value": v} for k, v in [
            ("corner-radius-75", "2px"), ("corner-radius-100", "4px"),
            ("corner-radius-200", "8px"), ("corner-radius-full", "999px")]],
        "space": [{"name": f"spacing-{n}", "value": v} for n, v in [
            ("50", "2px"), ("75", "4px"), ("100", "8px"), ("200", "12px"),
            ("300", "16px"), ("400", "24px"), ("500", "32px"), ("600", "40px")]],
        "shadow": [{"name": "drop-shadow-emphasized", "value": "0 1px 4px rgba(0,0,0,.15)"},
                   {"name": "drop-shadow-elevated", "value": "0 2px 8px rgba(0,0,0,.15)"}],
        "button": {
            "evidence": "spectrum-css/components/button/index.css · react-spectrum s2/src/Button.tsx",
            "height": "32px", "padding": "0 18px", "radius": "16px",
            "font_size": "14px", "font_weight": 700, "border_width": "2px",
            "variants": [
                {"label": "accent · fill", "bg": pal["brand-bg"], "fg": "#ffffff", "border": "transparent"},
                {"label": "primary · fill", "bg": val("neutral-background-color-default") or "#292929",
                 "fg": "#ffffff", "border": "transparent"},
                {"label": "primary · outline", "bg": "transparent", "fg": pal["text-primary"],
                 "border": pal["text-primary"]},
                {"label": "negative · fill", "bg": pal["danger-bg"], "fg": "#ffffff", "border": "transparent"},
            ],
        },
    }


# ─────────────────────────────────────────────────────────── Material Web
def material_web():
    ref = txt("material-web/tokens/versions/v0_192/_md-ref-palette.scss")
    prim = dict(re.findall(r"'([\w-]+)':\s*if\(\$exclude-hardcoded-values,\s*null,\s*(#[0-9a-fA-F]{3,8})", ref))
    sysc = txt("material-web/tokens/versions/v0_192/_md-sys-color.scss")
    # 라이트 스킴 블록만 (light 정의가 파일 후반부)
    light_block = sysc.split("@function values-light")[-1]
    mapping = dict(re.findall(r"'([\w-]+)':\s*map\.get\(\$deps,\s*'md-ref-palette',\s*'([\w-]+)'\)", light_block))

    def sysv(k):
        return prim.get(mapping.get(k, ""), None)

    pal = {
        "surface": sysv("surface") or "#fef7ff",
        "surface-raised": sysv("surface-container") or sysv("surface-variant"),
        "text-primary": sysv("on-surface"),
        "text-secondary": sysv("on-surface-variant"),
        "border": sysv("outline"),
        "brand-bg": sysv("primary"),
        "brand-fg": sysv("on-primary"),
        "danger-bg": sysv("error"),
        "success-bg": None, "warning-bg": None,
    }
    tsc = txt("material-web/tokens/versions/v0_192/_md-sys-typescale.scss")
    ty = []
    for name in ["label-small", "label-large", "body-medium", "body-large",
                 "title-medium", "headline-small"]:
        sz = re.search(rf"'{name}-size':\s*if\(\$exclude-hardcoded-values,\s*null,\s*([\d.]+(?:px|rem))", tsc)
        wt = re.search(rf"'{name}-weight':\s*if\(\$exclude-hardcoded-values,\s*null,\s*(\d+)", tsc)
        lh = re.search(rf"'{name}-line-height':\s*if\(\$exclude-hardcoded-values,\s*null,\s*([\d.]+(?:px|rem))", tsc)
        if sz:
            ty.append({"name": name, "size": sz.group(1),
                       "weight": int(wt.group(1)) if wt else 400,
                       "line_height": lh.group(1) if lh else None})
    return {
        "palette": pal, "type": ty,
        "radius": [{"name": k, "value": v} for k, v in [
            ("shape-corner-extra-small", "4px"), ("shape-corner-small", "8px"),
            ("shape-corner-medium", "12px"), ("shape-corner-large", "16px"),
            ("shape-corner-full", "999px")]],
        "space": [{"name": "(토큰 없음)", "value": "—"}],
        "shadow": [{"name": f"elevation-level{i}", "value": v} for i, v in enumerate([
            "none", "0 1px 2px rgba(0,0,0,.3), 0 1px 3px 1px rgba(0,0,0,.15)",
            "0 1px 2px rgba(0,0,0,.3), 0 2px 6px 2px rgba(0,0,0,.15)",
            "0 4px 8px 3px rgba(0,0,0,.15), 0 1px 3px rgba(0,0,0,.3)"])],
        "button": {
            "evidence": "material-web/button/internal/_filled-button.scss · _shared.scss",
            "height": "40px", "padding": "0 24px", "radius": "999px",
            "font_size": "0.875rem", "font_weight": 500, "border_width": "1px",
            "variants": [
                {"label": "filled", "bg": pal["brand-bg"], "fg": pal["brand-fg"], "border": "transparent"},
                {"label": "filled-tonal", "bg": sysv("secondary-container"),
                 "fg": sysv("on-secondary-container"), "border": "transparent"},
                {"label": "outlined", "bg": "transparent", "fg": pal["brand-bg"], "border": pal["border"]},
                {"label": "text", "bg": "transparent", "fg": pal["brand-bg"], "border": "transparent"},
            ],
        },
    }


# ─────────────────────────────────────────────────────────── MUI
def mui():
    src = txt("material-ui/packages/mui-material/src/styles/createPalette.js")
    colors = {}
    for fam in ["blue", "purple", "red", "orange", "green", "grey", "lightBlue"]:
        c = txt(f"material-ui/packages/mui-material/src/colors/{fam}.js")
        colors[fam] = dict(re.findall(r"(\w+):\s*'(#[0-9a-fA-F]{3,8})'", c))

    def ref(expr):
        m = re.fullmatch(r"(\w+)\[(\w+)\]", expr.strip())
        return colors.get(m.group(1), {}).get(m.group(2)) if m else None

    def default_of(fn, key="main"):
        blk = re.search(rf"function getDefault{fn}\(mode.*?\{{(.*?)\n\}}", src, re.S)
        if not blk:
            return None
        light = blk.group(1).split("return")[-1]
        m = re.search(rf"{key}:\s*([\w\[\]']+)", light)
        return ref(m.group(1)) if m else None

    pal = {
        "surface": "#ffffff", "surface-raised": "#ffffff",
        "text-primary": "rgba(0, 0, 0, 0.87)", "text-secondary": "rgba(0, 0, 0, 0.6)",
        "border": "rgba(0, 0, 0, 0.12)",
        "brand-bg": default_of("Primary") or colors["blue"].get("700"),
        "brand-fg": "#ffffff",
        "danger-bg": default_of("Error") or colors["red"].get("700"),
        "success-bg": default_of("Success") or colors["green"].get("800"),
        "warning-bg": default_of("Warning") or colors["orange"].get("700"),
    }
    return {
        "palette": pal,
        "type": [{"name": n, "size": s, "weight": w, "line_height": lh} for n, s, w, lh in [
            ("caption", "0.75rem", 400, "1.66"), ("body2", "0.875rem", 400, "1.43"),
            ("body1", "1rem", 400, "1.5"), ("h6", "1.25rem", 500, "1.6"),
            ("h5", "1.5rem", 400, "1.334"), ("h4", "2.125rem", 400, "1.235")]],
        "radius": [{"name": "shape.borderRadius", "value": "4px"}],
        "space": [{"name": f"spacing({i})", "value": f"{i * 8}px"} for i in (0.5, 1, 2, 3, 4, 5, 6, 8)],
        "shadow": [{"name": "shadows[1]", "value": "0 2px 1px -1px rgba(0,0,0,.2), 0 1px 1px rgba(0,0,0,.14)"},
                   {"name": "shadows[4]", "value": "0 2px 4px -1px rgba(0,0,0,.2), 0 4px 5px rgba(0,0,0,.14)"},
                   {"name": "shadows[8]", "value": "0 5px 5px -3px rgba(0,0,0,.2), 0 8px 10px 1px rgba(0,0,0,.14)"}],
        "button": {
            "evidence": "material-ui/packages/mui-material/src/Button/Button.js",
            "height": "36.5px", "padding": "6px 16px", "radius": "4px",
            "font_size": "0.875rem", "font_weight": 500, "border_width": "1px",
            "uppercase": True,
            "variants": [
                {"label": "contained", "bg": pal["brand-bg"], "fg": "#ffffff", "border": "transparent"},
                {"label": "outlined", "bg": "transparent", "fg": pal["brand-bg"],
                 "border": "rgba(25,118,210,.5)"},
                {"label": "text", "bg": "transparent", "fg": pal["brand-bg"], "border": "transparent"},
                {"label": "contained · error", "bg": pal["danger-bg"], "fg": "#ffffff", "border": "transparent"},
            ],
        },
    }


# ─────────────────────────────────────────────────────────── Polaris
def polaris():
    prim = txt("polaris/polaris-tokens/src/colors.ts")
    fams = {}
    # `export const gray: Color = { 1: 'rgba(255, 255, 255, 1)', … }`
    for m in re.finditer(r"export const (\w+)(?::\s*\w+)?\s*=\s*\{(.*?)\n\};", prim, re.S):
        # 키 표기가 섞여 있다 — gray 는 `1:`, red 는 `'1':`
        fams[m.group(1)] = dict(re.findall(r"'?(\d+)'?:\s*'([^']+)'", m.group(2)))
    col = txt("polaris/polaris-tokens/src/themes/base/color.ts")

    def tok(name):
        m = re.search(rf"'{re.escape(name)}':\s*\{{\s*value:\s*([^,\n]+)", col)
        if not m:
            return None
        expr = m.group(1).strip().rstrip(",")
        if expr.startswith("'#"):
            return expr.strip("'")
        r = re.fullmatch(r"colors\.(\w+)\[(\d+)\]", expr)
        return fams.get(r.group(1), {}).get(r.group(2)) if r else None

    pal = {
        "surface": tok("color-bg"), "surface-raised": tok("color-bg-surface"),
        "text-primary": tok("color-text"), "text-secondary": tok("color-text-secondary"),
        "border": tok("color-border"),
        "brand-bg": tok("color-bg-fill-brand"), "brand-fg": tok("color-text-brand-on-bg-fill"),
        "danger-bg": tok("color-bg-fill-critical"), "success-bg": tok("color-bg-fill-success"),
        "warning-bg": tok("color-bg-fill-caution"),
    }
    # font/space/radius 는 값을 직접 쓰지 않고 size 스케일을 참조한다 (`value: size[300]`)
    size = dict(re.findall(r"'(\w+)':\s*'([^']+)'", txt("polaris/polaris-tokens/src/size.ts")))

    def sized(src, prefix):
        out = {}
        for m in re.finditer(rf"'{prefix}-(\w+)':\s*\{{\s*value:\s*([^,\n]+)", src):
            expr = m.group(2).strip().rstrip(",")
            r = re.fullmatch(r"size\[(\w+)\]", expr)
            val = size.get(r.group(1)) if r else (expr.strip("'") if expr.startswith("'") else None)
            if val:
                out[m.group(1)] = val
        return out

    fs = sized(txt("polaris/polaris-tokens/src/themes/base/font.ts"), "font-size")
    sp = sized(txt("polaris/polaris-tokens/src/themes/base/space.ts"), "space")
    br = sized(txt("polaris/polaris-tokens/src/themes/base/border.ts"), "border-radius")
    sh = dict(re.findall(r"'shadow-(\w+)':\s*\{\s*value:\s*'([^']+)'", txt("polaris/polaris-tokens/src/themes/base/shadow.ts")))
    return {
        "palette": pal,
        "type": [{"name": f"font-size-{k}", "size": v, "weight": 450, "line_height": None}
                 for k, v in sorted(fs.items(), key=lambda kv: _num(kv[0]))[:7]],
        "radius": [{"name": f"border-radius-{k}", "value": v} for k, v in list(br.items())[:6]],
        "space": [{"name": f"space-{k}", "value": v} for k, v in sorted(sp.items(), key=lambda kv: _num(kv[0]))[:8]],
        "shadow": [{"name": f"shadow-{k}", "value": v} for k, v in list(sh.items())[:4]],
        "button": {
            "evidence": "polaris/polaris-react/src/components/Button/Button.module.css",
            "height": "32px", "padding": "0 12px", "radius": br.get("200", "8px"),
            "font_size": fs.get("325", "0.8125rem"), "font_weight": 650, "border_width": "1px",
            "variants": [
                {"label": "primary", "bg": pal["brand-bg"], "fg": pal["brand-fg"], "border": "transparent"},
                {"label": "secondary", "bg": tok("color-bg-fill"), "fg": pal["text-primary"],
                 "border": pal["border"]},
                {"label": "tertiary", "bg": "transparent", "fg": pal["text-primary"], "border": "transparent"},
                {"label": "primary · critical", "bg": pal["danger-bg"],
                 "fg": tok("color-text-critical-on-bg-fill"), "border": "transparent"},
            ],
        },
    }


# ─────────────────────────────────────────────────────────── Ant Design
def antd():
    seed = txt("ant-design/components/theme/themes/seed.ts")
    sv = dict(re.findall(r"(\w+):\s*'?(#[0-9a-fA-F]{3,8}|\d+)'?", seed))
    presets = txt("ant-design/components/theme/themes/default/colors.ts")
    pal = {
        "surface": "#ffffff", "surface-raised": "#ffffff",
        "text-primary": "rgba(0, 0, 0, 0.88)", "text-secondary": "rgba(0, 0, 0, 0.65)",
        "border": "#d9d9d9",
        "brand-bg": sv.get("colorPrimary", "#1677ff"), "brand-fg": "#ffffff",
        "danger-bg": sv.get("colorError", "#ff4d4f"),
        "success-bg": sv.get("colorSuccess", "#52c41a"),
        "warning-bg": sv.get("colorWarning", "#faad14"),
    }
    fs = int(sv.get("fontSize", 14))
    return {
        "palette": pal,
        "type": [{"name": f"fontSize{n}", "size": f"{s}px", "weight": w, "line_height": None}
                 for n, s, w in [("SM", 12, 400), ("", fs, 400), ("LG", 16, 400),
                                 ("XL", 20, 400), ("Heading3", 24, 600), ("Heading2", 30, 600)]],
        "radius": [{"name": k, "value": f"{v}px"} for k, v in
                   [("borderRadiusXS", 2), ("borderRadiusSM", 4), ("borderRadius", 6), ("borderRadiusLG", 8)]],
        "space": [{"name": k, "value": f"{v}px"} for k, v in
                  [("paddingXXS", 4), ("paddingXS", 8), ("paddingSM", 12), ("padding", 16),
                   ("paddingMD", 20), ("paddingLG", 24), ("paddingXL", 32)]],
        "shadow": [{"name": "boxShadowTertiary",
                    "value": "0 1px 2px 0 rgba(0,0,0,.03), 0 1px 6px -1px rgba(0,0,0,.02)"},
                   {"name": "boxShadowSecondary",
                    "value": "0 6px 16px 0 rgba(0,0,0,.08), 0 3px 6px -4px rgba(0,0,0,.12)"}],
        "button": {
            "evidence": "ant-design/components/button/style/index.ts · theme/themes/seed.ts",
            "height": f"{sv.get('controlHeight', 32)}px", "padding": "0 15px",
            "radius": f"{sv.get('borderRadius', 6)}px",
            "font_size": f"{fs}px", "font_weight": 400, "border_width": "1px",
            "variants": [
                {"label": "primary · solid", "bg": pal["brand-bg"], "fg": "#ffffff", "border": "transparent"},
                {"label": "default · outlined", "bg": "#ffffff", "fg": pal["text-primary"],
                 "border": pal["border"]},
                {"label": "primary · filled", "bg": "#e6f4ff", "fg": pal["brand-bg"], "border": "transparent"},
                {"label": "danger · solid", "bg": pal["danger-bg"], "fg": "#ffffff", "border": "transparent"},
            ],
        },
    }


EXTRACTORS = {
    "Spectrum": spectrum, "Material Web": material_web, "MUI": mui, "Fluent 2": fluent,
    "Carbon": carbon, "Polaris": polaris, "shadcn/ui": shadcn, "Ant Design": antd,
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    result, missing = {}, []
    for name, fn in EXTRACTORS.items():
        d = fn()
        result[name] = d
        gaps = [k for k in SLOTS if not d["palette"].get(k)]
        if gaps:
            missing.append((name, gaps))
        print(f"{name:14s} palette {len(SLOTS) - len(gaps)}/{len(SLOTS)}  "
              f"type {len(d['type'])}  radius {len(d['radius'])}  space {len(d['space'])}  "
              f"button {len(d['button']['variants'])}")
    (OUT / "values.json").write_text(json.dumps({"slots": SLOTS, "systems": result},
                                                ensure_ascii=False, indent=1))
    if missing:
        print("\n해석 못한 슬롯 (해당 시스템에 그 개념이 없거나 별칭 체인이 끊긴 경우):")
        for name, gaps in missing:
            print(f"  {name:14s} {', '.join(gaps)}")
    print(f"\n-> {OUT / 'values.json'}")


if __name__ == "__main__":
    main()
