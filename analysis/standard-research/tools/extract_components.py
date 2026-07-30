#!/usr/bin/env python3
"""컴포넌트 인벤토리를 추출해 정규 개념(canonical component)으로 매핑하고 교집합을 구한다.

입력: sources/ + figma/raw/*-components-extracted.json
출력: measured/components.json

집계 규칙
- 코드 인벤토리는 "공개 컴포넌트 디렉터리/파일 1개 = 1건". 내부 유틸(`_`, `internal`, `utils`,
  `testing` 등)과 테스트는 제외한다.
- 시스템마다 분해 단위가 달라(Carbon 은 DataTable 하위를 개별 디렉터리로 둔다) 절대 수치는
  비교하지 않는다. 정규 개념으로 접은 뒤의 *커버리지*만 비교한다.
"""
import json
import re
from collections import defaultdict
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

SRC = paths.SOURCES
FIGMA = paths.FIGMA_RAW

EXCLUDE = re.compile(
    # ⚠️ 경계 없는 조각은 실제 컴포넌트를 잡는다. 아래는 그 사고를 겪고 좁힌 결과다.
    #   `spec`  → A**spec**tRatio · aspect-ratio 를 버렸다      → (^|-)spec
    #   `index` → Polaris IndexTable · IndexFilters 를 버렸다   → ^index$
    #   `colors?$` → Spectrum 의 color(ColorPicker 계열)를 버렸다 → ^colors$ (복수만)
    #   `images?` → Image 컴포넌트를 버렸다                      → 제거
    r"^(_|\.)|internal|(^|-|\.)spec(s|$|-|\.)|test|stories|legacy|unstable|deprecated|"
    r"^(index|types?|constants?|styles?|hooks?|context|shared|helpers?|locales?|"
    r"version|theme|themes|tokens?|colors|typography-tokens|experimental|next|"
    r"utils?|util)$|"
    # 컴포넌트가 아닌 인프라/문서 디렉터리 (material-web: catalog, docs, labs, focus, ripple …)
    r"^(catalog|docs?|labs?|focus|ripple|elevation|css|scripts?|testing|tools?|"
    r"node_modules|dist|build|examples?|demo|site|assets?|fonts?|"
    r"polyfills?|patches?|config|codemod.*|migration.*|template.*|"
    r"transitions?|zero-styled|generate-utility-class.*|class-name.*|"
    r"use-[a-z-]+|with-[a-z-]+|create-[a-z-]+|sass|scss|aria|positioning|tabster)$"
)

# 정규 개념 -> 별칭 정규식. 다수 시스템이 같은 개념을 다른 이름으로 부른다.
# canonicalize 는 좁은 패턴(`.*` 없음)을 전부 시도한 뒤 넓은 패턴으로 넘어간다.
# 그래서 `.*-button` 이 IconButton·ToggleButton·Radio 를 삼키지 않는다.
# 같은 표 안에서는 위에 있는 것이 이긴다 — 겹치는 좁은 패턴끼리는 순서를 신경 써야 한다.
CANON = {
    "IconButton":      r"^icon-?button$",
    "ToggleButton":    r"^(toggle-?button|switch-?button)$",
    "ButtonGroup":     r"^(button-?group|segmented|toggle-?button-?group|action-?group)$",
    "Button":          r"^(button|action-?button|md-?button|.*-button)$",
    "Link":            r"^(link|anchor)$",
    "TextInput":       r"^(input|text-?field|text-?input|textbox|filled-?text-?field)$",
    "Textarea":        r"^(textarea|text-?area)$",
    "NumberInput":     r"^(number-?field|number-?input|input-?number)$",
    "PasswordInput":   r"^(password-?input|password-?field)$",
    "SearchInput":     r"^(search|search-?field|search-?input)$",
    "Calendar":        r"^(calendar|range-?calendar)$",
    "Select":          r"^(select|picker|dropdown|native-?select)$",
    "Combobox":        r"^(combo-?box|autocomplete|auto-?complete)$",
    "Checkbox":        r"^(checkbox|check-?box)$",
    "Radio":           r"^(radio|radio-?group|radio-?button)$",
    "Switch":          r"^(switch|toggle)$",
    "Slider":          r"^(slider|range-?slider|range-?calendar)?$|^slider$",
    "DatePicker":      r"^(date-?picker|date-?input|date-?field)$",
    "TimePicker":      r"^(time-?picker|time-?field|time-?input)$",
    "FileUpload":      r"^(file-?upload|file-?uploader|file-?trigger|upload|drop-?zone|dropzone)$",
    "Form":            r"^(form|form-?group|form-?item|fieldset|form-?layout)$",
    # 폼 *필드 래퍼*(label+control+help+error 묶음)는 Form 컨테이너와 다른 개념이다.
    "Field":           r"^(field|form-?field|form-?control|input-?wrapper)$",
    "Label":           r"^(label|form-?label)$",
    "Dialog":          r"^(dialog|modal|alert-?dialog)$",
    "Drawer":          r"^(drawer|sheet|side-?panel|side-?nav-?panel|tray)$",
    "Popover":         r"^(popover|overlay|flyout)$",
    "Tooltip":         r"^(tooltip|tool-?tip)$",
    "Menu":            r"^(menu|dropdown-?menu|context-?menu|overflow-?menu|action-?list|action-?menu)$",
    "Toast":           r"^(toast|snackbar|toaster|notification-?toast)$",
    "Alert":           r"^(alert|banner|inline-?message|message|message-?bar|inline-?alert|callout-?card|notification)$",
    "Tabs":            r"^(tabs|tab|tab-?list|tab-?panel)$",
    "Breadcrumbs":     r"^(breadcrumb|breadcrumbs)$",
    "Pagination":      r"^(pagination|paginator|paginat.*)$",
    "Stepper":         r"^(stepper|steps|progress-?stepper|progress-?indicator)$",
    "Navigation":      r"^(nav|navbar|navigation|side-?nav|top-?nav|header|ui-?shell|menu-?bar|app-?bar|tab-?bar|footer|layout)$",
    "Table":           r"^(table|data-?table|data-?grid|table-?view|grid-?list)$",
    "List":            r"^(list|list-?box|list-?view|ordered-?list|unordered-?list|resource-?list|list-?item)$",
    "Tree":            r"^(tree|tree-?view|tree-?grid|tree-?select)$",
    "Card":            r"^(card|tile|elevated-?card|filled-?card|outlined-?card)$",
    "Accordion":       r"^(accordion|collapse|disclosure|expandable|details)$",
    "Badge":           r"^(badge|tag|chip|pill|label-?badge|status-?badge)$",
    "Avatar":          r"^(avatar|avatar-?group|persona)$",
    "Icon":            r"^(icon|icons|svg-?icon|icon-?indicator)$",
    "Image":           r"^(image|img|thumbnail|media)$",
    "Progress":        r"^(progress|progress-?bar|progress-?circle|linear-?progress|circular-?progress|meter)$",
    "Spinner":         r"^(spinner|loading|loader|activity-?indicator|circular-?progress-?indicator)$",
    "Skeleton":        r"^(skeleton|skeleton-?text|skeleton-?placeholder|shimmer)$",
    "Divider":         r"^(divider|separator|hr)$",
    "Tooltip/Toggletip": r"^(toggletip|contextual-?help)$",
    "Layout":          r"^(grid|stack|flex|box|container|inline|view|space|row|col|column|layout-?grid|content-?layout|page)$",
    "Typography":      r"^(text|typography|heading|title|paragraph)$",
    "InlineCode":      r"^(code|kbd|blockquote|snippet|code-?snippet)$",
    "Chart":           r"^(chart|charts|sparkline|data-?viz)$",
    "Carousel":        r"^(carousel|slideshow)$",
    "Rating":          r"^(rate|rating|star-?rating)$",
    "ColorPicker":     r"^(color-?picker|color-?area|color-?field|color-?slider|color-?swatch|color-?wheel)$",
    "Command":         r"^(command|command-?palette|quick-?search)$",
    "Tag/TokenInput":  r"^(tag-?group|tag-?field|token-?field|chips)$",
    "Toolbar":         r"^(toolbar|action-?bar|button-?bar)$",
    "Empty":           r"^(empty|empty-?state|empty-?search-?result)$",
    "Scroll":          r"^(scroll-?area|scrollbar|scroller)$",
    "Resizable":       r"^(resizable|splitter|split-?view)$",
}

# 코드 인벤토리 소스: (system, glob 루트, 방식)
CODE_SOURCES = {
    "Spectrum":     ("react-spectrum/packages/@adobe/react-spectrum/src", "dir"),
    "Material Web": ("material-web", "dir"),
    "MUI":          ("material-ui/packages/mui-material/src", "dir"),
    "Fluent 2":     ("fluentui/packages/react-components", "dir:react-"),
    "Carbon":       ("carbon/packages/react/src/components", "dir"),
    "Polaris":      ("polaris/polaris-react/src/components", "dir"),
    "shadcn/ui":    ("shadcn-ui/apps/v4/registry/new-york-v4/ui", "tsx"),
    "Ant Design":   ("ant-design/components", "dir"),
}

FIGMA_KITS = {
    "Carbon": "carbon", "Fluent 2": "fluent2",
    "Material Web": "material3", "Spectrum": "spectrum",
}


def kebab(s):
    s = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "-", s)
    return s.lower()


# `.*` 가 든 패턴은 넓다 (`.*-button`). 좁은 패턴을 먼저 다 시도한 뒤 넓은 것으로 넘어간다.
# 순서만 조정하면 `RadioButton` 처럼 나중에 추가되는 전문 개념이 또 삼켜진다 —
# 우선순위를 사람이 기억해야 하는 구조 자체를 없앤다.
SPECIFIC = {k: v for k, v in CANON.items() if ".*" not in v}
BROAD = {k: v for k, v in CANON.items() if ".*" in v}


def canonicalize(raw):
    n = kebab(raw)
    for table in (SPECIFIC, BROAD):
        for canon, pat in table.items():
            if re.match(pat, n):
                return canon
    return None


def code_inventory():
    out = {}
    for system, (rel, mode) in CODE_SOURCES.items():
        base = SRC / rel
        raw = []
        if not base.exists():
            out[system] = {"raw_count": 0, "error": f"경로 없음: {rel}"}
            continue
        if mode == "tsx":
            raw = [p.stem for p in base.glob("*.tsx")]
        elif mode.startswith("dir:"):
            pre = mode.split(":", 1)[1]
            # 이름으로 인프라를 걸러내면 목록을 계속 손봐야 한다. 구조로 판정한다 —
            # Fluent v9 는 컴포넌트를 내보내는 패키지에만 library/src/components 가 있다.
            # aria · utilities · positioning · tabster · jsx-runtime · storybook-addon ·
            # conformance-griffel · theme-sass 에는 이 디렉터리가 없다.
            raw = [p.name[len(pre):] for p in base.iterdir()
                   if p.is_dir() and p.name.startswith(pre)
                   and (p / "library/src/components").is_dir()]
        else:
            raw = [p.name for p in base.iterdir() if p.is_dir()]
        dropped = {r for r in raw if EXCLUDE.search(kebab(r))}
        raw = [r for r in raw if r not in dropped]
        mapped = defaultdict(list)
        unmapped = []
        for r in raw:
            c = canonicalize(r)
            (mapped[c].append(r) if c else unmapped.append(r))
        out[system] = {
            "raw_count": len(raw),
            "dropped_infra": sorted(dropped),  # 조용히 버리지 않는다
            "source": rel,
            "canonical": {k: sorted(v) for k, v in sorted(mapped.items())},
            "unmapped": sorted(unmapped),
        }
    return out


def figma_variant_axes():
    """Figma 킷의 variant property 이름 빈도 — variant 축 표준화 판정 재료."""
    out = {}
    for system, key in FIGMA_KITS.items():
        p = FIGMA / f"{key}-components-extracted.json"
        if not p.exists():
            continue
        d = json.loads(p.read_text())
        axes = defaultdict(int)
        vals = defaultdict(set)
        for cs in d["component_sets"]:
            for axis, spec in (cs.get("variant_properties") or {}).items():
                a = kebab(axis)
                axes[a] += 1
                for v in (spec.get("values") or [])[:40]:
                    vals[a].add(str(v))
        total = len(d["component_sets"])
        # variant 조합 폭발량 — SET 하나가 몇 개 인스턴스로 전개되는가
        counts = sorted((cs.get("variant_count") or 0) for cs in d["component_sets"])
        top = sorted(d["component_sets"], key=lambda c: -(c.get("variant_count") or 0))[:8]
        buckets = {"1-4": 0, "5-12": 0, "13-32": 0, "33-96": 0, "97+": 0}
        for c in counts:
            if c <= 4:
                buckets["1-4"] += 1
            elif c <= 12:
                buckets["5-12"] += 1
            elif c <= 32:
                buckets["13-32"] += 1
            elif c <= 96:
                buckets["33-96"] += 1
            else:
                buckets["97+"] += 1
        out[system] = {
            "component_sets": total,
            "variants_total": sum(counts),
            "variants_median": counts[len(counts) // 2] if counts else 0,
            "variants_max": counts[-1] if counts else 0,
            "variants_per_set": round(sum(counts) / total, 1) if total else 0,
            "variant_buckets": buckets,
            "axes_per_set": round(sum(len(cs.get("variant_properties") or {})
                                      for cs in d["component_sets"]) / total, 2) if total else 0,
            "top_exploded": [{"name": c["name"], "variants": c.get("variant_count") or 0,
                              "axes": len(c.get("variant_properties") or {})} for c in top],
            "axes": {a: {"used_in": c, "pct": round(c / total * 100, 1),
                         "values": sorted(vals[a])[:20]}
                     for a, c in sorted(axes.items(), key=lambda kv: -kv[1])},
        }
    return out


def main():
    inv = code_inventory()
    systems = [s for s in inv if "error" not in inv[s]]

    # 정규 개념별 커버리지
    coverage = []
    for canon in CANON:
        have = [s for s in systems if canon in inv[s].get("canonical", {})]
        coverage.append({
            "component": canon,
            "coverage": len(have),
            "systems": have,
            "missing": [s for s in systems if s not in have],
            "aliases": {s: inv[s]["canonical"][canon] for s in have},
        })
    coverage.sort(key=lambda r: (-r["coverage"], r["component"]))

    result = {
        "systems": systems,
        "system_count": len(systems),
        "inventory": inv,
        "coverage": coverage,
        "figma_variant_axes": figma_variant_axes(),
    }
    out_path = paths.write_json("components", result)

    print("=== 코드 인벤토리 ===")
    for s in systems:
        i = inv[s]
        print(f"  {s:14s} 원시 {i['raw_count']:4d} → 정규 {len(i['canonical']):3d}개 개념, 미매핑 {len(i['unmapped']):3d}")
    n = len(systems)
    print(f"\n=== 정규 컴포넌트 커버리지 ({n}개 시스템) ===")
    for r in coverage:
        if r["coverage"] >= 2:
            print(f"  {r['coverage']}/{n}  {r['component']:20s} 미보유: {', '.join(r['missing']) or '-'}")
    print("\n=== Figma variant 축 (상위) ===")
    for s, d in result["figma_variant_axes"].items():
        top = list(d["axes"].items())[:6]
        print(f"  {s:14s} ({d['component_sets']} sets): " + ", ".join(f"{a}({v['pct']}%)" for a, v in top))
    print(f"\n-> {out_path}")


if __name__ == "__main__":
    main()
