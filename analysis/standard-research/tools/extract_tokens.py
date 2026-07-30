#!/usr/bin/env python3
"""각 시스템 소스에서 semantic 토큰 이름을 추출해 정규화한다.

입력: sources/<repo>/... (sources/MANIFEST.md 의 고정 커밋)
출력: measured/tokens.json  — {system: {"names": [...], "source": "...", "layer": "..."}}

집계 규칙
- semantic(alias) 계층만 수집한다. primitive 램프(gray-100 등)는 제외 — 표준화 대상이 아니다.
- 이름은 kebab-case 로 정규화하고 시스템 접두사(--md-sys-, --spectrum-, color 등)를 제거하지 않는다.
  (접두사 제거는 classify_tokens.py 가 담당)
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

SRC = paths.SOURCES


def read(p):
    return (SRC / p).read_text(encoding="utf-8", errors="replace")


def camel_to_kebab(s):
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", s)
    s = re.sub(r"(?<=[A-Z])(?=[A-Z][a-z])", "-", s)
    return s.lower()


# ---------------------------------------------------------------- Spectrum
def spectrum():
    """spectrum-design-data: DTCG 유사 JSON. color-aliases + layout + typography 의 최상위 키."""
    names = set()
    base = SRC / "spectrum-tokens/packages/tokens/src"
    for f in ["color-aliases.json", "semantic-color-palette.json", "layout.json", "typography.json"]:
        p = base / f
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        for k, v in d.items():
            if k.startswith("$"):
                continue
            if isinstance(v, dict):
                names.add(k)
    return names, "spectrum-tokens/packages/tokens/src/{color-aliases,semantic-color-palette,layout,typography}.json", "alias(semantic)"


# ---------------------------------------------------------------- Material
def material_web():
    """material-web: tokens/_md-sys-*.scss 의 $supported-tokens + versions/*/의 실제 토큰 맵.

    최상위 _md-sys-state.scss 등 일부는 versions/v0_192/ 로 위임만 하므로 양쪽을 모두 읽는다.
    """
    names = set()
    for base in [SRC / "material-web/tokens", SRC / "material-web/tokens/versions/v0_192"]:
        if not base.exists():
            continue
        for p in sorted(base.glob("_md-sys-*.scss")):
            cat = p.stem.replace("_md-sys-", "")
            txt = p.read_text()
            m = re.search(r"\$supported-tokens:\s*\((.*?)\n\);", txt, re.S)
            if m:
                for tok in re.findall(r"'([^']+)'", m.group(1)):
                    names.add(f"{cat}-{tok}")
            # values() 맵의 키 (state 등 supported-tokens 목록이 없는 파일)
            for tok in re.findall(r"^\s+'([a-z0-9][a-z0-9-]*)':", txt, re.M):
                names.add(f"{cat}-{tok}")
    return names, "material-web/tokens/{,versions/v0_192/}_md-sys-*.scss", "sys(semantic)"


def mui():
    """MUI: styles/*.d.ts 의 타입 선언이 semantic 표면의 정본.

    interface/type 블록 멤버를 읽어 알려진 루트 타입에서 이름을 전개한다.
    """
    base = SRC / "material-ui/packages/mui-material/src/styles"
    ifaces = {}
    for p in base.glob("*.d.ts"):
        txt = p.read_text()
        for m in re.finditer(r"(?:interface|type)\s+(\w+)(?:\s*=)?\s*\{(.*?)\n\}", txt, re.S):
            members = re.findall(r"^\s{2}(\w+)\??[:\s]", m.group(2), re.M)
            if members:
                ifaces.setdefault(m.group(1), set()).update(members)

    names = set()

    def expand(prefix, tname):
        for mem in sorted(ifaces.get(tname, ())):
            names.add(f"{prefix}-{camel_to_kebab(mem)}" if prefix else camel_to_kebab(mem))

    for intent in ["primary", "secondary", "error", "warning", "info", "success"]:
        expand(f"palette-{intent}", "PaletteColor")
    expand("palette-text", "TypeText")
    expand("palette-action", "TypeAction")
    expand("palette-background", "TypeBackground")
    expand("palette-common", "CommonColors")
    names.add("palette-divider")
    # 타이포그래피: variant union + FontStyle 멤버 (TypographyVariants 는 상속 전용이라 멤버가 없다)
    tp = base / "createTypography.d.ts"
    if tp.exists():
        txt = tp.read_text()
        um = re.search(r"type TypographyVariant\s*=(.*?);", txt, re.S)
        if um:
            for v in re.findall(r"'([^']+)'", um.group(1)):
                names.add(f"typography-{camel_to_kebab(v)}")
        expand("typography", "FontStyle")
    expand("z-index", "ZIndex")
    expand("transitions-duration", "Duration")
    expand("transitions-easing", "Easing")
    names.update({"shape-border-radius", "spacing"})
    for i in range(25):  # shadows[0..24] — elevation 스케일
        names.add(f"shadows-{i}")
    names.discard("")
    return names, "material-ui/packages/mui-material/src/styles/*.d.ts (타입 선언)", "palette/typography/shape(semantic)"


# ---------------------------------------------------------------- Fluent 2
def fluent():
    """Fluent 2: packages/tokens/src/alias/lightColor.ts 의 키 + global size/font 토큰."""
    names = set()
    p = SRC / "fluentui/packages/tokens/src/alias/lightColor.ts"
    if p.exists():
        for m in re.finditer(r"^\s{2}(\w+):", p.read_text(), re.M):
            names.add(camel_to_kebab(m.group(1)))
    # tokens.ts 가 CSS var 이름의 정본. 화이트리스트를 두면 colorStatus* 등이 통째로 빠진다.
    p2 = SRC / "fluentui/packages/tokens/src/tokens.ts"
    if p2.exists():
        for m in re.finditer(r"var\(--([a-zA-Z][a-zA-Z0-9]*)\)", p2.read_text()):
            names.add(camel_to_kebab(m.group(1)))
    names.discard("")
    return names, "fluentui/packages/tokens/src/{alias/lightColor.ts,tokens.ts}", "alias(semantic)"


# ---------------------------------------------------------------- Carbon
def carbon():
    """Carbon: 색상은 themes/dtcg (DTCG), 그 외는 layout/type/motion 패키지의 unstable_tokens.

    dtcg/white.json 은 *색상 테마* 하나뿐이므로 여기만 읽으면 spacing/type/motion 이 통째로 빠진다.
    """
    names = set()
    p = SRC / "carbon/packages/themes/src/dtcg/white.json"
    if p.exists():
        d = json.loads(p.read_text())

        def walk(node, prefix=""):
            for k, v in node.items():
                if k.startswith("$"):
                    continue
                path = f"{prefix}-{k}" if prefix else k
                if isinstance(v, dict):
                    if "$value" in v:
                        names.add(path)
                    else:
                        walk(v, path)

        walk(d)
    # 비색상 계층
    for pkg in ["layout", "type", "motion", "elements"]:
        tp = SRC / f"carbon/packages/{pkg}/src/tokens.ts"
        if not tp.exists():
            continue
        for tok in re.findall(r"^\s+'([A-Za-z0-9_]+)',", tp.read_text(), re.M):
            names.add(camel_to_kebab(tok))
    # 타이포 스케일·모션 커브는 별도 파일
    for rel in ["carbon/packages/type/src/styles.ts", "carbon/packages/motion/src/index.ts"]:
        tp = SRC / rel
        if tp.exists():
            for tok in re.findall(r"^export const ([a-zA-Z0-9_]+)", tp.read_text(), re.M):
                names.add(camel_to_kebab(tok))
    return names, "carbon/packages/{themes/src/dtcg/white.json, layout|type|motion|elements/src/tokens.ts}", "theme(semantic, DTCG) + scale"


# ---------------------------------------------------------------- Polaris
def polaris():
    """Polaris: polaris-tokens/src/themes/base/*.ts 의 토큰 키."""
    names = set()
    base = SRC / "polaris/polaris-tokens/src/themes/base"
    for p in sorted(base.glob("*.ts")):
        if p.stem in ("index", "types"):
            continue
        txt = p.read_text()

        def qualify(key, stem=None):
            """스템을 무조건 붙이면 안 된다 — color.ts 의 객체 키는 이미 `color-` 로 시작한다.
            그대로 붙이면 `color-color-bg-fill-brand` 와 `color-bg-fill-brand` 가 둘 다 생겨
            같은 토큰이 두 번 세어진다 (Polaris 가 820개로 부풀었던 원인).
            """
            stem = stem or p.stem
            return key if key == stem or key.startswith(stem + "-") else f"{stem}-{key}"

        # 실제 토큰 객체 키: '  'token-name': {' 또는 "  'token-name': '"
        for m in re.finditer(r"^\s{2}'([a-z0-9][a-z0-9-]*)':", txt, re.M):
            names.add(qualify(m.group(1)))
        # union 타입 선언에서도 수집 (color.ts 는 타입으로만 나열)
        for m in re.finditer(r"^\s*\|\s*'([a-z0-9][a-z0-9-]*)'", txt, re.M):
            names.add(qualify(m.group(1)))
    return names, "polaris/polaris-tokens/src/themes/base/*.ts", "base theme(semantic)"


# ---------------------------------------------------------------- shadcn/ui
def shadcn():
    """shadcn/ui: apps/v4/app/globals.css 의 :root CSS 변수 (@theme inline 매핑 포함)."""
    names = set()
    p = SRC / "shadcn-ui/apps/v4/app/globals.css"
    if p.exists():
        txt = p.read_text()
        for m in re.finditer(r"^\s*--([a-z0-9][a-z0-9-]*)\s*:", txt, re.M):
            names.add(m.group(1))
    return names, "shadcn-ui/apps/v4/app/globals.css (:root CSS vars)", "semantic(단층)"


# ---------------------------------------------------------------- Ant Design
def antd():
    """Ant Design: components/theme/interface/{seeds,maps,alias}.ts 의 인터페이스 필드."""
    names = set()
    base = SRC / "ant-design/components/theme/interface"
    files = list(base.glob("*.ts")) + list((base / "maps").glob("*.ts"))
    for p in files:
        if p.stem in ("index", "cssinjs-utils", "components", "presetColors"):
            continue
        for m in re.finditer(r"^\s{2}(\w+)\??:\s*(?:string|number|CSSProperties)", p.read_text(), re.M):
            names.add(camel_to_kebab(m.group(1)))
    names.discard("")
    return names, "ant-design/components/theme/interface/{seeds,alias,maps/*}.ts", "seed→map→alias"


EXTRACTORS = {
    "Spectrum": spectrum,
    "Material Web": material_web,
    "MUI": mui,
    "Fluent 2": fluent,
    "Carbon": carbon,
    "Polaris": polaris,
    "shadcn/ui": shadcn,
    "Ant Design": antd,
}


def main():
    result = {}
    for name, fn in EXTRACTORS.items():
        # 예외를 삼키고 빈 집합을 넣으면 한 시스템이 0개인 채로 "8개 시스템 리포트" 가
        # 만들어진다. 고정 소스의 구조가 바뀐 것이므로 파이프라인을 세우는 게 맞다.
        names, source, layer = fn()
        if not names:
            raise ValueError(f"{name}: 토큰을 하나도 추출하지 못했습니다 — "
                             f"소스 구조가 바뀐 것 같습니다 ({source})")
        result[name] = {
            "count": len(names),
            "layer": layer,
            "source": source,
            "names": sorted(names),
        }
        print(f"{name:14s} {len(names):5d}  {layer:22s} {source}")
    p = paths.write_json("tokens", result)
    print(f"\n-> {p}")


if __name__ == "__main__":
    main()
