#!/usr/bin/env python3
"""파이프라인 전체 실행 — 의존 순서를 코드로 못박는다.

README 에 나열만 해두면 순서를 틀리게 돌려서 "선행 파일 없음"으로 실패하거나,
더 나쁘게는 낡은 중간 산출물로 리포트를 만들게 된다.

사용
  python3 analysis/standard-research/run.py            전체
  python3 analysis/standard-research/run.py --reports   렌더링만 (측정은 건너뜀)
  python3 analysis/standard-research/run.py --check     재현성 검사 (출력이 커밋된 것과 같은지)
"""
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent / "tools"
REPO = Path(__file__).resolve().parent.parent.parent

# (스크립트, 산출물, 선행 산출물) — 선행이 없으면 실행 전에 막는다
MEASURE = [
    ("extract_tokens.py",     "measured/tokens.json",      []),
    ("extract_values.py",     "measured/values.json",      ["curated/button-geometry.json"]),
    ("extract_components.py", "measured/components.json",  []),
    ("measure_dependency.py", "measured/dependency.json",  []),
]
DERIVE = [
    ("classify_tokens.py",    "derived/vocabulary.json",   ["measured/tokens.json"]),
    ("extract_naming.py",     "derived/naming.json",       ["measured/tokens.json"]),
    ("mfi.py",                "derived/mfi.json",          ["measured/components.json"]),
]
RENDER = [
    ("render_research.py",  "reports/design-system-standard-research.md",
     ["measured/tokens.json", "derived/vocabulary.json", "measured/components.json",
      "derived/mfi.json", "measured/dependency.json", "curated/button-api.json"]),
    ("render_visual.py",    "reports/design-system-standard-research-visual.html",
     ["derived/naming.json"]),
    ("render_specimens.py", "reports/design-system-specimens.html",
     ["measured/values.json"]),
]
RESEARCH = Path(__file__).resolve().parent


def run(stage, steps):
    print(f"\n\033[1m── {stage} ──\033[0m")
    for script, out, needs in steps:
        gaps = [n for n in needs if not (RESEARCH / n).exists()]
        if gaps:
            print(f"  ✗ {script} — 선행 산출물 없음: {', '.join(gaps)}")
            return False
        r = subprocess.run([sys.executable, str(TOOLS / script)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"  ✗ {script}\n{r.stdout[-1500:]}{r.stderr[-1500:]}")
            return False
        size = (RESEARCH / out).stat().st_size if (RESEARCH / out).exists() else 0
        print(f"  ✓ {script:24s} → {out:52s} {size:>9,}B")
        if r.stderr.strip():
            for line in r.stderr.strip().splitlines():
                print(f"      ⚠ {line}")
    return True


def main():
    args = set(sys.argv[1:])
    stages = ([("측정 (sources → measured)", MEASURE),
               ("파생 (measured → derived)", DERIVE)]
              if "--reports" not in args else [])
    stages.append(("렌더 (→ reports)", RENDER))

    for name, steps in stages:
        if not run(name, steps):
            print("\n중단됨.")
            return 1

    if "--check" in args:
        print("\n\033[1m── 재현성 검사 ──\033[0m")
        r = subprocess.run(["git", "status", "--porcelain",
                            "analysis/standard-research"],
                           cwd=REPO, capture_output=True, text=True)
        dirty = [l for l in r.stdout.splitlines() if l.strip()]
        if dirty:
            print("  ✗ 재실행 결과가 커밋된 것과 다릅니다:")
            for l in dirty:
                print(f"      {l}")
            return 1
        print("  ✓ 재실행 결과가 커밋된 것과 동일합니다 (diff 0)")
    print("\n완료.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
