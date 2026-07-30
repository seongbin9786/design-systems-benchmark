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
SOURCES = REPO / "sources"
MANIFEST = SOURCES / "MANIFEST.md"


def preflight():
    """측정 전에 *소스가 전부 있고 매니페스트 SHA 와 같은지* 확인한다.

    중간 산출물만 검사하면 부분 클론을 못 잡는다. 추출기들은 없는 소스에 대해
    빈 값을 돌려주고 성공으로 끝나므로, 일부만 받은 상태에서도 리포트가 나온다 —
    토큰은 8개 시스템, 컴포넌트는 6개 시스템 같은 뒤섞인 결과가 만들어진다.
    clone.sh 가 키 단위 클론을 지원하니 실제로 일어날 수 있는 상황이다.

    SHA 만 봐서도 안 된다. 소스를 들여다보다 파일을 고치면 HEAD 는 그대로이므로
    "매니페스트 커밋을 재면 이 결과가 나온다" 는 주장이 거짓이 된다. 작업 트리가
    깨끗한지도 확인한다 (추적 파일 변경 · 미추적 파일 둘 다).
    """
    import re
    import subprocess

    if not MANIFEST.exists():
        print(f"  ✗ {MANIFEST} 가 없습니다 — `bash sources/clone.sh` 를 먼저 실행하세요")
        return False

    man = MANIFEST.read_text(encoding="utf-8")
    want = dict(re.findall(r"\|\s*`([\w-]+)`\s*\|[^|]*\|\s*`([0-9a-f]{40})`", man))
    # 매니페스트 마지막 열의 sparse 경로도 대조한다 — HEAD 가 맞아도 sparse 가 좁혀져 있으면
    # 파일이 없는데 작업 트리는 깨끗해서 SHA 검사만으로는 통과한다.
    want_sparse = {}
    for row in man.splitlines():
        m = re.match(r"\|\s*`([\w-]+)`\s*\|", row)
        if not m:
            continue
        cols = [c.strip() for c in row.strip("|").split("|")]
        if len(cols) >= 7 and cols[6] != "(전체)":
            want_sparse[m.group(1)] = sorted(cols[6].split())
    if not want:
        print("  ✗ MANIFEST.md 에서 전체 SHA 를 읽지 못했습니다")
        return False

    bad = []
    for key, sha in sorted(want.items()):
        d = SOURCES / key
        if not (d / ".git").is_dir():
            bad.append((key, "없음"))
            continue
        cur = subprocess.run(["git", "-C", str(d), "rev-parse", "HEAD"],
                             capture_output=True, text=True).stdout.strip()
        if cur != sha:
            bad.append((key, f"HEAD {cur[:7]} ≠ 매니페스트 {sha[:7]}"))
            continue
        # sparse-checkout 을 쓰므로 `--porcelain` 은 체크아웃 밖 파일을 보고하지 않는다.
        dirty = subprocess.run(["git", "-C", str(d), "status", "--porcelain",
                                "--untracked-files=normal"],
                               capture_output=True, text=True).stdout.strip()
        if dirty:
            n = len(dirty.splitlines())
            first = dirty.splitlines()[0].strip()
            bad.append((key, f"로컬 변경 {n}건 (예: {first}) — HEAD 는 맞지만 내용이 다르다"))
            continue
        exp = want_sparse.get(key)
        if exp:
            got = sorted(subprocess.run(["git", "-C", str(d), "sparse-checkout", "list"],
                                        capture_output=True, text=True).stdout.split())
            if got != exp:
                bad.append((key, f"sparse 경로 {len(got)}개 ≠ 매니페스트 {len(exp)}개 — 파일이 빠져 있다"))

    if bad:
        print(f"  ✗ 소스 {len(bad)}/{len(want)}개가 매니페스트와 어긋납니다:")
        for key, why in bad:
            print(f"      {key:18s} {why}")
        print("    `bash sources/clone.sh` 로 맞추거나, 로컬 변경은 `git -C sources/<key>`")
        print("    에서 되돌리세요. 이 상태로 측정하면 리포트가 주장하는 커밋과 실제로 잰")
        print("    내용이 어긋납니다.")
        return False
    print(f"  ✓ 소스 {len(want)}/{len(want)}개가 매니페스트 SHA 와 일치")
    return True


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

    if "--reports" not in args:
        print("\n\033[1m── 사전 검사 (소스 == MANIFEST) ──\033[0m")
        if not preflight():
            print("\n중단됨.")
            return 1

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
